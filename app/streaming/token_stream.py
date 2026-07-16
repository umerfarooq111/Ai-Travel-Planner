def _extract_chunk_text(chunk) -> str:
    content = chunk.content
    if not content:
        return ""
    if isinstance(content, list):
        return content[0].get("text", "") if content else ""
    return str(content)


async def token_stream(state, graph, config):
    async for event in graph.astream_events(state, config=config, version="v2"):
        kind = event["event"]
        node_name = event.get("metadata", {}).get("langgraph_node")

        if kind == "on_chain_start" and node_name:
            yield f"__STATUS__:{node_name}"
        elif kind == "on_chat_model_stream" and node_name == "planner":
            text = _extract_chunk_text(event["data"]["chunk"])
            if text:
                yield text

    yield "__STATUS__:completed"
