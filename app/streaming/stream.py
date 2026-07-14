from app.agent.graph import graph
from app.streaming.events import format_event

async def stream_agent(input, config=None):
    async for event in graph.astream(
        input,
        config=config,
        stream_mode="updates"
    ):
        for node, state in event.items():
            yield format_event(
                node,
                state
            )