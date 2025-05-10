"""
Helper utilities for financial product design in the UI.
This file provides utility functions that bridge between the UI and the backend agents,
without using the agent graph.
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

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import the agents directly
try:
    from components.agents.product_design import product_design_advisor
    from components.agents.compliance_check import product_compliance_checker
    DIRECT_IMPORT_AVAILABLE = True
    logger.info("Successfully imported product design agents for direct use.")
except ImportError as e:
    logger.warning(f"Could not import product design agents directly: {e}")
    logger.warning("Will use alternative implementation.")
    DIRECT_IMPORT_AVAILABLE = False

def design_product(requirements: Dict[str, Any], use_api: bool = False) -> Dict[str, Any]:
    """
    Design a financial product based on the provided requirements.
    
    Args:
        requirements: Dict containing product requirements
        use_api: Whether to use API (not implemented yet)
        
    Returns:
        Dict containing the designed product
    """
    try:
        if DIRECT_IMPORT_AVAILABLE and not use_api:
            logger.info("Using direct agent call for product design")
            # Call the product design advisor agent directly
            product_design = product_design_advisor.design_product(requirements)
            
            # Get product concept for compliance check
            product_concept = {
                "name": product_design.get("suggested_product_concept_name", ""),
                "contracts": product_design.get("recommended_islamic_contracts", []),
                "structure": product_design.get("proposed_product_structure_overview", ""),
                "requirements": requirements
            }
            
            # Call the compliance checker agent directly
            compliance_assessment = product_compliance_checker.check_compliance(product_concept)
            
            # Merge the compliance assessment into the product design
            merged_result = {**product_design}
            
            # Override compliance info with the dedicated assessment
            if compliance_assessment:
                if "compliance_checkpoints" in compliance_assessment:
                    merged_result["shariah_compliance_checkpoints"] = compliance_assessment["compliance_checkpoints"]
                if "potential_concerns" in compliance_assessment:
                    merged_result["potential_areas_of_concern"] = compliance_assessment["potential_concerns"]
                if "risk_mitigation" in compliance_assessment:
                    merged_result["potential_risks_and_mitigation_notes"] = compliance_assessment["risk_mitigation"]
                if "next_steps" in compliance_assessment:
                    merged_result["next_steps_for_detailed_design"] = compliance_assessment["next_steps"]
            
            return merged_result
        else:
            logger.info("Direct agent call not available, using fallback implementation")
            # Fallback implementation - simplified version for testing
            # In a real implementation, this would call an API
            return create_fallback_product_design(requirements)
            
    except Exception as e:
        logger.error(f"Error in product design: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}

def create_fallback_product_design(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a fallback product design when the direct agent call is not available.
    This is a simplified version for testing and demonstration purposes.
    
    Args:
        requirements: Dict containing product requirements
        
    Returns:
        Dict containing a simple product design
    """
    # Extract requirements
    product_objective = requirements.get("product_objective", "Investment")
    risk_appetite = requirements.get("risk_appetite", "Medium")
    investment_tenor = requirements.get("investment_tenor", "Medium-term")
    target_audience = requirements.get("target_audience", "Investors")
    
    # Determine the default contract based on requirements
    contract = "Mudarabah"
    if risk_appetite == "Low":
        contract = "Murabaha"
    elif risk_appetite == "Medium" and "real estate" in str(requirements.get("asset_focus", "")).lower():
        contract = "Ijarah"
    
    # Create a basic product design
    return {
        "suggested_product_concept_name": f"{target_audience} {product_objective} {contract}",
        "recommended_islamic_contracts": [contract],
        "rationale_for_contract_selection": f"Selected {contract} based on {risk_appetite} risk appetite and {investment_tenor} tenor.",
        "proposed_product_structure_overview": f"""
PRODUCT_STRUCTURE:
1. Parties and Roles:
- Islamic Bank: Acts as the {contract} provider
- Investors: Provide capital
- Fund Manager: Manages investments

2. Flow of Funds/Assets:
- Investors provide capital to the bank
- Bank deploys capital according to {contract} principles
- Returns distributed according to pre-agreed ratios

3. Profit/Loss Mechanism:
- Profit sharing based on pre-agreed ratios
- Losses borne according to Shariah principles

4. Ownership Structure:
- Clear ownership of underlying assets
- Compliant with Shariah requirements
""",
        "key_aaoifi_fas_considerations": {
            "4": "Key accounting requirements for Mudarabah and Musharakah financing",
            "28": "Key accounting requirements for Murabaha and other deferred payment sales",
            "32": "Key accounting requirements for Ijarah and Ijarah Muntahia Bittamleek"
        },
        "shariah_compliance_checkpoints": [
            "Ensure clear profit-sharing mechanism",
            "Avoid guaranteed returns",
            "Maintain asset backing",
            "Ensure clear ownership structure"
        ],
        "potential_areas_of_concern": [
            "Risk of non-compliance with profit distribution",
            "Potential for hidden interest (Riba)"
        ],
        "potential_risks_and_mitigation_notes": "The product must ensure clear separation between profit and principal to avoid resembling interest-based products.",
        "next_steps_for_detailed_design": [
            "Develop detailed term sheet",
            "Consult with Shariah scholars",
            "Create operational workflows",
            "Prepare marketing materials"
        ],
        "original_requirements": requirements
    }

def save_product_design(product_design: Dict[str, Any]) -> str:
    """
    Save a product design to the database or file system.
    This is a simplified version for demonstration purposes.
    
    Args:
        product_design: The product design to save
        
    Returns:
        Identifier for the saved design
    """
    # In a real implementation, this would save to a database
    # For now, just return a fake ID
    import datetime
    design_id = f"design_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    logger.info(f"Product design saved with ID: {design_id}")
    
    return design_id

def load_past_designs() -> List[Dict[str, Any]]:
    """
    Load past product designs.
    This is a simplified version for demonstration purposes.
    
    Returns:
        List of past product designs
    """
    # In a real implementation, this would load from a database
    # For now, just return a list of sample designs
    sample_designs = [
        {
            "id": "design_sample1",
            "name": "Corporate Mudarabah Investment Fund",
            "date_created": "2023-05-12",
            "contract_type": "Mudarabah",
            "risk_profile": "Medium-High"
        },
        {
            "id": "design_sample2",
            "name": "Retail Home Ijarah Plan",
            "date_created": "2023-04-22",
            "contract_type": "Ijarah Muntahia Bittamleek",
            "risk_profile": "Low-Medium"
        },
        {
            "id": "design_sample3",
            "name": "SME Murabaha Financing",
            "date_created": "2023-03-18",
            "contract_type": "Murabaha",
            "risk_profile": "Low"
        }
    ]
    
    return sample_designs 