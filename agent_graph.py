from typing import Dict, Any, Tuple, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from state import State, create_empty_state
from agents import (
    orchestrator,
    standards_extractor,
    use_case_processor,
    transaction_analyzer,
    transaction_rationale,
    knowledge_integration,
)


# Add these imports at the top if not already present
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
import regex as re


def route_query(state: State) -> str:
    """
    Determine which agent should handle the user query based on the Orchestrator's decision.

    Returns:
        str: The next node to route to in the graph.
    """
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
        elif "Both" in route:
            # For "Both" we'll start with standards extraction first
            return "standards_extractor_for_use_case"

    # Default to end if no specific routing determined
    return END


def extract_standard_ids(state: State) -> Dict[str, Any]:
    """
    Extract FAS standard IDs mentioned in the query to use for standards extraction.
    Updates the state with standard_ids for later processing.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    query = messages[-1].content if hasattr(messages[-1], "content") else ""

    # Simple pattern matching for standard IDs - can be made more sophisticated
    standard_ids = []
    for std in ["4", "7", "10", "28", "32"]:
        if f"FAS {std}" in query or f"FAS{std}" in query:
            standard_ids.append(std)

    # Use default standard if none detected
    if not standard_ids:
        standard_ids = [
            "28"
        ]  # Default to FAS 28 for Ijarah if no specific standard mentioned

    # Create a new state with standard_ids included
    new_state = state.copy()
    new_state["standard_ids"] = standard_ids

    return new_state


def prepare_standards_for_use_case(state: State) -> Dict[str, Any]:
    """
    Process standards info before sending to use case processor.
    This node extracts standard information relevant to a use case scenario.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    query = messages[-1].content if hasattr(messages[-1], "content") else ""
    standard_ids = state.get(
        "standard_ids", ["28"]
    )  # Default to FAS 28 if none specified

    # Extract standards info for each relevant standard
    standards_info = {}
    for std_id in standard_ids:
        info = standards_extractor.extract_standard_info(std_id, query)
        standards_info[std_id] = info

    # Create a new state with standards_info included
    new_state = state.copy()
    new_state["standards_info"] = standards_info

    return new_state


def route_after_standards_extraction(state: State) -> str:
    """
    Determine the next step after standards extraction.
    If it came from the use case flow, continue to use case processing.
    """
    if "for_use_case" in state.get("current_flow", ""):
        return "use_case_processor"
    return END


def process_use_case_with_standards(state: State) -> Dict[str, Any]:
    """
    Process use case with extracted standards information.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    query = messages[-1].content if hasattr(messages[-1], "content") else ""
    standards_info = state.get("standards_info", {})

    # Combine all standards info for context
    combined_standards_info = {
        "extracted_info": "\n\n".join(
            [
                f"FAS {std_id}:\n{info['extracted_info']}"
                for std_id, info in standards_info.items()
            ]
        )
    }

    # Process the use case with standards information
    result = use_case_processor.process_use_case(query, combined_standards_info)

    # Create a new message with the result
    from langchain_core.messages import AIMessage

    new_message = AIMessage(content=result["accounting_guidance"])

    # Create a new state with the new message
    new_state = state.copy()
    new_state["messages"] = messages + [new_message]

    return new_state


def _extract_transaction_details(query):
    """Extract structured transaction details from query text."""
    # This is a simplified implementation
    # In a real system, you'd use NLP or a specialized agent to extract this information

    transaction_details = {"context": query, "journal_entries": []}

    # Try to extract journal entries using regex
    entries = re.findall(r"Dr\.\s+([^\$]+)\s+\$?([\d,]+)", query, re.IGNORECASE)
    credits = re.findall(r"Cr\.\s+([^\$]+)\s+\$?([\d,]+)", query, re.IGNORECASE)

    # Match debits and credits
    for i, (debit_account, debit_amount) in enumerate(entries):
        credit_account = credits[i][0] if i < len(credits) else "Unknown Account"
        amount = debit_amount.replace(",", "")

        transaction_details["journal_entries"].append(
            {
                "debit_account": debit_account.strip(),
                "credit_account": credit_account.strip(),
                "amount": float(amount),
            }
        )

    return transaction_details


# Modify the analyze_transaction function to log retrieved chunks
def analyze_transaction(state):
    """Analyze a transaction to identify applicable standards."""
    query = state["messages"][-1].content
    logging.info(f"Processing transaction query: {query[:100]}...")

    # Extract transaction details from the query
    transaction_details = _extract_transaction_details(query)

    # Before analyzing, add logging to display chunks from the retrieval process
    retrieval_query = transaction_analyzer._build_structured_query(transaction_details)

    # Get the retrieved nodes directly to log them
    retrieved_nodes = transaction_analyzer.retriever.retrieve(retrieval_query)

    # Log information about retrieved chunks
    logging.info(f"Retrieved {len(retrieved_nodes)} chunks for transaction analysis")
    for i, node in enumerate(retrieved_nodes[:3]):  # Show first 3 chunks
        logging.info(f"Chunk {i + 1}/{len(retrieved_nodes)}: {node.text[:150]}...")

    # Analyze the transaction
    analysis_result = transaction_analyzer.analyze_transaction(transaction_details)

    # Store the result in state
    new_state = state.copy()
    new_state["transaction_analysis"] = analysis_result
    new_state["retrieved_chunks"] = {
        "count": len(retrieved_nodes),
        "chunks": [node.text for node in retrieved_nodes],
    }

    # Add the analysis to messages
    response_msg = AIMessage(content=analysis_result["analysis"])
    new_state["messages"] = state["messages"] + [response_msg]

    # If standards were identified, proceed to rationale analysis
    if analysis_result["identified_standards"]:
        return "transaction_rationale", new_state
    else:
        return "final_response", new_state


def explain_standards_rationale(state):
    """Explain why identified standards apply to the transaction."""
    # Get the transaction analysis from state
    analysis = state["transaction_analysis"]
    transaction_details = analysis["transaction_details"]
    standards = analysis["identified_standards"]

    # Get rationale for each standard (limit to top 2 for efficiency)
    standard_rationales = {}
    for std in standards[:2]:
        rationale_result = transaction_rationale.explain_standard_application(
            transaction_details, std
        )
        standard_rationales[std] = rationale_result["rationale"]

    # Store rationales in state
    new_state = state.copy()
    new_state["standard_rationales"] = standard_rationales

    return "knowledge_integration", new_state


def integrate_transaction_knowledge(state):
    """Integrate transaction analysis with standards knowledge."""
    # Get analysis and rationales from state
    analysis = state["transaction_analysis"]
    rationales = state["standard_rationales"]

    # Integrate knowledge
    integration_result = knowledge_integration.integrate_knowledge(analysis, rationales)

    # Add integrated analysis to messages
    response_msg = AIMessage(content=integration_result["integrated_analysis"])

    new_state = state.copy()
    new_state["messages"] = state["messages"] + [response_msg]

    return "final_response", new_state


def build_agent_graph() -> StateGraph:
    """
    Build the multi-agent graph for the Islamic finance standards system.

    This graph implements the workflow between:
    - Orchestrator Agent - for query routing
    - Standards Extractor Agent - for extracting information from standards
    - Use Case Processor Agent - for processing financial scenarios
    - Transaction Analyzer Agent - for analyzing reverse transactions
    - Transaction Rationale Agent - for explaining standard applicability
    - Knowledge Integration Agent - for integrating transaction analysis with standards

    The graph is designed to be extensible for future agent additions.
    """
    # Create the graph with the State type
    graph_builder = StateGraph(State)

    # Add nodes for each agent
    graph_builder.add_node("orchestrator", orchestrator)
    graph_builder.add_node("standards_extractor", standards_extractor)
    graph_builder.add_node("use_case_processor", use_case_processor)

    # Add Category 2 specialized nodes
    graph_builder.add_node("transaction_analyzer", analyze_transaction)
    graph_builder.add_node("transaction_rationale", explain_standards_rationale)
    graph_builder.add_node("knowledge_integration", integrate_transaction_knowledge)

    # Add a final response node
    graph_builder.add_node("final_response", lambda state: (END, state))

    # Add special processing nodes
    graph_builder.add_node("extract_standard_ids", extract_standard_ids)
    graph_builder.add_node(
        "standards_extractor_for_use_case",
        lambda state: {**state, "current_flow": "for_use_case"},
    )
    graph_builder.add_node(
        "prepare_standards_for_use_case", prepare_standards_for_use_case
    )
    graph_builder.add_node(
        "process_use_case_with_standards", process_use_case_with_standards
    )

    # Set entry point to the orchestrator
    graph_builder.set_entry_point("orchestrator")

    # Add conditional edges from orchestrator
    graph_builder.add_conditional_edges(
        "orchestrator",
        route_query,
        {
            "use_case_processor": "extract_standard_ids",
            "standards_extractor": "extract_standard_ids",
            "standards_extractor_for_use_case": "extract_standard_ids",
            "transaction_analyzer": "transaction_analyzer",
            END: END,
        },
    )

    # Standard extraction flow
    graph_builder.add_edge("extract_standard_ids", "standards_extractor")
    graph_builder.add_conditional_edges(
        "standards_extractor",
        lambda state: "for_use_case"
        if "for_use_case" in state.get("current_flow", "")
        else "end",
        {"for_use_case": "prepare_standards_for_use_case", "end": END},
    )

    # Use case flow with standards info
    graph_builder.add_edge(
        "prepare_standards_for_use_case", "process_use_case_with_standards"
    )
    graph_builder.add_edge("process_use_case_with_standards", END)

    # Direct use case processing (without standards extraction)
    graph_builder.add_edge("extract_standard_ids", "use_case_processor")
    graph_builder.add_edge("use_case_processor", END)

    # Transaction analyzer flow
    graph_builder.add_edge("transaction_analyzer", "transaction_rationale")
    graph_builder.add_edge("transaction_rationale", "knowledge_integration")
    graph_builder.add_edge("knowledge_integration", "final_response")
    graph_builder.add_edge("final_response", END)

    # Compile the graph
    return graph_builder.compile()


# Create the agent graph
agent_graph = build_agent_graph()
