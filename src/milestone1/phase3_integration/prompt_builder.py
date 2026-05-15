import json
from typing import List
from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences

def build_prompt_payload(preferences: UserPreferences, candidates: List[Restaurant]) -> str:
    """
    Constructs the prompt for the LLM combining user preferences and the filtered candidate list.
    """
    system_instructions = (
        "You are an AI restaurant recommendation assistant for Zomato.\n"
        "Your task is to recommend restaurants from the provided candidate list based on the user's preferences.\n"
        "Rules:\n"
        "1. ONLY recommend restaurants present in the Candidate List. Do not hallucinate.\n"
        "2. Provide an explanation for each recommendation detailing why it fits.\n"
        "3. Output MUST be in structured JSON format as a list of dictionaries with keys: 'restaurant_name', 'explanation'.\n"
    )
    
    user_pref_text = (
        f"Location: {preferences.location}\n"
        f"Budget: {preferences.budget}\n"
        f"Preferred Cuisines: {', '.join(preferences.cuisines) if preferences.cuisines else 'Any'}\n"
        f"Minimum Rating: {preferences.min_rating}\n"
        f"Additional Preferences: {preferences.additional_text}\n"
    )
    
    candidates_data = []
    for r in candidates:
        candidates_data.append({
            "name": r.name,
            "location": r.location,
            "cuisines": r.cuisines,
            "rating": r.rating,
            "cost_band": r.cost_band
        })
        
    candidates_text = json.dumps(candidates_data, indent=2)
    
    full_prompt = (
        f"{system_instructions}\n"
        f"--- USER PREFERENCES ---\n{user_pref_text}\n"
        f"--- CANDIDATE LIST ---\n{candidates_text}\n"
        f"--- YOUR JSON OUTPUT ---\n"
    )
    
    return full_prompt
