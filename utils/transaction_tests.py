"""
Transaction testing module for the Islamic Finance standards system.
"""

from agents import transaction_analyzer, transaction_rationale, knowledge_integration
from components.test.reverse_transactions import test_cases
import logging
from components.evaluation.report_generator import EvaluationReportGenerator
import os
import json
import argparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import evaluation components (only if available)
try:
    # Import the new debate-based evaluation system
    from components.evaluation.evaluation_manager import evaluation_manager

    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False
    print("Evaluation components not available. Skipping evaluation functionality.")
import json


def run_category2_tests(verbose=False, evaluate=False, test_discrete_scoring=False):
    """
    Run tests specifically for Category 2 (Reverse Transactions Analysis)

    Args:
        verbose: If True, show more detailed output
        evaluate: If True, run evaluation on results
        test_discrete_scoring: If True, explicitly test the discrete scoring system (1-4 scale)
    """
    print_header()

    logger.info("Starting Category 2 tests with the following settings:")
    logger.info(f"- Verbose output: {'Enabled' if verbose else 'Disabled'}")
    logger.info(f"- Evaluation: {'Enabled' if evaluate else 'Disabled'}")
    logger.info(
        f"- Discrete Scoring Test: {'Enabled' if test_discrete_scoring else 'Disabled'}"
    )

    # Initialize evaluation components if requested
    evaluation_results = []
    if evaluate:
        initialize_evaluation(evaluation_results)

    # If testing discrete scoring is requested, run a specific test for that
    if test_discrete_scoring and EVALUATION_AVAILABLE:
        logger.info("Running discrete scoring system test...")
        test_discrete_scoring_system()
        return

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # The transaction is now directly a string description
        transaction = test_case["transaction"]

        # Display the transaction description
        print(transaction)

        # Analyze and process the transaction
        try:
            analysis_result, correct_standard = analyze_transaction(
                transaction, verbose
            )

            # Process standards and generate rationale
            process_standards_and_rationale(
                transaction,
                analysis_result,
                correct_standard,
                test_case,
                evaluation_results,
                evaluate,
                verbose,
            )
        except Exception as e:
            print(f"Error analyzing transaction: {e}")

        # Ask user to continue
        if i < len(test_cases):
            # cont = input("\nContinue to next test case? (y/n): ")
            cont = "y"
            if cont.lower() not in ["y", "yes"]:
                break
        print("=====================================================================")

    # Print summary of evaluation results if evaluation was performed
    if evaluate and evaluation_results:
        print_evaluation_summary(evaluation_results)


def print_header():
    """Print the test category header."""
    print("\n" + "=" * 80)
    print("CATEGORY 2: REVERSE TRANSACTIONS ANALYSIS TESTS")
    print("=" * 80)


def initialize_evaluation(evaluation_results):
    """Initialize evaluation components and print status message."""
    if EVALUATION_AVAILABLE:
        print(
            "Evaluation mode enabled. Results will be scored using debate-based evaluation."
        )
        print("Debates will be conducted across Shariah, Financial, and Legal domains.")
        print(
            "Using enhanced scoring system with both traditional (1-10) and discrete (1-4) scales."
        )

        logger.info("Initializing evaluation system with the following components:")
        logger.info("- Debate-based evaluation: Enabled")
        logger.info("- Traditional scoring (1-10 scale): Enabled")
        logger.info("- Discrete scoring (1-4 scale): Enabled")
        logger.info("- Report generation: Enabled (Markdown format)")
    else:
        print(
            "Warning: Evaluation requested but components not available. Continuing without evaluation."
        )
        logger.warning(
            "Evaluation components not available. Skipping evaluation functionality."
        )


def analyze_transaction(transaction, verbose):
    """
    Analyze a transaction and extract the correct standard.

    Args:
        transaction: The transaction description
        verbose: Whether to show verbose output

    Returns:
        tuple: (analysis_result, correct_standard)
    """
    print("\n----- ANALYSIS RESULTS -----")

    # Perform transaction analysis
    analysis_result = transaction_analyzer.analyze_transaction(transaction)
    print("\nTransaction Analysis:")
    print(analysis_result["analysis"])

    # Extract the correct standard using the clear indicator phrase
    correct_standard = extract_correct_standard(analysis_result["analysis"])

    # Display verbose information if requested
    if verbose and "retrieval_stats" in analysis_result:
        display_retrieval_stats(analysis_result["retrieval_stats"])

    return analysis_result, correct_standard


def extract_correct_standard(analysis_text):
    """
    Extract the correct standard from analysis text.

    Args:
        analysis_text: The analysis text to parse

    Returns:
        str or None: The extracted standard if found
    """
    correct_standard = None
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

    return correct_standard


def display_retrieval_stats(stats):
    """Display retrieval statistics for verbose mode."""
    print("\n--- RAG Retrieval Stats ---")
    print(f"Retrieved {stats['chunk_count']} chunks")
    print("\nSample chunks:")
    for j, chunk_summary in enumerate(stats["chunks_summary"]):
        print(f"\nChunk {j + 1}: {chunk_summary}")


def process_standards_and_rationale(
    transaction,
    analysis_result,
    correct_standard,
    test_case,
    evaluation_results,
    evaluate,
    verbose,
):
    """
    Process standards and generate rationale for the transaction.

    Args:
        transaction: The transaction description
        analysis_result: Result from transaction analysis
        correct_standard: The correct standard if explicitly identified
        test_case: The current test case
        evaluation_results: List to store evaluation results
        evaluate: Whether to run evaluation
        verbose: Whether to show verbose output
    """
    # Use identified standards from the analysis, but prioritize the clearly marked one
    standards = analysis_result["identified_standards"]
    if not standards:
        print("\nNo standards identified for this transaction.")
        return

    print(f"\nAll Identified Standards: {', '.join(standards)}")

    # Prioritize the clearly marked standard if available
    top_standard = correct_standard if correct_standard else standards[0]

    # Get rationale for the top standard
    rationale = transaction_rationale.explain_standard_application(
        transaction, top_standard
    )
    print(f"\n{top_standard} Application Rationale:")
    print(rationale["rationale"])

    # Run evaluation if requested and available
    if evaluate and EVALUATION_AVAILABLE:
        run_debate_evaluation(
            transaction,
            analysis_result,
            top_standard,
            rationale,
            test_case,
            evaluation_results,
            verbose,
        )


def run_debate_evaluation(
    transaction,
    analysis_result,
    top_standard,
    rationale,
    test_case,
    evaluation_results,
    verbose,
):
    """
    Run debate-based evaluation on a transaction response.

    Args:
        transaction: The transaction description
        analysis_result: Result from transaction analysis
        top_standard: The top standard to evaluate
        rationale: Rationale for the standard application
        test_case: The current test case
        evaluation_results: List to store evaluation results
        verbose: Whether to show verbose output
    """
    print("\n----- DEBATE-BASED EVALUATION RESULTS -----")
    logger.info(f"Starting debate-based evaluation for test case: {test_case['name']}")
    logger.info(f"Top standard identified: {top_standard}")

    try:
        # Process through knowledge integration for a comprehensive response
        # logger.info("Integrating knowledge from analysis and rationales...")
        # standard_rationales = {top_standard: rationale["rationale"]}
        # integrated_result = knowledge_integration.integrate_knowledge(
        #     analysis_result, standard_rationales
        # )
        # full_response = integrated_result["integrated_analysis"]

        logger.info("Starting multi-domain debate evaluation...")
        logger.info("Using domains: shariah, finance, legal")
        logger.info("Generating comprehensive report with both scoring systems...")

        # Run multi-domain debate-based evaluation with enhanced discrete scoring
        eval_result = evaluation_manager.evaluate_response(
            prompt=transaction,
            response=f"""
            Analysis Result: {analysis_result}
            
            Rationale for the analysis: {rationale}
            """,
            fetch_additional_context=True,
            # No need for use_debate_system parameter as debate system is always used now
            generate_report=True,  # Generate a report with both scoring systems
            report_format="markdown",
            save_report=True,
            output_dir="reports",
            debate_domains=[
                "shariah",
                "finance",
                "legal",
            ],  # Use all domains for comprehensive evaluation
        )

        # Log successful evaluation
        traditional_score = eval_result.get("aggregated_scores", {}).get(
            "overall_score", "N/A"
        )
        discrete_score = eval_result.get("aggregated_scores", {}).get(
            "overall_discrete_score", "N/A"
        )
        logger.info(
            f"Evaluation completed successfully with scores: Traditional={traditional_score}/10, Discrete={discrete_score}/4"
        )

        # report_md = EvaluationReportGenerator.generate_markdown_report(eval_result)        # Save additional JSON file with test case details
        try:
            # Create reports directory if it doesn't exist
            test_case_dir = os.path.join("reports", "test_cases")
            os.makedirs(test_case_dir, exist_ok=True)

            # Create a filename based on the test case
            test_case_file = os.path.join(
                test_case_dir,
                f"{test_case['name'].replace(' ', '_').lower()}_results.json",
            )

            # Add test case metadata to the results
            case_results = {
                "test_case": test_case["name"],
                "transaction": transaction,
                "identified_standard": top_standard,
                "evaluation_results": eval_result,
            }

            # Use json module to properly serialize the data
            with open(test_case_file, "w", encoding="utf-8") as f:
                # Handle non-serializable objects with a default converter
                json.dump(case_results, f, indent=2, default=lambda o: str(o))
            logger.info(f"Test case results saved to {test_case_file}")
        except Exception as e:
            logger.error(f"Error saving test case results: {e}")

        # Display evaluation results with new verbose output
        print("\n--- Evaluation Summary ---")
        display_evaluation_results(eval_result, verbose)

        # Store results for later analysis and summary
        store_evaluation_results(eval_result, test_case, evaluation_results)

        # Save detailed debate results to file
        save_debate_results(eval_result, test_case)

    except Exception as e:
        print(f"Error during debate-based evaluation: {e}")


def display_evaluation_results(eval_result, verbose):
    """
    Display the evaluation results.

    Args:
        eval_result: The evaluation result
        verbose: Whether to show verbose output
    """
    logger.info("Displaying evaluation results...")

    # Extract scores from results
    traditional_score = eval_result.get("aggregated_scores", {}).get(
        "overall_score", "N/A"
    )
    discrete_score = eval_result.get("aggregated_scores", {}).get(
        "overall_discrete_score", "N/A"
    )

    # Print overall scores - both traditional and discrete
    print(f"Overall Traditional Score: {traditional_score}/10")
    if discrete_score != "N/A":
        print(f"Overall Discrete Score: {discrete_score}/4")

    # Display discrete scores by domain if available
    discrete_scores = eval_result.get("aggregated_scores", {}).get(
        "discrete_scores", {}
    )
    if discrete_scores:
        print("\n--- Discrete Scores by Domain ---")
        for domain, score_info in discrete_scores.items():
            domain_score = score_info.get("score", "N/A")
            print(f"- {domain}: {domain_score}/4")
            if verbose:
                justification = score_info.get(
                    "justification", "No justification provided."
                )
                print(f"  Justification: {justification[:150]}...")

    # Display debate summary
    if "debate_results" in eval_result:
        print("\n--- Debate Summary ---")
        domains = list(eval_result["debate_results"].keys())
        print(f"Debates conducted in domains: {domains}")
        logger.info(
            f"Found debate results for {len(domains)} domains: {', '.join(domains)}"
        )

        # Print a sample from one domain's debate
        if domains:
            first_domain = domains[0]
            domain_result = eval_result["debate_results"][first_domain]
            if "summary" in domain_result and "summary" in domain_result["summary"]:
                summary = domain_result["summary"]["summary"]
                print(f"\nSample from {first_domain} domain:")
                print(f"{summary[:300]}...")

            print("\nTo see full debate details, run with --verbose option")

            # Show detailed debate info in verbose mode
            if verbose:
                display_detailed_debate_info(eval_result["debate_results"])

    # Display report path if available
    if "report_file" in eval_result:
        print(f"\nDetailed report saved to: {eval_result['report_file']}")
    elif "report_files" in eval_result:
        print("\nDetailed reports saved to:")
        for format_name, path in eval_result["report_files"].items():
            print(f"- {format_name}: {path}")


def display_detailed_debate_info(debate_results):
    """
    Display detailed information about the debates.

    Args:
        debate_results: The debate results to display
    """
    print("\n--- DETAILED DEBATE INFORMATION ---")
    for domain, debate in debate_results.items():
        print(f"\n=== {domain.upper()} DOMAIN DEBATE ===")

        # Show rounds info
        print(f"Completed {debate.get('rounds_completed', 0)} debate rounds")

        # Show some debate history
        if "debate_history" in debate:
            print("\nDebate arguments:")
            for idx, entry in enumerate(debate["debate_history"]):
                agent = entry.get("agent_type", "Unknown")
                argument = entry.get("argument", "")
                print(f"\n- Round {idx + 1}, {agent}:")
                # Print first 200 chars of each argument
                print(f"{argument[:200]}..." if len(argument) > 200 else argument)


def store_evaluation_results(eval_result, test_case, evaluation_results):
    """
    Store the evaluation results for later analysis.

    Args:
        eval_result: The evaluation result
        test_case: The current test case
        evaluation_results: List to store results in
    """
    evaluation_results.append(
        {
            "name": test_case["name"],
            "evaluation": eval_result,
            "debate_enabled": eval_result.get("debate_enabled", False),
            "domains": [d for d in eval_result.get("debate_results", {}).keys()],
        }
    )


def save_debate_results(eval_result, test_case):
    """
    Save detailed debate results to a file.

    Args:
        eval_result: The evaluation result
        test_case: The current test case
    """
    try:
        debate_file = f"debate_results_{test_case['name'].replace(' ', '_')}.json"
        with open(debate_file, "w") as f:
            json.dump(eval_result.get("debate_results", {}), f, indent=2, default=str)
        print(f"\nDetailed debate results saved to {debate_file}")
    except Exception as save_err:
        print(f"Warning: Could not save debate details: {save_err}")


def print_evaluation_summary(evaluation_results):
    """
    Print a summary of all evaluation results.

    Args:
        evaluation_results: List of evaluation results
    """
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    logger.info(
        f"Generating evaluation summary for {len(evaluation_results)} test cases"
    )

    # Track average scores
    traditional_scores = []
    discrete_scores = []

    for result in evaluation_results:
        name = result["name"]
        traditional_score = result["evaluation"].get("overall_score", "N/A")
        # Also display discrete score if available
        discrete_score = (
            result["evaluation"]
            .get("aggregated_scores", {})
            .get("overall_discrete_score", "N/A")
        )
        domains = ", ".join(result["domains"]) if result["domains"] else "None"

        # Add scores to tracking lists if they're numeric
        if isinstance(traditional_score, (int, float)):
            traditional_scores.append(traditional_score)
        if isinstance(discrete_score, (int, float)):
            discrete_scores.append(discrete_score)

        print(f"\n{name}:")
        print(f"  Overall Score: {traditional_score}/10")
        if discrete_score != "N/A":
            print(f"  Discrete Score: {discrete_score}/4")
        print(f"  Debate Domains: {domains}")

    # Print average scores if available
    if traditional_scores:
        avg_traditional = sum(traditional_scores) / len(traditional_scores)
        print(f"\nAverage Traditional Score: {avg_traditional:.2f}/10")
    if discrete_scores:
        avg_discrete = sum(discrete_scores) / len(discrete_scores)
        print(f"Average Discrete Score: {avg_discrete:.2f}/4")

    # Log completion of evaluation
    logger.info("Evaluation summary complete")
    if traditional_scores:
        avg_trad = sum(traditional_scores) / len(traditional_scores)
        logger.info(f"Average traditional score: {avg_trad:.2f}/10")
    if discrete_scores:
        avg_disc = sum(discrete_scores) / len(discrete_scores)
        logger.info(f"Average discrete score: {avg_disc:.2f}/4")


if __name__ == "__main__":
    """
    Main entry point for running transaction tests.
    Command line arguments:
    --verbose: Show more detailed output
    --evaluate: Run evaluation on results
    --test-discrete: Run a specific test for the discrete scoring system
    """
    import argparse
    import time

    # Configure argument parser
    parser = argparse.ArgumentParser(
        description="Run transaction analysis tests with enhanced evaluation."
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--evaluate", action="store_true", help="Run evaluation on results"
    )
    parser.add_argument(
        "--test-discrete",
        action="store_true",
        help="Run a test of the discrete scoring system",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set up logging to file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(f"{log_dir}/transaction_tests_{timestamp}.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Log startup info
    logger.info("=== Transaction Tests Started ===")
    logger.info(
        f"Arguments: verbose={args.verbose}, evaluate={args.evaluate}, test_discrete={args.test_discrete}"
    )

    # Run the tests
    start_time = time.time()
    run_category2_tests(
        verbose=args.verbose,
        evaluate=args.evaluate,
        test_discrete_scoring=args.test_discrete,
    )
    end_time = time.time()

    # Log completion
    duration = end_time - start_time
    logger.info(f"=== Transaction Tests Completed in {duration:.2f} seconds ===")
    print(f"\nTests completed in {duration:.2f} seconds")
    print(f"Log file: {log_dir}/transaction_tests_{timestamp}.log")


def test_discrete_scoring_system():
    """
    Test the enhanced evaluation system with discrete scoring.
    This function runs a standalone test of the 1-4 scoring system.
    """
    print("\n" + "=" * 80)
    print("DISCRETE SCORING SYSTEM TEST")
    print("=" * 80)

    logger.info("Running standalone test for discrete 1-4 scoring system...")

    # Sample prompt and response related to Islamic finance
    prompt = """
    A client wants to buy a car through an Islamic bank. 
    What financing options can the bank provide that are Shariah-compliant?
    """

    response = """
    The Islamic bank can offer several Shariah-compliant financing options for purchasing a car:

    1. Murabaha (Cost-Plus Financing): The bank purchases the car and then sells it to the client at a marked-up price.
       The client knows the original cost and the bank's profit margin upfront, and makes payments in installments.

    2. Ijarah Muntahia Bittamleek (Lease-to-Own): The bank purchases the car and leases it to the client for a fixed
       period with agreed-upon rental payments. At the end of the lease term, ownership transfers to the client.

    3. Diminishing Musharakah: The bank and client jointly own the car. The client gradually buys the bank's share
       over time while paying rent for the bank's portion until the client fully owns the car.

    All these options avoid interest (riba), ensure that risk is shared appropriately, and are asset-backed,
    making them Shariah-compliant alternatives to conventional car loans.
    """

    logger.info("Creating test directories for reports...")
    # Create reports directory if it doesn't exist
    os.makedirs("reports/test_discrete", exist_ok=True)

    print("\nRunning evaluation with discrete scoring system...")
    # Test the evaluation system with both scoring methods
    try:
        evaluation_result = evaluation_manager.evaluate_response(
            prompt=prompt,
            response=response,
            fetch_additional_context=True,
            generate_report=True,
            report_format="all",  # Generate reports in all formats
            save_report=True,
            output_dir="reports/test_discrete",
            debate_domains=["shariah", "finance", "legal"],  # Test all domains
        )

        # Print basic results
        print("\nTest completed successfully!")

        # Display overall scores
        traditional_score = evaluation_result.get("aggregated_scores", {}).get(
            "overall_score", "N/A"
        )
        discrete_score = evaluation_result.get("aggregated_scores", {}).get(
            "overall_discrete_score", "N/A"
        )

        print(f"\nTraditional Score (1-10): {traditional_score}")
        print(f"Discrete Score (1-4): {discrete_score}")

        # Show discrete scores by domain
        print("\nDiscrete scores by domain:")
        discrete_scores = evaluation_result.get("aggregated_scores", {}).get(
            "discrete_scores", {}
        )
        for domain, score_info in discrete_scores.items():
            print(f"- {domain}: {score_info.get('score', 'N/A')}/4")
            print(
                f"  Justification: {score_info.get('justification', 'No justification provided.')[:100]}..."
            )

        # Show where reports are saved
        if "report_files" in evaluation_result:
            print("\nReports saved to:")
            for format_name, file_path in evaluation_result["report_files"].items():
                print(f"- {format_name}: {file_path}")

        logger.info("Discrete scoring test completed successfully.")
        return True

    except Exception as e:
        print(f"\nError during discrete scoring test: {e}")
        logger.error(f"Error testing discrete scoring system: {e}")
        return False
