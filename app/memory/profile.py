from pydantic import BaseModel, Field
from typing import List


class UserProfile(BaseModel):
    user_id: str

    travel_style: str = ""

    preferred_transport: str = ""

    preferred_accommodation: str = ""

    favorite_destinations: List[str] = Field(default_factory=list)

    interests: List[str] = Field(default_factory=list)

    average_budget: int = 0

    preferred_currency: str = "PKR"
