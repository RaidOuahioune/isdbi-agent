from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from components.agents.base_agent import Agent
from components.agents.prompts import CROSS_STANDARD_ANALYZER_SYSTEM_PROMPT
from retreiver import retriever
import re
import logging

# CROSS_STANDARD_ANALYZER_SYSTEM_PROMPT = """You are the Cross-Standard Impact Analyzer Agent for an Islamic Finance standards system.
# Your role is to:
# 1. Analyze proposed enhancements to AAOIFI standards and assess their impact on other related standards
# 2. Identify potential contradictions between the proposed changes and existing standards
# 3. Discover potential synergies where the enhancement might benefit other standards
# 4. Create a clear impact assessment showing the relationships between standards

# When analyzing a proposed standard enhancement:
# - Consider the core principles shared across Islamic finance standards
# - Identify concepts and definitions that appear in multiple standards
# - Assess if the proposed changes align with or contradict other standards
# - Consider how implementation of the change might affect institutions' compliance with other standards
# - Provide specific references to related standards to support your analysis

# Focus on the 5 selected standards: FAS 4 (Musharakah and Mudarabah), FAS 7 (Zakat), 
# FAS 10 (Istisna'a and Parallel Istisna'a), FAS 28 (Murabaha and Other Deferred Payment Sales), 
# and FAS 32 (Ijarah and Ijarah Muntahia Bittamleek).

# Your final output should include:
# 1. A summary of the proposed enhancement
# 2. A detailed cross-standard impact analysis
# 3. A compatibility matrix showing impact levels (High/Medium/Low/None) for each related standard
# 4. Specific recommendations for maintaining cross-standard consistency
# """

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        proposal = enhancement_results.get("proposed_changes_summary", "")
        
        # Return a graceful failure if proposal is missing
        if not proposal:
            logger.error("No proposal text provided for cross-standard analysis")
            return self._generate_fallback_analysis(standard_id)
        
        logger.info(f"Analyzing cross-standard impact for FAS {standard_id}")
        logger.debug(f"Proposal text length: {len(proposal)} characters")
        
        # Extract original and proposed text for reference
        original_text, proposed_text = self._extract_original_and_proposed(proposal)
        
        logger.info(f"Extracted original text ({len(original_text)} chars) and proposed text ({len(proposed_text)} chars)")
        
        # Get related standards content
        related_standards = self._get_related_standards(standard_id)
        
        # Prepare the context for the agent prompt
        # Use the full proposal text for better context
        context = self._prepare_context(standard_id, original_text, proposed_text, related_standards, proposal)
        
        # Prepare message for analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=context)
        ]
        
        # Get analysis result
        try:
            response = self.llm.invoke(messages)
            analysis_text = response.content
        except Exception as e:
            logger.error(f"Error invoking LLM for cross-standard analysis: {e}")
            analysis_text = f"Error generating cross-standard analysis: {str(e)}"
            return self._generate_fallback_analysis(standard_id, error_message=str(e))
        
        # Extract the compatibility matrix from the response
        compatibility_matrix = self._extract_compatibility_matrix(analysis_text)
        
        return {
            "standard_id": standard_id,
            "original_text": original_text,
            "proposed_text": proposed_text,
            "cross_standard_analysis": analysis_text,
            "compatibility_matrix": compatibility_matrix
        }
        
    def _generate_fallback_analysis(self, standard_id: str, error_message: str = None) -> Dict[str, Any]:
        """
        Generate a fallback analysis when the normal process fails.
        
        Args:
            standard_id: The standard ID
            error_message: Optional error message
            
        Returns:
            Dict with fallback analysis
        """
        error_note = f" Error: {error_message}" if error_message else ""
        
        fallback_analysis = f"""
## Cross-Standard Impact Analysis (Automated Fallback)

The system was unable to perform a detailed cross-standard impact analysis.{error_note}

To properly analyze cross-standard impacts, please ensure:
1. The proposal contains clearly marked original and proposed text sections
2. The enhancement details are sufficient for analysis
3. The system has access to related standards content

Please review the proposal structure and try again. For a comprehensive analysis, 
ensure that the original and proposed text sections are clearly labeled and formatted.
"""
        
        # Create a fallback compatibility matrix
        related_standard_ids = ["4", "7", "10", "28", "32"]
        related_standard_ids = [sid for sid in related_standard_ids if sid != standard_id]
        
        compatibility_matrix = [
            {"standard_id": sid, "impact_level": "Unknown", "impact_type": "Unknown"}
            for sid in related_standard_ids
        ]
        
        return {
            "standard_id": standard_id,
            "original_text": "Text extraction failed",
            "proposed_text": "Text extraction failed",
            "cross_standard_analysis": fallback_analysis,
            "compatibility_matrix": compatibility_matrix
        }
        
    def _prepare_context(self, standard_id: str, original_text: str, proposed_text: str, 
                         related_standards: Dict[str, str], full_proposal: str = None) -> str:
        """
        Prepare the context for the agent prompt.
        
        Args:
            standard_id: The ID of the standard being enhanced
            original_text: The original text from the standard
            proposed_text: The proposed enhanced text
            related_standards: Dict of related standards content
            full_proposal: Optional full proposal text to include if extraction failed
            
        Returns:
            Formatted context string for the prompt
        """
        context = f"""Please analyze how the proposed enhancement to FAS {standard_id} might impact other AAOIFI standards.

## Current Standard Being Enhanced
FAS {standard_id}

## Full Enhancement Proposal
{full_proposal}"""

        # Also include the extracted original and proposed text if available
        if original_text and proposed_text:
            context += f"""

## Extracted Original Text
{original_text}

## Extracted Proposed Enhanced Text
{proposed_text}"""

        context += """

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

Your response MUST follow this format:
```
## Cross-Standard Impact Analysis

[Your detailed analysis here]

## Compatibility Matrix

| Standard ID | Impact Level | Impact Type |
|-------------|--------------|-------------|
| FAS 4       | [Level]      | [Type]      |
| FAS 7       | [Level]      | [Type]      |
| FAS 10      | [Level]      | [Type]      |
| FAS 28      | [Level]      | [Type]      |
| FAS 32      | [Level]      | [Type]      |

## Recommendations

[Your recommendations for maintaining consistency]
```
"""
        return context
    
    def _extract_original_and_proposed(self, proposal_text: str) -> tuple:
        """Extract original and proposed text from a proposal description."""
        # Try to use the standardized format we've enforced in the proposer agent
        original_text = ""
        proposed_text = ""
        
        # Look for the standardized format with markdown headers
        orig_pattern = r"## Original Text\s*\n\*\*Original Text:\*\*\s*(.*?)(?=##|\Z)"
        prop_pattern = r"## Proposed Modified Text\s*\n\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\Z)"
        
        orig_match = re.search(orig_pattern, proposal_text, re.DOTALL)
        prop_match = re.search(prop_pattern, proposal_text, re.DOTALL)
        
        if orig_match and prop_match:
            original_text = orig_match.group(1).strip()
            proposed_text = prop_match.group(1).strip()
            return original_text, proposed_text
        
        # Backup patterns for the updated format
        orig_pattern2 = r"\*\*Original Text:\*\*\s*(.*?)(?=\*\*Proposed|##|\Z)"
        prop_pattern2 = r"\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\*\*Rationale|\Z)"
        
        orig_match = re.search(orig_pattern2, proposal_text, re.DOTALL)
        prop_match = re.search(prop_pattern2, proposal_text, re.DOTALL)
        
        if orig_match and prop_match:
            original_text = orig_match.group(1).strip()
            proposed_text = prop_match.group(1).strip()
            return original_text, proposed_text
        
        # More robust pattern matching for both single and multiple enhancement proposals
        # Look for various patterns that might appear in the proposal text
        original_patterns = [
            r"Original text:(.*?)(?:Proposed text:|$)",  # Simple case
            r"Original Text:(.*?)(?:Proposed Text:|Proposed Modified Text:|$)",  # Capital case
            r"\*\*Original Text\*\*\s*(?:\(.*?\))?\s*:(.*?)(?:\*\*Proposed|$)",  # Markdown format with stars
            r"Original Text \(.*?\):(.*?)(?:Proposed|$)",  # With parentheses
        ]
        
        proposed_patterns = [
            r"Proposed text:(.*?)(?:Rationale:|$)",  # Simple case
            r"Proposed Text:(.*?)(?:Rationale:|$)",  # Capital case
            r"Proposed Modified Text:(.*?)(?:Rationale:|$)",  # With "Modified"
            r"\*\*Proposed (?:Modified )?Text\*\*\s*(?:\(.*?\))?\s*:(.*?)(?:\*\*Rationale|$)",  # Markdown format
            r"Proposed (?:Modified )?Text \(.*?\):(.*?)(?:Rationale|$)",  # With parentheses
        ]
        
        # First try to find a single original/proposed pair
        for pattern in original_patterns:
            match = re.search(pattern, proposal_text, re.DOTALL | re.IGNORECASE)
            if match:
                original_text = match.group(1).strip()
                break
        
        for pattern in proposed_patterns:
            match = re.search(pattern, proposal_text, re.DOTALL | re.IGNORECASE)
            if match:
                proposed_text = match.group(1).strip()
                break
        
        # If we found both, return them
        if original_text and proposed_text:
            return original_text, proposed_text
        
        # If not found, try to extract from "Enhancement Proposal" or "Proposal" sections
        proposals = re.findall(r'(?:Enhancement Proposal|Proposal) \d+:.*?(?=(?:Enhancement Proposal|Proposal) \d+:|$)', 
                             proposal_text, re.DOTALL | re.IGNORECASE)
        
        if proposals:
            # For the first proposal, try to find original and proposed text
            for proposal in proposals:
                orig = ""
                prop = ""
                
                # Try all patterns on this specific proposal
                for pattern in original_patterns:
                    match = re.search(pattern, proposal, re.DOTALL | re.IGNORECASE)
                    if match:
                        orig = match.group(1).strip()
                        break
                        
                for pattern in proposed_patterns:
                    match = re.search(pattern, proposal, re.DOTALL | re.IGNORECASE)
                    if match:
                        prop = match.group(1).strip()
                        break
                        
                if orig and prop:
                    original_text = orig
                    proposed_text = prop
                    break
        
        # If still not found, look for sections marked with >
        if not original_text or not proposed_text:
            # Try to find quoted blocks with > markings (often used in Markdown)
            quote_blocks = re.findall(r'>\s*(.*?)(?=>\s*|$)', proposal_text, re.DOTALL)
            if len(quote_blocks) >= 2:
                # Assume first quote block is original, second is proposed
                original_text = quote_blocks[0].strip()
                proposed_text = quote_blocks[1].strip()
        
        # Last resort: If still nothing found, look for any text with bullet points or numbered lists
        if not original_text or not proposed_text:
            # Try to find sections with bullet points or numbering
            sections = re.findall(r'(?:\d+\.\s+|\*\s+|-).*?(?=\d+\.\s+|\*\s+|-|$)', proposal_text, re.DOTALL)
            if len(sections) >= 2:
                original_text = sections[0].strip()
                proposed_text = sections[1].strip()
        
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
        matrix_pattern = r"(?:Compatibility Matrix|Impact Matrix).*?\n(?:\|.*?\|.*?\|.*?\|\n)+(?:\|.*?\|.*?\|.*?\|\n?)+"
        matrix_match = re.search(matrix_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        
        if not matrix_match:
            logger.warning("No compatibility matrix found in analysis text")
            return default_matrix
        
        # Parse the matrix text
        matrix_text = matrix_match.group(0)
        matrix = []
        
        # Look for rows like "| FAS 4 | Medium | Synergy |"
        row_pattern = r"\|\s*FAS\s+(\d+)\s*\|\s*(High|Medium|Low|None)\s*\|\s*(Contradiction|Synergy|Both|None)\s*\|"
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
            logger.warning("Failed to parse compatibility matrix rows")
            return default_matrix
            
        return matrix

# Initialize the agent
cross_standard_analyzer = CrossStandardAnalyzerAgent() 