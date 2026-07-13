from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.streaming.token_stream import token_stream
from app.api.schemas import TravelRequest

router = APIRouter()

@router.post("/travel/chat/stream")
async def travel_chat(
    travel_req: TravelRequest,
    request: Request
):
    graph = request.app.state.graph
    async def event_generator():
        async for token in token_stream(
            travel_req.model_dump(),
            graph
        ):

            yield {"event": "token","data": token}

    return EventSourceResponse(
        event_generator()
    )