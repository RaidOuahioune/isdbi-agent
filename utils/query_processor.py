"""
Query processing module for the Islamic Finance standards system.
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from agent_graph import agent_graph
from state import create_empty_state


def process_query(query: str) -> AIMessage:
    """
    Process a user query through the multi-agent system.

    Args:
        query: The user's query about Islamic finance standards or scenarios.

    Returns:
        AIMessage: The response from the agent system.
    """
    # Create a new message
    message = HumanMessage(content=query)

    # Create initial state with the user message
    state = create_empty_state()
    state["messages"] = [message]

    # Process the message through the agent graph
    result = agent_graph.invoke(state)

    # Extract and return the AI's response
    messages = result["messages"]
    return messages[-1] if messages else AIMessage(content="No response was generated.")
