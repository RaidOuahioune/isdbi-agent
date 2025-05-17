from typing import Dict, Any, Optional
from components.agents.transaction_analyzer import transaction_analyzer
from components.agents.transaction_rationale import transaction_rationale


class TransactionService:
    """Service for interacting with transaction-related agents."""
    
    @staticmethod
    def analyze_transaction(transaction_details: str, additional_context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a financial transaction and determine compliance."""
        try:
            # Build the context
            context = transaction_details
            if additional_context:
                context += f"\n\nAdditional Context:\n{additional_context}"
                
            # Analyze the transaction
            analysis = transaction_analyzer.analyze_transaction(context)
            
            # Get rationale if available
            rationale = None
            try:
                rationale_result = transaction_rationale.generate_rationale(
                    transaction=transaction_details,
                    analysis=analysis["analysis"]
                )
                rationale = rationale_result.get("rationale", None)
            except Exception as e:
                # Log but continue even if rationale generation fails
                import logging
                logging.warning(f"Error generating rationale: {str(e)}")
                
            # Combine results
            result = {
                "analysis": analysis["analysis"],
                "compliant": analysis.get("compliant", False),
                "rationale": rationale
            }
            
            return result
        except Exception as e:
            # Log the exception
            import logging
            logging.error(f"Error analyzing transaction: {str(e)}")
            # Re-raise a more informative exception
            raise Exception(f"Failed to analyze transaction: {str(e)}")
