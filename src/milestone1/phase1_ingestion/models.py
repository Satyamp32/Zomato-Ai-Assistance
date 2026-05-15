from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Restaurant(BaseModel):
    """Canonical model for a Restaurant across the application."""
    name: str = Field(..., description="Name of the restaurant")
    location: str = Field(..., description="City or specific location")
    cuisines: List[str] = Field(default_factory=list, description="List of cuisines offered")
    cost_band: str = Field(default="medium", description="Estimated cost band (e.g., low, medium, high)")
    rating: float = Field(default=0.0, description="Aggregate user rating out of 5.0")

    @field_validator("rating", mode="before")
    def parse_rating(cls, v):
        try:
            val = float(v)
            if val < 0 or val > 5:
                return 0.0
            return val
        except (ValueError, TypeError):
            return 0.0

    @field_validator("cuisines", mode="before")
    def parse_cuisines(cls, v):
        if isinstance(v, str):
            return [c.strip() for c in v.split(",") if c.strip()]
        if isinstance(v, list):
            return v
        return []
