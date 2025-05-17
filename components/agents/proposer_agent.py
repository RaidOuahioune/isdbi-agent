from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from components.agents.base_agent import Agent
from components.agents.prompts import PROPOSER_SYSTEM_PROMPT
import logging

class ProposerAgent(Agent):
    """Agent responsible for generating enhancement proposals"""
    
    def __init__(self):
        super().__init__(system_prompt=PROPOSER_SYSTEM_PROMPT)
    
    async def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an enhancement proposal based on analysis"""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Based on the following analysis of AAOIFI FAS {context['standard_id']},
propose specific enhancements to address the identified issues:

Trigger Scenario:
{context['trigger_scenario']}

Original Text:
{context['original_text']}

Analysis:
{context['analysis'].get('review_analysis', '')}

Enhancement Areas:
{self._format_enhancement_areas(context['analysis'].get('enhancement_areas', []))}

Provide a detailed proposal for enhancing the standard to better address the scenario.
""")
            ]
            
            response = self._invoke_with_retry(messages)
            
            return {
                "proposal": response.content,
                "rationale": self._extract_rationale(response.content)
            }
            
        except Exception as e:
            logging.error(f"Error generating proposal: {str(e)}")
            return {
                "proposal": "Proposal generation failed due to technical error",
                "rationale": ""
            }
    
    def _format_enhancement_areas(self, areas: List[str]) -> str:
        """Format enhancement areas for prompt"""
        return "\n".join(f"- {area}" for area in areas)
    
    def _extract_rationale(self, proposal: str) -> str:
        """Extract the rationale from the proposal text"""
        try:
            messages = [
                SystemMessage(content="Extract the rationale/justification for the proposed changes. Return as a concise summary."),
                HumanMessage(content=proposal)
            ]
            
            response = self._invoke_with_retry(messages)
            return response.content
            
        except Exception as e:
            logging.error(f"Error extracting rationale: {str(e)}")
            return ""

# Initialize the agent
proposer_agent = ProposerAgent()