from typing import Dict, Any, Tuple, List
from langgraph.graph import StateGraph, END

from state import State, create_empty_state
from agents import orchestrator, standards_extractor, use_case_processor, reviewer_agent, proposer_agent, validator_agent


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
        query = latest_message.content
        # Use the orchestrator to determine routing
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
        standard_ids = ["28"]  # Default to FAS 28 for Ijarah if no specific standard mentioned
    
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
    
    # Extract standard ID (similar to extract_standard_ids)
    standard_id = "10"  # Default to FAS 10 (Istisna'a) if none specified
    for std in ["4", "7", "10", "28", "32"]:
        if f"FAS {std}" in query or f"FAS{std}" in query:
            standard_id = std
            break
    
    # The rest of the query serves as the trigger scenario
    # We could do more sophisticated extraction here
    trigger_scenario = query
    
    # Create a new state with enhancement info included
    new_state = state.copy()
    new_state["enhancement_info"] = {
        "standard_id": standard_id,
        "trigger_scenario": trigger_scenario
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
    review_result = reviewer_agent.extract_standard_elements(standard_id, trigger_scenario)
    
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
    from langchain_core.messages import AIMessage
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
    standard_ids = state.get("standard_ids", ["28"])  # Default to FAS 28 if none specified
    
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
        "extracted_info": "\n\n".join([
            f"FAS {std_id}:\n{info['extracted_info']}" 
            for std_id, info in standards_info.items()
        ])
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


def build_agent_graph() -> StateGraph:
    """
    Build the multi-agent graph for the Islamic finance standards system.
    
    This graph implements workflows between:
    - Orchestrator Agent - for query routing
    - Standards Extractor Agent - for extracting information from standards
    - Use Case Processor Agent - for processing financial scenarios
    - Standards Enhancement Agents - for enhancing standards
    
    The graph is designed to be extensible for future agent additions.
    """
    # Create the graph with the State type
    graph_builder = StateGraph(State)
    
    # Add nodes for each agent
    graph_builder.add_node("orchestrator", orchestrator)
    graph_builder.add_node("standards_extractor", standards_extractor)
    graph_builder.add_node("use_case_processor", use_case_processor)
    
    # Add special processing nodes
    graph_builder.add_node("extract_standard_ids", extract_standard_ids)
    graph_builder.add_node("standards_extractor_for_use_case", 
                           lambda state: {**state, "current_flow": "for_use_case"})
    graph_builder.add_node("prepare_standards_for_use_case", prepare_standards_for_use_case)
    graph_builder.add_node("process_use_case_with_standards", process_use_case_with_standards)
    
    # Add nodes for standards enhancement workflow
    graph_builder.add_node("extract_enhancement_info", extract_enhancement_info)
    graph_builder.add_node("reviewer_agent", run_reviewer_agent)
    graph_builder.add_node("proposer_agent", run_proposer_agent)
    graph_builder.add_node("validator_agent", run_validator_agent)
    graph_builder.add_node("format_enhancement_results", format_enhancement_results)
    
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
            "enhancement_workflow": "extract_enhancement_info",
            END: END
        }
    )
    
    # Standard extraction flow
    graph_builder.add_edge("extract_standard_ids", "standards_extractor")
    graph_builder.add_conditional_edges(
        "standards_extractor",
        lambda state: "for_use_case" if "for_use_case" in state.get("current_flow", "") else "end",
        {
            "for_use_case": "prepare_standards_for_use_case",
            "end": END
        }
    )
    
    # Use case flow with standards info
    graph_builder.add_edge("prepare_standards_for_use_case", "process_use_case_with_standards")
    graph_builder.add_edge("process_use_case_with_standards", END)
    
    # Direct use case processing (without standards extraction)
    graph_builder.add_edge("extract_standard_ids", "use_case_processor")
    graph_builder.add_edge("use_case_processor", END)
    
    # Standards enhancement workflow
    graph_builder.add_edge("extract_enhancement_info", "reviewer_agent")
    graph_builder.add_edge("reviewer_agent", "proposer_agent")
    graph_builder.add_edge("proposer_agent", "validator_agent")
    graph_builder.add_edge("validator_agent", "format_enhancement_results")
    graph_builder.add_edge("format_enhancement_results", END)
    
    # Compile the graph
    return graph_builder.compile()

# Create the agent graph
agent_graph = build_agent_graph()