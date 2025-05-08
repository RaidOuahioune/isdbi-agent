from typing import Annotated, Any, Dict, Optional, Union, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    # Track which agent is currently active
    current_agent: str
    # Store results from different agents
    agent_results: Dict[str, Any]
    # Store extracted standard information
    standard_info: Dict[str, Any]
    # Store accounting entries
    accounting_entries: List[Dict[str, Any]]
    # Track the query type for proper routing
    query_type: str


graph_builder = StateGraph(State)


# Helper functions for state management
def create_empty_state() -> Dict[str, Any]:
    """Create a fresh, empty state dictionary."""
    return {
        "messages": [],
        "current_agent": "orchestrator",  # Start with the orchestrator
        "agent_results": {},
        "standard_info": {},
        "accounting_entries": [],
        "query_type": "unknown"
    }


def is_valid_message(message: Any) -> bool:
    """Check if a message object is valid and contains content."""
    if not isinstance(message, dict):
        return False
    if "content" not in message or not message["content"]:
        return False
    if "role" not in message:
        return False
    return True

# Query type identification functions
def identify_query_type(query: str) -> str:
    """Identify the type of query to route to appropriate agents."""
    query_lower = query.lower()
    
    # Use case scenario indicators
    if any(term in query_lower for term in ["use case", "scenario", "accounting", "journal entries", 
                                           "financial scenario", "accounting treatment", "recognition",
                                           "ijarah", "murabaha", "musharakah"]):
        return "use_case_scenario"
    
    # Reverse transaction indicators
    elif any(term in query_lower for term in ["reverse", "transaction", "journal entry", 
                                             "identify standard", "which standard"]):
        return "reverse_transaction"
    
    # Standard enhancement indicators
    elif any(term in query_lower for term in ["enhance", "enhancement", "improve", "standard", 
                                             "modify", "update", "clarify"]):
        return "standard_enhancement"
    
    # Default to unknown if we can't determine
    return "unknown"
