from app.llm.model import model

from app.optimization.toon import encode_toon

from app.tools.weather import weather_tool
from app.tools.currency import currency_converter
from app.tools.travel import destination_info

from app.prompts.travel_prompt import TRAVEL_PLANNER_PROMPT

from app.schemas.travel import TravelRequirements

import asyncio



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

Extract the following information:

- destination
- duration
- budget
- currency
- preferences


User request:

{state["user_query"]}
"""


    structured_model = model.with_structured_output(
        TravelRequirements
    )


    response = structured_model.invoke(
        prompt
    )


    state["destination"] = response.destination

    state["duration"] = response.duration

    state["budget"] = response.budget

    state["currency"] = response.currency

    state["preferences"] = response.preferences


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


    if isinstance(response.content, list):

        itinerary = response.content[0]["text"]

    else:

        itinerary = response.content



    state["itinerary"] = itinerary

    state["final_response"] = itinerary


    return state





async def tool_executor(state):

    results = {}


    # -------------------------------
    # STEP 1
    # Travel information first
    # -------------------------------

    if "travel" in state["required_tools"]:


        travel = await destination_info(

            state["destination"]

        )


        results["travel"] = travel



    # -------------------------------
    # STEP 2
    # Run independent tools parallel
    # -------------------------------


    tasks = []

    names = []



    if "weather" in state["required_tools"]:


        tasks.append(

            weather_tool(

                state["destination"]

            )

        )


        names.append("weather")




    if "currency" in state["required_tools"]:


        destination_currency = (

            results["travel"]["currency"]

        )


        tasks.append(

            currency_converter(

                amount=state["budget"],

                from_currency=state["currency"],

                to_currency=destination_currency

            )

        )


        names.append("currency")




    if tasks:


        responses = await asyncio.gather(

            *tasks

        )


        for name, response in zip(
            names,
            responses
        ):

            results[name] = response



    state["tool_results"] = results


    return state