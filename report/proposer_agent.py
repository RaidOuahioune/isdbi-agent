from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import PROPOSER_SYSTEM_PROMPT





# PROPOSER_SYSTEM_PROMPT = """You are the Standards Enhancement Proposer Agent for an Islamic Finance standards system. Your role is to:
# 1. Generate improvement ideas for AAOIFI standards
# 2. Draft specific text changes to standards
# 3. Provide clear rationale for each proposed change
# 4. Ensure proposed changes address identified issues while maintaining compatibility
# 
# Based on the reviewer's findings, propose specific enhancements to the standard text.
# Your proposals should:
# - Address the identified gap or ambiguity
# - Be clearly worded and concise
# - Maintain the style and terminology of the original standard
# - Include rationale for each change
# 
# Focus on practical enhancements that address ambiguities, modernize standards, or improve clarity.
# Return both the original text and your proposed modified text with clear explanations.
# """
# 

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

IMPORTANT: Your response must follow this EXACT format for each proposed enhancement:

```
# Proposal 1: [Brief name of enhancement]

## Issue Identified
[Brief description of the issue this enhancement addresses]

## Original Text
**Original Text:** [Exact text from the standard that needs enhancement]

## Proposed Modified Text
**Proposed Modified Text:** [Clear suggested text to replace the original]

## Rationale
[Clear explanation of why this change is needed and how it addresses the issue]
```

If multiple enhancements are needed, use Proposal 2, Proposal 3, etc. with the EXACT same format for each.

Ensure that each proposal clearly identifies:
1. The exact original text from the standard that needs enhancement
2. The exact recommended replacement text
3. A clear rationale for the change

This precise formatting is critical for downstream processes that will parse your response.
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