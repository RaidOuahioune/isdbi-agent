"""
Handler for standard (non-debate) evaluations in the ISDBI evaluation system.
"""

from typing import Dict, Any, List, Optional, Set
import logging

logger = logging.getLogger(__name__)

class StandardEvaluationHandler:
    """
    Handles standard (non-debate) evaluations and processing of results.
    """
    
    def __init__(self):
        """Initialize the standard evaluation handler."""
        pass
    
    def run_standard_evaluation(
        self,
        prompt: str,
        response: str,
        context: Optional[List[Dict[str, str]]],
        fetch_additional_context: bool,
        expertise: str,
        agent: Any,  # The actual agent implementation
        expert_evaluations: Dict[str, Dict[str, Any]],
        keywords_collected: Set[str],
        context_docs_used: List[str],
    ):
        """
        Run standard (non-debate) evaluation for an expertise area.
        
        Args:
            prompt: The original user prompt
            response: The response to evaluate
            context: Optional context documents
            fetch_additional_context: Whether to fetch additional context
            expertise: The expertise area
            agent: The expert agent to use for evaluation
            expert_evaluations: Dictionary to store evaluation results
            keywords_collected: Set to collect keywords used
            context_docs_used: List to track context documents used
        """
        logger.info(f"Running {expertise} evaluation...")
        try:
            # Run evaluation with the enhanced tool-calling capabilities
            evaluation = agent.evaluate(
                prompt=prompt,
                response=response,
                context=context,
                fetch_additional_context=fetch_additional_context,
            )

            # Store evaluation results
            expert_evaluations[expertise] = evaluation

            # Process context metadata
            self._process_context_metadata(
                evaluation, expertise, keywords_collected, context_docs_used
            )

            logger.info(f"{expertise} evaluation complete.")
        except Exception as e:
            logger.error(f"Error in {expertise} evaluation: {e}")
            expert_evaluations[expertise] = {
                "evaluation": f"Error during evaluation: {str(e)}",
                "scores": {},
            }
    
    def _process_context_metadata(
        self, 
        evaluation: Dict[str, Any], 
        expertise: str, 
        keywords_collected: Set[str], 
        context_docs_used: List[str]
    ):
        """
        Process and collect context metadata from an evaluation.
        
        Args:
            evaluation: The evaluation result
            expertise: The expertise area
            keywords_collected: Set to collect keywords used
            context_docs_used: List to track context documents used
        """
        if "context_used" in evaluation:
            if "keywords_used" in evaluation["context_used"]:
                keywords_collected.update(
                    evaluation["context_used"].get("keywords_used", [])
                )

            additional_context_count = evaluation["context_used"].get(
                "additional_context_count", 0
            )
            if additional_context_count > 0:
                context_docs_used.append(
                    f"{expertise}: {additional_context_count} docs"
                )

# Create a singleton instance
standard_handler = StandardEvaluationHandler()
