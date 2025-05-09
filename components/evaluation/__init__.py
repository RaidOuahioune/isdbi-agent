"""
Main module for the ISDBI evaluation system.
Provides a simple API for evaluating responses from the multi-agent system.
"""

from typing import Dict, Any, List, Optional
import logging

# Import evaluation components
from components.evaluation.evaluation_manager import evaluation_manager
from components.evaluation.context_retriever import retrieve_evaluation_context
from components.evaluation.report_generator import EvaluationReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ISDBIEvaluator:
    """
    Main evaluator class that provides an API for the evaluation system.
    """
    
    def __init__(self):
        self.evaluation_manager = evaluation_manager
        self.report_generator = EvaluationReportGenerator()
    
    def evaluate(
        self,
        prompt: str,
        response: str,
        retrieve_context: bool = True,
        output_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Evaluate a response from the multi-agent system.
        
        Args:
            prompt: The original user prompt
            response: The system response to evaluate
            retrieve_context: Whether to retrieve context from vector DB
            output_format: Format for the report ('text', 'json', or 'markdown')
            
        Returns:
            Evaluation result with report in the specified format
        """
        logger.info(f"Starting evaluation for prompt: {prompt[:50]}...")
        
        # Retrieve context if requested
        context = None
        if retrieve_context:
            context = retrieve_evaluation_context(prompt, response)
        
        # Run the evaluation
        evaluation_result = self.evaluation_manager.evaluate_response(
            prompt, response, context
        )
        
        # Generate report in the requested format
        if output_format == "json":
            report = self.report_generator.generate_json_report(evaluation_result)
        elif output_format == "markdown":
            report = self.report_generator.generate_markdown_report(evaluation_result)
        else:  # Default to text
            report = self.report_generator.generate_text_report(evaluation_result)
        
        # Add visualization data
        visualization_data = self.report_generator.get_visualization_data(evaluation_result)
        
        # Return full results
        return {
            "evaluation_result": evaluation_result,
            "report": report,
            "visualization_data": visualization_data,
            "overall_score": evaluation_result.get("overall_score", 0)
        }


# Initialize the evaluator as a singleton
evaluator = ISDBIEvaluator()
