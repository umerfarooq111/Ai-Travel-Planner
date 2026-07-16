def decision_node(state):
    tools = []
    if state.get("destination"):
        tools.append("travel")
        tools.append("weather")

    if state.get("currency"):
        tools.append("currency")

    print("\nAgent Decision:")
    print(tools)
    return {"required_tools": tools}
