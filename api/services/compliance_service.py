"""
Service for compliance verification functionality.
"""
import logging
from typing import Dict, Any

from ui.utils.compliance_utils import verify_compliance

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for handling compliance verification operations."""

    @staticmethod
    def verify_document_compliance(document_content: str, document_name: str = "Uploaded Document") -> Dict[str, Any]:
        """
        Verify compliance of a financial report with AAOIFI standards.
        
        Args:
            document_content: The content of the financial report
            document_name: The name of the document
            
        Returns:
            Dict with compliance verification results
        """
        try:
            # Call the existing verify_compliance function
            result = verify_compliance(document_content, document_name)
            return result
        except Exception as e:
            logger.error(f"Error in compliance verification: {str(e)}")
            raise Exception(f"Failed to verify compliance: {str(e)}")
