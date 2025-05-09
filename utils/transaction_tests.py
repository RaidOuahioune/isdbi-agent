# filepath: c:\Users\ELITE COMPUTER\Desktop\Hackaton\isdbi\isdbi-agent\utils\transaction_tests.py
"""
Transaction testing module for the Islamic Finance standards system.
"""

from agents import transaction_analyzer, transaction_rationale


def run_category2_tests(verbose=False):
    """
    Run tests specifically for Category 2 (Reverse Transactions Analysis)
    """
    print("\n" + "=" * 80)
    print("CATEGORY 2: REVERSE TRANSACTIONS ANALYSIS TESTS")
    print("=" * 80)

    # Define test cases specifically for reverse transactions using string descriptions
    # Each test case now has a different format to demonstrate flexibility
    test_cases = [
        {
            "name": "GreenTech Buyout",
            "transaction": """
TRANSACTION SUMMARY: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.

FINANCIAL ENTRIES:
Dr. GreenTech Equity $1,750,000
Cr. Cash $1,750,000

KEY FACTS:
- Buyout Price: $1,750,000
- Bank Ownership: 100%
- Accounting Treatment: Derecognition of GreenTech's equity, Recognition of acquisition expense
            """,
        },
        {
            "name": "Contract Change Order Reversal",
            "transaction": """Contract Change Order Cancellation Details
--------------------------------------------------------------------------------
The client cancels the change order, reverting to the original contract terms.
--------------------------------------------------------------------------------
JOURNAL ENTRIES
* Debit: Accounts Payable $1,000,000
* Credit: Work-in-Progress $1,000,000

CONTRACT INFORMATION:
Revised Contract Value: Back to $5,000,000
Timeline Restored: 2 years

ACCOUNTING IMPACT: Adjustment of revenue and cost projections, Reversal of additional cost accruals
            """,
        },
        {
            "name": "Sukuk Early Termination",
            "transaction": """Sukuk Certificate #SC-2025-03 Early Termination Notice

The Sukuk is being terminated early in year 3 of a 5-year term.

Accounting Records:
1. Dr. Sukuk Liability $7,650,000
   Cr. Cash $7,650,000
2. Dr. Early Termination Fee $150,000
   Cr. Income $150,000

Background Information:
* Original Sukuk Amount: $10,000,000
* Early Termination Penalty: 2% of outstanding balance
* Accounting Treatment: Derecognition of liability, Recognition of termination fee
            """,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n----- TEST CASE {i}: {test_case['name']} -----\n")

        # The transaction is now directly a string description
        transaction = test_case["transaction"]

        # Display the transaction description
        print(transaction)

        print("\n----- ANALYSIS RESULTS -----")

        try:
            # Perform transaction analysis
            analysis_result = transaction_analyzer.analyze_transaction(transaction)
            print("\nTransaction Analysis:")
            print(analysis_result["analysis"])

            # If verbose mode is enabled, show all chunks
            if verbose and "retrieval_stats" in analysis_result:
                stats = analysis_result["retrieval_stats"]
                print("\n--- RAG Retrieval Stats ---")
                print(f"Retrieved {stats['chunk_count']} chunks")
                print("\nSample chunks:")
                for j, chunk_summary in enumerate(stats["chunks_summary"]):
                    print(f"\nChunk {j + 1}: {chunk_summary}")

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
