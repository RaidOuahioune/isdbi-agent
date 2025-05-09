"""
Report generator and visualization module for the evaluation system.
"""

from typing import Dict, Any, List, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationReportGenerator:
    """
    Generates formatted evaluation reports and visualizations.
    """
    
    @staticmethod
    def generate_text_report(evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a text-based evaluation report.
        
        Args:
            evaluation_result: The full evaluation result from EvaluationManager
            
        Returns:
            Formatted text report
        """
        # Extract data from evaluation results
        expert_evaluations = evaluation_result.get("expert_evaluations", {})
        aggregated_scores = evaluation_result.get("aggregated_scores", {})
        consensus_report = evaluation_result.get("consensus_report", "")
        overall_score = aggregated_scores.get("overall_score", 0)
        
        # Generate header
        report = f"""
=======================================================================
                     ISDBI EVALUATION REPORT                        
=======================================================================
OVERALL SCORE: {overall_score}/10
=======================================================================

"""
        
        # Add consensus report
        report += f"""
CONSENSUS EVALUATION
-------------------
{consensus_report}

"""
        
        # Add score summary
        report += f"""
SCORE SUMMARY
------------
Overall Score: {overall_score}/10
Median Score: {aggregated_scores.get("median_score", 0)}/10
Range: {aggregated_scores.get("min_score", 0)} - {aggregated_scores.get("max_score", 0)}
Standard Deviation: {aggregated_scores.get("score_std_dev", 0)}

"""
        
        # Add expert evaluations
        report += """
DETAILED EXPERT EVALUATIONS
--------------------------
"""
        
        for expertise, evaluation in expert_evaluations.items():
            report += f"""
{expertise.upper()} EVALUATION:
{'-' * len(f"{expertise.upper()} EVALUATION:")}
{evaluation.get("evaluation", "No evaluation provided.")}

Scores: {evaluation.get("scores", {})}

"""
        
        return report
    
    @staticmethod
    def generate_json_report(evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a JSON-formatted evaluation report.
        
        Args:
            evaluation_result: The full evaluation result from EvaluationManager
            
        Returns:
            JSON string report
        """
        return json.dumps(evaluation_result, indent=2)
    
    @staticmethod
    def generate_markdown_report(evaluation_result: Dict[str, Any]) -> str:
        """
        Generate a Markdown-formatted evaluation report suitable for displaying in UI.
        
        Args:
            evaluation_result: The full evaluation result from EvaluationManager
            
        Returns:
            Markdown string report
        """
        # Extract data from evaluation results
        expert_evaluations = evaluation_result.get("expert_evaluations", {})
        aggregated_scores = evaluation_result.get("aggregated_scores", {})
        consensus_report = evaluation_result.get("consensus_report", "")
        overall_score = aggregated_scores.get("overall_score", 0)
        
        # Generate markdown report
        md_report = f"""
# ISDBI Evaluation Report

## Overall Score: {overall_score}/10

## Consensus Evaluation

{consensus_report}

## Score Summary

| Metric | Value |
|--------|-------|
| Overall Score | {overall_score}/10 |
| Median Score | {aggregated_scores.get("median_score", 0)}/10 |
| Min Score | {aggregated_scores.get("min_score", 0)}/10 |
| Max Score | {aggregated_scores.get("max_score", 0)}/10 |
| Standard Deviation | {aggregated_scores.get("score_std_dev", 0)} |

## Expert Evaluations
"""
        
        for expertise, evaluation in expert_evaluations.items():
            md_report += f"""
### {expertise.title()} Evaluation

{evaluation.get("evaluation", "No evaluation provided.")}

#### Scores:
"""
            
            scores = evaluation.get("scores", {})
            if scores:
                md_report += "| Criterion | Score |\n|----------|-------|\n"
                for criterion, score in scores.items():
                    md_report += f"| {criterion} | {score}/10 |\n"
            else:
                md_report += "*No scores provided*\n"
        
        return md_report
    
    @staticmethod
    def get_visualization_data(evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data for visualization from evaluation result.
        
        Args:
            evaluation_result: The full evaluation result
            
        Returns:
            Dictionary with structured data for visualization
        """
        # Extract scores by expert for visualization
        expert_evaluations = evaluation_result.get("expert_evaluations", {})
        visualization_data = {
            "radar_data": {
                "labels": [],
                "datasets": []
            },
            "overall_score": evaluation_result.get("overall_score", 0)
        }
        
        # Extract average scores for each expertise area
        expertise_avg_scores = {}
        for expertise, evaluation in expert_evaluations.items():
            scores = evaluation.get("scores", {})
            if scores:
                avg_score = sum(scores.values()) / len(scores) if scores else 0
                expertise_avg_scores[expertise.replace("_", " ").title()] = round(avg_score, 1)
        
        # Format data for radar chart
        visualization_data["radar_data"]["labels"] = list(expertise_avg_scores.keys())
        visualization_data["radar_data"]["datasets"].append({
            "label": "Expert Scores",
            "data": list(expertise_avg_scores.values())
        })
        
        return visualization_data
