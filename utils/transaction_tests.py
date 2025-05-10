"""
Transaction testing module for the Islamic Finance standards system.
"""

from agents import transaction_analyzer, transaction_rationale, knowledge_integration
from components.test.reverse_transactions import test_cases

# Import evaluation components (only if available)
try:
    from components.evaluation import ISDBIEvaluator

    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False
    print("Evaluation components not available. Skipping evaluation functionality.")
import json


def run_category2_tests(verbose=False, evaluate=False):
    """
    Run tests specifically for Category 2 (Reverse Transactions Analysis)

    Args:
        test: If True, run only a subset of tests
        verbose: If True, show more detailed output
        evaluate: If True, run evaluation on results
    """
    print("\n" + "=" * 80)
    print("CATEGORY 2: REVERSE TRANSACTIONS ANALYSIS TESTS")
    print("=" * 80)

    # Initialize evaluation components if requested
    evaluator = None
    evaluation_results = []
    if evaluate and EVALUATION_AVAILABLE:
        evaluator = ISDBIEvaluator()
        print("Evaluation mode enabled. Results will be scored by expert agents.")
    elif evaluate and not EVALUATION_AVAILABLE:
        print(
            "Warning: Evaluation requested but components not available. Continuing without evaluation."
        )

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # The transaction is now directly a string description
        transaction = test_case["transaction"]

        # Display the transaction description
        print(transaction)

        print("\n----- ANALYSIS RESULTS -----")

        try:
            # Perform transaction analysis with updated prompt
            analysis_result = transaction_analyzer.analyze_transaction(transaction)
            print("\nTransaction Analysis:")
            print(analysis_result["analysis"])

            # Extract the correct standard using the clear indicator phrase
            correct_standard = None
            analysis_text = analysis_result["analysis"]

            if "THE CORRECT STANDARD IS:" in analysis_text:
                # Extract the standard mentioned after the indicator phrase
                start_idx = analysis_text.find("THE CORRECT STANDARD IS:") + len(
                    "THE CORRECT STANDARD IS:"
                )
                end_idx = analysis_text.find("\n", start_idx)
                if end_idx == -1:  # If no newline after the phrase
                    end_idx = len(analysis_text)
                correct_standard = analysis_text[start_idx:end_idx].strip()
                print(f"\nClearly Identified Standard: {correct_standard}")

            # If verbose mode is enabled, show all chunks
            if verbose and "retrieval_stats" in analysis_result:
                stats = analysis_result["retrieval_stats"]
                print("\n--- RAG Retrieval Stats ---")
                print(f"Retrieved {stats['chunk_count']} chunks")
                print("\nSample chunks:")
                for j, chunk_summary in enumerate(stats["chunks_summary"]):
                    print(f"\nChunk {j + 1}: {chunk_summary}")

            # Use identified standards from the analysis, but prioritize the clearly marked one
            standards = analysis_result["identified_standards"]
            if standards:
                print(f"\nAll Identified Standards: {', '.join(standards)}")

                # Prioritize the clearly marked standard if available
                top_standard = correct_standard if correct_standard else standards[0]

                # Get rationale for the top standard
                rationale = transaction_rationale.explain_standard_application(
                    transaction, top_standard
                )

                print(f"\n{top_standard} Application Rationale:")
                print(rationale["rationale"])

                # Run evaluation if requested
                if evaluate and evaluator:
                    print("\n----- EVALUATION RESULTS -----")
                    try:
                        # Process through knowledge integration for a comprehensive response
                        standard_rationales = {top_standard: rationale["rationale"]}
                        integrated_result = knowledge_integration.integrate_knowledge(
                            analysis_result, standard_rationales
                        )
                        full_response = integrated_result["integrated_analysis"]

                        # Run evaluation
                        eval_result = evaluator.evaluate(
                            prompt=transaction,
                            response=full_response,
                            retrieve_context=True,
                            output_format="markdown",
                        )

                        # Print and store evaluation results
                        print(
                            f"Overall Score: {eval_result.get('overall_score', 'N/A')}/10"
                        )
                        print(
                            f"Strongest Area: {eval_result.get('strongest_area', 'N/A')}"
                        )
                        print(f"Weakest Area: {eval_result.get('weakest_area', 'N/A')}")

                        # Store results for later analysis
                        evaluation_results.append(
                            {"name": test_case["name"], "evaluation": eval_result}
                        )
                    except Exception as e:
                        print(f"Error during evaluation: {e}")

        except Exception as e:
            print(f"Error analyzing transaction: {e}")

        if i < len(test_cases):
            cont = input("\nContinue to next test case? (y/n): ")
            if cont.lower() not in ["y", "yes"]:
                break
