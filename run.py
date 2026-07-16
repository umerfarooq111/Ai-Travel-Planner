import sys
import asyncio
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agent.graph import workflow
from app.agent.state import build_initial_state
from app.streaming.events import format_event

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

config = {"configurable": {"thread_id": "cli_thread"}}


async def main():
    async with aiosqlite.connect("travel_planner_checkpoints.db") as conn:
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()
        graph = workflow.compile(checkpointer=checkpointer)

        state = build_initial_state(
            "Plan a 5 day trip to Turkey with budget of 200000 PKR",
            "cli_thread",
        )

        async for event in graph.astream(
            state,
            config=config,
            stream_mode="updates",
        ):
            for node, state_val in event.items():
                print("\nSTREAM EVENT")
                formatted = format_event(node, state_val)
                print(formatted)


if __name__ == "__main__":
    asyncio.run(main())
