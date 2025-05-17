"""
Service for financial product design functionality.
"""
import logging
from typing import Dict, Any

from ui.utils.product_design_utils import design_product

logger = logging.getLogger(__name__)


class ProductDesignService:
    """Service for handling product design operations."""

    @staticmethod
    def design_financial_product(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a financial product based on the provided requirements.
        
        Args:
            request_data: Dict containing product requirements
            
        Returns:
            Dict containing the designed product details
        """
        try:
            # Call the existing design_product function 
            results = design_product(request_data)
            return results
        except Exception as e:
            logger.error(f"Error in product design: {str(e)}")
            raise Exception(f"Failed to design product: {str(e)}")
