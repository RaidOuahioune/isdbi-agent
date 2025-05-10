"""
Utility for handling and saving evaluation results
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class ResultsHandler:
    """Handles saving and loading of evaluation results"""
    
    def __init__(self):
        self.results_dir = Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def save_compliance_results(self, results: List[Dict[str, Any]], format: str = "json"):
        """
        Save compliance evaluation results in the specified format
        
        Args:
            results: List of evaluation results for each test case
            format: Output format ('json' or 'csv')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            output_file = self.results_dir / f"compliance_results_{timestamp}.json"
            
            # Format results for JSON
            formatted_results = []
            for result in results:
                test_case = result["test_case"]
                eval_result = result["evaluation"]
                
                formatted_results.append({
                    "test_case": test_case,
                    "overall_score": eval_result.get("overall_score", 0),
                    "expert_scores": {
                        expertise: evaluation.get("scores", {})
                        for expertise, evaluation in eval_result.get("expert_evaluations", {}).items()
                    }
                })
                
            with open(output_file, "w") as f:
                json.dump(formatted_results, f, indent=2)
                
        elif format == "csv":
            output_file = self.results_dir / f"compliance_results_{timestamp}.csv"
            
            # Prepare CSV headers and rows
            headers = ["test_case", "overall_score"]
            expert_types = ["shariah_compliance", "financial_accuracy", 
                          "standards_compliance", "logical_reasoning", "practical_application"]
            
            for expert in expert_types:
                headers.extend([f"{expert}_score"])
            
            rows = []
            for result in results:
                row = {
                    "test_case": result["test_case"],
                    "overall_score": result["evaluation"].get("overall_score", 0)
                }
                
                # Add expert scores
                expert_evals = result["evaluation"].get("expert_evaluations", {})
                for expert in expert_types:
                    eval_data = expert_evals.get(expert, {})
                    scores = eval_data.get("scores", {})
                    # Use the main score or average of subscores
                    if isinstance(scores, dict):
                        score = sum(scores.values()) / len(scores) if scores else 0
                    else:
                        score = 0
                    row[f"{expert}_score"] = round(score, 2)
                
                rows.append(row)
            
            # Write CSV file
            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
                
        print(f"Results saved to: {output_file}")