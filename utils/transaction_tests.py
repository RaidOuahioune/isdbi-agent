"""
Transaction testing module for the Islamic Finance standards system.
"""

import logging
from agents import transaction_analyzer, transaction_rationale

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