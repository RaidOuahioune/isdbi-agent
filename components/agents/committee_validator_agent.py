# filepath: c:\Users\monce\Documents\isdbi-agent\components\agents\committee_validator_agent.py
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
from components.agents.base_agent import Agent
from components.agents.prompts import COMMITTEE_VALIDATOR_SYSTEM_PROMPT
from shariah_principles import format_principles_for_validation
from retreiver import retriever
import difflib
import re
# Import the diff_utils functions
from tools.diff_utils import analyze_text_differences, format_difference_details

class CommitteeValidatorAgent(Agent):
    """Agent responsible for validating committee-edited enhancements to standards."""
    
    def __init__(self):
        super().__init__(system_prompt=COMMITTEE_VALIDATOR_SYSTEM_PROMPT)
    
    def validate_committee_edit(self, 
                              original_text: str, 
                              ai_proposed_text: str,
                              committee_edited_text: str,
                              standard_id: str,
                              trigger_scenario: str,
                              previous_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the committee-edited text against the original and AI-proposed text.
        
        Args:
            original_text: The original text from the standard
            ai_proposed_text: The text proposed by the AI agents
            committee_edited_text: The text edited by the committee
            standard_id: The ID of the standard (e.g., "10" for FAS 10)
            trigger_scenario: The scenario that triggered the enhancement
            previous_analysis: The previous analysis results from all agents
            
        Returns:
            Dict with validation results
        """
        # Get formatted principles for this standard
        shariah_principles = format_principles_for_validation(standard_id)
        
        # Extract relevant previous analyses for context
        review_analysis = previous_analysis.get("review", "")
        validation_result = previous_analysis.get("validation", "")
        
        # Convert the validation results to a summary for context
        validation_summary = self._extract_validation_summary(validation_result)
        
        # Perform detailed difference analysis using the imported functions
        diff_analysis = analyze_text_differences(ai_proposed_text, committee_edited_text)
        difference_details = format_difference_details(diff_analysis)
        
        # Prepare message for validation
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please validate this committee-edited enhancement to AAOIFI FAS {standard_id}:
            
Trigger Scenario:
{trigger_scenario}

Original Standard Text:
{original_text}

AI-Proposed Text:
{ai_proposed_text}

Committee-Edited Text:
{committee_edited_text}

## DETAILED DIFFERENCE ANALYSIS:
{difference_details}

Previous Review Analysis (Summary):
{review_analysis[:500]}...

Previous Validation (Summary):
{validation_summary}

Shariah Principles to Consider:
{shariah_principles}

Please provide:
1. Assessment of the specific changes made by the committee (focus on the exact differences highlighted above)
2. Status Decision: APPROVED, REJECTED, or NEEDS REVISION 
3. Brief Rationale: (max 3-5 sentences)
4. Suggestions: If needed, provide brief suggestions for improvement
            """)
        ]
        
        # Get validation result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "committee_validation_result": response.content,
            "original_text": original_text,
            "ai_proposed_text": ai_proposed_text,
            "committee_edited_text": committee_edited_text,
            "diff_analysis": diff_analysis
        }
    
    def _extract_validation_summary(self, validation_text: str) -> str:
        """
        Extract a summary from the previous validation results.
        
        Args:
            validation_text: The full validation text
            
        Returns:
            A summary of the validation
        """
        # Extract decision if available
        decision = ""
        if "APPROVED" in validation_text:
            decision = "APPROVED"
        elif "REJECTED" in validation_text:
            decision = "REJECTED"
        elif "NEEDS REVISION" in validation_text:
            decision = "NEEDS REVISION"
        
        # Extract a short summary (first 300 characters)
        summary = validation_text[:300] + "..." if len(validation_text) > 300 else validation_text
        
        if decision:
            return f"Previous decision: {decision}\n\nSummary: {summary}"
        else:
            return f"Summary: {summary}"

# Initialize the agent
committee_validator_agent = CommitteeValidatorAgent()
