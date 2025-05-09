from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import VALIDATOR_SYSTEM_PROMPT
from shariah_principles import format_principles_for_validation
from retreiver import retriever

class ValidatorAgent(Agent):
    """Agent responsible for validating proposed changes."""
    
    def __init__(self):
        super().__init__(system_prompt=VALIDATOR_SYSTEM_PROMPT)
    
    def validate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the proposed enhancements.
        
        Args:
            proposal: The dictionary returned by ProposerAgent.generate_enhancement_proposal()
            
        Returns:
            Dict with validation results
        """
        # Extract necessary information from proposal
        standard_id = proposal["standard_id"]
        trigger_scenario = proposal["trigger_scenario"]
        enhancement_proposal = proposal["enhancement_proposal"]
        
        # Get formatted principles for this standard
        shariah_principles = format_principles_for_validation(standard_id)
        
        # Use retriever to get related standards information
        related_query = f"Related standards to FAS {standard_id} and consistency considerations"
        related_nodes = retriever.retrieve(related_query)
        related_standards = "\n\n".join([node.text for node in related_nodes])
        
        # Prepare message for validation
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please validate this proposed enhancement to AAOIFI FAS {standard_id}:
            
Trigger Scenario:
{trigger_scenario}

Proposed Enhancement:
{enhancement_proposal}

Shariah Principles to Consider:
{shariah_principles}

Related Standards Context:
{related_standards}

Validate the proposal and provide:
1. Shariah Compliance Assessment: Does it comply with core Islamic principles?
2. Consistency Check: Is it consistent with the rest of FAS {standard_id} and other standards?
3. Practical Implementation Assessment: Can it be practically implemented?
4. Final Decision: APPROVED, REJECTED, or NEEDS REVISION with detailed reasoning
            """)
        ]
        
        # Get validation result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "enhancement_proposal": enhancement_proposal,
            "validation_result": response.content
        }

# Initialize the agent
validator_agent = ValidatorAgent()