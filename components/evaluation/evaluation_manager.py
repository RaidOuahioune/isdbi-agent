# filepath: c:\Users\ELITE COMPUTER\Desktop\Hackaton\isdbi\isdbi-agent\components\evaluation\evaluation_manager.py
"""
Evaluation Manager for the ISDBI multi-agent evaluation system.
Coordinates between different evaluation components to produce a comprehensive assessment.
"""

from typing import Dict, Any, List, Optional
import logging
import json

# You may need to install langchain with: pip install langchain-core
from langchain_core.messages import SystemMessage, HumanMessage

# Import base agent class
from components.agents.base_agent import Agent
from components.agents.prompts import EVALUATION_MANAGER_SYSTEM_PROMPT

# Import report generator for formatted output
from components.evaluation.report_generator import EvaluationReportGenerator

# Import expert evaluator agents
from components.evaluation.expert_agents import (
    shariah_expert,
    finance_expert,
    standards_expert,
)

# Import evaluation components
from components.evaluation.score_processor import score_processor
from components.evaluation.debate_evaluation_handler import debate_handler
from components.evaluation.standard_evaluation_handler import standard_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationManager(Agent):
    """
    Manager class that coordinates evaluation across expert agents
    and aggregates results into a comprehensive assessment.
    Uses specialized handlers for debate and standard evaluations.
    """

    def __init__(self):
        super().__init__(system_prompt=EVALUATION_MANAGER_SYSTEM_PROMPT)

        # Initialize expert agents dictionary
        self.expert_agents = {
            "shariah_compliance": shariah_expert,
            "financial_accuracy": finance_expert,
            "standards_compliance": standards_expert,
            # "logical_reasoning": reasoning_expert,
            # "practical_application": practical_expert,
        }

        # Initialize report generator
        self.report_generator = EvaluationReportGenerator()

    def evaluate_response(
        self,
        prompt: str,
        response: str,
        reference_answer: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        fetch_additional_context: bool = True,
        debate_domains: Optional[List[str]] = None,
        generate_report: bool = False,
        report_format: str = "markdown",  # Options: "text", "markdown", "json", "all"
        save_report: bool = False,
        output_dir: str = "reports",
    ) -> Dict[str, Any]:
        """
        Coordinate full evaluation of a response across all expert agents.

        Args:
            prompt: Original user prompt
            response: The multi-agent system response to evaluate
            reference_answer: Optional ground truth/reference answer
            context: Optional list of context documents from vector DB
            fetch_additional_context: Whether to fetch additional context automatically
            debate_domains: List of domains to debate (shariah, finance, legal)
            generate_report: Whether to generate a formatted report
            report_format: Format to generate ("text", "markdown", "json", "all")
            save_report: Whether to save the report to disk
            output_dir: Directory to save reports to if save_report is True

        Returns:
            Comprehensive evaluation report with scores and feedback
        """
        # Initialize evaluation tracking variables
        expert_evaluations, keywords_collected, context_docs_used, debate_results = (
            self._initialize_evaluation_trackers()
        )

        # Log evaluation start
        self._log_evaluation_start(prompt, reference_answer, context)

        # Set default debate domains if not provided
        if debate_domains is None:
            debate_domains = ["shariah", "finance", "legal"]

        # Create a mapping of expertise to debate domains
        expertise_to_domain = self._get_expertise_domain_mapping()

        # Run individual domain evaluations for remaining domains
        self._run_individual_evaluations(
            prompt,
            response,
            context,
            fetch_additional_context,
            debate_domains,
            expertise_to_domain,
            expert_evaluations,
            keywords_collected,
            context_docs_used,
            debate_results,
        )

        # Apply discrete scoring (1-4) using the scoring agent
        debate_handler.apply_discrete_scoring(
            prompt, response, debate_results, expert_evaluations, expertise_to_domain
        )

        # Aggregate results and generate final report
        evaluation_results = self._compile_evaluation_results(
            expert_evaluations,
            keywords_collected,
            context_docs_used,
            debate_results,
            prompt,
            response,
            fetch_additional_context,
            context,
        )

        # Generate and save reports if requested
        if generate_report:
            if report_format == "text":
                evaluation_results["formatted_report"] = self.generate_text_report(
                    evaluation_results
                )
                if save_report:
                    evaluation_results["report_file"] = self.save_text_report(
                        evaluation_results, output_dir
                    )
            elif report_format == "markdown":
                evaluation_results["formatted_report"] = self.generate_markdown_report(
                    evaluation_results
                )
                if save_report:
                    evaluation_results["report_file"] = self.save_markdown_report(
                        evaluation_result=evaluation_results,
                        report_dir=output_dir,
                        file_path="evaluation_report.md",
                    )
            elif report_format == "json":
                evaluation_results["formatted_report"] = self.generate_json_report(
                    evaluation_results
                )
                if save_report:
                    evaluation_results["report_file"] = self.save_json_report(
                        evaluation_results, report_dir=output_dir
                    )
            elif report_format == "all":
                evaluation_results["formatted_reports"] = {
                    "text": self.generate_text_report(evaluation_results),
                    "markdown": self.generate_markdown_report(evaluation_results),
                    "json": self.generate_json_report(evaluation_results),
                }
                if save_report:
                    evaluation_results["report_files"] = self.save_all_formats(
                        evaluation_results, output_dir
                    )

        return evaluation_results

    def _initialize_evaluation_trackers(self):
        """Initialize tracking variables for the evaluation process."""
        return {}, set(), [], {}

    def _log_evaluation_start(self, prompt, reference_answer, context):
        """Log the start of the evaluation process."""
        logger.info(f"Starting evaluation of response to prompt: {prompt}")
        logger.info(f"Evaluating response to prompt: {prompt[:50]}...")

        if reference_answer:
            logger.info("Reference answer provided for comparison")
        if context:
            logger.info(f"Context provided with {len(context)} documents")

    def _get_expertise_domain_mapping(self):
        """Return mapping between expertise areas and debate domains."""
        return {
            "shariah_compliance": "shariah",
            "financial_accuracy": "finance",
            "standards_compliance": "legal",
        }

    def _run_individual_evaluations(
        self,
        prompt,
        response,
        context,
        fetch_additional_context,
        debate_domains,
        expertise_to_domain,
        expert_evaluations,
        keywords_collected,
        context_docs_used,
        debate_results,
    ):
        """Run evaluations for individual domains not covered in multi-domain debate."""
        for expertise, agent in self.expert_agents.items():
            # Skip if already evaluated in multi-domain debate
            if expertise in debate_results:
                continue

            # Always use debate for expertise areas that map to domains
            if debate_handler.should_use_debate_for_expertise(
                expertise, expertise_to_domain, debate_domains
            ):
                debate_handler.run_single_domain_debate(
                    prompt,
                    response,
                    expertise,
                    expertise_to_domain,
                    context,
                    debate_results,
                    expert_evaluations,
                )
                continue

            # For standard evaluations (non-debate)
            standard_handler.run_standard_evaluation(
                prompt,
                response,
                context,
                fetch_additional_context,
                expertise,
                agent,
                expert_evaluations,
                keywords_collected,
                context_docs_used,
            )

    def _compile_evaluation_results(
        self,
        expert_evaluations,
        keywords_collected,
        context_docs_used,
        debate_results,
        prompt,
        response,
        fetch_additional_context,
        context,
    ):
        """Compile all evaluation results into the final report."""
        # Aggregate scores
        aggregated_scores = score_processor.aggregate_scores(expert_evaluations)

        # Generate consensus report
        consensus_report = self._generate_consensus_report(
            expert_evaluations, aggregated_scores, prompt, response
        )

        # Prepare the evaluation summary
        result = {
            "expert_evaluations": expert_evaluations,
            "aggregated_scores": aggregated_scores,
            "consensus_report": consensus_report,
            "overall_score": aggregated_scores.get("overall_score", 0),
            "discrete_scores": aggregated_scores.get("discrete_scores", {}),
            "context_metadata": {
                "keywords_extracted": list(keywords_collected),
                "context_usage": context_docs_used,
                "total_provided_context": len(context or []) if context else 0,
                "auto_context_enabled": fetch_additional_context,
            },
        }

        # Include debate results if any
        if debate_results:
            result["debate_results"] = debate_results
            result["debate_enabled"] = True

        return result

    def _generate_consensus_report(
        self,
        expert_evaluations: Dict[str, Dict[str, Any]],
        aggregated_scores: Dict[str, Any],
        original_prompt: str,
        original_response: str,
    ) -> str:
        """
        Generate a consensus report based on all expert evaluations.

        Args:
            expert_evaluations: Dictionary of expert evaluations
            aggregated_scores: Dictionary of aggregated score statistics
            original_prompt: The original user prompt
            original_response: The system response that was evaluated

        Returns:
            Consensus report text
        """
        # Format expert evaluations for the prompt
        expert_summaries = {}
        for expertise, evaluation in expert_evaluations.items():
            # Extract the evaluation as a summary
            eval_text = evaluation.get("evaluation", "")

            # Add discrete score information if available
            discrete_score = evaluation.get("discrete_score")
            if discrete_score:
                justification = evaluation.get("score_justification", "")
                eval_text += f"\n\nDiscrete Score (1-4): {discrete_score}\nJustification: {justification}"

            expert_summaries[expertise] = eval_text

        # Format aggregated scores
        scores_str = json.dumps(aggregated_scores, indent=2)

        # Include discrete scoring info in the prompt
        discrete_scoring_info = ""
        if "discrete_scores" in aggregated_scores:
            discrete_scoring_info = "\n\nDiscrete Scoring (1-4 scale):\n"
            for domain, score_info in aggregated_scores["discrete_scores"].items():
                discrete_scoring_info += (
                    f"{domain}: {score_info['score']} - {score_info['justification']}\n"
                )

            if "overall_discrete_score" in aggregated_scores:
                discrete_scoring_info += f"\nOverall Discrete Score: {aggregated_scores['overall_discrete_score']}/4"

        # Prepare message for generating consensus
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please generate a consensus evaluation report based on these expert evaluations:
                
Original Prompt:
{original_prompt}

Response Evaluated:
{original_response}

Expert Evaluations:
{json.dumps(expert_summaries, indent=2)}

Aggregated Scores:
{scores_str}
{discrete_scoring_info}

Generate a comprehensive consensus report that:
1. Summarizes the overall quality of the response using both the traditional scale (score: {aggregated_scores.get("overall_score", 0)}/10) 
   and the discrete scale ({aggregated_scores.get("overall_discrete_score", 0)}/4)
2. Identifies key strengths across multiple expert evaluations
3. Highlights consistent weaknesses or areas for improvement
4. Provides specific recommendations for enhancing future responses
5. Summarizes the level of agreement between experts
                """
            ),
        ]

        # Generate consensus report
        response = self.llm.invoke(messages)

        return response.content

    def generate_text_report(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a text-based evaluation report.

        Args:
            evaluation_result: The full evaluation result from evaluate_response

        Returns:
            Formatted text report
        """
        return self.report_generator.generate_text_report(evaluation_result)

    def generate_markdown_report(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a markdown-based evaluation report.

        Args:
            evaluation_result: The full evaluation result from evaluate_response

        Returns:
            Formatted markdown report
        """
        return self.report_generator.generate_markdown_report(evaluation_result)

    def generate_json_report(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a JSON-based evaluation report.

        Args:
            evaluation_result: The full evaluation result from evaluate_response

        Returns:
            Formatted JSON report
        """
        return self.report_generator.generate_json_report(evaluation_result)

    def save_text_report(
        self, evaluation_result: Dict[str, Any], report_dir: str = "reports"
    ) -> str:
        """
        Save a text report to disk.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Directory to save report to

        Returns:
            Path to saved report
        """
        return self.report_generator.save_text_report(
            evaluation_result, report_dir=report_dir
        )

    def save_markdown_report(
        self,
        evaluation_result: Dict[str, Any],
        report_dir: str = "reports",
        file_path: str = None,
    ) -> str:
        """
        Save a markdown report to disk.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Directory to save report to
            file_path: Optional specific file path to save to

        Returns:
            Path to saved report
        """
        return self.report_generator.save_markdown_report(
            evaluation_result, report_dir=report_dir, file_path=file_path
        )

    def save_json_report(
        self, evaluation_result: Dict[str, Any], report_dir: str = "reports"
    ) -> str:
        """
        Save a JSON report to disk.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Directory to save report to

        Returns:
            Path to saved report
        """
        return self.report_generator.save_json_report(
            evaluation_result, report_dir=report_dir
        )

    def save_all_formats(
        self, evaluation_result: Dict[str, Any], report_dir: str = "reports"
    ) -> Dict[str, str]:
        """
        Save reports in all formats.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Directory to save reports to

        Returns:
            Dictionary of format -> file path mappings
        """
        return self.report_generator.save_all_formats(
            evaluation_result, report_dir=report_dir
        )


# Create a singleton instance
evaluation_manager = EvaluationManager()
