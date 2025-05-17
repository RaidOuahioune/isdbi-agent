"""
Standards enhancement testing module for the Islamic Finance standards system.
"""

from enhancement import run_standards_enhancement, ENHANCEMENT_TEST_CASES
from components.orchestration.enhancement_orchestrator import EnhancementOrchestrator
import logging
import os
import json
import argparse
import time
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import evaluation components (only if available)
try:
    # Import the debate-based evaluation system
    from components.evaluation.evaluation_manager import evaluation_manager

    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False
    print("Evaluation components not available. Skipping evaluation functionality.")


def run_category3_tests(verbose=False, evaluate=False, test_discrete_scoring=False):
    """
    Run tests specifically for Category 3 (Standards Enhancement)

    Args:
        verbose: If True, show more detailed output
        evaluate: If True, run evaluation on results
        test_discrete_scoring: If True, explicitly test the discrete scoring system (1-4 scale)
    """
    print_header()

    logger.info("Starting Category 3 tests with the following settings:")
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

    for i, test_case in enumerate(ENHANCEMENT_TEST_CASES, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        standard_id = test_case["standard_id"]
        trigger_scenario = test_case["trigger_scenario"]

        # Display the test information
        print(f"Standard ID: FAS {standard_id}")
        print(f"Trigger Scenario: {trigger_scenario}")

        # Process the enhancement
        try:
            enhancement_result = process_enhancement(
                standard_id, 
                trigger_scenario, 
                test_case,
                evaluation_results,
                evaluate,
                verbose
            )
        except Exception as e:
            print(f"Error processing enhancement: {e}")

        # Ask user to continue
        if i < len(ENHANCEMENT_TEST_CASES):
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
    print("CATEGORY 3: STANDARDS ENHANCEMENT TESTS")
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


def process_enhancement(
    standard_id, 
    trigger_scenario, 
    test_case, 
    evaluation_results, 
    evaluate, 
    verbose
):
    """
    Process a standards enhancement test case.

    Args:
        standard_id: The standard ID to enhance
        trigger_scenario: The trigger scenario to use
        test_case: The current test case
        evaluation_results: List to store evaluation results
        evaluate: Whether to run evaluation
        verbose: Whether to show verbose output
    """
    print("\n----- ENHANCEMENT RESULTS -----")

    # Define a progress callback to display status
    def progress_callback(phase, detail):
        if verbose:
            print(f"Progress [{phase}]: {detail}")

    # Perform enhancement
    enhancement_result = run_standards_enhancement(
        standard_id, 
        trigger_scenario, 
        progress_callback=progress_callback if verbose else None,
        include_cross_standard_analysis=True,
        generate_pdf=False  # Don't generate PDFs during testing
    )
    
    # Display enhancement results
    display_enhancement_results(enhancement_result, verbose)

    # Run evaluation if requested and available
    if evaluate and EVALUATION_AVAILABLE:
        run_debate_evaluation(
            standard_id,
            trigger_scenario,
            enhancement_result,
            test_case,
            evaluation_results,
            verbose,
        )
    
    return enhancement_result


def display_enhancement_results(result, verbose):
    """
    Display the enhancement results.

    Args:
        result: The enhancement result to display
        verbose: Whether to show verbose output
    """
    if "error" in result:
        print(f"\nError during enhancement: {result['error']}")
        return

    # Display the final proposal
    print("\nEnhancement Proposal:")
    if "final_proposal" in result:
        print(result["final_proposal"])
    elif "current_proposal_structured_text" in result:
        print(result["current_proposal_structured_text"])
    else:
        print("No proposal found in results.")

    # Display the validator's assessment
    if "validation_summary" in result:
        print("\nValidation Assessment:")
        print(result["validation_summary"])

    # Display cross-standard impact analysis if available
    if "cross_standard_analysis" in result:
        print("\nCross-Standard Impact Analysis:")
        print(result["cross_standard_analysis"])

    # If verbose, show additional details like expert contributions
    if verbose:
        if "discussion_history" in result:
            print("\n--- Expert Discussion Details ---")
            for i, entry in enumerate(result["discussion_history"]):
                expert = entry.get("agent_type", "Unknown")
                contribution = entry.get("contribution", "")
                print(f"\nExpert {i+1} ({expert}):")
                print(contribution[:300] + "..." if len(contribution) > 300 else contribution)
        
        if "consensus_metrics_history" in result:
            print("\n--- Consensus Metrics ---")
            for i, metrics in enumerate(result["consensus_metrics_history"]):
                print(f"Round {i+1}:")
                print(f"- Agreement Level: {metrics.get('agreement_level', 'N/A')}")
                print(f"- Confidence: {metrics.get('confidence', 'N/A')}")


def run_debate_evaluation(
    standard_id,
    trigger_scenario,
    enhancement_result,
    test_case,
    evaluation_results,
    verbose,
):
    """
    Run debate-based evaluation on an enhancement response.

    Args:
        standard_id: The standard ID
        trigger_scenario: The trigger scenario
        enhancement_result: Result from enhancement process
        test_case: The current test case
        evaluation_results: List to store evaluation results
        verbose: Whether to show verbose output
    """
    print("\n----- DEBATE-BASED EVALUATION RESULTS -----")
    logger.info(f"Starting debate-based evaluation for test case: {test_case['name']}")
    logger.info(f"Standard being enhanced: FAS {standard_id}")

    try:
        # Prepare the prompt and response for evaluation
        prompt = f"Standard ID: FAS {standard_id}\nTrigger Scenario: {trigger_scenario}"
        
        response = ""
        if "final_proposal" in enhancement_result:
            response += f"Enhancement Proposal:\n{enhancement_result['final_proposal']}\n\n"
        elif "current_proposal_structured_text" in enhancement_result:
            response += f"Enhancement Proposal:\n{enhancement_result['current_proposal_structured_text']}\n\n"
        
        if "validation_summary" in enhancement_result:
            response += f"Validation Assessment:\n{enhancement_result['validation_summary']}\n\n"
            
        if "cross_standard_analysis" in enhancement_result:
            response += f"Cross-Standard Analysis:\n{enhancement_result['cross_standard_analysis']}"

        logger.info("Starting multi-domain debate evaluation...")
        logger.info("Using domains: shariah, finance, legal")
        logger.info("Generating comprehensive report with both scoring systems...")

        # Run multi-domain debate-based evaluation with enhanced discrete scoring
        eval_result = evaluation_manager.evaluate_response(
            prompt=prompt,
            response=response,
            fetch_additional_context=True,
            generate_report=True,
            report_format="markdown",
            save_report=True,
            output_dir="reports/enhancement",
            debate_domains=[
                "shariah",
                "finance",
                "legal",
            ],
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

        # Save additional JSON file with test case details
        try:
            # Create reports directory if it doesn't exist
            test_case_dir = os.path.join("reports", "enhancement", "test_cases")
            os.makedirs(test_case_dir, exist_ok=True)

            # Create a filename based on the test case
            test_case_file = os.path.join(
                test_case_dir,
                f"FAS_{standard_id}_{test_case['name'].replace(' ', '_').lower()}_results.json",
            )

            # Add test case metadata to the results
            case_results = {
                "test_case": test_case["name"],
                "standard_id": standard_id,
                "trigger_scenario": trigger_scenario,
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
        logger.error(f"Error during debate-based evaluation: {e}")


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
            "standard_id": test_case["standard_id"],
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
        # Create directory if it doesn't exist
        os.makedirs("reports/enhancement", exist_ok=True)
        
        # Create filename based on test case
        debate_file = f"reports/enhancement/debate_results_FAS_{test_case['standard_id']}_{test_case['name'].replace(' ', '_')}.json"
        
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
        standard_id = result.get("standard_id", "Unknown")
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

        print(f"\nFAS {standard_id} - {name}:")
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


def test_discrete_scoring_system():
    """
    Test the enhanced evaluation system with discrete scoring.
    This function runs a standalone test of the 1-4 scoring system.
    """
    print("\n" + "=" * 80)
    print("DISCRETE SCORING SYSTEM TEST")
    print("=" * 80)

    logger.info("Running standalone test for discrete 1-4 scoring system...")

    # Sample prompt and response related to Islamic finance standards enhancement
    prompt = """
    Standard ID: FAS 10 (Istisna'a)
    Trigger Scenario: A financial institution wants to structure an Istisna'a contract for the development 
    of a large-scale AI software platform. The current wording of FAS 10 on 'well-defined 
    subject matter' and 'determination of cost' is causing uncertainty for intangible assets 
    like software development.
    """

    response = """
    Enhancement Proposal:
    
    PROPOSED ENHANCEMENT TO FAS 10 (ISTISNA'A)
    
    Section 3: Definition and Nature of Istisna'a
    
    Add new sub-section 3.4: "Application to Digital and Intangible Assets"
    
    3.4.1 The Istisna'a contract may be applied to the development and creation of digital and intangible 
    assets, including but not limited to software development, digital platforms, artificial intelligence 
    systems, and other technological solutions, provided they meet the fundamental requirements of Istisna'a.
    
    3.4.2 For digital and intangible assets, "well-defined subject matter" shall include:
    a) Comprehensive functional specifications and technical requirements documentation
    b) Clear deliverables and acceptance criteria
    c) Defined development methodology and project phases
    d) Specific performance metrics and quality standards
    
    3.4.3 For determination of cost in digital asset development:
    a) Development costs shall be estimated based on standard industry practices
    b) Labor hours and expertise levels shall be clearly specified
    c) Licensing of pre-existing components shall be explicitly documented
    d) Ongoing maintenance and support services shall be distinguished from the Istisna'a contract
    
    Section 5: Measurement
    
    Add to existing paragraph 5.1:
    
    5.1.x For digital and intangible assets, percentage-of-completion shall be determined through:
    a) Achievement of predefined development milestones
    b) Completion of specific modules or components
    c) Successful passage of agreed-upon testing protocols
    d) Formal client acceptance of interim deliverables
    
    Section 7: Disclosure
    
    Add new paragraph 7.3:
    
    7.3 For Istisna'a contracts related to digital and intangible assets, the financial institution shall disclose:
    a) The nature and specifications of the digital asset being developed
    b) The methodology used to determine percentage-of-completion
    c) Key risk factors specific to digital asset development
    d) Ownership and intellectual property rights arrangements
    e) Post-delivery support and maintenance agreements (if applicable)
    
    Validation Assessment:
    
    The proposed enhancement to FAS 10 addresses the application of Istisna'a contracts to digital and intangible 
    assets with a high degree of specificity and clarity. It maintains adherence to Shariah principles while 
    providing practical guidance for modern applications. The amendments properly address the key concerns of 
    "well-defined subject matter" and "determination of cost" for digital assets by providing clear parameters 
    and requirements. The enhancements are integrated seamlessly into the existing standard structure and use 
    consistent terminology. The proposals also appropriately address measurement issues specific to digital assets 
    and include comprehensive disclosure requirements to ensure transparency. Overall, this enhancement successfully 
    bridges the gap between traditional Istisna'a principles and modern digital asset development needs.
    
    Cross-Standard Analysis:
    
    This enhancement to FAS 10 has moderate implications for other AAOIFI standards:
    
    1. FAS 1 (General Presentation and Disclosure): Minimal impact; the new disclosure requirements align with 
       existing principles but add digital asset specifics.
    
    2. FAS 25 (Investment in Sukuk): Medium impact; if Istisna'a-based Sukuk are issued for digital asset projects, 
       new guidance may be needed for valuation of these assets.
    
    3. FAS 30 (Impairment and Credit Losses): Significant impact; new considerations needed for assessing impairment 
       of in-progress digital assets under Istisna'a, as their value assessment differs from tangible assets.
    
    4. FAS 31 (Investment Agency): Low impact; could affect situations where Investment Agency is used alongside 
       Istisna'a for digital asset development.
    
    5. FAS 35 (Risk Reserves): Medium impact; may require development of specific risk reserve calculations for 
       digital asset Istisna'a projects due to their unique risk profiles.
    
    Recommended follow-up: Develop implementation notes for FAS 30 specifically addressing impairment assessment 
    methodologies for in-progress digital assets under Istisna'a contracts.
    """

    logger.info("Creating test directories for reports...")
    # Create reports directory if it doesn't exist
    os.makedirs("reports/enhancement/test_discrete", exist_ok=True)

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
            output_dir="reports/enhancement/test_discrete",
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


if __name__ == "__main__":
    """
    Main entry point for running enhancement tests.
    Command line arguments:
    --verbose: Show more detailed output
    --evaluate: Run evaluation on results
    --test-discrete: Run a specific test for the discrete scoring system
    """
    parser = argparse.ArgumentParser(
        description="Run standards enhancement tests with enhanced evaluation."
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
    file_handler = logging.FileHandler(f"{log_dir}/enhancement_tests_{timestamp}.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Log startup info
    logger.info("=== Enhancement Tests Started ===")
    logger.info(
        f"Arguments: verbose={args.verbose}, evaluate={args.evaluate}, test_discrete={args.test_discrete}"
    )

    # Run the tests
    start_time = time.time()
    run_category3_tests(
        verbose=args.verbose,
        evaluate=args.evaluate,
        test_discrete_scoring=args.test_discrete,
    )
    end_time = time.time()

    # Log completion
    duration = end_time - start_time
    logger.info(f"=== Enhancement Tests Completed in {duration:.2f} seconds ===")
    print(f"\nTests completed in {duration:.2f} seconds")
    print(f"Log file: {log_dir}/enhancement_tests_{timestamp}.log") 