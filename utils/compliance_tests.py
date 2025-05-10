"""
Compliance testing module for the Islamic Finance standards system.
"""

import os
import logging
from typing import Dict, Any, Tuple
from pathlib import Path

from utils.document_processor import DocumentProcessor
from components.agents.compliance_verfiier import ComplianceVerifierAgent
from components.evaluation import evaluator
from utils.results_handler import ResultsHandler

def load_test_case(file_path: str) -> Tuple[str, str]:
    """
    Load a test case file and separate the report from violations.
    Returns tuple of (report_content, violations)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content at the violations section
    parts = content.split('VIOLATIONS:')
    if len(parts) != 2:
        raise ValueError(f"Invalid test case format in {file_path}")
        
    report = parts[0].strip()
    violations = parts[1].strip()
    
    return report, violations

def run_compliance_tests(verbose: bool = False, output_format: str = "json"):
    """
    Run compliance verification tests using cases from use_cases/compliance folder
    
    Args:
        verbose: If True, show detailed output
        output_format: Format to save results ('json' or 'csv')
    """
    print("\n" + "=" * 80)
    print("COMPLIANCE VERIFICATION TESTS")
    print("=" * 80)
    
    # Initialize components
    compliance_verifier = ComplianceVerifierAgent()
    results_handler = ResultsHandler()
    
    # Get all test cases
    test_cases_dir = Path(__file__).parent.parent / "use_cases" / "compliance"
    test_files = sorted(test_cases_dir.glob("*.txt"))
    
    results = []
    
    for test_file in test_files:
        print(f"\n\n----- TEST CASE: {test_file.name} -----\n")
        
        try:
            # Load and split test case
            report_content, violations = load_test_case(str(test_file))
            
            if verbose:
                print("Processing report...")
            
            # Run compliance verification
            verification_result = compliance_verifier.verify_compliance(report_content)
            
            print("\nCompliance Verification Results:")
            print("=" * 50)
            print(verification_result["compliance_report"])
            
            # Evaluate the verification against ground truth
            if verbose:
                print("\nEvaluating verification results...")
                
            eval_result = evaluator.evaluate(
                prompt=report_content,
                response=verification_result["compliance_report"],
                reference_answer=violations,
                output_format="text"  # Changed to text since we handle formatting separately
            )
            
            if verbose:
                print("\nEvaluation Results:")
                print(f"Overall Score: {eval_result.get('overall_score', 'N/A')}/10")
            
            results.append({
                "test_case": test_file.name,
                "evaluation": eval_result
            })
            
        except Exception as e:
            logging.error(f"Error processing test case {test_file}: {str(e)}")
            
        if test_file != test_files[-1]:
            cont = input("\nContinue to next test case? (y/n): ")
            if cont.lower() not in ["y", "yes"]:
                break
    
    # Save results
    results_handler.save_compliance_results(results, format=output_format)
    
    return results