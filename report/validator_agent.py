from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
import requests
import json
import os
from components.agents.base_agent import Agent
from components.agents.prompts import VALIDATOR_SYSTEM_PROMPT
from shariah_principles import format_principles_for_validation
from retreiver import retriever





# VALIDATOR_SYSTEM_PROMPT = """You are the Standards Validator Agent for an Islamic Finance standards system. Your role is to:
# 1. Evaluate proposed changes against Shariah principles
# 2. Check compliance with core Islamic finance concepts
# 3. Verify internal consistency within the standard
# 4. Ensure proposed changes are practical and implementable
# 5. Provide clear reasoning for approval or rejection

# Given a proposed enhancement to an AAOIFI standard, evaluate whether it:
# - Complies with core Shariah principles (no Riba, Gharar, or Maysir)
# - Maintains consistency with the rest of the standard
# - Maintains alignment with other related standards
# - Provides practical guidance that can be implemented

# For each validation check, provide specific reasoning with references to Shariah principles or other aspects of the standard.
# Clearly indicate whether the proposal is APPROVED, REJECTED, or NEEDS REVISION with detailed feedback.
# """


class ValidatorAgent(Agent):
    """Agent responsible for validating proposed changes."""
    
    def __init__(self, use_compliance_api: bool = True, compliance_api_url: Optional[str] = None):
        """
        Initialize the validator agent.
        
        Args:
            use_compliance_api: Whether to use the Islamic Finance Compliance API
            compliance_api_url: URL of the Islamic Finance Compliance API
        """
        super().__init__(system_prompt=VALIDATOR_SYSTEM_PROMPT)
        self.use_compliance_api = use_compliance_api
        # Use environment variable if available, otherwise use provided URL or default
        self.compliance_api_url = os.environ.get(
            "ISLAMIC_FINANCE_API_URL", 
            compliance_api_url or "http://10.80.12.74:8000/api/ask"
        )
    
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
        validation_result = response.content
        
        # Use the Islamic Finance Compliance API as an additional validation source if enabled
        if self.use_compliance_api:
            try:
                shariah_compliance_check = self.check_shariah_compliance(standard_id, enhancement_proposal)
                validation_result = self.merge_validation_results(response.content, shariah_compliance_check)
            except Exception as e:
                print(f"ERROR using Islamic Finance Compliance API: {e}")
                # Fallback to the original validation if API fails
                validation_result = response.content
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "enhancement_proposal": enhancement_proposal,
            "validation_result": validation_result
        }
    
    def check_shariah_compliance(self, standard_id: str, enhancement_proposal: str) -> str:
        """
        Use the Islamic Finance Compliance API to get additional Shariah compliance insights.
        
        Args:
            standard_id: The ID of the standard being enhanced
            enhancement_proposal: The proposed changes to the standard
            
        Returns:
            String containing Shariah compliance assessment from external API
        """
        # API endpoint
        api_url = self.compliance_api_url
        
        # Construct a clear question for the API
        question = f"Is the following enhancement to FAS {standard_id} compliant with Shariah principles, specifically regarding Quran and Sunnah references? Enhancement details: {enhancement_proposal}"
        
        # Prepare the request
        payload = {
            "question": question,
            "top_k": 8,  # Retrieve more relevant documents for better context
            "temperature": 0.1  # Keep factual and precise
        }
        
        # Make the API request
        response = requests.post(api_url, json=payload, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("answer", "No answer provided from Islamic Finance Compliance API")
        else:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")
    
    def merge_validation_results(self, llm_validation: str, api_validation: str) -> str:
        """
        Merge validation results from the LLM and the external API.
        
        Args:
            llm_validation: Validation result from the primary LLM
            api_validation: Validation result from the Islamic Finance Compliance API
            
        Returns:
            Combined validation results structured for output parsing
        """
        combined_result = f"""# Validation Results

## Primary Validation Assessment
{llm_validation}

## Additional Shariah Compliance Insights
The following insights were provided by specialized Islamic Finance Compliance resources with access to Quran and Sunnah references:

{api_validation}

## Final Decision
"""
        
        # Extract the decision from the LLM validation if possible
        decision_match = None
        if "APPROVED" in llm_validation:
            decision_match = "APPROVED"
        elif "REJECTED" in llm_validation:
            decision_match = "REJECTED"
        elif "NEEDS REVISION" in llm_validation:
            decision_match = "NEEDS REVISION"
        
        # Determine if the API validation affects the decision
        api_contradicts_llm = False
        
        # Check if API validation contradicts LLM decision
        if decision_match == "APPROVED" and ("non-compliant" in api_validation.lower() or "contradicts" in api_validation.lower()):
            api_contradicts_llm = True
        
        # Add final decision based on both sources
        if api_contradicts_llm:
            combined_result += """Based on the specialized Islamic Finance Compliance assessment, there are important Shariah considerations that need to be addressed. Therefore, the final decision is: NEEDS REVISION

Please review the additional Shariah compliance insights and address the identified concerns."""
        elif decision_match:
            combined_result += f"After reviewing both the primary assessment and specialized Islamic Finance Compliance insights, the final decision is: {decision_match}"
        else:
            combined_result += "After reviewing both assessments, the final decision could not be determined clearly. Please review both validation results for a comprehensive understanding."
        
        return combined_result

# Initialize the agent with default settings (API enabled)
validator_agent = ValidatorAgent()