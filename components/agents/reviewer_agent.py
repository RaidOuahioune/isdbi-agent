from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import REVIEWER_SYSTEM_PROMPT
from retreiver import retriever



# REVIEWER_SYSTEM_PROMPT = """You are the Standards Reviewer Agent for an Islamic Finance standards system. Your role is to:
# 1. Parse and extract key elements from AAOIFI standards
# 2. Identify potential ambiguities, gaps, or inconsistencies in standards
# 3. Analyze the standard in the context of specific trigger scenarios
# 4. Extract sections that may need enhancement

# Given a standard ID and a trigger scenario, you will retrieve and analyze the relevant standard sections that may need enhancement.
# You should identify specific clauses, definitions, or guidelines that could be improved in light of the trigger scenario.

# Focus on the 5 selected standards: FAS 4, 7, 10, 28, and 32.

# Return detailed findings including:
# - The specific section/clause of the standard being analyzed
# - The potential gap or ambiguity identified
# - Why this might be an issue in the context of the trigger scenario
# """

class ReviewerAgent(Agent):
    """Agent responsible for reviewing standards and identifying areas for enhancement."""
    
    def __init__(self):
        super().__init__(system_prompt=REVIEWER_SYSTEM_PROMPT)
    
    def extract_standard_elements(self, standard_id: str, trigger_scenario: str) -> Dict[str, Any]:
        """
        Extract key elements and identify areas for enhancement.
        
        Args:
            standard_id: The ID of the standard (e.g., "10" for FAS 10)
            trigger_scenario: The scenario that triggers the need for enhancement
            
        Returns:
            Dict with analysis results
        """
        # Use retriever to get relevant chunks from standards
        retrieval_query = f"Standard FAS {standard_id} elements that might need enhancement regarding: {trigger_scenario}"
        retrieved_nodes = retriever.retrieve(retrieval_query)
        
        # Extract text content from retrieved nodes
        context = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Prepare message for analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please review AAOIFI FAS {standard_id} and identify elements that might need enhancement:
            
Trigger Scenario:
{trigger_scenario}

Relevant Sections from FAS {standard_id}:
{context}

Provide a detailed analysis of sections that might need enhancement, including:
1. Specific clauses or definitions that lack clarity or could be improved
2. Areas where the standard might not fully address the trigger scenario
3. Specific text that could be ambiguous when applied to this scenario
4. Potential inconsistencies within the standard or with other standards
            """)
        ]
        
        # Get analysis result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review_content": context, 
            "review_analysis": response.content
        }

# Initialize the agent
reviewer_agent = ReviewerAgent()