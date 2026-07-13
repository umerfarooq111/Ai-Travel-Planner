from app.llm.model import model
from app.optimization.toon import encode_toon
import re
from app.tools.weather import weather_tool
from app.tools.currency import currency_converter
from app.tools.travel import destination_info
from app.prompts.travel_prompt import TRAVEL_PLANNER_PROMPT
def requirement_analyzer(state):
    state.setdefault("destination", None)
    state.setdefault("duration", None)
    state.setdefault("budget", None)
    state.setdefault("currency", None)
    state.setdefault("preferences", "")
    state.setdefault("itinerary", None)
    state.setdefault("final_response", None)
    state.setdefault("required_tools", [])
    state.setdefault("tool_results", {})

    prompt = f"""
You are a travel requirement analyzer.

Extract:
destination
duration
budget
currency
preferences

User request:
{state['user_query']}

Return only:
destination:
duration:
budget:
currency:
preferences:
"""

    response = model.invoke(prompt)

    if isinstance(response.content, list):
        extracted = response.content[0]["text"]
    else:
        extracted = response.content

    destination = re.search(r"destination:\s*(.*)",extracted,re.I)

    duration = re.search(r"duration:\s*(\d+)",extracted,re.I)

    budget = re.search(r"budget:\s*(\d+)",extracted,re.I)

    currency = re.search(r"currency:\s*(.*)",extracted,re.I)

    preferences = re.search(
        r"preferences:\s*(.*)",
        extracted,
        re.I | re.S
    )

    if destination:
        state["destination"] = destination.group(1).strip()

    if duration:
        state["duration"] = int(duration.group(1))

    if budget:
        state["budget"] = int(budget.group(1))

    if currency:
        state["currency"] = currency.group(1).strip()

    if preferences:
        state["preferences"] = preferences.group(1).strip()

    compressed = encode_toon(state)

    print("\nCompressed State:")
    print(compressed)

    return state

def itinerary_generator(state):

    prompt = TRAVEL_PLANNER_PROMPT.format(
        destination=state["destination"],
        duration=state["duration"],
        budget=state["budget"],
        currency=state["currency"],
        tool_results=state["tool_results"]
    )
    response = model.invoke(prompt)
    if isinstance(response.content,list):
        itinerary=response.content[0]["text"]
    else:
        itinerary=response.content

    state["itinerary"]=itinerary
    state["final_response"]=itinerary
    return state

def tool_executor(state):
    results={}
    for tool in state["required_tools"]:
        if tool=="weather":
            results["weather"]=weather_tool(state["destination"])
        elif tool=="currency":
            results["currency"]=currency_converter(state["currency"])
        elif tool=="travel":
            results["travel"]=destination_info(state["destination"])

    state["tool_results"]=results
    return state