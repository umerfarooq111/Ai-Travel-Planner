import asyncio
from pydantic import BaseModel, Field
from typing import Optional

from app.llm.model import model
from app.tools.currency import currency_converter
from app.tools.travel import destination_info
from app.optimization.toon import encode_toon
from app.prompts.travel_prompt import TRAVEL_PLANNER_PROMPT
from app.schemas.travel import TravelRequirements
from app.tools.weather import weather_tool


class BudgetIntent(BaseModel):
    intent_description: str = Field(description="Description of the user's intent regarding the budget.")
    adjust_budget: bool = Field(description="True if the user wants to increase or decrease the budget, False otherwise.")
    budget_multiplier: float = Field(default=1.0, description="Multiplier to adjust the budget (e.g. 0.7 to make it cheaper, 1.3 to make it more premium/expensive).")
    explicit_budget: Optional[int] = Field(default=None, description="Explicit new budget if specified in the user request.")


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

    updates = {}
    if response.destination:
        updates["destination"] = response.destination
    if response.duration:
        updates["duration"] = response.duration
    if response.budget:
        updates["budget"] = response.budget
    if response.currency:
        updates["currency"] = response.currency
    if response.preferences:
        updates["preferences"] = response.preferences

    merged_state = {**state, **updates}
    compressed = encode_toon(merged_state)
    print("\nCompressed State:")
    print(compressed)
    return updates


def itinerary_generator(state):
    budget = state.get("budget") or 2000
    currency = state.get("currency") or "USD"
    
    # 1. LLM-derived budget intent analysis (runs if there is a previous itinerary)
    if state.get("itinerary") and budget:
        intent_prompt = f"""
        Analyze the user's travel request to determine if they want to adjust the budget of their trip.
        Current User Request: "{state["user_query"]}"
        Current Budget: {budget} {currency}
        
        If the user wants to make the trip cheaper or reduce the budget, set adjust_budget=True and budget_multiplier to a value less than 1.0 (e.g. 0.7 for 30% cheaper).
        If the user wants a more premium/expensive trip, set adjust_budget=True and budget_multiplier to a value greater than 1.0 (e.g. 1.3).
        If the user specifies an explicit new budget number, set explicit_budget to that value.
        Otherwise, set adjust_budget=False and budget_multiplier=1.0.
        """
        try:
            structured_model = model.with_structured_output(BudgetIntent)
            intent = structured_model.invoke(intent_prompt)
            if intent.adjust_budget:
                if intent.explicit_budget:
                    budget = intent.explicit_budget
                else:
                    budget = int(budget * intent.budget_multiplier)
                print(f"\n[LLM Budget Update] Intent: {intent.intent_description}, New Budget: {budget}")
        except Exception as e:
            print(f"Error in budget intent analysis: {e}")

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

    # 2. Pass ONLY relevant current state (destination, duration, budget, currency, tool_results) to the prompt.
    prompt = TRAVEL_PLANNER_PROMPT.format(
        destination=state["destination"],
        duration=state["duration"],
        budget=budget,
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
        "budget": budget,
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
