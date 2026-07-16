def format_event(node, state):
    messages = {
        "analyzer": "Understanding your travel requirements",
        "preference": "Loading your travel preferences",
        "decision": "Deciding required information",
        "tools": "Collecting travel information",
        "planner": "Generating your personalized itinerary",
    }

    return {
        "node": node,
        "message": messages.get(node, "Processing"),
        "data": state,
    }
