import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agent_graph import agent_graph
from state import create_empty_state
from agents import (
    orchestrator,
    standards_extractor,
    use_case_processor,
    transaction_analyzer,
    transaction_rationale,
)

# Load environment variables
load_dotenv()


def process_query(query: str) -> AIMessage:
    """
    Process a user query through the multi-agent system.

    Args:
        query: The user's query about Islamic finance standards or scenarios.

    Returns:
        AIMessage: The response from the agent system.
    """
    # Create a new message
    message = HumanMessage(content=query)

    # Create initial state with the user message
    state = create_empty_state()
    state["messages"] = [message]

    # Process the message through the agent graph
    result = agent_graph.invoke(state)

    # Extract and return the AI's response
    messages = result["messages"]
    return messages[-1] if messages else AIMessage(content="No response was generated.")


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


def sample_queries() -> List[Dict[str, str]]:
    """
    Return a list of sample queries to test the system.
    """
    return [
        {
            "name": "Basic Ijarah Scenario",
            "query": """
            A bank enters into an Ijarah agreement with a customer for equipment 
            valued at $100,000 for a 5-year lease term with annual payments of $25,000. 
            How should the bank account for this transaction according to AAOIFI standards?
            """,
        },
        {
            "name": "Murabaha Transaction",
            "query": """
            A customer approaches an Islamic bank to finance the purchase of a vehicle 
            worth $50,000. The bank agrees to purchase the vehicle and sell it to the 
            customer at a marked-up price of $55,000, to be paid in 12 monthly installments.
            What are the journal entries for this Murabaha transaction?
            """,
        },
        {
            "name": "Specific Standard Information",
            "query": "What are the key requirements in FAS 28 for Murabaha accounting?",
        },
        {
            "name": "Multiple Standards Scenario",
            "query": """
            A company needs to acquire manufacturing equipment worth $500,000. They are 
            considering either an Ijarah arrangement or an Istisna'a contract. What are 
            the accounting implications of each approach according to AAOIFI standards?
            """,
        },
        {
            "name": "GreenTech Buyout - Reverse Transaction",
            "query": """
            Analyze this reverse transaction:
            
            Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
            
            Journal Entries:
            Dr. GreenTech Equity $1,750,000
            Cr. Cash $1,750,000
            
            Additional Information:
            Buyout Price: $1,750,000
            Bank Ownership: 100%
            Accounting Treatment: Derecognition of GreenTech's equity, Recognition of acquisition expense
            
            What AAOIFI standards apply to this reverse transaction?
            """,
        },
        {
            "name": "Contract Change Order Reversal",
            "query": """
            Analyze this reverse transaction:
            
            Context: The client cancels the change order, reverting to the original contract terms.
            
            Journal Entries:
            Dr. Accounts Payable $1,000,000
            Cr. Work-in-Progress $1,000,000
            
            Additional Information:
            Revised Contract Value: Back to $5,000,000
            Timeline Restored: 2 years
            Accounting Treatment: Adjustment of revenue and cost projections, Reversal of additional cost accruals
            
            Which AAOIFI standards apply to this contract reversal?
            """,
        },
        {
            "name": "Sukuk Early Termination",
            "query": """
            Analyze this reverse transaction:
            
            Context: The Sukuk is being terminated early in year 3 of a 5-year term.
            
            Journal Entries:
            Dr. Sukuk Liability $7,500,000
            Cr. Cash $7,650,000
            Dr. Early Termination Fee $150,000
            
            Additional Information:
            Original Sukuk Amount: $10,000,000
            Early Termination Penalty: 2% of outstanding balance
            Accounting Treatment: Derecognition of liability, Recognition of termination fee
            
            What AAOIFI standards apply to this early Sukuk termination?
            """,
        },
    ]


def run_sample_tests():
    """
    Run a series of sample tests to demonstrate the system capabilities.
    """
    samples = sample_queries()

    for i, sample in enumerate(samples, 1):
        print(f"\n\n===== SAMPLE TEST {i}: {sample['name']} =====\n")
        print(f"Query: {sample['query'].strip()}")
        print("\n----- RESPONSE -----")

        try:
            response = process_query(sample["query"])
            print(response.content)
        except Exception as e:
            print(f"Error processing sample: {e}")

        print("\n==========================================================")

        # Ask if user wants to continue with next sample
        if i < len(samples):
            cont = input("\nContinue to next sample? (y/n): ")
            if cont.lower() not in ["y", "yes"]:
                break


def run_category2_tests(verbose=False):
    """
    Run tests specifically for Category 2 (Reverse Transactions Analysis)
    """
    print("\n" + "=" * 80)
    print("CATEGORY 2: REVERSE TRANSACTIONS ANALYSIS TESTS")
    print("=" * 80)

    # Define test cases specifically for reverse transactions
    test_cases = [
        {
            "name": "GreenTech Buyout",
            "transaction": {
                "context": "GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.",
                "journal_entries": [
                    {
                        "debit_account": "GreenTech Equity",
                        "credit_account": "Cash",
                        "amount": 1750000,
                    }
                ],
                "additional_info": {
                    "Buyout Price": "$1,750,000",
                    "Bank Ownership": "100%",
                    "Accounting Treatment": "Derecognition of GreenTech's equity, Recognition of acquisition expense",
                },
            },
        },
        {
            "name": "Contract Change Order Reversal",
            "transaction": {
                "context": "The client cancels the change order, reverting to the original contract terms.",
                "journal_entries": [
                    {
                        "debit_account": "Accounts Payable",
                        "credit_account": "Work-in-Progress",
                        "amount": 1000000,
                    }
                ],
                "additional_info": {
                    "Revised Contract Value": "Back to $5,000,000",
                    "Timeline Restored": "2 years",
                    "Accounting Treatment": "Adjustment of revenue and cost projections, Reversal of additional cost accruals",
                },
            },
        },
        {
            "name": "Sukuk Early Termination",
            "transaction": {
                "context": "The Sukuk is being terminated early in year 3 of a 5-year term.",
                "journal_entries": [
                    {
                        "debit_account": "Sukuk Liability",
                        "credit_account": "Cash",
                        "amount": 7650000,
                    },
                    {
                        "debit_account": "Early Termination Fee",
                        "credit_account": "Income",
                        "amount": 150000,
                    },
                ],
                "additional_info": {
                    "Original Sukuk Amount": "$10,000,000",
                    "Early Termination Penalty": "2% of outstanding balance",
                    "Accounting Treatment": "Derecognition of liability, Recognition of termination fee",
                },
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # Format transaction details for display
        transaction = test_case["transaction"]

        print(f"Context: {transaction['context']}")
        print("\nJournal Entries:")
        for entry in transaction["journal_entries"]:
            print(f"Dr. {entry['debit_account']} ${entry['amount']:,.2f}")
            print(f"Cr. {entry['credit_account']} ${entry['amount']:,.2f}")

        print("\nAdditional Information:")
        for key, value in transaction["additional_info"].items():
            print(f"{key}: {value}")

        print("\n----- ANALYSIS RESULTS -----")

        try:
            # Perform transaction analysis
            analysis_result = transaction_analyzer.analyze_transaction(transaction)
            print("\nTransaction Analysis:")
            print(analysis_result["analysis"])

            # If verbose mode is enabled, show all chunks
            if verbose and "retrieval_stats" in analysis_result:
                stats = analysis_result["retrieval_stats"]
                print(f"\n--- RAG Retrieval Stats ---")
                print(f"Retrieved {stats['chunk_count']} chunks")
                print("\nSample chunks:")
                for i, chunk_summary in enumerate(stats["chunks_summary"]):
                    print(f"\nChunk {i + 1}: {chunk_summary}")

            # If standards were identified, get rationales
            if analysis_result["identified_standards"]:
                standards = analysis_result["identified_standards"]
                print(f"\nIdentified Standards: {', '.join(standards)}")

                # Get rationale for top standard
                if standards:
                    top_standard = standards[0]
                    rationale = transaction_rationale.explain_standard_application(
                        transaction, top_standard
                    )

                    print(f"\n{top_standard} Application Rationale:")
                    print(rationale["rationale"])

        except Exception as e:
            print(f"Error analyzing transaction: {e}")

        if i < len(test_cases):
            cont = input("\nContinue to next test case? (y/n): ")
            if cont.lower() not in ["y", "yes"]:
                break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Islamic Finance Standards Multi-Agent System"
    )
    parser.add_argument(
        "--samples", action="store_true", help="Run sample test queries"
    )
    parser.add_argument(
        "--category2",
        action="store_true",
        help="Run Category 2 reverse transaction tests",
    )
    parser.add_argument(
        "--category2-verbose",
        action="store_true",
        help="Run Category 2 reverse transaction tests with detailed retrieval logs",
    )
    args = parser.parse_args()

    if args.category2_verbose:
        run_category2_tests(verbose=True)
    elif args.category2:
        run_category2_tests()
    elif args.samples:
        run_sample_tests()
    else:
        run_interactive_session()
