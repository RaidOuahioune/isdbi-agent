"""
Utility functions for standards enhancement operations.
"""

import os
import json
import datetime
from pathlib import Path
import pandas as pd

# Create directory for storing past enhancements if it doesn't exist
ENHANCEMENTS_DIR = Path(__file__).parent.parent.parent / "past_enhancements"
ENHANCEMENTS_DIR.mkdir(exist_ok=True)

def save_enhancement(results):
    """Save enhancement results to a file for future reference."""
    if not results:
        return False
    
    # Create a unique filename with timestamp and standard ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fas{results['standard_id']}_{timestamp}.json"
    filepath = ENHANCEMENTS_DIR / filename
    
    # Create metadata
    metadata = {
        "timestamp": timestamp,
        "standard_id": results['standard_id'],
        "trigger_scenario": results['trigger_scenario'],
        "decision": "APPROVED" if "APPROVED" in results['validation'] else 
                    "REJECTED" if "REJECTED" in results['validation'] else "NEEDS REVISION"
    }
    
    # Save the full results
    enhancement_data = {
        "metadata": metadata,
        "results": results
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(enhancement_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving enhancement: {e}")
        return False

def load_past_enhancements():
    """Load all saved enhancement results."""
    enhancements = []
    
    # List all JSON files in the directory
    for file in ENHANCEMENTS_DIR.glob("*.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # Add the filename for reference
                data["filename"] = file.name
                enhancements.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # Sort by timestamp (newest first)
    enhancements.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)
    return enhancements

def create_export_markdown(results):
    """Create a markdown export of enhancement results."""
    markdown_content = f"""# Standards Enhancement Results for FAS {results['standard_id']}

## Trigger Scenario
{results['trigger_scenario']}

## Review Findings
{results['review']}

## Proposed Enhancements
{results['proposal']}

## Validation Results
{results['validation']}"""

    # Add cross-standard analysis if available
    if "cross_standard_analysis" in results:
        markdown_content += f"""

## Cross-Standard Impact Analysis
{results['cross_standard_analysis']}"""
        
    return markdown_content

def create_export_html(results):
    """Create an HTML export of enhancement results."""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Standards Enhancement Report - FAS {results['standard_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1 {{ color: #1e3a8a; }}
        h2 {{ color: #2563eb; margin-top: 20px; }}
        .review-section {{ background-color: #f0f9ff; padding: 15px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }}
        .proposal-section {{ background-color: #f0fdf4; padding: 15px; border-radius: 5px; border-left: 5px solid #22c55e; margin-bottom: 20px; }}
        .validation-section {{ background-color: #fff7ed; padding: 15px; border-radius: 5px; border-left: 5px solid #f59e0b; margin-bottom: 20px; }}
        .cross-standard-section {{ background-color: #eef2ff; padding: 15px; border-radius: 5px; border-left: 5px solid #818cf8; margin-bottom: 20px; }}
        .scenario-section {{ background-color: #f8fafc; padding: 15px; border-radius: 5px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        pre {{ white-space: pre-wrap; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
        th {{ background-color: #f1f5f9; }}
    </style>
</head>
<body>
    <h1>Standards Enhancement Report - FAS {results['standard_id']}</h1>
    
    <h2>Trigger Scenario</h2>
    <div class="scenario-section">
        <p>{results['trigger_scenario']}</p>
    </div>
    
    <h2>Review Findings</h2>
    <div class="review-section">
        {results['review']}
    </div>
    
    <h2>Proposed Enhancements</h2>
    <div class="proposal-section">
        {results['proposal']}
    </div>
    
    <h2>Validation Results</h2>
    <div class="validation-section">
        {results['validation']}
    </div>
"""
    
    # Add cross-standard analysis if available
    if "cross_standard_analysis" in results:
        html_content += f"""
    <h2>Cross-Standard Impact Analysis</h2>
    <div class="cross-standard-section">
        {results['cross_standard_analysis']}
    </div>
"""
        
        # Add compatibility matrix if available
        if "compatibility_matrix" in results:
            html_content += """
    <h3>Compatibility Matrix</h3>
    <table>
        <tr>
            <th>Standard</th>
            <th>Impact Level</th>
            <th>Impact Type</th>
        </tr>
"""
            
            for item in results["compatibility_matrix"]:
                html_content += f"""
        <tr>
            <td>FAS {item['standard_id']}</td>
            <td>{item['impact_level']}</td>
            <td>{item['impact_type']}</td>
        </tr>
"""
            
            html_content += """
    </table>
"""
    
    # Complete the HTML
    html_content += f"""    
    <hr>
    <footer>
        <p><small>Generated by AAOIFI Standards Enhancement System - {datetime.datetime.now().strftime("%Y-%m-%d")}</small></p>
    </footer>
</body>
</html>"""
    
    return html_content 