"""
This file serves as a compatibility layer that re-exports all agents from 
the new modular structure to maintain backward compatibility with existing code.
"""

# Re-export all agents from the components directory
from components.agents.orchestrator import orchestrator
from components.agents.standards_extractor import standards_extractor
from components.agents.use_case_processor import use_case_processor
from components.agents.reviewer_agent import reviewer_agent
from components.agents.proposer_agent import proposer_agent
from components.agents.validator_agent import validator_agent
from components.agents.transaction_analyzer import transaction_analyzer
from components.agents.transaction_rationale import transaction_rationale
from components.agents.knowledge_integration import knowledge_integration
from components.agents.cross_standard_analyzer import cross_standard_analyzer

# Re-export the base agent class
from components.agents.base_agent import Agent

# For backward compatibility, if any code directly imports these names
standards_agent = standards_extractor 
use_case_agent = use_case_processor

__all__ = [
    "orchestrator",
    "standards_extractor",
    "standards_agent",  # Alias for backward compatibility
    "use_case_processor",
    "use_case_agent",  # Alias for backward compatibility
    "reviewer_agent",
    "proposer_agent",
    "validator_agent",
    "cross_standard_analyzer",  # Our new agent
    "transaction_analyzer",
    "transaction_rationale",
    "knowledge_integration",
    "Agent",
]
