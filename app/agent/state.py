from typing import TypedDict, Optional, List


class TravelState(TypedDict):

    user_query: str

    destination: Optional[str]

    duration: Optional[int]

    budget: Optional[int]

    currency: Optional[str]

    preferences: Optional[str]

    itinerary: Optional[str]

    final_response: Optional[str]

    required_tools: List[str]

    tool_results: dict