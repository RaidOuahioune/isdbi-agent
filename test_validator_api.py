import json
from components.agents.validator_agent import ValidatorAgent
from ui.output_parser import OutputParser

def test_validator_with_api():
    """Test the validator agent with the Islamic Finance Compliance API enabled"""
    
    # Create a sample proposal for testing
    test_proposal = {
        "standard_id": "10",  # FAS 10 (Istisna'a)
        "trigger_scenario": "A financial institution is offering Istisna'a contracts where they act as the manufacturer (sani') but are insisting on taking full payment upfront before manufacturing begins. Some customers have raised concerns about this practice.",
        "enhancement_proposal": """## Original Text
**Original Text:** 3/1/1 An Istisna'a contract is permissible for the creation of an asset which is the obligation of the manufacturer (sani').

## Proposed Modified Text
**Proposed Modified Text:** 3/1/1 An Istisna'a contract is permissible for the creation of an asset which is the obligation of the manufacturer (sani'). The manufacturer must not require full payment in advance, as this contradicts the purpose of Istisna'a as a manufacturing contract. Payment may be made in installments linked to stages of completion, or deferred until delivery.

## Rationale
The original text does not address payment timing, which has led to practices where some financial institutions require full upfront payment. This effectively transforms the contract into a salam contract (advance payment for future delivery) rather than a true Istisna'a. This enhancement clarifies the payment structure to maintain the distinct nature of Istisna'a contracts.
"""
    }
    
    # Initialize validator agent with API enabled
    validator_with_api = ValidatorAgent(use_compliance_api=True)
    
    # Get validation with API
    print("Testing validator with Islamic Finance Compliance API...")
    validation_with_api = validator_with_api.validate_proposal(test_proposal)
    
    # Initialize validator agent with API disabled
    validator_without_api = ValidatorAgent(use_compliance_api=False)
    
    # Get validation without API
    print("Testing validator without Islamic Finance Compliance API...")
    validation_without_api = validator_without_api.validate_proposal(test_proposal)
    
    # Print results
    print("\n===== VALIDATION WITH API =====")
    print(validation_with_api["validation_result"])
    
    print("\n===== VALIDATION WITHOUT API =====")
    print(validation_without_api["validation_result"])
    
    # Test compatibility with output parser
    print("\n===== TESTING OUTPUT PARSER COMPATIBILITY =====")
    
    # Create a full results dictionary that mimics what would be passed to the output parser
    full_results = {
        "standard_id": test_proposal["standard_id"],
        "trigger_scenario": test_proposal["trigger_scenario"],
        "proposal": test_proposal["enhancement_proposal"],
        "validation": validation_with_api["validation_result"],
    }
    
    # Parse the results using the OutputParser
    try:
        print("Parsing results with OutputParser...")
        parsed_results = OutputParser.parse_markdown_sections("# Standards Enhancement Results for FAS 10\n\n" + 
                                                             "## Trigger Scenario\n" + full_results["trigger_scenario"] + "\n\n" +
                                                             "## Proposed Enhancements\n" + full_results["proposal"] + "\n\n" +
                                                             "## Validation Results\n" + full_results["validation"])
        
        print("Successfully parsed results:")
        print(f"- Standard ID: {parsed_results['standard_id']}")
        print(f"- Contains trigger scenario: {'trigger_scenario' in parsed_results}")
        print(f"- Contains proposal: {'proposal' in parsed_results}")
        print(f"- Contains validation: {'validation' in parsed_results}")
        
        # Extract original and proposed text
        original_text, proposed_text = OutputParser.extract_original_and_proposed(parsed_results.get("proposal", ""))
        print(f"- Successfully extracted original and proposed text: {bool(original_text and proposed_text)}")
        
        # Test diff generation
        if original_text and proposed_text:
            print("- Generating diff...")
            diff_result = OutputParser.generate_enhanced_diff(original_text, proposed_text)
            print(f"- Successfully generated diff: {bool(diff_result)}")
    except Exception as e:
        print(f"Error during output parsing: {e}")
    
    # Save results to files
    with open("validation_with_api.json", "w") as f:
        json.dump(validation_with_api, f, indent=2)
    
    with open("validation_without_api.json", "w") as f:
        json.dump(validation_without_api, f, indent=2)
    
    print("\nResults saved to validation_with_api.json and validation_without_api.json")

if __name__ == "__main__":
    test_validator_with_api() 