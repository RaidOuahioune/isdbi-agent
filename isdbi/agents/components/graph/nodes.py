"""
Graph processing nodes for the Islamic Finance standards system.
This module contains functions that implement the processing logic for graph nodes.
"""

from typing import Dict, Any, Tuple, List
import re
import logging
from langchain_core.messages import AIMessage
from state import State

from components.agents.standards_extractor import standards_extractor
from components.agents.use_case_processor import use_case_processor
from components.agents.reviewer_agent import reviewer_agent
from components.agents.proposer_agent import proposer_agent
from components.agents.validator_agent import validator_agent
from components.agents.transaction_analyzer import transaction_analyzer
from components.agents.transaction_rationale import transaction_rationale
from components.agents.knowledge_integration import knowledge_integration


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


def extract_enhancement_info(state: State) -> Dict[str, Any]:
    """
    Extract information needed for standards enhancement from the user query.
    This includes the standard ID and the trigger scenario.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    query = messages[-1].content if hasattr(messages[-1], "content") else ""

    # Extract standard ID
    standard_id = "10"  # Default to FAS 10 (Istisna'a) if none specified
    for std in ["4", "7", "10", "28", "32"]:
        if f"FAS {std}" in query or f"FAS{std}" in query:
            standard_id = std
            break

    # The rest of the query serves as the trigger scenario
    trigger_scenario = query

    # Create a new state with enhancement info included
    new_state = state.copy()
    new_state["enhancement_info"] = {
        "standard_id": standard_id,
        "trigger_scenario": trigger_scenario,
    }

    return new_state


def run_reviewer_agent(state: State) -> Dict[str, Any]:
    """
    Run the Reviewer Agent to extract and analyze standard elements.
    """
    enhancement_info = state.get("enhancement_info", {})
    standard_id = enhancement_info.get("standard_id", "10")
    trigger_scenario = enhancement_info.get("trigger_scenario", "")

    # Run the Reviewer Agent
    review_result = reviewer_agent.extract_standard_elements(
        standard_id, trigger_scenario
    )

    # Create a new state with review results included
    new_state = state.copy()
    new_state["review_result"] = review_result

    return new_state


def run_proposer_agent(state: State) -> Dict[str, Any]:
    """
    Run the Proposer Agent to generate enhancement proposals.
    """
    review_result = state.get("review_result", {})

    # Run the Proposer Agent
    proposal_result = proposer_agent.generate_enhancement_proposal(review_result)

    # Create a new state with proposal results included
    new_state = state.copy()
    new_state["proposal_result"] = proposal_result

    return new_state


def run_validator_agent(state: State) -> Dict[str, Any]:
    """
    Run the Validator Agent to validate the proposed changes.
    """
    proposal_result = state.get("proposal_result", {})

    # Run the Validator Agent
    validation_result = validator_agent.validate_proposal(proposal_result)

    # Create a new state with validation results included
    new_state = state.copy()
    new_state["validation_result"] = validation_result

    return new_state


def format_enhancement_results(state: State) -> Dict[str, Any]:
    """
    Format the results of the standards enhancement workflow for display to the user.
    """
    messages = state.get("messages", [])
    review_result = state.get("review_result", {})
    proposal_result = state.get("proposal_result", {})
    validation_result = state.get("validation_result", {})

    # Extract key information
    standard_id = review_result.get("standard_id", "")
    trigger_scenario = review_result.get("trigger_scenario", "")
    review_analysis = review_result.get("review_analysis", "")
    enhancement_proposal = proposal_result.get("enhancement_proposal", "")
    validation_output = validation_result.get("validation_result", "")

    # Create a formatted message
    formatted_message = f"""# Standards Enhancement Results for FAS {standard_id}

## Trigger Scenario
{trigger_scenario}

## Review Findings
{review_analysis}

## Proposed Enhancements
{enhancement_proposal}

## Validation Results
{validation_output}
"""

    new_message = AIMessage(content=formatted_message)

    # Create a new state with the formatted results
    new_state = state.copy()
    new_state["messages"] = messages + [new_message]

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


# Analyze transaction function
def analyze_transaction(state):
    """Analyze a transaction to identify applicable standards."""
    query = state["messages"][-1].content
    logging.info(f"Processing transaction query: {query[:100]}...")

    # Use the transaction description directly as a string
    transaction_input = query

    # Get the retrieved nodes directly to log them
    retrieved_nodes = transaction_analyzer.retriever.retrieve(transaction_input)

    # Log information about retrieved chunks
    logging.info(f"Retrieved {len(retrieved_nodes)} chunks for transaction analysis")
    for i, node in enumerate(retrieved_nodes[:3]):  # Show first 3 chunks
        logging.info(f"Chunk {i + 1}/{len(retrieved_nodes)}: {node.text[:150]}...")

    # Analyze the transaction (transaction_analyzer now handles string input)
    analysis_result = transaction_analyzer.analyze_transaction(transaction_input)

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
    transaction_input = state["messages"][
        -1
    ].content  # Use original query as string input
    standards = analysis["identified_standards"]

    # Get rationale for each standard (limit to top 2 for efficiency)
    standard_rationales = {}
    for std in standards[:2]:
        rationale_result = transaction_rationale.explain_standard_application(
            transaction_input, std
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
