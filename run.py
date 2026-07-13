import sys
from app.streaming.stream import stream_agent

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

state={

"user_query":
"Plan a 5 day trip to Turkey with budget of 200000 PKR",

"destination":None,
"duration":None,
"budget":None,
"currency":None,
"preferences":None,
"itinerary":None,
"final_response":None,
"required_tools":[],
"tool_results":{}
}

config = {"configurable": {"thread_id": "cli_thread"}}

for chunk in stream_agent(state, config=config):
    print("\nSTREAM EVENT")
    print(chunk)