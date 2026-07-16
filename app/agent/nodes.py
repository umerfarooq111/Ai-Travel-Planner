import asyncio

from app.llm.model import model
from app.tools.currency import currency_converter
from app.tools.travel import destination_info
from app.optimization.toon import encode_toon
from app.prompts.travel_prompt import TRAVEL_PLANNER_PROMPT
from app.schemas.travel import TravelRequirements
from app.tools.weather import weather_tool


def requirement_analyzer(state):
    prompt = f"""
    You are a travel requirement analyzer.

    Extract the following information:

    - destination
    - duration
    - budget
    - currency
    - preferences

    User request:

    {state["user_query"]}
    """
    structured_model = model.with_structured_output(TravelRequirements)
    response = structured_model.invoke(prompt)

    updates = {
        "destination": response.destination,
        "duration": response.duration,
        "budget": response.budget,
        "currency": response.currency,
        "preferences": response.preferences or "",
    }

    compressed = encode_toon({**state, **updates})
    print("\nCompressed State:")
    print(compressed)
    return updates


def itinerary_generator(state):
    user_profile = state.get("user_profile") or {}
    profile_context = ""
    if user_profile:
        favorites = ", ".join(user_profile.get("favorite_destinations", []))
        profile_context = f"""
User profile:
- Travel style: {user_profile.get("travel_style", "N/A")}
- Favorite destinations: {favorites or "N/A"}
- Average budget: {user_profile.get("average_budget", "N/A")} {user_profile.get("preferred_currency", "")}
"""

    prompt = TRAVEL_PLANNER_PROMPT.format(
        destination=state["destination"],
        duration=state["duration"],
        budget=state["budget"],
        currency=state["currency"],
        tool_results=state["tool_results"],
    )
    if profile_context:
        prompt = profile_context + "\n" + prompt

    content_parts = []
    for chunk in model.stream(prompt):
        if isinstance(chunk.content, list):
            text = chunk.content[0].get("text", "") if chunk.content else ""
        else:
            text = chunk.content or ""
        if text:
            content_parts.append(text)

    itinerary = "".join(content_parts)
    return {
        "itinerary": itinerary,
        "final_response": itinerary,
    }


async def tool_executor(state):
    results = {}

    if "travel" in state["required_tools"]:
        travel = await destination_info(state["destination"])
        results["travel"] = travel

    tasks = []
    names = []

    if "weather" in state["required_tools"]:
        tasks.append(weather_tool(state["destination"]))
        names.append("weather")

    if "currency" in state["required_tools"]:
        destination_currency = results.get("travel", {}).get("currency", "USD")
        tasks.append(
            currency_converter(
                amount=state["budget"],
                from_currency=state["currency"],
                to_currency=destination_currency,
            )
        )
        names.append("currency")

    if tasks:
        responses = await asyncio.gather(*tasks)
        for name, response in zip(names, responses):
            results[name] = response

    return {"tool_results": results}
