from typing import Dict, Any, Optional
from components.agents.use_case_processor import use_case_processor
from components.agents.standards_extractor import standards_extractor


class UseCaseService:
    """Service for interacting with use case processor agent."""
    
    @staticmethod
    def process_use_case(scenario: str, standards_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a financial scenario and provide accounting guidance."""
        try:
            result = use_case_processor.process_use_case(
                scenario=scenario,
                standards_info=standards_info
            )
            return result
        except Exception as e:
            # Log the exception
            import logging
            logging.error(f"Error processing use case: {str(e)}")
            # Re-raise a more informative exception
            raise Exception(f"Failed to process use case: {str(e)}")


class StandardsService:
    """Service for interacting with standards extractor agent."""
    
    @staticmethod
    def extract_standards(document_text: str, query: Optional[str] = None) -> Dict[str, Any]:
        """Extract standards information from document text."""
        try:
            extraction_params = {"document_text": document_text}
            if query:
                extraction_params["query"] = query
                
            result = standards_extractor.extract_standards(**extraction_params)
            return result
        except Exception as e:
            # Log the exception
            import logging
            logging.error(f"Error extracting standards: {str(e)}")
            # Re-raise a more informative exception
            raise Exception(f"Failed to extract standards: {str(e)}")
