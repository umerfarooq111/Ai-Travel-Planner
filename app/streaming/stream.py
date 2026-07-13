from app.agent.graph import graph
from app.streaming.events import format_event

def stream_agent(input):


    for event in graph.stream(
        input,
        stream_mode="updates"
    ):


        for node,state in event.items():


            yield format_event(
                node,
                state
            )