from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class UserPreferences(BaseModel):
    """Structured fields for user preferences."""
    location: str = Field(..., description="City or location")
    budget: str = Field(default="medium", description="Budget band: low, medium, high")
    cuisines: List[str] = Field(default_factory=list, description="List of preferred cuisines")
    min_rating: float = Field(default=0.0, description="Minimum acceptable rating (0.0 to 5.0)")
    additional_text: Optional[str] = Field(default="", description="Optional free-text preferences")

    @field_validator("budget", mode="before")
    def validate_budget(cls, v):
        if not v:
            return "medium"
        v_lower = str(v).lower()
        if v_lower in ["low", "medium", "high"]:
            return v_lower
        return "medium"

    @field_validator("min_rating", mode="before")
    def validate_min_rating(cls, v):
        try:
            val = float(v)
            if val < 0.0 or val > 5.0:
                return 0.0
            return val
        except (ValueError, TypeError):
            return 0.0

    @field_validator("additional_text", mode="before")
    def limit_additional_text(cls, v):
        """Limit additional text to 500 chars to avoid prompt injection/bloat."""
        if not v:
            return ""
        v_str = str(v)
        if len(v_str) > 500:
            return v_str[:500]
        return v_str
