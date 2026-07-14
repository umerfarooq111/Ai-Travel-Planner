from pydantic import BaseModel, Field


class TravelRequirements(BaseModel):
    destination: str = Field(description="Travel destination")
    duration: int = Field(description="Duration in days")
    budget: int = Field(description="Budget amount")
    currency: str = Field(description="Budget currency")
    preferences: str = Field(description="User preferences")