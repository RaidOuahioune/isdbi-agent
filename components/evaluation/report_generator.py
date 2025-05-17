"""
Report generator and visualization module for the evaluation system.
"""

from typing import Dict, Any, List, Optional
import json
import logging
import os
import datetime
from pathlib import Path

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
{"-" * len(f"{expertise.upper()} EVALUATION:")}
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
            "radar_data": {"labels": [], "datasets": []},
            "overall_score": evaluation_result.get("overall_score", 0),
        }

        # Extract average scores for each expertise area
        expertise_avg_scores = {}
        for expertise, evaluation in expert_evaluations.items():
            scores = evaluation.get("scores", {})
            if scores:
                avg_score = sum(scores.values()) / len(scores) if scores else 0
                expertise_avg_scores[expertise.replace("_", " ").title()] = round(
                    avg_score, 1
                )

        # Format data for radar chart
        visualization_data["radar_data"]["labels"] = list(expertise_avg_scores.keys())
        visualization_data["radar_data"]["datasets"].append(
            {"label": "Expert Scores", "data": list(expertise_avg_scores.values())}
        )

        return visualization_data

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """
        Ensure the specified directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory_path}")
        except Exception as e:
            logger.error(
                f"Error creating directory {directory_path}: {e}"
            ) @ staticmethod

    def save_text_report(
        evaluation_result: Dict[str, Any],
        report_dir: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """
        Generate and save a text report to a file.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Optional directory to save the report in
            file_path: Optional file path, if None will generate a timestamp-based path

        Returns:
            Path to the saved file
        """
        # Generate default file path if not provided
        if file_path is None:
            reports_dir = (
                Path(report_dir) / "text" if report_dir else Path("reports/text")
            )
            EvaluationReportGenerator.ensure_directory_exists(reports_dir)

            # Get evaluation ID or use timestamp
            eval_id = evaluation_result.get(
                "evaluation_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            )

            file_path = reports_dir / f"evaluation_{eval_id}.txt"

        # Generate the report
        report_text = EvaluationReportGenerator.generate_text_report(evaluation_result)

        # Save to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            logger.info(f"Text report saved to {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving text report to {file_path}: {e}")
            return "" @ staticmethod

    def save_json_report(
        evaluation_result: Dict[str, Any],
        report_dir: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """
        Generate and save a JSON report to a file.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Optional directory to save the report in
            file_path: Optional file path, if None will generate a timestamp-based path

        Returns:
            Path to the saved file
        """
        # Generate default file path if not provided
        if file_path is None:
            reports_dir = (
                Path(report_dir) / "json" if report_dir else Path("reports/json")
            )
            EvaluationReportGenerator.ensure_directory_exists(reports_dir)

            # Get evaluation ID or use timestamp
            eval_id = evaluation_result.get(
                "evaluation_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            )

            file_path = reports_dir / f"evaluation_{eval_id}.json"

        # Save to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(evaluation_result, f, indent=2)
            logger.info(f"JSON report saved to {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving JSON report to {file_path}: {e}")
            return "" @ staticmethod

    def save_markdown_report(
        evaluation_result: Dict[str, Any],
        report_dir: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """
        Generate and save a Markdown report to a file.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Optional directory to save the report in
            file_path: Optional file path, if None will generate a timestamp-based path

        Returns:
            Path to the saved file
        """
        # Generate default file path if not provided
        if file_path is None:
            reports_dir = (
                Path(report_dir) / "markdown"
                if report_dir
                else Path("reports/markdown")
            )
            EvaluationReportGenerator.ensure_directory_exists(reports_dir)

            # Get evaluation ID or use timestamp
            eval_id = evaluation_result.get(
                "evaluation_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            )

            file_path = reports_dir / f"evaluation_{eval_id}.md"

        # Generate the report
        report_md = EvaluationReportGenerator.generate_markdown_report(
            evaluation_result
        )

        # Save to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_md)
            logger.info(f"Markdown report saved to {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving markdown report to {file_path}: {e}")
            return "" @ staticmethod

    def save_all_formats(
        evaluation_result: Dict[str, Any],
        report_dir: Optional[str] = None,
        filename_base: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Save the evaluation report in all available formats.

        Args:
            evaluation_result: The full evaluation result
            report_dir: Optional directory to save the reports in
            filename_base: Optional base name for the report files

        Returns:
            Dictionary mapping format to saved file path
        """
        # Get evaluation ID or generate timestamp
        eval_id = evaluation_result.get(
            "evaluation_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        # Use filename_base if provided, otherwise use eval_id
        file_base = filename_base or f"evaluation_{eval_id}"

        # Set up base directory
        if report_dir is None:
            base_dir = Path("reports")
        else:
            base_dir = Path(report_dir)

        # Ensure base directory exists
        EvaluationReportGenerator.ensure_directory_exists(
            base_dir
        )  # Create paths for each format
        text_path = base_dir / "text" / f"{file_base}.txt"
        json_path = base_dir / "json" / f"{file_base}.json"
        md_path = base_dir / "markdown" / f"{file_base}.md"

        # Ensure subdirectories exist
        EvaluationReportGenerator.ensure_directory_exists(base_dir / "text")
        EvaluationReportGenerator.ensure_directory_exists(base_dir / "json")
        EvaluationReportGenerator.ensure_directory_exists(base_dir / "markdown")

        # Save in each format
        saved_paths = {
            "text": EvaluationReportGenerator.save_text_report(
                evaluation_result, str(base_dir), text_path
            ),
            "json": EvaluationReportGenerator.save_json_report(
                evaluation_result, str(base_dir), json_path
            ),
            "markdown": EvaluationReportGenerator.save_markdown_report(
                evaluation_result, str(base_dir), md_path
            ),
        }

        logger.info(f"Evaluation report saved in all formats: {saved_paths}")
        return saved_paths
