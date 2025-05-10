#!/usr/bin/env python3
"""
Test script for the Financial Product Design Advisor.
This script runs through the test cases and captures results.
"""

import sys
import os
import json
from pathlib import Path
import time
from datetime import datetime
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import the product design function directly
try:
    from ui.utils.product_design_utils import design_product
    logger.info("Successfully imported product design utilities")
except ImportError as e:
    logger.error(f"Failed to import product design utilities: {e}")
    sys.exit(1)

# Define test cases based on the test case document
TEST_CASES = {
    "low_risk_product": {
        "name": "Low-Risk Product",
        "description": "Testing recommendation for low-risk requirements",
        "input": {
            "product_objective": "Secure asset financing for retail clients",
            "risk_appetite": "Low",
            "investment_tenor": "Short-term (up to 1 year)",
            "target_audience": "Retail investors",
            "asset_focus": "Vehicles/Equipment",
            "desired_features": ["Asset-backed", "Fixed periodic payments"]
        },
        "expected_contracts": ["Murabaha"]
    },
    "medium_risk_real_estate": {
        "name": "Medium-Risk Real Estate Product",
        "description": "Testing recommendation for real estate financing",
        "input": {
            "product_objective": "Home ownership financing product",
            "risk_appetite": "Medium",
            "investment_tenor": "Long-term (5+ years)",
            "target_audience": "Retail investors",
            "asset_focus": "Real estate",
            "desired_features": ["Asset-backed", "Fixed periodic payments", "Early termination option"]
        },
        "expected_contracts": ["Ijarah Muntahia Bittamleek", "Diminishing Musharakah"]
    },
    "high_risk_investment": {
        "name": "High-Risk Investment Product",
        "description": "Testing recommendation for high-risk investments",
        "input": {
            "product_objective": "Equity participation in technology startups",
            "risk_appetite": "High",
            "investment_tenor": "Medium-term (1-5 years)",
            "target_audience": "High Net Worth Individuals",
            "asset_focus": "Technology",
            "desired_features": ["Profit-sharing", "Tradable/Securitizable"]
        },
        "expected_contracts": ["Musharakah", "Mudarabah"]
    },
    "conflicting_requirements": {
        "name": "Conflicting Requirements",
        "description": "Testing with seemingly conflicting requirements",
        "input": {
            "product_objective": "Guaranteed returns with high profit potential",
            "risk_appetite": "Low",
            "investment_tenor": "Short-term (up to 1 year)",
            "desired_features": ["Capital protection features", "Profit-sharing"],
            "specific_exclusions": ["Avoid high market risk exposure"]
        },
        "expected_concerns": ["guaranteed returns", "fixed returns", "riba"]
    },
    "minimal_input": {
        "name": "Minimal Input",
        "description": "Testing with minimal input data",
        "input": {
            "product_objective": "Investment product"
        },
        "expected_result": "Should generate a recommendation"
    },
    "non_compliant_features": {
        "name": "Non-Compliant Features",
        "description": "Testing compliance identification of problematic features",
        "input": {
            "product_objective": "Fixed income investment product with guaranteed principal",
            "risk_appetite": "Low",
            "additional_notes": "Principal must be guaranteed and returns must be fixed at 5% annually"
        },
        "expected_concerns": ["guaranteed principal", "fixed returns", "interest", "riba"]
    },
    "complex_structure": {
        "name": "Complex Multi-Tier Structure",
        "description": "Testing compliance assessment of complex structures",
        "input": {
            "product_objective": "Multi-layered investment product with commodity Murabaha and options",
            "risk_appetite": "Medium",
            "additional_notes": "Product will use commodity Murabaha to generate fixed returns and incorporate derivatives for risk management"
        },
        "expected_concerns": ["derivatives", "options", "synthetic", "commodity murabaha"]
    },
    "islamic_mortgage": {
        "name": "Islamic Mortgage Alternative",
        "description": "Testing generation of a home financing product",
        "input": {
            "product_objective": "Shariah-compliant home financing product",
            "risk_appetite": "Medium",
            "investment_tenor": "Long-term (5+ years)",
            "target_audience": "Retail investors",
            "asset_focus": "Real estate",
            "desired_features": ["Asset-backed", "Fixed periodic payments", "Early termination option"],
            "additional_notes": "Must be competitive with conventional mortgages in terms of cost and flexibility"
        },
        "expected_contracts": ["Diminishing Musharakah", "Ijarah Muntahia Bittamleek"]
    },
    "sme_financing": {
        "name": "SME Financing Product",
        "description": "Testing generation of a business financing product for SMEs",
        "input": {
            "product_objective": "Working capital financing for small businesses",
            "risk_appetite": "Medium",
            "investment_tenor": "Medium-term (1-5 years)",
            "target_audience": "SMEs",
            "asset_focus": "No specific preference",
            "desired_features": ["Asset-backed", "Staged funding"],
            "additional_notes": "Needs to accommodate seasonal business cycles and varying cash flows"
        },
        "expected_contracts": ["Murabaha", "Salam"]
    },
    "investment_fund": {
        "name": "Islamic Investment Fund",
        "description": "Testing generation of an investment fund product",
        "input": {
            "product_objective": "Diversified ethical investment fund",
            "risk_appetite": "Medium to High",
            "investment_tenor": "Medium-term (1-5 years)",
            "target_audience": "Retail investors",
            "asset_focus": "Equity",
            "desired_features": ["Tradable/Securitizable", "Profit-sharing"],
            "additional_notes": "Focus on ethical screening and ESG factors alongside Shariah compliance"
        },
        "expected_contracts": ["Mudarabah", "Wakalah"]
    }
}

def evaluate_result(test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate the test result against expected outcomes.
    
    Args:
        test_case: The test case configuration
        result: The product design result
        
    Returns:
        Evaluation results
    """
    evaluation = {
        "test_case": test_case["name"],
        "passed": False,
        "contract_match": False,
        "concerns_identified": False,
        "has_standards": False,
        "has_compliance": False,
        "notes": []
    }
    
    # Check if any result was generated
    if not result or "error" in result:
        evaluation["notes"].append("Failed to generate a result")
        return evaluation
    
    # Check basic result structure
    if "recommended_islamic_contracts" not in result:
        evaluation["notes"].append("Missing recommended contracts")
        return evaluation
    
    # Check if expected contracts are present
    if "expected_contracts" in test_case:
        expected_contracts = [c.lower() for c in test_case["expected_contracts"]]
        recommended_contracts = [c.lower() for c in result["recommended_islamic_contracts"]]
        
        for expected in expected_contracts:
            if any(expected in rec for rec in recommended_contracts):
                evaluation["contract_match"] = True
                break
        
        if not evaluation["contract_match"]:
            evaluation["notes"].append(f"Expected one of {expected_contracts}, got {recommended_contracts}")
    
    # Check for expected concerns
    if "expected_concerns" in test_case:
        concerns_text = str(result.get("potential_areas_of_concern", "")).lower()
        concerns_text += str(result.get("potential_risks_and_mitigation_notes", "")).lower()
        
        found_concerns = []
        for concern in test_case["expected_concerns"]:
            if concern.lower() in concerns_text:
                found_concerns.append(concern)
        
        if found_concerns:
            evaluation["concerns_identified"] = True
        else:
            evaluation["notes"].append(f"Expected concerns about {test_case['expected_concerns']} not identified")
    
    # Check if standards info is present
    if result.get("key_aaoifi_fas_considerations"):
        evaluation["has_standards"] = True
    else:
        evaluation["notes"].append("Missing AAOIFI standards information")
    
    # Check if compliance info is present
    if result.get("shariah_compliance_checkpoints") and result.get("potential_areas_of_concern"):
        evaluation["has_compliance"] = True
    else:
        evaluation["notes"].append("Missing Shariah compliance information")
    
    # Overall pass/fail
    if "expected_contracts" in test_case and not evaluation["contract_match"]:
        evaluation["passed"] = False
    elif "expected_concerns" in test_case and not evaluation["concerns_identified"]:
        evaluation["passed"] = False
    elif not evaluation["has_standards"] or not evaluation["has_compliance"]:
        evaluation["passed"] = False
    else:
        evaluation["passed"] = True
    
    return evaluation

def run_tests(save_results: bool = True) -> Dict[str, Any]:
    """
    Run all defined test cases.
    
    Args:
        save_results: Whether to save the results to a file
        
    Returns:
        Test results
    """
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": 0,
        "tests_passed": 0,
        "test_results": {}
    }
    
    # Create results directory if saving
    if save_results:
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
    
    # Run each test case
    for test_id, test_case in TEST_CASES.items():
        logger.info(f"Running test case: {test_case['name']}")
        
        try:
            # Run the product design function
            start_time = time.time()
            result = design_product(test_case["input"])
            elapsed_time = time.time() - start_time
            
            # Evaluate the result
            evaluation = evaluate_result(test_case, result)
            
            # Save result details
            test_results["tests_run"] += 1
            if evaluation["passed"]:
                test_results["tests_passed"] += 1
            
            # Store full result data
            test_results["test_results"][test_id] = {
                "name": test_case["name"],
                "description": test_case["description"],
                "elapsed_time": elapsed_time,
                "evaluation": evaluation,
                "input": test_case["input"]
            }
            
            # Log the outcome
            status = "PASSED" if evaluation["passed"] else "FAILED"
            logger.info(f"Test {test_id}: {status} ({elapsed_time:.2f}s)")
            for note in evaluation.get("notes", []):
                logger.info(f"  - {note}")
            
            # Save individual test result
            if save_results:
                result_file = results_dir / f"result_{test_id}.json"
                with open(result_file, "w") as f:
                    result_data = {
                        "test_case": test_case,
                        "result": result,
                        "evaluation": evaluation,
                        "elapsed_time": elapsed_time
                    }
                    json.dump(result_data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error running test {test_id}: {e}")
            test_results["tests_run"] += 1
            test_results["test_results"][test_id] = {
                "name": test_case["name"],
                "description": test_case["description"],
                "error": str(e),
                "input": test_case["input"]
            }
    
    # Calculate summary
    test_results["success_rate"] = (test_results["tests_passed"] / test_results["tests_run"]) if test_results["tests_run"] > 0 else 0
    
    # Save overall results
    if save_results:
        summary_file = results_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump(test_results, f, indent=2)
    
    return test_results

def run_single_test(test_id: str, save_result: bool = True) -> Dict[str, Any]:
    """
    Run a single test case.
    
    Args:
        test_id: The ID of the test to run
        save_result: Whether to save the result to a file
        
    Returns:
        Test result
    """
    if test_id not in TEST_CASES:
        logger.error(f"Test ID '{test_id}' not found in test cases")
        return {"error": "Test ID not found"}
    
    test_case = TEST_CASES[test_id]
    logger.info(f"Running single test case: {test_case['name']}")
    
    try:
        # Run the product design function
        start_time = time.time()
        result = design_product(test_case["input"])
        elapsed_time = time.time() - start_time
        
        # Evaluate the result
        evaluation = evaluate_result(test_case, result)
        
        # Log the outcome
        status = "PASSED" if evaluation["passed"] else "FAILED"
        logger.info(f"Test {test_id}: {status} ({elapsed_time:.2f}s)")
        for note in evaluation.get("notes", []):
            logger.info(f"  - {note}")
        
        # Save test result
        if save_result:
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            
            result_file = results_dir / f"result_{test_id}.json"
            with open(result_file, "w") as f:
                result_data = {
                    "test_case": test_case,
                    "result": result,
                    "evaluation": evaluation,
                    "elapsed_time": elapsed_time
                }
                json.dump(result_data, f, indent=2)
        
        return {
            "test_case": test_case,
            "result": result,
            "evaluation": evaluation,
            "elapsed_time": elapsed_time
        }
    
    except Exception as e:
        logger.error(f"Error running test {test_id}: {e}")
        return {
            "test_case": test_case,
            "error": str(e)
        }

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run Financial Product Design Advisor tests")
    parser.add_argument("--test", help="Run a specific test by ID")
    parser.add_argument("--list", action="store_true", help="List available test cases")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to files")
    args = parser.parse_args()
    
    if args.list:
        # List available test cases
        print("Available test cases:")
        for test_id, test_case in TEST_CASES.items():
            print(f"  {test_id}: {test_case['name']}")
    elif args.test:
        # Run a specific test
        run_single_test(args.test, not args.no_save)
    else:
        # Run all tests
        results = run_tests(not args.no_save)
        print(f"\nTest Summary: {results['tests_passed']}/{results['tests_run']} tests passed ({results['success_rate']*100:.1f}%)") 