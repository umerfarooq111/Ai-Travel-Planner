async def token_stream(state, graph):
    thread_id = state.get("user_id") or "default_user"
    config = {"configurable": {"thread_id": thread_id}}

    async for event in graph.astream_events(
        state,
        config=config,
        version="v2"
    ):


        kind = event["event"]


        if kind == "on_chat_model_stream":


            chunk = event["data"]["chunk"]


            if chunk.content:

                yield chunk.content