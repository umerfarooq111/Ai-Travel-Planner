from contextlib import asynccontextmanager
import aiosqlite
from fastapi import FastAPI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agent.graph import workflow
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiosqlite.connect("travel_planner_checkpoints.db") as conn:
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()
        app.state.graph = workflow.compile(checkpointer=checkpointer)
        yield

app = FastAPI(
    title="AI Travel Planner Agent",
    version="1.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
def home():

    return {

        "message":
        "AI Travel Planner Agent Running"

    }