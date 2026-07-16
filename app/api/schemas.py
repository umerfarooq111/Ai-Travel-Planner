from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    user_query: str
    user_id: str = Field(default="anonymous")
