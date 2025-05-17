"""
Score processing utilities for the evaluation system.
Extracts and aggregates scores from evaluation outputs.
"""

import re
from statistics import mean, median, stdev
from typing import Dict, Any, List

import logging
logger = logging.getLogger(__name__)

class ScoreProcessor:
    """
    Processes and aggregates evaluation scores.
    """
    
    @staticmethod
    def extract_debate_scores(debate_summary: str) -> Dict[str, float]:
        """
        Extract scores from debate summary text.

        Args:
            debate_summary: The debate summary text

        Returns:
            Dict of criterion -> score mappings
        """
        lines = debate_summary.split("\n")
        scores = {}

        # Look for overall score pattern in the summary
        overall_match = re.search(r"(\d+(?:\.\d+)?)\s*\/\s*10", debate_summary)
        if overall_match:
            scores["Overall Score"] = float(overall_match.group(1))

        # Look for specific criteria scores
        for line in lines:
            if ":" in line and any(
                score in line.lower() for score in ["score", "/10", "rating", "points"]
            ):
                parts = line.split(":")
                if len(parts) >= 2:
                    criterion = parts[0].strip()
                    # Try to extract a number from the score part
                    score_text = parts[1].strip()
                    for word in score_text.split():
                        try:
                            score = float(word.replace("/10", ""))
                            scores[criterion] = score
                            break
                        except ValueError:
                            continue

        return scores
    
    @staticmethod
    def aggregate_scores(expert_evaluations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
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
        discrete_scores = {}

        for expertise, evaluation in expert_evaluations.items():
            # Handle regular scores (1-10 scale)
            scores = evaluation.get("scores", {})
            scores_by_expert[expertise] = scores

            # Extract numeric scores only
            numeric_scores = [
                score for score in scores.values() if isinstance(score, (int, float))
            ]
            all_scores.extend(numeric_scores)

            # Handle discrete scores (1-4 scale)
            discrete_score = evaluation.get("discrete_score")
            if discrete_score:
                discrete_scores[expertise] = {
                    "score": discrete_score,
                    "justification": evaluation.get("score_justification", ""),
                }

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

        # Add discrete scores if available
        if discrete_scores:
            aggregated["discrete_scores"] = discrete_scores

            # Calculate average discrete score
            discrete_values = [
                score["score"] for score in discrete_scores.values() if score["score"]
            ]
            if discrete_values:
                aggregated["avg_discrete_score"] = round(mean(discrete_values), 2)
                aggregated["overall_discrete_score"] = round(mean(discrete_values))

        return aggregated

# Create a singleton instance
score_processor = ScoreProcessor()
