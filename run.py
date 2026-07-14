import sys
import asyncio
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agent.graph import workflow
from app.streaming.events import format_event

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

state = {
    "user_query": "Plan a 5 day trip to Turkey with budget of 200000 PKR",
    "destination": None,
    "duration": None,
    "budget": None,
    "currency": None,
    "preferences": None,
    "itinerary": None,
    "final_response": None,
    "required_tools": [],
    "tool_results": {}
}

config = {"configurable": {"thread_id": "cli_thread"}}

async def main():
    async with aiosqlite.connect("travel_planner_checkpoints.db") as conn:
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()
        graph = workflow.compile(checkpointer=checkpointer)
        
        async for event in graph.astream(
            state,
            config=config,
            stream_mode="updates"
        ):
            for node, state_val in event.items():
                print("\nSTREAM EVENT")
                formatted = format_event(node, state_val)
                print(formatted)

if __name__ == "__main__":
    asyncio.run(main())