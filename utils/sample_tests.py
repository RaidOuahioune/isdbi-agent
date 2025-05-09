"""
Sample testing module for the Islamic Finance standards system.
"""

from typing import List, Dict
from utils.query_processor import process_query

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
            """
        },
        {
            "name": "Digital Assets Enhancement",
            "query": """
            Enhance FAS 10 (Istisna'a) to address challenges with intangible digital assets. 
            Financial institutions need guidance on how to structure Istisna'a contracts 
            for software development projects where the "subject matter" evolves during 
            development and may not be fully specifiable upfront.
            """
        },
        {
            "name": "Tokenized Investments Enhancement",
            "query": """
            Enhance FAS 4 (Mudarabah) to address tokenized investments on blockchain platforms
            where ownership units can be traded in real-time on secondary markets. Current 
            standards don't clearly address how to handle profit distributions and accounting
            for these digital representations of investment units.
            """
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