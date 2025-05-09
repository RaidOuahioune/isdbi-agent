from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from components.agents.base_agent import Agent
from components.agents.prompts import CROSS_STANDARD_ANALYZER_SYSTEM_PROMPT
from retreiver import retriever
import re

class CrossStandardAnalyzerAgent(Agent):
    """
    Agent responsible for analyzing how proposed standard enhancements might affect other standards.
    This agent identifies potential contradictions or synergies across different standards.
    """
    
    def __init__(self):
        super().__init__(system_prompt=CROSS_STANDARD_ANALYZER_SYSTEM_PROMPT)
    
    def analyze_cross_standard_impact(self, enhancement_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how a proposed standard enhancement might impact other related standards.
        
        Args:
            enhancement_results: The results from the standard enhancement process
            
        Returns:
            Dict with cross-standard impact analysis
        """
        # Extract key information from enhancement results
        standard_id = enhancement_results.get("standard_id", "")
        proposal = enhancement_results.get("proposal", "")
        original_text, proposed_text = self._extract_original_and_proposed(proposal)
        
        # Get related standards content
        related_standards = self._get_related_standards(standard_id)
        
        # Prepare the context for the agent prompt
        context = self._prepare_context(standard_id, original_text, proposed_text, related_standards)
        
        # Prepare message for analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=context)
        ]
        
        # Get analysis result
        response = self.llm.invoke(messages)
        
        # Extract the compatibility matrix from the response
        compatibility_matrix = self._extract_compatibility_matrix(response.content)
        
        return {
            "standard_id": standard_id,
            "original_text": original_text,
            "proposed_text": proposed_text,
            "cross_standard_analysis": response.content,
            "compatibility_matrix": compatibility_matrix
        }
    
    def _extract_original_and_proposed(self, proposal_text: str) -> tuple:
        """Extract original and proposed text from a proposal description."""
        # Simplified version - actual implementation would be more robust
        original_match = re.search(r"Original text:(.*?)(?:Proposed text:|$)", proposal_text, re.DOTALL)
        proposed_match = re.search(r"Proposed text:(.*?)(?:Rationale:|$)", proposal_text, re.DOTALL)
        
        original_text = original_match.group(1).strip() if original_match else ""
        proposed_text = proposed_match.group(1).strip() if proposed_match else ""
        
        return original_text, proposed_text
    
    def _get_related_standards(self, current_standard_id: str) -> Dict[str, str]:
        """
        Retrieve content from standards related to the current one.
        
        Args:
            current_standard_id: The ID of the standard being enhanced
            
        Returns:
            Dict mapping standard IDs to their content excerpts
        """
        # Standard IDs we're focusing on
        all_standard_ids = ["4", "7", "10", "28", "32"]
        
        # Remove the current standard from the list
        related_standard_ids = [sid for sid in all_standard_ids if sid != current_standard_id]
        
        # Dictionary to store related standards content
        related_standards = {}
        
        # Retrieve content for each related standard
        for standard_id in related_standard_ids:
            # Construct a query to retrieve key concepts from this standard
            retrieval_query = f"Key concepts, principles, and definitions in FAS {standard_id}"
            retrieved_nodes = retriever.retrieve(retrieval_query)
            
            # Extract text content from retrieved nodes
            content = "\n\n".join([node.text for node in retrieved_nodes[:5]])  # Limit to top 5 results
            related_standards[standard_id] = content
        
        return related_standards
    
    def _prepare_context(self, standard_id: str, original_text: str, proposed_text: str, related_standards: Dict[str, str]) -> str:
        """
        Prepare the context for the agent prompt.
        
        Args:
            standard_id: The ID of the standard being enhanced
            original_text: The original text from the standard
            proposed_text: The proposed enhanced text
            related_standards: Dict of related standards content
            
        Returns:
            Formatted context string for the prompt
        """
        context = f"""Please analyze how the proposed enhancement to FAS {standard_id} might impact other AAOIFI standards.

## Current Standard Being Enhanced
FAS {standard_id}

## Original Text
{original_text}

## Proposed Enhanced Text
{proposed_text}

## Related Standards Content"""
        
        # Add content from related standards
        for sid, content in related_standards.items():
            context += f"\n\n### FAS {sid}\n{content}"
        
        context += """

Please provide a detailed cross-standard impact analysis including:
1. A summary of how the proposed changes might affect other standards
2. Identification of potential contradictions or inconsistencies
3. Identification of potential synergies or positive impacts
4. A compatibility matrix showing the impact level (High/Medium/Low/None) for each standard
5. Specific recommendations for maintaining consistency across standards

Format the compatibility matrix as a table with columns for Standard ID, Impact Level, and Impact Type (Contradiction/Synergy/Both/None).
"""
        return context
    
    def _extract_compatibility_matrix(self, analysis_text: str) -> List[Dict[str, str]]:
        """
        Extract the compatibility matrix from the analysis text.
        
        Args:
            analysis_text: The full analysis text from the agent
            
        Returns:
            List of dicts representing the compatibility matrix
        """
        # Default empty matrix
        default_matrix = [
            {"standard_id": "4", "impact_level": "None", "impact_type": "None"},
            {"standard_id": "7", "impact_level": "None", "impact_type": "None"},
            {"standard_id": "10", "impact_level": "None", "impact_type": "None"},
            {"standard_id": "28", "impact_level": "None", "impact_type": "None"},
            {"standard_id": "32", "impact_level": "None", "impact_type": "None"}
        ]
        
        # Try to extract a matrix table from the response
        # This is a simplified extractor - would need more robust parsing in production
        matrix_pattern = r"(?:Compatibility Matrix|Impact Matrix).*?\n(.*?)(?:\n\n|\n#|\Z)"
        matrix_match = re.search(matrix_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        
        if not matrix_match:
            return default_matrix
        
        # Parse the matrix text
        matrix_text = matrix_match.group(1)
        matrix = []
        
        # Look for rows like "FAS 4 | Medium | Synergy"
        row_pattern = r"FAS\s+(\d+)\s*\|\s*(High|Medium|Low|None)\s*\|\s*(Contradiction|Synergy|Both|None)"
        for match in re.finditer(row_pattern, matrix_text, re.IGNORECASE):
            standard_id = match.group(1)
            impact_level = match.group(2)
            impact_type = match.group(3)
            
            matrix.append({
                "standard_id": standard_id,
                "impact_level": impact_level,
                "impact_type": impact_type
            })
        
        # If we couldn't parse anything, return the default matrix
        if not matrix:
            return default_matrix
            
        return matrix

# Initialize the agent
cross_standard_analyzer = CrossStandardAnalyzerAgent() 