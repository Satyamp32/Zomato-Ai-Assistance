import os
import json
from typing import List
from groq import Groq
from dotenv import load_dotenv
from milestone1.phase4_llm.models import LLMRecommendation

def get_groq_client():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is missing from environment variables.")
    return Groq(api_key=api_key)

def recommend_with_groq(prompt_payload: str, top_k: int = 5) -> List[LLMRecommendation]:
    """
    Calls the Groq API to get recommendations formatted as JSON.
    If it fails, raises an Exception.
    """
    client = get_groq_client()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt_payload
            }
        ],
        model=model,
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=1500,
    )
    
    # We expect the LLM to output a JSON object with a list of recommendations
    # e.g., {"recommendations": [{"restaurant_name": "...", "explanation": "..."}]}
    content = response.choices[0].message.content
    
    try:
        data = json.loads(content)
        # Handle cases where the LLM might return a list directly or under a key
        if isinstance(data, dict):
            # Try to find a list value
            for key, val in data.items():
                if isinstance(val, list):
                    raw_list = val
                    break
            else:
                raw_list = [data] # Fallback if it's just a single object
        elif isinstance(data, list):
            raw_list = data
        else:
            raise ValueError("Unexpected JSON format returned by LLM")
            
        recs = []
        for item in raw_list[:top_k]:
            recs.append(LLMRecommendation(**item))
            
        return recs
        
    except Exception as e:
        raise ValueError(f"Failed to parse LLM output: {e}\nRaw content:\n{content}")
