import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import our internal logic
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase2_preferences.parser import parse_preferences
from milestone1.phase1_ingestion.loader import load_restaurants
from milestone1.phase3_integration.filter import filter_and_rank
from milestone1.phase3_integration.prompt_builder import build_prompt_payload
from milestone1.phase4_llm.client import recommend_with_groq
from milestone1.phase4_llm.models import LLMRecommendation

app = FastAPI(title="Zomato AI Recommendation API", version="1.0.0")

# Setup CORS (Allowing * for Vercel production deployment URLs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationResponse(BaseModel):
    status: str
    message: str
    candidates_analyzed: int
    recommendations: List[LLMRecommendation]

@app.get("/health")
def health_check():
    has_groq = bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here")
    return {"status": "ok", "groq_configured": has_groq}

@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
def get_recommendations(prefs: UserPreferences, limit: int = 200, top_k: int = 5):
    try:
        # Load restaurants (uses limit due to Hugging Face stream constraints)
        restaurants = load_restaurants(limit=limit)
        
        # Filter and rank candidates
        filtered = filter_and_rank(prefs, restaurants)
        if not filtered:
            return RecommendationResponse(
                status="no_candidates",
                message="No restaurants match your exact filters. Try adjusting your location or budget.",
                candidates_analyzed=len(restaurants),
                recommendations=[]
            )
            
        # Build prompt
        prompt = build_prompt_payload(prefs, filtered)
        
        # Call LLM
        recs = recommend_with_groq(prompt, top_k=top_k)
        
        return RecommendationResponse(
            status="success",
            message="Recommendations generated successfully.",
            candidates_analyzed=len(filtered),
            recommendations=recs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
