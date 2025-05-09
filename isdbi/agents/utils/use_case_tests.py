"""
Use case testing module for the Islamic Finance standards system.
"""



import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.agents.use_case_processor import use_case_processor
from components.test.use_case import test_cases
from retreiver import retriever 


def run_use_case_tests(verbose=False):
    """
    Run tests for Category 3 (Use Case Processing)
    Tests accounting guidance generation for Islamic finance use cases
    """
    print("\n" + "=" * 80)
    print("CATEGORY 3: USE CASE PROCESSING TESTS")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # The use case scenario is in the transaction field
        scenario = test_case["transaction"]

        # Display the scenario
        print(scenario)

        print("\n----- PROCESSING RESULTS -----")

        try:
            # Process the use case using the processor agent
            result = use_case_processor.process_use_case(scenario)
            
            print("\nAccounting Guidance:")
            print(result["accounting_guidance"])
            
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
                        print(f"\nChunk {j+1} (excerpt):")
                        # Show a shortened version of the chunk
                        text = node.text
                        print(text[:200] + "..." if len(text) > 200 else text)
                
        except Exception as e:
            print(f"Error processing use case: {e}")
            
        if i < len(test_cases):
            cont = input("\nContinue to next test case? (y/n): ")
            if cont.lower() not in ["y", "yes"]:
                break


if __name__ == "__main__":
    # You can run the file directly to test use cases
    run_use_case_tests()