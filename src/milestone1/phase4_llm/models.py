from pydantic import BaseModel, Field

class LLMRecommendation(BaseModel):
    restaurant_name: str = Field(..., description="The name of the recommended restaurant")
    explanation: str = Field(..., description="Why this restaurant was recommended")
