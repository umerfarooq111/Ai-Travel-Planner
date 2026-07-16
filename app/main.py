from fastapi import FastAPI
from app.agent.graph import graph
from app.api.routes import router

app = FastAPI(title="AI Travel Planner Agent")
app.state.graph = graph

app.include_router(router)


@app.get("/")
def home():
    return {"message": "AI Travel Planner Agent Running"}