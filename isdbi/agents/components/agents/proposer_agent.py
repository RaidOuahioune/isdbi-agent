from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import PROPOSER_SYSTEM_PROMPT

class ProposerAgent(Agent):
    """Agent responsible for proposing enhancements to standards."""
    
    def __init__(self):
        super().__init__(system_prompt=PROPOSER_SYSTEM_PROMPT)
    
    def generate_enhancement_proposal(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposed enhancements based on reviewer findings.
        
        Args:
            review_result: The dictionary returned by ReviewerAgent.extract_standard_elements()
            
        Returns:
            Dict with the proposal details
        """
        # Extract necessary information from review results
        standard_id = review_result["standard_id"]
        trigger_scenario = review_result["trigger_scenario"]
        review_content = review_result["review_content"]
        review_analysis = review_result["review_analysis"]
        
        # Prepare message for generating proposals
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please propose enhancements to AAOIFI FAS {standard_id} based on this review:
            
Trigger Scenario:
{trigger_scenario}

Relevant Standard Content:
{review_content}

Reviewer Analysis:
{review_analysis}

Provide specific enhancement proposals including:
1. The original text of sections needing enhancement
2. Your proposed modified text
3. Clear rationale for each proposed change
4. How the change addresses the trigger scenario
            """)
        ]
        
        # Get proposal result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review_analysis": review_analysis,
            "enhancement_proposal": response.content
        }

# Initialize the agent
proposer_agent = ProposerAgent()