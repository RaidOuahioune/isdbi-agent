"""
Evaluation Manager for the ISDBI multi-agent evaluation system.
Coordinates the evaluation process and aggregates results from expert agents.
"""

from typing import Dict, Any, List, Optional
import logging
from statistics import mean, median, stdev
import json
from langchain_core.messages import SystemMessage, HumanMessage

# Import base agent class
from components.agents.base_agent import Agent
from components.agents.prompts import EVALUATION_MANAGER_SYSTEM_PROMPT

# Import expert evaluator agents
from components.evaluation.expert_agents import (
    shariah_expert,
    finance_expert,
    standards_expert,
    reasoning_expert,
    practical_expert,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationManager(Agent):
    """
    Manager class that coordinates evaluation across expert agents
    and aggregates results into a comprehensive assessment.
    """

    def __init__(self):
        super().__init__(system_prompt=EVALUATION_MANAGER_SYSTEM_PROMPT)

        # Initialize expert agents dictionary
        self.expert_agents = {
            "shariah_compliance": shariah_expert,
            "financial_accuracy": finance_expert,
            "standards_compliance": standards_expert,
            "logical_reasoning": reasoning_expert,
            "practical_application": practical_expert,
        }

    def evaluate_response(
        self,
        prompt: str,
        response: str,
        context: Optional[List[Dict[str, str]]] = None,
        fetch_additional_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Coordinate full evaluation of a response across all expert agents.

        Args:
            prompt: Original user prompt
            response: The multi-agent system response to evaluate
            context: Optional list of context documents from vector DB
            fetch_additional_context: Whether to fetch additional context automatically

        Returns:
            Comprehensive evaluation report with scores and feedback
        """
        logger.info(f"Starting evaluation of response to prompt: {prompt[:50]}...")

        # Collect evaluations from each expert agent
        expert_evaluations = {}
        keywords_collected = set()
        context_docs_used = []

        for expertise, agent in self.expert_agents.items():
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

                # Track keywords and context used for reporting
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

                logger.info(f"{expertise} evaluation complete.")
            except Exception as e:
                logger.error(f"Error in {expertise} evaluation: {e}")
                expert_evaluations[expertise] = {
                    "evaluation": f"Error during evaluation: {str(e)}",
                    "scores": {},
                }

        # Aggregate scores
        aggregated_scores = self._aggregate_scores(expert_evaluations)

        # Generate consensus report
        consensus_report = self._generate_consensus_report(
            expert_evaluations, aggregated_scores, prompt, response
        )

        # Prepare the evaluation summary with metadata about context usage
        return {
            "expert_evaluations": expert_evaluations,
            "aggregated_scores": aggregated_scores,
            "consensus_report": consensus_report,
            "overall_score": aggregated_scores.get("overall_score", 0),
            "context_metadata": {
                "keywords_extracted": list(keywords_collected),
                "context_usage": context_docs_used,
                "total_provided_context": len(context or []),
                "auto_context_enabled": fetch_additional_context,
            },
        }

    def _aggregate_scores(
        self, expert_evaluations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate scores from individual expert evaluations.

        Args:
            expert_evaluations: Dictionary of expert evaluations with scores

        Returns:
            Dictionary of aggregated scores with statistics
        """
        # Extract all scores from all experts
        all_scores = []
        scores_by_expert = {}

        for expertise, evaluation in expert_evaluations.items():
            scores = evaluation.get("scores", {})
            scores_by_expert[expertise] = scores

            # Extract numeric scores only
            numeric_scores = [
                score for score in scores.values() if isinstance(score, (int, float))
            ]
            all_scores.extend(numeric_scores)

        # Calculate aggregate statistics
        aggregated = {
            "scores_by_expert": scores_by_expert,
            "overall_score": round(mean(all_scores), 2) if all_scores else 0,
            "median_score": round(median(all_scores), 2) if all_scores else 0,
            "min_score": round(min(all_scores), 2) if all_scores else 0,
            "max_score": round(max(all_scores), 2) if all_scores else 0,
        }

        # Add standard deviation if we have enough scores
        if len(all_scores) > 1:
            aggregated["score_std_dev"] = round(stdev(all_scores), 2)

        return aggregated

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
            # Extract the first 300 characters of each evaluation as a summary
            eval_text = evaluation.get("evaluation", "")
            expert_summaries[expertise] = (
                eval_text[:300] + "..." if len(eval_text) > 300 else eval_text
            )

        # Format aggregated scores
        scores_str = json.dumps(aggregated_scores, indent=2)

        # Prepare message for generating consensus
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please generate a consensus evaluation report based on these expert evaluations:
                
Original Prompt:
{original_prompt}

Response Evaluated:
{original_response[:500]}... (truncated for brevity)

Expert Evaluations:
{json.dumps(expert_summaries, indent=2)}

Aggregated Scores:
{scores_str}

Generate a comprehensive consensus report that:
1. Summarizes the overall quality of the response (score: {aggregated_scores.get("overall_score", 0)}/10)
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


# Initialize the evaluation manager
evaluation_manager = EvaluationManager()
