from fastapi import FastAPI

from app.api.routes import router



app = FastAPI(

    title="AI Travel Planner Agent",

    version="1.0"

)



app.include_router(router)



@app.get("/")
def home():

    return {

        "message":
        "AI Travel Planner Agent Running"

    }