"""
Standards Enhancement Demo

This script provides a demonstration of the Standards Enhancement feature
with the multi-agent architecture of Reviewer, Proposer, and Validator.
"""

import argparse
import sys
import time
from typing import Optional

from enhancement import run_standards_enhancement, ENHANCEMENT_TEST_CASES, format_results_for_display


def progress_callback(phase: str, detail: Optional[str] = None):
    """Simple callback function to show progress in the terminal."""
    if phase == "review_start":
        print("\n[PROGRESS] Starting review phase...")
    elif phase == "review_complete":
        print("[PROGRESS] Review phase completed")
        print("[PROGRESS] Starting proposal phase...")
    elif phase == "proposal_complete":
        print("[PROGRESS] Proposal phase completed")
        print("[PROGRESS] Starting validation phase...")
    elif phase == "validation_complete":
        print("[PROGRESS] Validation phase completed")
    elif phase == "cross_analysis_start":
        print("[PROGRESS] Starting cross-standard impact analysis...")
    elif phase == "cross_analysis_complete":
        print("[PROGRESS] Cross-standard impact analysis completed")
    
    if detail:
        print(f"[DETAIL] {detail}")


def run_demo_with_test_case(test_case_index, include_cross_standard=True):
    """Run a demo with a specific test case."""
    try:
        case = ENHANCEMENT_TEST_CASES[test_case_index]
    except IndexError:
        print(f"Error: Test case index {test_case_index} is out of range.")
        print(f"Available test cases: 0-{len(ENHANCEMENT_TEST_CASES)-1}")
        sys.exit(1)
    
    print("\n" + "="*80)
    print(f"Running Standards Enhancement for: {case['name']} (FAS {case['standard_id']})")
    if include_cross_standard:
        print("Including cross-standard impact analysis")
    else:
        print("Without cross-standard impact analysis")
    print("="*80)
    
    # Run the enhancement process with progress callback
    results = run_standards_enhancement(
        case['standard_id'], 
        case['trigger_scenario'],
        progress_callback,
        include_cross_standard_analysis=include_cross_standard
    )
    
    # Display the results
    formatted_results = format_results_for_display(results)
    print("\n" + formatted_results)
    
    return results


def run_interactive_demo():
    """Run an interactive demo of the Standards Enhancement feature."""
    print("\nStandards Enhancement Demo")
    print("=========================")
    print("This demo shows how AI agents can help enhance AAOIFI Financial Accounting Standards.")
    print("\nSelect a test case:")
    
    # Display available test cases
    for i, case in enumerate(ENHANCEMENT_TEST_CASES):
        print(f"{i}. {case['name']} (FAS {case['standard_id']})")
    
    # Get user selection
    while True:
        try:
            choice = input("\nEnter test case number (or 'q' to quit): ")
            if choice.lower() in ['q', 'quit', 'exit']:
                print("Exiting demo.")
                break
                
            test_case_index = int(choice)
            
            # Ask about cross-standard analysis
            cross_analysis = input("Include cross-standard impact analysis? (y/n, default: y): ").lower()
            include_cross = False if cross_analysis == 'n' else True
            
            results = run_demo_with_test_case(test_case_index, include_cross)
            
            # Ask if user wants to try another case
            another = input("\nTry another case? (y/n): ")
            if another.lower() not in ['y', 'yes']:
                print("Exiting demo.")
                break
                
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nDemo interrupted. Exiting.")
            break


def run_custom_demo():
    """Run a demo with custom input from the user."""
    print("\nCustom Standards Enhancement")
    print("===========================")
    
    # Get standard ID
    while True:
        standard_id = input("Enter standard ID (4, 7, 10, 28, 32): ")
        if standard_id in ['4', '7', '10', '28', '32']:
            break
        print("Invalid standard ID. Please choose from: 4, 7, 10, 28, 32")
    
    # Get trigger scenario
    print("\nEnter trigger scenario (describe a situation that might require enhancing the standard):")
    print("Example: Digital assets in Istisna'a contracts need clearer guidance...")
    trigger_scenario = input("> ")
    
    if not trigger_scenario:
        print("Empty scenario. Using default...")
        trigger_scenario = "A financial institution wants to apply this standard to digital assets and needs clearer guidance."
    
    # Ask about cross-standard analysis
    cross_analysis = input("Include cross-standard impact analysis? (y/n, default: y): ").lower()
    include_cross = False if cross_analysis == 'n' else True
    
    # Run the enhancement process
    print("\n" + "="*80)
    print(f"Running Standards Enhancement for custom scenario (FAS {standard_id})")
    if include_cross:
        print("Including cross-standard impact analysis")
    else:
        print("Without cross-standard impact analysis")
    print("="*80)
    
    # Run with progress callback
    results = run_standards_enhancement(
        standard_id, 
        trigger_scenario, 
        progress_callback,
        include_cross_standard_analysis=include_cross
    )
    
    # Display the results
    formatted_results = format_results_for_display(results)
    print("\n" + formatted_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standards Enhancement Demo")
    parser.add_argument("--test-case", type=int, help="Run a specific test case by index")
    parser.add_argument("--custom", action="store_true", help="Run with custom input")
    parser.add_argument("--all", action="store_true", help="Run all test cases")
    parser.add_argument("--no-cross-standard", action="store_true", help="Skip cross-standard impact analysis")
    
    args = parser.parse_args()
    
    # Determine whether to include cross-standard analysis
    include_cross_standard = not args.no_cross_standard
    
    if args.test_case is not None:
        run_demo_with_test_case(args.test_case, include_cross_standard)
    elif args.custom:
        run_custom_demo()
    elif args.all:
        print("\nRunning all test cases:")
        for i in range(len(ENHANCEMENT_TEST_CASES)):
            run_demo_with_test_case(i, include_cross_standard)
            if i < len(ENHANCEMENT_TEST_CASES) - 1:
                input("\nPress Enter to continue to the next test case...")
    else:
        run_interactive_demo() 