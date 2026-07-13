def decision_node(state):
    tools=[]
    if state.get("destination"):
        tools.append("travel")
        tools.append("weather")

    if state.get("currency"):
        tools.append("currency")

    state["required_tools"]=tools
    print("\nAgent Decision:")
    print(tools)
    return state