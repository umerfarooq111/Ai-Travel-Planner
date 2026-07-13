from app.agent.graph import graph



async def token_stream(state):


    async for event in graph.astream_events(
        state,
        version="v2"
    ):


        kind = event["event"]


        if kind == "on_chat_model_stream":


            chunk = event["data"]["chunk"]


            if chunk.content:

                yield chunk.content