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
from utils.interactive_session import run_interactive_session
from utils.sample_tests import run_sample_tests
from utils.transaction_tests import run_category2_tests

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
    args = parser.parse_args()

    if args.category2_verbose:
        run_category2_tests(verbose=True)
    elif args.category2:
        run_category2_tests()
    elif args.samples:
        run_sample_tests()
    else:
        run_interactive_session()
