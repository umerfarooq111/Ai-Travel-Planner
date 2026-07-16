from langgraph.graph import END, START, StateGraph

from app.agent.decision import decision_node
from app.agent.nodes import itinerary_generator, requirement_analyzer, tool_executor
from app.agent.preference_node import preference_node
from app.agent.state import TravelState

workflow = StateGraph(TravelState)
workflow.add_node("analyzer", requirement_analyzer)
workflow.add_node("preference", preference_node)
workflow.add_node("decision", decision_node)
workflow.add_node("tools", tool_executor)
workflow.add_node("planner", itinerary_generator)

workflow.add_edge(START, "analyzer")
workflow.add_edge("analyzer", "preference")
workflow.add_edge("preference", "decision")
workflow.add_edge("decision", "tools")
workflow.add_edge("tools", "planner")
workflow.add_edge("planner", END)
