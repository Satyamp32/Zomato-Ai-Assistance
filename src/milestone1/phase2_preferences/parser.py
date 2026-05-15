from typing import Dict, Any
from pydantic import ValidationError
from milestone1.phase2_preferences.models import UserPreferences

def parse_preferences(data: Dict[str, Any]) -> UserPreferences:
    """Parse and validate raw dictionary data into UserPreferences object."""
    try:
        prefs = UserPreferences(**data)
        return prefs
    except ValidationError as e:
        # In a real API, we'd raise an HTTP 422 here.
        # For the CLI, we can raise a ValueError or the ValidationError itself.
        raise ValueError(f"Invalid preferences provided: {e}")

# Note: The allowed_cities_from_restaurants function mentioned in Phase 2
# can be added here if we want to check against the dataset actively.
# For now, validation is schema-based.
