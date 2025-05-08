from typing import Dict, Any, List
from langchain_core.messages import AIMessage

from agents import reviewer_agent, proposer_agent, validator_agent


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
    }
]


def run_standards_enhancement(standard_id: str, trigger_scenario: str) -> Dict[str, Any]:
    """
    Run the standards enhancement process with the three specialized agents.
    
    Args:
        standard_id: The ID of the standard to enhance (e.g., "10" for FAS 10)
        trigger_scenario: The scenario that triggers the need for enhancement
        
    Returns:
        Dict with the enhancement results including:
        - Original standard excerpt
        - Identified issues
        - Proposed enhancements
        - Validation results
    """
    print(f"Starting enhancement process for FAS {standard_id}...")
    print(f"Trigger scenario: {trigger_scenario}")
    
    # Step 1: Reviewer Agent - Extract and analyze standard
    print("\nStep 1: Reviewing standard and identifying enhancement areas...")
    review_result = reviewer_agent.extract_standard_elements(standard_id, trigger_scenario)
    
    # Step 2: Proposer Agent - Generate enhancement proposals
    print("\nStep 2: Generating enhancement proposals...")
    proposal_result = proposer_agent.generate_enhancement_proposal(review_result)
    
    # Step 3: Validator Agent - Validate proposals
    print("\nStep 3: Validating enhancement proposals...")
    validation_result = validator_agent.validate_proposal(proposal_result)
    
    # Compile final results
    return {
        "standard_id": standard_id,
        "trigger_scenario": trigger_scenario,
        "review": review_result["review_analysis"],
        "proposal": proposal_result["enhancement_proposal"],
        "validation": validation_result["validation_result"],
        "full_results": {
            "review_result": review_result,
            "proposal_result": proposal_result,
            "validation_result": validation_result
        }
    }


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
    
    return "\n".join(output)


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
    
    # Run enhancement
    result = run_standards_enhancement(standard_id, trigger)
    
    # Display formatted results
    formatted_results = format_results_for_display(result)
    print("\n")
    print(formatted_results)


if __name__ == "__main__":
    run_enhancement_demo()