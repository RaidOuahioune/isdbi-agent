from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List # Added List
from components.agents.base_agent import Agent
# from components.agents.prompts import PROPOSER_SYSTEM_PROMPT # Assuming this is defined elsewhere or inline

# Define PROPOSER_SYSTEM_PROMPT if not imported
PROPOSER_SYSTEM_PROMPT = """You are the Standards Enhancement Proposer Agent for an Islamic Finance standards system. Your role is to:
1. Generate improvement ideas for AAOIFI standards based on review findings.
2. Draft specific text changes to standards, clearly identifying original and proposed text.
3. Provide a clear rationale for each proposed change.
4. Ensure proposed changes address identified issues while maintaining compatibility with the overall standard.

Based on the reviewer's findings (including analysis and specific enhancement areas), propose specific enhancements to the standard text.
Your proposals should:
- Directly address the identified gap, ambiguity, or enhancement area.
- Be clearly worded and concise.
- Maintain the style and terminology of the original AAOIFI standard.
- Include a specific rationale for each distinct change.

Focus on practical enhancements that address ambiguities, modernize standards, or improve clarity.
It is critical that you return your response in the specified structured format for each proposal.
"""

class ProposerAgent(Agent):
    """Agent responsible for proposing enhancements to standards with structured output."""

    def __init__(self):
        super().__init__(system_prompt=PROPOSER_SYSTEM_PROMPT)

    def _format_enhancement_areas(self, areas: List[str]) -> str:
        """Format enhancement areas for prompt. Helper from new version."""
        if not areas:
            return "No specific enhancement areas were pre-identified."
        return "\n".join(f"- {area}" for area in areas)

    # If your ReviewerAgent now returns a more complex structure like the 'new' ProposerAgent expects:
    # async def generate_enhancement_proposal(self, reviewer_output: Dict[str, Any]) -> Dict[str, Any]:
    # Otherwise, stick to the simpler review_result if that's what ReviewerAgent provides.
    async def generate_enhancement_proposal(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposed enhancements based on reviewer findings, ensuring structured output.
        
        Args:
            review_result: The dictionary from the ReviewerAgent.
                           Expected keys: "standard_id", "trigger_scenario",
                                          "retrieved_context" (or "review_content"),
                                          "review_analysis", "enhancement_areas" (optional).
        Returns:
            Dict with the proposal details, where 'enhancement_proposal' is structured.
        """
        standard_id = review_result.get("standard_id", "N/A")
        trigger_scenario = review_result.get("trigger_scenario", "N/A")
        # Use 'retrieved_context' if that's what your current ReviewerAgent provides,
        # or 'review_content' if it's the older key.
        original_standard_text_context = review_result.get("retrieved_context") or review_result.get("review_content", "Original text not provided in review.")
        reviewer_analysis_text = review_result.get("review_analysis", "No detailed analysis provided.")
        enhancement_areas_list = review_result.get("enhancement_areas", [])

        formatted_enhancement_areas = self._format_enhancement_areas(enhancement_areas_list)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please propose specific enhancements to AAOIFI FAS {standard_id} based on the following review:
            
Trigger Scenario:
{trigger_scenario}

Identified Enhancement Areas from Reviewer:
{formatted_enhancement_areas}

Relevant Original Standard Content (Context provided by Reviewer):
{original_standard_text_context}

Reviewer's Detailed Analysis:
{reviewer_analysis_text}

IMPORTANT: Your response must follow this EXACT format for each proposed enhancement. If no enhancement is deemed necessary for a particular area, state that clearly under a proposal heading.

Proposal 1: [Brief, descriptive name for the enhancement, e.g., "Clarification of Term X"]
Issue Addressed / Enhancement Area
[Brief description of the issue this enhancement addresses, or the enhancement area it targets, based on the reviewer's findings.]
Original Text Snippet (if applicable)
Original Text: [Quote the specific, concise snippet from the 'Relevant Original Standard Content' above that this proposal aims to modify or replace. If adding new text where none existed, state "N/A - New section/clause".]
Proposed Modified or New Text
Proposed Text: [Provide the clear, exact text for the modification or the new addition. If deleting text, indicate "Text to be deleted: [quoted text]".]
Rationale
[Explain clearly why this change is necessary or beneficial. How does it address the identified issue or enhancement area? How does it improve the standard in light of the trigger scenario and reviewer's analysis?]

If multiple distinct enhancements are needed, create "Proposal 2", "Proposal 3", etc., following the exact same format for each.
Ensure each proposal is self-contained and clearly links the issue, original text (if any), proposed text, and rationale.
This precise formatting is critical for downstream automated parsing.
            """)
        ]
        
        # Assuming self.llm.invoke is async, as in your other agents
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "reviewer_analysis_summary": reviewer_analysis_text, # Or a summary if too long
            "enhancement_proposal_structured": response.content # This content is expected to be parsable
        }

# Initialize the agent
proposer_agent = ProposerAgent()