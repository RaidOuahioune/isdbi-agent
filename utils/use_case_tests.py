"""
Use case testing module for the Islamic Finance standards system.
"""

import sys
import os
import json

# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.agents.use_case_processor import use_case_processor
from components.test.use_case import test_cases
from retreiver import retriever

# Try importing evaluation components
try:
    # Import the new debate-based evaluation system
    from components.evaluation.evaluation_manager import evaluation_manager

    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False
    print("Evaluation components not available. Skipping evaluation functionality.")


def run_use_case_tests(verbose=False, evaluate=False):
    """
    Run tests for Category 3 (Use Case Processing)
    Tests accounting guidance generation for Islamic finance use cases

    Args:
        verbose: If True, show detailed retrieval information
        evaluate: If True, run evaluation on the results using expert agents
    """
    print("\n" + "=" * 80)
    print("CATEGORY 1: USE CASE PROCESSING TESTS")
    print("=" * 80)

    # Initialize evaluation components if requested
    evaluator = evaluation_manager
    evaluation_results = []
    if evaluate and EVALUATION_AVAILABLE:
        # evaluator = ISDBIEvaluator()
        print("Evaluation mode enabled. Results will be scored by expert agents.")
    elif evaluate and not EVALUATION_AVAILABLE:
        print(
            "Warning: Evaluation requested but components not available. Continuing without evaluation."
        )

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # The use case scenario is in the transaction field
        scenario = test_case["transaction"]

        # Display the scenario
        print(scenario)

        print("\n----- PROCESSING RESULTS -----")

        try:  # Process the use case using the processor agent
            result = use_case_processor.process_use_case(scenario)
            print("\nAccounting Guidance:")
            print(result["accounting_guidance"])

            # Run evaluation if requested
            if evaluate and evaluator:
                print("\n----- EVALUATION RESULTS -----")
                try:
                    # Use the accounting guidance as the response to evaluate
                    response = result["accounting_guidance"]

                    # Log the scenario and response
                    print("\n--- Logging Scenario and Response ---")
                    print(f"Scenario: {scenario}")
                    print(f"Response: {response}")

                    # # Run evaluation
                    # eval_result = evaluator.evaluate(
                    #     prompt=scenario,
                    #     response=response,
                    #     retrieve_context=True,
                    #     output_format="markdown",
                    # )

                    # # Print evaluation results
                    # print(
                    #     f"Overall Score: {eval_result.get('overall_score', 'N/A')}/10"
                    # )
                    # print(f"Strongest Area: {eval_result.get('strongest_area', 'N/A')}")
                    # print(f"Weakest Area: {eval_result.get('weakest_area', 'N/A')}")

                    # Store results for later analysis
                    # evaluation_results.append(
                    #     {"name": test_case["name"], "evaluation": eval_result}
                    # )

                    eval_result = evaluation_manager.evaluate_response(
                        prompt=scenario,
                        response=response,
                        fetch_additional_context=True,
                        debate_domains=[
                            "shariah",
                            "finance",
                            "legal",
                        ],  # Use all domains for comprehensive evaluation
                    )

                    traditional_score = eval_result.get("aggregated_scores", {}).get(
                        "overall_score", "N/A"
                    )
                    discrete_score = eval_result.get("aggregated_scores", {}).get(
                        "overall_discrete_score", "N/A"
                    )
                    print(
                        f"Evaluation completed successfully with scores: Traditional={traditional_score}/10, Discrete={discrete_score}/4"
                    )
                except Exception as e:
                    print(f"Error during evaluation: {e}")

            # If verbose mode is enabled, show additional details
            if verbose:
                print("\n--- Retrieval Details ---")
                # Get retrieved nodes for the scenario
                retrieved_nodes = retriever.retrieve(scenario)
                print(f"Retrieved {len(retrieved_nodes)} context chunks")

                if len(retrieved_nodes) > 0:
                    print("\nSample chunks:")
                    # Display a limited number of chunks to avoid overwhelming output
                    for j, node in enumerate(retrieved_nodes[:3]):
                        print(f"\nChunk {j + 1}:")
                        # Show a shortened version of the chunk
                        text = node.text
                        print(text[:200] + "..." if len(text) > 200 else text)

        except Exception as e:
            print(f"Error processing use case: {e}")
            if i < len(test_cases):
                # cont = input("\nContinue to next test case? (y/n): ")
                cont = "y"
                if cont.lower() not in ["y", "yes"]:
                    break
            print("-------------------------------------------")

    # Save evaluation results if we have any
    if evaluate and evaluation_results:
        try:
            results_file = "evaluation_results/use_case_evaluation_results.json"
            with open(results_file, "w") as f:
                json.dump(evaluation_results, f, indent=2)
            print(f"\nEvaluation results saved to {results_file}")
        except Exception as e:
            print(f"Error saving evaluation results: {e}")


if __name__ == "__main__":
    # You can run the file directly to test use cases
    run_use_case_tests(evaluate=True)
