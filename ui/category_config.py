"""
Category configuration for the AAOIFI Standards Enhancement System demo.
This module defines the categories and test cases for the standards enhancement.
"""

# Categories of standards enhancements
ENHANCEMENT_CATEGORIES = {
    "category1": "Governance & Disclosure", 
    "category2": "Investment Products",
    "category3": "Financial Transactions"
}

# Test cases for each category
ENHANCEMENT_TEST_CASES = [
    {
        "name": "Digital Assets in Istisna'a",
        "standard_id": "10",
        "category": "category3",
        "output_file": "category3_agent_output.txt",
        "trigger_scenario": """A financial institution wants to structure an Istisna'a contract for the development 
                              of a large-scale AI software platform. The current wording of FAS 10 on 'well-defined 
                              subject matter' and 'determination of cost' is causing uncertainty for intangible assets 
                              like software development."""
    },
    {
        "name": "Tokenized Mudarabah Investments",
        "standard_id": "4",
        "category": "category2",
        "output_file": "category2_agent_output.txt",
        "trigger_scenario": """Fintech platforms are offering investment in tokenized Mudarabah funds where investors can 
                              buy/sell fractional ownership tokens on blockchain networks. FAS 4 needs clarification on 
                              how to handle these digital representations of investment units and profit distribution in 
                              real-time token trading scenarios."""
    },
    {
        "name": "Green Sukuk Environmental Impact",
        "standard_id": "32",
        "category": "category1",
        "output_file": "category1_agent_output.txt",
        "trigger_scenario": """Islamic financial institutions are increasingly issuing 'Green Sukuk' to fund 
                              environmentally sustainable projects, but FAS 32 lacks specific guidance on how to account 
                              for and report environmental impact metrics alongside financial returns."""
    }
]

def get_test_cases_by_category(category):
    """Get test cases filtered by category"""
    return [case for case in ENHANCEMENT_TEST_CASES if case["category"] == category]

def get_default_output_file(category):
    """Get the default output file for a category"""
    for case in ENHANCEMENT_TEST_CASES:
        if case["category"] == category:
            return case.get("output_file")
    return "category3_agent_output.txt"  # Default fallback 