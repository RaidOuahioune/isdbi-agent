"""
Main agent graph builder for the Islamic Finance standards system.
This module builds and exports the agent graph for the application.
"""

from typing import Dict, Any, Tuple, List
import logging
import sys
import regex as re
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from state import State, create_empty_state

# Import agents
from components.agents.orchestrator import orchestrator
from components.agents.standards_extractor import standards_extractor
from components.agents.use_case_processor import use_case_processor
from components.agents.reviewer_agent import reviewer_agent
from components.agents.proposer_agent import proposer_agent
from components.agents.validator_agent import validator_agent
from components.agents.transaction_analyzer import transaction_analyzer
from components.agents.transaction_rationale import transaction_rationale
from components.agents.knowledge_integration import knowledge_integration

# Import graph routing and node functions
from components.graph.router import route_query, route_after_standards_extraction
from components.graph.nodes import (
    extract_standard_ids,
    extract_enhancement_info,
    run_reviewer_agent,
    run_proposer_agent,
    run_validator_agent,
    format_enhancement_results,
    prepare_standards_for_use_case,
    process_use_case_with_standards,
    analyze_transaction,
    explain_standards_rationale,
    integrate_transaction_knowledge,
)


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
            END: END,
            "transaction_analyzer": "transaction_analyzer",
        }
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
    
    # Standards enhancement workflow
    graph_builder.add_edge("extract_enhancement_info", "reviewer_agent")
    graph_builder.add_edge("reviewer_agent", "proposer_agent")
    graph_builder.add_edge("proposer_agent", "validator_agent")
    graph_builder.add_edge("validator_agent", "format_enhancement_results")
    graph_builder.add_edge("format_enhancement_results", END)
    
    # Transaction analyzer flow
    graph_builder.add_edge("transaction_analyzer", "transaction_rationale")
    graph_builder.add_edge("transaction_rationale", "knowledge_integration")
    graph_builder.add_edge("knowledge_integration", "final_response")
    graph_builder.add_edge("final_response", END)

    # Compile the graph
    return graph_builder.compile()


# Create the agent graph
agent_graph = build_agent_graph()
