from langgraph.graph import StateGraph, END , START
from app.agent.state import TravelState
from app.agent.nodes import (requirement_analyzer,tool_executor,itinerary_generator)
from app.agent.decision import decision_node
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


workflow=StateGraph(TravelState)
workflow.add_node("analyzer",requirement_analyzer)
workflow.add_node("decision",decision_node)
workflow.add_node("tools",tool_executor)
workflow.add_node("planner",itinerary_generator)
workflow.add_edge(START,"analyzer")
workflow.add_edge("analyzer","decision")
workflow.add_edge("decision","tools")
workflow.add_edge("tools","planner")
workflow.add_edge("planner",END)


conn = sqlite3.connect("travel_planner_checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

graph = workflow.compile(checkpointer=memory)