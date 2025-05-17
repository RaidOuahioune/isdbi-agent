from components.agents.base_agent import Agent
from typing import Dict, Any, List, Optional
import re
import logging

# Set up prompt for the clause extractor agent
CLAUSE_EXTRACTOR_PROMPT = """
You are a specialized AI assistant tasked with extracting structured clause information from Islamic finance standard enhancement proposals.

Your primary goal is to identify specific clauses and their proposed modifications from the enhancement results.

When analyzing the enhancement proposal output:
1. Look for clearly defined clause identifiers (usually in formats like X/Y/Z, X.Y.Z, or simple numbers)
2. Extract the precise text of the proposed modification for each clause
3. Return the information in a structured format with clause_id and proposed_text

IMPORTANT:
- Focus only on the Enhancement Proposal section, not discussions or other parts
- Extract only the final proposed changes, not the original text or discussion points
- If clauses are not clearly numbered, try to infer logical sections and assign simple numeric IDs (1, 2, 3, etc.)
- Make sure the proposed_text is clean, coherent, and represents the complete modification
- If a clause has multiple sub-proposals, treat each as a separate enhancement
- Return the clauses in the order they appear in the document

Keep your responses structured and accurate. Your output will be used to generate PDF documents with the enhanced standard.
"""

class ClauseExtractorAgent(Agent):
    """
    Agent specialized in extracting clause information from enhancement results.
    """
    
    def __init__(self):
        super().__init__(system_prompt=CLAUSE_EXTRACTOR_PROMPT)
    
    def extract_clauses(self, enhancement_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract clauses and their proposed modifications from enhancement results.
        
        Args:
            enhancement_results: The results from the enhancement process
            
        Returns:
            List[Dict[str, str]]: List of dicts with clause_id and proposed_text
        """
        try:
            # Get the proposal text - try multiple possible locations
            proposal_text = ""
            possible_keys = [
                "final_proposal_structured", 
                "initial_proposal_structured",
                "enhancement_proposal",
                "proposal"
            ]
            
            for key in possible_keys:
                if key in enhancement_results and enhancement_results[key]:
                    proposal_text = enhancement_results[key]
                    if isinstance(proposal_text, dict):
                        # Try to extract from nested dict
                        for nested_key in possible_keys:
                            if nested_key in proposal_text:
                                proposal_text = proposal_text[nested_key]
                                break
                    break
            
            # If still no proposal text, try one more fallback
            if not proposal_text and isinstance(enhancement_results.get("proposal"), dict):
                proposal_text = enhancement_results["proposal"].get("proposal", "")
            
            if not proposal_text:
                logging.warning("No proposal text found in enhancement results")
                return []
            
            # Ensure proposal_text is a string
            if not isinstance(proposal_text, str):
                proposal_text = str(proposal_text)
            
            # Create a message to send to the LLM
            message = f"""
I need you to extract specific clause modifications from the following enhancement proposal:

{proposal_text}

Please identify each clause ID and its corresponding proposed text. Format your response as a list of JSON objects, each with 'clause_id' and 'proposed_text' fields. Do not include any explanations before or after the JSON list.
"""
            
            # Use the LLM to extract the clauses
            response = self._invoke_with_retry([
                {"type": "system", "content": CLAUSE_EXTRACTOR_PROMPT},
                {"type": "human", "content": message}
            ])
            
            # Extract the content from the response
            response_content = response.content
            
            # Try to extract JSON from the response
            import json
            
            # Look for anything resembling a JSON list in the response
            json_pattern = r'\[\s*\{.*?\}\s*\]'
            json_match = re.search(json_pattern, response_content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                extracted_clauses = json.loads(json_str)
            else:
                # If no JSON found, try a more manual extraction approach
                logging.warning("No JSON found in LLM response, attempting manual extraction")
                extracted_clauses = self._manual_clause_extraction(proposal_text)
            
            # Validate the extracted clauses
            valid_clauses = []
            for clause in extracted_clauses:
                if isinstance(clause, dict) and 'clause_id' in clause and 'proposed_text' in clause:
                    # Clean the extracted text
                    clause['proposed_text'] = clause['proposed_text'].strip()
                    if clause['proposed_text']:  # Only include if there's actual text
                        valid_clauses.append(clause)
            
            if not valid_clauses:
                logging.warning("No valid clauses extracted from enhancement proposal")
                # Fall back to creating a single clause
                valid_clauses = [{"clause_id": "1", "proposed_text": proposal_text}]
            
            return valid_clauses
            
        except Exception as e:
            logging.error(f"Error extracting clauses: {str(e)}")
            # Return a fallback single clause with the entire proposal text
            if proposal_text:
                return [{"clause_id": "1", "proposed_text": proposal_text}]
            return []
    
    def _manual_clause_extraction(self, proposal_text: str) -> List[Dict[str, str]]:
        """
        Manually extract clauses from the proposal text as a fallback method.
        
        Args:
            proposal_text: The text of the enhancement proposal
            
        Returns:
            List[Dict[str, str]]: List of dicts with clause_id and proposed_text
        """
        clauses = []
        
        # Try to find clause patterns like "Clause X/Y/Z:" or similar
        clause_pattern = re.compile(r"(?:Clause|Section|Article)\s+(\d+(?:/\d+)*)\s*[:;]?\s*(.*?)(?=(?:Clause|Section|Article)|$)", 
                                    re.DOTALL | re.IGNORECASE)
        matches = clause_pattern.findall(proposal_text)
        
        if matches:
            for clause_id, text in matches:
                clauses.append({
                    "clause_id": clause_id.strip(),
                    "proposed_text": text.strip()
                })
        else:
            # Try an alternative approach - look for numbered items
            alt_pattern = re.compile(r"(\d+(?:\.\d+)*)\s*[.:]?\s*(.*?)(?=\d+(?:\.\d+)*\s*[.:]|\Z)", 
                                    re.DOTALL)
            matches = alt_pattern.findall(proposal_text)
            
            if matches:
                for clause_id, text in matches:
                    clauses.append({
                        "clause_id": clause_id.strip(),
                        "proposed_text": text.strip()
                    })
        
        # If still no clauses found, split by paragraphs and assign numbers
        if not clauses:
            paragraphs = re.split(r'\n\s*\n', proposal_text)
            for i, para in enumerate(paragraphs, 1):
                if para.strip():
                    clauses.append({
                        "clause_id": str(i),
                        "proposed_text": para.strip()
                    })
        
        return clauses

# Create an instance of the agent
clause_extractor_agent = ClauseExtractorAgent() 