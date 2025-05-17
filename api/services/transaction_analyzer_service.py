from typing import Dict, Any, Union
from components.agents.transaction_analyzer import TransactionAnalyzerAgent

# Initialize the agent
transaction_analyzer = TransactionAnalyzerAgent()

class TransactionAnalyzerService:
    """Service for the detailed transaction analyzer agent."""
    
    @staticmethod
    def analyze_transaction(transaction_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a transaction using the transaction analyzer agent.
        
        Args:
            transaction_input: Either a string describing the transaction or a dict
                              containing transaction context, journal entries, and additional info
                              
        Returns:
            Dict containing analysis results
        """
        try:
            # Call the transaction analyzer agent
            result = transaction_analyzer.analyze_transaction(transaction_input)
            return result
        except Exception as e:
            # Log the exception
            import logging
            logging.error(f"Error in transaction analyzer: {str(e)}")
            # Re-raise a more informative exception
            raise Exception(f"Failed to analyze transaction: {str(e)}")
