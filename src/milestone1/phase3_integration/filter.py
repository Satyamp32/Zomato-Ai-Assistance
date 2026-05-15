from typing import List, Tuple
from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences

def filter_and_rank(preferences: UserPreferences, restaurants: List[Restaurant], candidate_cap: int = 20) -> List[Restaurant]:
    """
    Applies deterministic filters based on UserPreferences and returns a sorted list of candidates.
    """
    filtered = []
    
    pref_location = preferences.location.lower()
    pref_cuisines = [c.lower() for c in preferences.cuisines]
    pref_budget = preferences.budget.lower()
    
    for r in restaurants:
        # 1. Location match (case insensitive substring)
        if pref_location not in r.location.lower():
            continue
            
        # 2. Rating match
        if r.rating < preferences.min_rating:
            continue
            
        # 3. Budget match (if dataset has low/medium/high, exact match; otherwise skipped if unstructured)
        # Assuming the ingest phase normalizes dataset cost into bands if possible. 
        # If strict matching is needed:
        # if pref_budget != "medium" and r.cost_band.lower() != pref_budget:
        #     continue

        # 4. Cuisine match (at least one cuisine overlaps if user specified any)
        if pref_cuisines:
            r_cuisines = [c.lower() for c in r.cuisines]
            overlap = any(c in r_cuisines for c in pref_cuisines)
            if not overlap:
                continue
                
        filtered.append(r)
        
    # Pre-sort the candidates by rating descending as a ranking hint for the LLM
    # Tie-breaking by name alphabetically
    sorted_candidates = sorted(filtered, key=lambda x: (-x.rating, x.name))
    
    # Cap the results to avoid LLM context window limits
    return sorted_candidates[:candidate_cap]
