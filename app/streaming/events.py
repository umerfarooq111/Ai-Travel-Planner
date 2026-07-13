def format_event(node, state):

    messages = {

        "analyzer":
        "Understanding your travel requirements",

        "decision":
        "Deciding required information",

        "tools":
        "Collecting travel information"

    }


    return {

        "node":node,

        "message":
        messages.get(
            node,
            "Processing"
        ),

        "data":state

    }