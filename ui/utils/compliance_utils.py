"""
Utility functions for compliance verification in the Streamlit application.
"""

import sys
import os
import tempfile
import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import the agent
from components.agents.compliance_verfiier import ComplianceVerifierAgent
from utils.document_processor import DocumentProcessor

# Function to handle file upload and processing
def process_uploaded_file(uploaded_file):
    """Process an uploaded file and extract its content."""
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.'+uploaded_file.name.split('.')[-1]) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_file_path = temp_file.name
    
    # Process the document
    processor = DocumentProcessor()
    try:
        result = processor.process_document(temp_file_path)
        # Clean up the temporary file
        os.unlink(temp_file_path)
        return result
    except Exception as e:
        # Clean up the temporary file even if processing fails
        os.unlink(temp_file_path)
        raise e

# Function to verify compliance
def verify_compliance(document_content: str, document_name: str = "Uploaded Document") -> Dict[str, Any]:
    """
    Verify compliance of a financial report with AAOIFI standards.
    
    Args:
        document_content: The content of the financial report
        document_name: The name of the document
        
    Returns:
        Dict with compliance verification results
    """
    # Initialize the agent
    agent = ComplianceVerifierAgent()
    
    # Verify compliance
    result = agent.verify_compliance(document_content)
    
    # Add metadata
    result["document_name"] = document_name
    result["timestamp"] = datetime.datetime.now().isoformat()
    
    # Process the compliance report to extract structured data
    result["structured_report"] = parse_compliance_report(result["compliance_report"])
    
    return result

# Function to parse the compliance report table into structured data
def parse_compliance_report(report: str) -> List[Dict[str, Any]]:
    """
    Parse the compliance report table into structured data.
    
    Args:
        report: The compliance report as a string
        
    Returns:
        List of dictionaries with structured compliance data
    """
    # Extract the table from markdown format
    table_pattern = r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|'
    matches = re.findall(table_pattern, report)
    
    # Skip the header and separator rows
    data_rows = matches[2:] if len(matches) >= 2 else []
    
    # Process each row into structured data
    structured_data = []
    for row in data_rows:
        standard, requirement, status, comments = row
        
        # Determine status code
        status_code = "unknown"
        if "✅" in status:
            status_code = "compliant"
        elif "⚠️" in status:
            status_code = "partial"
        elif "❌" in status:
            status_code = "missing"
        
        structured_data.append({
            "standard": standard.strip(),
            "requirement": requirement.strip(),
            "status": status.strip(),
            "status_code": status_code,
            "comments": comments.strip()
        })
    
    return structured_data

# Function to calculate compliance statistics
def calculate_compliance_stats(structured_report: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics based on the compliance report.
    
    Args:
        structured_report: The structured compliance report
        
    Returns:
        Dict with compliance statistics
    """
    total = len(structured_report)
    compliant = sum(1 for item in structured_report if item["status_code"] == "compliant")
    partial = sum(1 for item in structured_report if item["status_code"] == "partial")
    missing = sum(1 for item in structured_report if item["status_code"] == "missing")
    
    # Calculate percentages
    compliance_rate = (compliant / total) * 100 if total > 0 else 0
    partial_rate = (partial / total) * 100 if total > 0 else 0
    missing_rate = (missing / total) * 100 if total > 0 else 0
    
    # Group by standard
    standards = {}
    for item in structured_report:
        standard = item["standard"]
        if standard not in standards:
            standards[standard] = {
                "total": 0,
                "compliant": 0,
                "partial": 0,
                "missing": 0
            }
        
        standards[standard]["total"] += 1
        if item["status_code"] == "compliant":
            standards[standard]["compliant"] += 1
        elif item["status_code"] == "partial":
            standards[standard]["partial"] += 1
        elif item["status_code"] == "missing":
            standards[standard]["missing"] += 1
    
    # Calculate compliance rate per standard
    for standard in standards:
        std_total = standards[standard]["total"]
        standards[standard]["compliance_rate"] = (standards[standard]["compliant"] / std_total) * 100 if std_total > 0 else 0
    
    return {
        "total_requirements": total,
        "compliant": compliant,
        "partial": partial,
        "missing": missing,
        "compliance_rate": compliance_rate,
        "partial_rate": partial_rate,
        "missing_rate": missing_rate,
        "standards": standards
    }

# Function to save compliance verification results
def save_verification_result(result: Dict[str, Any], filename: str = None) -> str:
    """
    Save compliance verification results to a file.
    
    Args:
        result: The compliance verification result
        filename: Optional filename to save to
        
    Returns:
        Path to the saved file
    """
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_verification_{timestamp}.json"
    
    # Create the directory if it doesn't exist
    save_dir = Path("compliance_results")
    save_dir.mkdir(exist_ok=True)
    
    # Save the result to a file
    save_path = save_dir / filename
    with open(save_path, "w") as f:
        json.dump(result, f, indent=2)
    
    return str(save_path)

# Function to load saved verification results
def load_past_verifications() -> List[Dict[str, Any]]:
    """
    Load past compliance verification results.
    
    Returns:
        List of past verification results
    """
    results = []
    save_dir = Path("compliance_results")
    
    if not save_dir.exists():
        return results
    
    for file_path in save_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                result = json.load(f)
                result["file_path"] = str(file_path)
                results.append(result)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return results 