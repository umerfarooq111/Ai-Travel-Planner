from app.streaming.stream import stream_agent


state={

"user_query":
"Plan a 5 day trip to Turkey with budget of 200000 PKR",
"destination":None,
"duration":None,
"budget":None,
"currency":None,
"preferences":None,
"itinerary":None,
"required_tools":[],
"tool_results":{}
}

for chunk in stream_agent(state):
    print("\nSTREAM EVENT")
    print(chunk)