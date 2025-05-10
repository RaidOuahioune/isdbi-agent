"""
Helper utilities for transaction analysis in the UI.
This file provides utility functions that bridge between the UI and the backend agents,
without modifying the original agent code.
"""

import json
import sys
import logging
import traceback
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoint for server-based analysis
API_ENDPOINT = "http://localhost:8000/api/agent"

# Flag to track if direct import is available
DIRECT_IMPORT_AVAILABLE = False

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import the transaction analyzer for direct method
try:
    from components.agents.transaction_analyzer import analyze_transaction as agent_analyze_transaction
    DIRECT_IMPORT_AVAILABLE = True
    logger.info("Successfully imported transaction analyzer for direct use.")
except ImportError as e:
    logger.warning(f"Could not import transaction analyzer directly: {e}")
    logger.warning("Will use API method as fallback.")

def analyze_transaction(
    transaction_details: Union[str, Dict[str, Any]], 
    use_api: bool = False
) -> Dict[str, Any]:
    """
    Analyze a transaction to identify applicable AAOIFI standards.
    This function serves as a bridge between the UI and the backend,
    supporting both direct and API-based analysis methods.
    
    Args:
        transaction_details: Transaction data as either a dict or string
        use_api: Whether to force using the API method
        
    Returns:
        Dict containing analysis results or error information
    """
    # Decide which method to use
    if DIRECT_IMPORT_AVAILABLE and not use_api:
        logger.info("Using direct method for transaction analysis")
        return analyze_with_direct_method(transaction_details)
    else:
        logger.info("Using API method for transaction analysis")
        return analyze_with_api_method(transaction_details)

def analyze_with_direct_method(transaction_details: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze transaction using direct method by calling the agent directly.
    
    Args:
        transaction_details: Transaction data as either a dict or string
        
    Returns:
        Dict containing analysis results or error information
    """
    try:
        # Prepare the input for the analyzer
        if isinstance(transaction_details, dict):
            # Convert to JSON string for the analyzer
            transaction_json = json.dumps(transaction_details)
        else:
            # Already a string
            transaction_json = transaction_details
        
        # Call the agent directly without modifying its code
        return agent_analyze_transaction(transaction_json)
    
    except Exception as e:
        logger.error(f"Error in direct transaction analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}

def analyze_with_api_method(transaction_details: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze transaction using API method by calling the server endpoint.
    
    Args:
        transaction_details: Transaction data as either a dict or string
        
    Returns:
        Dict containing analysis results or error information
    """
    try:
        # Prepare the request data
        if isinstance(transaction_details, dict):
            # Convert dict to a string representation for the API
            prompt = json.dumps(transaction_details)
        else:
            # Already a string
            prompt = transaction_details
        
        request_data = {
            "prompt": prompt,
            "task": "analyze_transaction",
            "options": {}
        }
        
        logger.info(f"Sending API request to {API_ENDPOINT}")
        
        # Make the API request
        response = requests.post(API_ENDPOINT, json=request_data)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the results from the response
            api_response = response.json()
            logger.info(f"API response status: {api_response.get('status')}")
            
            if api_response.get("status") == "success":
                # Return full result which contains all the analysis data
                return api_response["result"].get("full_result", {})
            else:
                # Return error
                error_msg = api_response.get("result", {}).get("error", "API request failed")
                logger.error(f"API error: {error_msg}")
                return {"error": error_msg}
        else:
            # Return error
            error_msg = f"API request failed with status code {response.status_code}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    except Exception as e:
        logger.error(f"Error in API transaction analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}

def format_transaction_for_display(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a transaction for display in the UI.
    
    Args:
        transaction: The transaction details
        
    Returns:
        Formatted transaction data
    """
    # Add any formatting logic here
    return transaction

def extract_standards_from_analysis(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract standards information from analysis results.
    
    Args:
        analysis_result: The complete analysis result
        
    Returns:
        Dict with extracted standards information
    """
    # If the result already has the right structure, return it
    if "applicable_standards" in analysis_result:
        return analysis_result
    
    # Otherwise try to extract standards from the analysis text
    standards = []
    analysis_text = analysis_result.get("analysis", "")
    
    # This is just a placeholder - in a real implementation,
    # you'd use regex or other methods to extract standards
    
    if "FAS 4" in analysis_text:
        standards.append({
            "standard_id": "FAS 4",
            "name": "Musharaka Financing",
            "probability": "Not specified",
            "reasoning": "Mentioned in analysis"
        })
    
    if "FAS 7" in analysis_text:
        standards.append({
            "standard_id": "FAS 7",
            "name": "Salam and Parallel Salam",
            "probability": "Not specified",
            "reasoning": "Mentioned in analysis"
        })
    
    # Add other standards as needed
    
    # Update the result with extracted standards
    analysis_result["applicable_standards"] = standards
    
    return analysis_result 