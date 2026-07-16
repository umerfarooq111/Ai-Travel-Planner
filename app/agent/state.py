from typing import Any, Optional, TypedDict


class TravelState(TypedDict):
    user_query: str
    user_id: str

    destination: Optional[str]
    duration: Optional[int]
    budget: Optional[int]
    currency: Optional[str]
    preferences: Optional[str]
    itinerary: Optional[str]
    final_response: Optional[str]
    required_tools: list[str]
    tool_results: dict[str, Any]
    user_profile: Optional[dict[str, Any]]


def build_initial_state(user_query: str, user_id: str) -> TravelState:
    return {
        "user_query": user_query,
        "user_id": user_id,
        "destination": None,
        "duration": None,
        "budget": None,
        "currency": None,
        "preferences": None,
        "itinerary": None,
        "final_response": None,
        "required_tools": [],
        "tool_results": {},
        "user_profile": None,
    }
