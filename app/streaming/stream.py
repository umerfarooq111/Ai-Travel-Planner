from app.streaming.events import format_event


async def stream_agent(input_data, graph):
    config = {"configurable": {"thread_id": input_data["user_id"]}}
    async for event in graph.astream(input_data, config=config, stream_mode="updates"):
        for node, state in event.items():
            yield format_event(node, state)
