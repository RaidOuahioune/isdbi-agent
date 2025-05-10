"""
Main entry point for the Islamic Finance standards system.
This file has been refactored to use modular components from the utils directory.
"""

import os
import argparse
import logging
import sys
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Import utility modules
from utils.sample_tests import run_sample_tests
from utils.transaction_tests import run_category2_tests
from utils.verify_compliance import verify_document_compliance
from utils.compliance_tests import run_compliance_tests

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Islamic Finance Standards Multi-Agent System"
    )
    parser.add_argument(
        "--samples", action="store_true", help="Run sample test queries"
    )
    parser.add_argument(
        "--category2",
        action="store_true",
        help="Run Category 2 reverse transaction tests",
    )
    parser.add_argument(
        "--category2-verbose",
        action="store_true",
        help="Run Category 2 reverse transaction tests with detailed retrieval logs",
    )
    parser.add_argument(
        "--category2-evaluate",
        action="store_true",
        help="Run Category 2 tests with evaluation of results",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run standalone evaluation tests on transaction analysis outputs",
    )
    parser.add_argument(
        "--evaluate-verbose",
        action="store_true",
        help="Run standalone evaluation tests with detailed output",
    )

    parser.add_argument(
        "--verify",
        type=str,
        help="Verify compliance of a document (provide file path)",
    )

    parser.add_argument(
        "--verify-verbose",
        action="store_true",
        help="Show detailed output during verification",
    )

    parser.add_argument(
        "--compliance-tests",
        action="store_true",
        help="Run compliance verification tests"
    )
    parser.add_argument(
        "--compliance-verbose",
        action="store_true",
        help="Run compliance tests with detailed output"
    )
    
    parser.add_argument(
        "--compliance-output",
        choices=["json", "csv"],
        default="json",
        help="Output format for compliance test results"
    )
    
    args = parser.parse_args()

    if args.compliance_tests or args.compliance_verbose:
        run_compliance_tests(
            verbose=args.compliance_verbose,
            output_format=args.compliance_output
        )
    elif args.verify:
        verify_document_compliance(args.verify, args.verify_verbose)
    elif args.category2_verbose:
        run_category2_tests(verbose=True)
    elif args.category2_evaluate:
        run_category2_tests(evaluate=True)
    elif args.category2:
        run_category2_tests()
    elif args.evaluate_verbose:
        run_category2_tests(evaluate=True, verbose=True)
    # elif args.evaluate:
    #     run_evaluation_tests()
    elif args.samples:
        run_sample_tests()
    else:
        print("No valid argument provided. Use --help for more information.")
