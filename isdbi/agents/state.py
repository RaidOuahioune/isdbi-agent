from typing import Annotated, Any, Dict, Optional, Union

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# Helper functions for state management
def create_empty_state() -> Dict[str, Any]:
    """Create a fresh, empty state dictionary."""
    return {"messages": []}


def is_valid_message(message: Any) -> bool:
    """Check if a message object is valid and contains content."""
    if not isinstance(message, dict):
        return False
    if "content" not in message or not message["content"]:
        return False
    if "role" not in message:
        return False
    return True
