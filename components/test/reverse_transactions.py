test_cases = [
    {
        "name": "Test case 2",
        "transaction": """
        Context: The client pays all outstanding amounts on time, reducing expected losses.
      
         Adjustments:
            Loss provision reversed.
            Recognized revenue adjusted.
         
         Accounting Treatment:
            Reduction in impairment expense.
            Recognition of full contract revenue.
         
         Journal Entry for Loss Provision Reversal:
            Dr. Allowance for Impairment $500,000
            Cr. Provision for Losses $500,000
         This restores revenue after full payment. 

       """,
    },
    {
        "name": "Test case 1",
        "transaction": """
       Context: Buyer defaults, stopping project completion.
      Adjustments:
      Recognized Revenue: $6,500,000
      Impairment of Receivables: $500,000
      
      Accounting Treatment:
      Recognition of bad debt
      Adjustment of work-in-progress valuation
      
      Journal Entry for Default Adjustment:
      Dr. Bad Debt Expense $500,000
      Cr. Accounts Receivable $500,000

      This writes off uncollectible amounts.
       """,
    },
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
        "name": "Agricultural Commodity Advance Purchase Cancellation",
        "transaction": """Advance Purchase Agreement Cancellation Notice

Al-Falah Agricultural Bank and Sunrise Farms cancel their advance purchase agreement for wheat due to crop failure.

JOURNAL ENTRIES:
1. Dr. Advance Payment Liability $850,000
   Cr. Commodity Receivables $825,000
   Cr. Cancellation Income $25,000
2. Dr. Contract Termination Expense $15,000
   Cr. Cash $15,000

AGREEMENT DETAILS:
* Original Contract: Advance payment of $850,000 for 10,000 bushels of wheat
* Delivery Date: Originally scheduled for 6 months after payment
* Reason for Cancellation: Severe drought affecting crop yield
* Mutual Agreement Terms: Bank agrees to waive penalty in exchange for $15,000 administrative fee
* Accounting Treatment: Reversal of receivables, Partial recognition of profit, Settlement of fee

The agricultural bank had arranged to sell the wheat through a parallel agreement with a flour mill, which must now also be cancelled separately.
            """,
    },
    {
        "name": "Ijarah Early Termination",
        "transaction": """Asset Early Termination Notice

Al-Baraka Islamic Bank and TechCorp terminate their  agreement in year 2 of a 5-year term due to operational changes.

JOURNAL ENTRIES:
1. Dr.  Liability $4,500,000
   Cr. Right-of-Use Asset $3,800,000
   Cr. Cash $350,000
   Cr. Early Termination Income $350,000
2. Dr. Accumulated Depreciation $1,200,000
   Cr. Deferred  Cost $1,200,000

KEY INFORMATION:
* Original Asset Cost: $6,000,000
* Remaining Lease Liability: $4,500,000
* Carrying Value of ROU Asset: $3,800,000
* Early Termination Fee Paid by Lessee: $350,000
* Contract Terms: Lessee bears costs of early termination as per original agreement
* Accounting Treatment: Derecognition of lease liability and ROU asset, Recognition of termination fee as income
            """,
    },
    {
        "name": "Equipment Lease Modification",
        "transaction": """Equipment Lease Modification Agreement

GlobalTech Manufacturing and Al-Amal Bank agree to modify their existing 5-year equipment lease agreement at the end of year 2.

ACCOUNTING ENTRIES:
1. Dr. Lease Liability (Original) $3,200,000
   Cr. Right-of-Use Asset (Original) $2,950,000
   Cr. Gain on Lease Modification $250,000
2. Dr. Right-of-Use Asset (Modified) $2,800,000
   Cr. Lease Liability (Modified) $2,800,000

MODIFICATION DETAILS:
* Remaining Lease Payments: Reduced from $3,600,000 to $3,000,000
* Lease Term: Extended from 3 remaining years to 4 remaining years
* Equipment: Manufacturing equipment with original cost of $5,000,000
* Reason for Modification: Market conditions and revised operational needs
* Accounting Treatment: Remeasurement of lease liability and right-of-use asset

The lease modification was agreed upon due to changing market conditions, with reduced payment amounts but extended duration.
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
    {
        "name": "Hybrid Digital Asset Conversion",
        "transaction": """Digital Exchange Service Agreement - Conversion Report

Al-Mustaqbal Digital Bank processes a conversion of digital assets for client BlueSky Holdings.

JOURNAL ENTRIES:
1. Dr. Digital Currency Holdings (Ethereum) $3,200,000
   Cr. Digital Trust Certificates $2,950,000
   Cr. Exchange Service Revenue $250,000
2. Dr. Algorithmic Custodial Fee $45,000
   Cr. Smart Contract Service Income $45,000

TRANSACTION INFORMATION:
* Original Asset: Digital Trust Certificates representing ownership in renewable energy project
* Conversion Asset: Ethereum-based utility tokens allowing access to energy trading platform
* Holding Period: Certificates were held for 14 months of 36-month maturity
* Valuation Method: Mark-to-market with Shariah-compliant averaging over 30 days
* Risk Mitigation: Digital assets housed in multi-signature wallet with 3-of-5 approval structure
* Exchange Ratio: 1 Certificate = 1.08 utility tokens
* Accounting Treatment: Asset conversion, revenue recognition, custodial service recording

The transaction was executed through a novel hybrid exchange structure combining elements of partnership, agency, and sales concepts in accordance with the bank's innovative products committee guidance.
            """,
    },
    {
        "name": "Deferred Payment Sale Early Settlement",
        "transaction": """Financing Agreement Early Settlement Notice

Gulf Trading Company settles its outstanding financing obligation with Al-Noor Islamic Bank ahead of schedule.

JOURNAL ENTRIES:
1. Dr. Financing Receivables $2,400,000
   Cr. Cash $2,350,000
   Cr. Early Settlement Rebate $50,000
2. Dr. Unearned Profit $320,000
   Cr. Profit Income $320,000

TRANSACTION DETAILS:
* Original Asset: Commercial Equipment (Cost Price: $2,000,000)
* Original Selling Price: $2,720,000 (including $720,000 deferred profit)
* Original Payment Schedule: 36 monthly installments of $75,556
* Payments Made: 24 installments ($1,813,344 total)
* Remaining Balance at Settlement: $906,656
* Early Settlement Discount: $50,000 rebate offered as incentive
* Settlement Timing: Month 25 of 36-month term
* Accounting Treatment: Derecognition of receivables, Partial profit recognition, Rebate recording

The early settlement was completed according to the bank's policy that allows customers to settle financing facilities early with a rebate as approved by the Shariah board.
            """,
    },
]
