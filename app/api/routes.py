from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.streaming.token_stream import token_stream
from app.api.schemas import TravelRequest

router = APIRouter()

@router.post("/travel/chat/stream")
async def travel_chat(
    request: TravelRequest
):
    async def event_generator():
        async for token in token_stream(
            request.model_dump()
        ):

            yield {"event": "token","data": token}

    return EventSourceResponse(
        event_generator()
    )