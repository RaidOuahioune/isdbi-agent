from typing import Dict, Any, List, Optional, Callable
from langchain_core.messages import AIMessage

from agents import reviewer_agent, proposer_agent, validator_agent, cross_standard_analyzer


# Define test cases for standards enhancement
ENHANCEMENT_TEST_CASES = [
    {
        "name": "Digital Assets in Istisna'a",
        "standard_id": "10",
        "trigger_scenario": """A financial institution wants to structure an Istisna'a contract for the development 
                              of a large-scale AI software platform. The current wording of FAS 10 on 'well-defined 
                              subject matter' and 'determination of cost' is causing uncertainty for intangible assets 
                              like software development."""
    },
    {
        "name": "Tokenized Mudarabah Investments",
        "standard_id": "4",
        "trigger_scenario": """Fintech platforms are offering investment in tokenized Mudarabah funds where investors can 
                              buy/sell fractional ownership tokens on blockchain networks. FAS 4 needs clarification on 
                              how to handle these digital representations of investment units and profit distribution in 
                              real-time token trading scenarios."""
    },
    {
        "name": "Green Sukuk Environmental Impact",
        "standard_id": "32",
        "trigger_scenario": """Islamic financial institutions are increasingly issuing 'Green Sukuk' to fund 
                              environmentally sustainable projects, but FAS 32 lacks specific guidance on how to account 
                              for and report environmental impact metrics alongside financial returns."""
    },
    {
        "name": "Digital Banking Services in Ijarah",
        "standard_id": "28",
        "trigger_scenario": """Islamic banks are offering digital banking services through cloud-based infrastructure 
                              leased through Ijarah arrangements. FAS 28 needs enhancement to address how to classify, 
                              recognize, and measure these digital service agreements which may include both tangible 
                              and intangible components."""
    },
    {
        "name": "Cryptocurrency Zakat Calculation",
        "standard_id": "7",
        "trigger_scenario": """Islamic financial institutions holding cryptocurrencies as assets need guidance on how 
                              to calculate and distribute Zakat on these volatile digital assets. The current FAS 7 
                              doesn't address value fluctuations and verification methods specific to crypto assets."""
    }
]


def run_standards_enhancement(
    standard_id: str, 
    trigger_scenario: str,
    progress_callback: Optional[Callable[[str, str], None]] = None,
    include_cross_standard_analysis: bool = True  # New parameter to control cross-standard analysis
) -> Dict[str, Any]:
    """
    Run the standards enhancement process with the three specialized agents.
    
    Args:
        standard_id: The ID of the standard to enhance (e.g., "10" for FAS 10)
        trigger_scenario: The scenario that triggers the need for enhancement
        progress_callback: Optional callback function to report progress
        include_cross_standard_analysis: Whether to include cross-standard impact analysis
        
    Returns:
        Dict with the enhancement results including:
        - Original standard excerpt
        - Identified issues
        - Proposed enhancements
        - Validation results
        - Cross-standard impact analysis (if enabled)
    """
    print(f"Starting enhancement process for FAS {standard_id}...")
    print(f"Trigger scenario: {trigger_scenario}")
    
    # Report progress: starting review
    if progress_callback:
        progress_callback("review_start", "Starting review phase")
    
    # Step 1: Reviewer Agent - Extract and analyze standard
    print("\nStep 1: Reviewing standard and identifying enhancement areas...")
    review_result = reviewer_agent.extract_standard_elements(standard_id, trigger_scenario)
    
    # Report progress: review complete, starting proposal
    if progress_callback:
        progress_callback("review_complete", "Review phase completed")
    
    # Step 2: Proposer Agent - Generate enhancement proposals
    print("\nStep 2: Generating enhancement proposals...")
    proposal_result = proposer_agent.generate_enhancement_proposal(review_result)
    
    # Report progress: proposal complete, starting validation
    if progress_callback:
        progress_callback("proposal_complete", "Proposal phase completed")
    
    # Step 3: Validator Agent - Validate proposals
    print("\nStep 3: Validating enhancement proposals...")
    validation_result = validator_agent.validate_proposal(proposal_result)
    
    # Report progress: validation complete
    if progress_callback:
        progress_callback("validation_complete", "Validation phase completed")
    
    # First try to extract original and proposed text from the proposal
    from ui.output_parser import OutputParser
    proposal_text = proposal_result["enhancement_proposal"]
    original_text, proposed_text = OutputParser.extract_original_and_proposed(proposal_text)
    
    # Compile initial results
    results = {
        "standard_id": standard_id,
        "trigger_scenario": trigger_scenario,
        "review": review_result["review_analysis"],
        "proposal": proposal_result["enhancement_proposal"],
        "validation": validation_result["validation_result"],
        "original_text": original_text,
        "proposed_text": proposed_text,
        "full_results": {
            "review_result": review_result,
            "proposal_result": proposal_result,
            "validation_result": validation_result
        }
    }
    
    # Step 4 (Optional): Cross-Standard Impact Analyzer
    if include_cross_standard_analysis:
        if progress_callback:
            progress_callback("cross_analysis_start", "Starting cross-standard impact analysis")
            
        print("\nStep 4: Analyzing cross-standard impacts...")
        cross_analysis_result = cross_standard_analyzer.analyze_cross_standard_impact(results)
        
        if progress_callback:
            progress_callback("cross_analysis_complete", "Cross-standard analysis completed")
            
        # Add cross-standard analysis to the results
        results["cross_standard_analysis"] = cross_analysis_result["cross_standard_analysis"]
        results["compatibility_matrix"] = cross_analysis_result["compatibility_matrix"]
        results["full_results"]["cross_analysis_result"] = cross_analysis_result
    
    # Pre-process the results to ensure diffs are generated 
    processed_results = OutputParser.parse_results_from_agents(results)
    
    return processed_results


def format_results_for_display(results: Dict[str, Any]) -> str:
    """
    Format the enhancement results for display to users.
    
    Args:
        results: The dictionary returned by run_standards_enhancement()
        
    Returns:
        Formatted string with results
    """
    output = []
    
    # Header information
    output.append(f"# Standards Enhancement Results for FAS {results['standard_id']}")
    output.append("\n## Trigger Scenario")
    output.append(results['trigger_scenario'])
    
    # Review findings
    output.append("\n## Review Findings")
    output.append(results['review'])
    
    # Proposed enhancements
    output.append("\n## Proposed Enhancements")
    output.append(results['proposal'])
    
    # Validation results
    output.append("\n## Validation Results")
    output.append(results['validation'])
    
    # Add cross-standard analysis if available
    if "cross_standard_analysis" in results:
        output.append("\n## Cross-Standard Impact Analysis")
        output.append(results['cross_standard_analysis'])
    
    return "\n".join(output)


def find_test_case_by_keyword(keyword: str) -> Dict[str, Any]:
    """
    Find a test case by matching a keyword in the name or scenario.
    
    Args:
        keyword: The keyword to search for
        
    Returns:
        The matching test case or the first test case if no match
    """
    keyword = keyword.lower()
    
    for case in ENHANCEMENT_TEST_CASES:
        if (keyword in case["name"].lower() or 
            keyword in case["trigger_scenario"].lower()):
            return case
    
    # If no match found, return the first test case
    return ENHANCEMENT_TEST_CASES[0]


def get_test_case_by_standard_id(standard_id: str) -> Dict[str, Any]:
    """
    Find a test case that matches the given standard ID.
    
    Args:
        standard_id: The standard ID to search for (e.g., "10")
        
    Returns:
        The matching test case or None if no match
    """
    for case in ENHANCEMENT_TEST_CASES:
        if case["standard_id"] == standard_id:
            return case
    
    return None


def run_enhancement_demo():
    """
    Run an interactive demo of the Standards Enhancement feature.
    """
    print("Standards Enhancement Demo")
    print("=========================")
    print("Select a test case or enter your own:")
    
    # Show test cases
    for i, case in enumerate(ENHANCEMENT_TEST_CASES, 1):
        print(f"{i}. {case['name']} (FAS {case['standard_id']})")
    
    choice = input("\nChoice (or 'custom' for your own scenario): ")
    
    if choice.lower() == 'custom':
        standard_id = input("Enter standard ID (4, 7, 10, 28, or 32): ")
        trigger = input("Enter trigger scenario: ")
    else:
        try:
            case_idx = int(choice) - 1
            if case_idx < 0 or case_idx >= len(ENHANCEMENT_TEST_CASES):
                raise ValueError("Invalid index")
            
            case = ENHANCEMENT_TEST_CASES[case_idx]
            standard_id = case['standard_id']
            trigger = case['trigger_scenario']
        except:
            print("Invalid choice. Using default case.")
            standard_id = "10"
            trigger = ENHANCEMENT_TEST_CASES[0]['trigger_scenario']
    
    # Ask if cross-standard analysis should be included
    include_cross = input("Include cross-standard impact analysis? (y/n, default: y): ").lower()
    include_cross_analysis = False if include_cross == 'n' else True
    
    # Run enhancement
    result = run_standards_enhancement(standard_id, trigger, include_cross_standard_analysis=include_cross_analysis)
    
    # Display formatted results
    formatted_results = format_results_for_display(result)
    print("\n")
    print(formatted_results)


if __name__ == "__main__":
    run_enhancement_demo()