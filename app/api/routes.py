from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.agent.state import build_initial_state
from app.api.schemas import TravelRequest
from app.streaming.token_stream import token_stream

router = APIRouter()


@router.post("/travel/chat/stream")
async def travel_chat(travel_req: TravelRequest, request: Request):
    graph = request.app.state.graph
    user_id = travel_req.user_id or "anonymous"
    config = {"configurable": {"thread_id": user_id}}
    state = build_initial_state(travel_req.user_query, user_id)

    async def event_generator():
        async for token in token_stream(state, graph, config):
            yield {"event": "token", "data": token}

    return EventSourceResponse(event_generator())


@router.get("/travel/state/{thread_id}")
async def get_travel_state(thread_id: str, request: Request):
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await graph.aget_state(config)

    if snapshot and snapshot.values:
        return snapshot.values

    return {}
