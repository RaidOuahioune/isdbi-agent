"""
Interactive session module for the Islamic Finance standards system.
"""

import os
# from utils.query_processor import process_query
from enhancement import (
    run_standards_enhancement,
    ENHANCEMENT_TEST_CASES,
    format_results_for_display,
)

from components.evaluation import ISDBIEvaluator

evaluator = ISDBIEvaluator()


def run_interactive_session():
    """
    Run an interactive session with the multi-agent system.
    """
    print("Islamic Finance Standards Multi-Agent System")
    print("===========================================")
    print("Type 'exit' to quit.")
    print("\nAvailable commands:")
    print(
        "- /standards <id>: Get information about a specific standard (e.g., /standards 28)"
    )
    print("- /agents: List the available agents")
    print("- /clear: Clear the conversation history")
    print(
        "- /enhance <id>: Run standards enhancement for a specific standard (e.g., /enhance 10)"
    )
    print()

    while True:
        query = input("\nYou: ")

        if query.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        elif query.lower() == "/agents":
            print("\nAvailable Agents:")
            print(
                "1. Orchestrator Agent - Coordinates agent interactions and routes queries"
            )
            print(
                "2. Standards Extractor Agent - Extracts information from AAOIFI standards"
            )
            print(
                "3. Use Case Processor Agent - Analyzes financial scenarios and provides accounting guidance"
            )
            print("4. Standards Enhancement Agents:")
            print(
                "   - Reviewer Agent - Reviews standards and identifies areas for enhancement"
            )
            print("   - Proposer Agent - Proposes specific enhancements to standards")
            print(
                "   - Validator Agent - Validates proposals against Shariah principles"
            )

            continue

        elif query.lower() == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            print("Conversation cleared.")
            continue

        elif query.lower().startswith("/standards "):
            # Extract standard ID
            std_id = query.split(" ")[1].strip()
            print(f"\nFetching information about FAS {std_id}...")

            # Create a more specific query for standards information
            query = f"Please provide detailed information about AAOIFI Financial Accounting Standard (FAS) {std_id}."

        elif query.lower().startswith("/enhance "):
            # Extract standard ID
            std_id = query.split(" ")[1].strip()

            if std_id not in ["4", "7", "10", "28", "32"]:
                print("\nInvalid standard ID. Please choose from: 4, 7, 10, 28, 32")
                continue

            print(f"\nRunning Standards Enhancement for FAS {std_id}...")
            print("Select a trigger scenario or enter your own:")

            # Show available test cases for this standard
            relevant_cases = [
                case for case in ENHANCEMENT_TEST_CASES if case["standard_id"] == std_id
            ]
            if relevant_cases:
                for i, case in enumerate(relevant_cases, 1):
                    print(f"{i}. {case['name']}")
                print(f"{len(relevant_cases) + 1}. Custom scenario")

                choice = input("Select option: ")
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(relevant_cases):
                        # Use existing test case
                        trigger_scenario = relevant_cases[choice_num - 1][
                            "trigger_scenario"
                        ]
                    else:
                        # Custom scenario
                        trigger_scenario = input("Enter trigger scenario: ")
                except ValueError:
                    # Default to first case or custom input
                    trigger_scenario = input("Enter trigger scenario: ")
            else:
                trigger_scenario = input("Enter trigger scenario: ")

            # Run enhancement
            results = run_standards_enhancement(std_id, trigger_scenario)
            formatted_results = format_results_for_display(results)

            eval_result = evaluator.evaluate(
                prompt=f"""
                We want to enhance the following standard FAS-{std_id} to adapt to the following scenario:
                
                {trigger_scenario}.
                """,
                response=formatted_results,
                retrieve_context=True,
                output_format="markdown",
            )

            # Print and store evaluation results
            print(f"Overall Score: {eval_result.get('overall_score', 'N/A')}/10")
            print(f"Strongest Area: {eval_result.get('strongest_area', 'N/A')}")
            print(f"Weakest Area: {eval_result.get('weakest_area', 'N/A')}")

            print("\n" + formatted_results)
            continue

        # Process the query through our agent system
        # try:
        #     response = process_query(query)
        #     print(f"\nAssistant: {response.content}")
        # except Exception as e:
        #     print(f"\nError processing query: {e}")
        #     print("Please try again with a different query.")
