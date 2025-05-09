"""
Graph router functions for Islamic Finance standards system.
This module contains the routing logic for the agent graph.
"""

from typing import Dict, Any, List
import regex as re
import logging
from langchain_core.messages import AIMessage
from state import State, create_empty_state

def route_query(state: State) -> str:
    """
    Determine which agent should handle the user query based on the Orchestrator's decision.

    Returns:
        str: The next node to route to in the graph.
    """
    from langgraph.graph import END
    from components.agents.orchestrator import orchestrator
    
    # Get the latest message (assumed to be from the user)
    messages = state.get("messages", [])
    if not messages:
        return END

    latest_message = messages[-1]

    if hasattr(latest_message, "content") and latest_message.content:
        query = latest_message.content.lower()

        # Check if this is a reverse transaction analysis request
        if (
            "journal entries" in query
            or "journal entry" in query
            or "dr." in query
            or "cr." in query
        ) and (
            "reverse" in query
            or "reversal" in query
            or "buyout" in query
            or "exit" in query
            or "cancel" in query
        ):
            return "transaction_analyzer"

        # Use the orchestrator to determine routing for other queries
        route = orchestrator.route_query(query)

        if "UseCase" in route:
            return "use_case_processor"
        elif "Standards" in route:
            return "standards_extractor"
        elif "Enhancement" in route or "enhancement" in route:
            return "enhancement_workflow"
        elif "Both" in route:
            # For "Both" we'll start with standards extraction first
            return "standards_extractor_for_use_case"

    # Default to end if no specific routing determined
    from langgraph.graph import END
    return END


def route_after_standards_extraction(state: State) -> str:
    """
    Determine the next step after standards extraction.
    If it came from the use case flow, continue to use case processing.
    """
    from langgraph.graph import END
    
    if "for_use_case" in state.get("current_flow", ""):
        return "use_case_processor"
    return END