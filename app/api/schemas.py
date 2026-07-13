from pydantic import BaseModel


class TravelRequest(BaseModel):

    user_query: str

    user_id: str | None = None