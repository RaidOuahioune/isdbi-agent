real_output = [
    {
        "name": "Ijarah MBT Accounting (in Lessee’s books) - Provided Example",
        "expected_solution": """
Initial Recognition at the Time of Commencement of Ijarah (1 January 2019):
Determine the Right-of-Use Asset (ROU)
Prime cost (Purchase + Import tax + Freight):
= 450,000 + 12,000 + 30,000 = 492,000
Less: Terminal value (i.e., Purchase price of USD 3,000 to acquire ownership)
= 492,000 − 3,000 = 489,000 (ROU)

Add Deferred Ijarah Cost:
Total rentals over 2 years = 300,000 × 2 = 600,000
Less: Prime cost of ROU = 489,000 (Note: FAS 32, para 29, refers to 'prime cost of right-of-use asset' not 'Present value of ROU' as in user's example for calculating deferred Ijarah cost)
Deferred Ijarah Cost = 600,000 − 489,000 = 111,000

Journal Entry:
Dr. Right of Use Asset (ROU) USD 489,000
Dr. Deferred Ijarah Cost USD 111,000
Cr. Ijarah Liability USD 600,000
            """
    },
    {
        "name": "Murabaha Sale - Initial Recognition (Seller's Books)",
        "expected_solution": """
1. Initial Recognition of Inventory (On Purchase - 15 February 2020):
Cost of goods = USD 100,000
Additional costs (shipping and insurance) = USD 5,000
Total cost of inventory = 100,000 + 5,000 = USD 105,000

Journal Entry:
Dr. Inventory for Murabaha USD 105,000 [cite: 506]
    Cr. Cash/Payables USD 105,000

2. Recognition of Sale and Receivable (On Sale - 20 February 2020):
Murabaha Sale Price = USD 125,000
Cost of Sales = USD 105,000
Murabaha Profit = 125,000 - 105,000 = USD 20,000

Journal Entries:
Dr. Murabaha Receivables USD 125,000 [cite: 511]
    Cr. Murabaha Sales Revenue USD 125,000 [cite: 510]
    Cr. Deferred Murabaha Profit USD 20,000 (contra-asset or recognized over time if cash price > cost) [cite: 532, 534]

Dr. Cost of Murabaha Sales USD 105,000 [cite: 531]
    Cr. Inventory for Murabaha USD 105,000 [cite: 522]

(Note: FAS 28, para 23, indicates that the profit (difference between revenue and cost of sales) is deferred. If the equivalent cash sale price of the goods sold is higher than the cost of sales, the profit to the extent of difference between the cash sale price and the cost of sales shall not be deferred. Assuming the entire profit is deferred for simplicity in this example as cash sale price is not given.)
            """
    },
    {
        "name": "Murabaha Purchase - Initial Recognition (Buyer's Books)",
        "expected_solution": """
Initial Recognition of Asset and Liability (On Purchase - 20 February 2020):
Cost of Asset (Murabaha Price) = USD 125,000

Journal Entry:
Dr. Asset (e.g., Inventory, Equipment) USD 125,000 [cite: 566, 567]
    Cr. Murabaha Payable USD 125,000 [cite: 570]
            """
    },
    {
        "name": "Istisna'a Contract - Revenue Recognition (Percentage of Completion - Seller's Books)",
        "expected_solution": """
Recognition for the year ended 31 December 2021:
Total Contract Price = USD 1,000,000
Total Estimated Cost = USD 800,000
Total Estimated Profit = 1,000,000 - 800,000 = USD 200,000

Costs incurred to date (31 Dec 2021) = USD 320,000
Percentage of Completion = (Costs incurred to date / Total Estimated Cost) * 100
Percentage of Completion = (320,000 / 800,000) * 100 = 40%

Revenue to be recognized for 2021 = Total Contract Price * Percentage of Completion
Revenue to be recognized for 2021 = 1,000,000 * 40% = USD 400,000 [cite: 684]

Cost of Istisna'a Revenue for 2021 = Costs incurred in 2021 = USD 320,000

Profit to be recognized for 2021 = Total Estimated Profit * Percentage of Completion
Profit to be recognized for 2021 = 200,000 * 40% = USD 80,000
Alternatively, Profit = Revenue Recognized - Cost of Revenue Recognized = 400,000 - 320,000 = USD 80,000

Journal Entry to recognize revenue and profit (summary):
Dr. Cost of Istisna'a Revenue USD 320,000
Dr. Istisna'a Work-in-Progress (for profit portion) USD 80,000 [cite: 686]
    Cr. Istisna'a Revenue USD 400,000

(Assuming billings match revenue recognition for simplicity here. Detailed entries for costs incurred would be Dr. Istisna'a Work-in-Progress, Cr. Cash/Payables. Billings: Dr. Accounts Receivable, Cr. Istisna'a Billings)
            """
    },
    {
        "name": "Parallel Istisna'a - Cost Recognition (Bank as Buyer in Parallel, Seller in Main - Seller's Books)",
        "expected_solution": """
Entries for Salam Islamic Bank for the year ended 31 December 2022:

1. Billing from Subcontractor (Precision Manufacturing Co.):
Journal Entry:
Dr. Istisna'a Costs (Asset) USD 200,000 [cite: 678]
    Cr. Istisna'a Accounts Payable (to Precision Manufacturing Co.) USD 200,000 [cite: 678]

2. Billing to Customer (Tech Solutions Inc.):
Journal Entry:
Dr. Istisna'a Accounts Receivable (from Tech Solutions Inc.) USD 250,000 [cite: 680]
    Cr. Istisna'a Billings (Liability/Contra-asset) USD 250,000 [cite: 681]

Revenue and Profit Recognition (assuming percentage of completion based on subcontractor's progress is 200,000/400,000 = 50%):
Istisna'a Revenue (Main Contract) = 500,000 * 50% = USD 250,000
Cost of Istisna'a Revenue (Main Contract cost from parallel) = 400,000 * 50% = USD 200,000
Istisna'a Profit for the period = 250,000 - 200,000 = USD 50,000

Journal Entry to recognize revenue and profit:
Dr. Cost of Istisna'a Revenue USD 200,000
Dr. Istisna'a Costs (Asset - for profit portion) USD 50,000 [cite: 702]
    Cr. Istisna'a Revenue USD 250,000
            """
    },
    {
        "name": "Salam Contract - Initial Recognition and Payment (Bank as Buyer - Buyer's Books)",
        "expected_solution": """
Initial Recognition and Payment (1 June 2023):
Salam Capital Paid = USD 200,000

Journal Entry:
Dr. Salam Financing (Asset) USD 200,000 [cite: 1067, 1069, 1074]
    Cr. Cash USD 200,000
            """
    },
    {
        "name": "Salam Contract - Receipt of Goods (Different Quality - Buyer's Books)",
        "expected_solution": """
Receipt of Goods (1 December 2023):
Book Value of Contracted Al-Muslam Fihi (Salam Financing Asset) = USD 200,000
Market Value of Received Al-Muslam Fihi = USD 190,000
Loss on receipt = 200,000 - 190,000 = USD 10,000

Journal Entry:
Dr. Inventory (Premium Dates - at market value) USD 190,000 [cite: 1078]
Dr. Loss on Salam Contract USD 10,000 [cite: 1078]
    Cr. Salam Financing (Asset) USD 200,000
            """
    },
    {
        "name": "Musharaka Financing - Initial Capital Contribution (Bank's Books)",
        "expected_solution": """
Initial Capital Contribution (1 January 2024):
Bank's Cash Contribution = USD 200,000

Journal Entry:
Dr. Musharaka Financing (Asset - Enterprise Solutions Ltd.) USD 200,000 [cite: 1324, 1325, 1327]
    Cr. Cash USD 200,000
            """
    },
    {
        "name": "Diminishing Musharaka - Bank's Share Transfer (Bank's Books)",
        "expected_solution": """
Transfer of Bank's Share (30 June 2024):
Historical Cost of Share Sold = USD 50,000
Sale Price (Fair Value) = USD 55,000
Gain on Sale of Musharaka Share = 55,000 - 50,000 = USD 5,000

Journal Entries:
Dr. Cash USD 55,000
    Cr. Musharaka Financing (Asset - Future Homes Ltd.) USD 50,000 [cite: 1328]
    Cr. Gain on Sale of Musharaka Share (Income) USD 5,000 [cite: 1328]
            """
    },
    {
        "name": "Ijarah - Lessor Accounting (Initial Recognition of Underlying Asset)",
        "expected_solution": """
Initial Recognition of Ijarah Asset (1 March 2020):
Purchase Price = USD 30,000
Non-recoverable Purchase Taxes = USD 1,000
Transportation Costs = USD 500
Total Cost of Ijarah Asset = 30,000 + 1,000 + 500 = USD 31,500

Journal Entry:
Dr. Ijarah Assets (e.g., Vehicles for Lease) USD 31,500 [cite: 225, 226, 261]
    Cr. Cash/Payables USD 31,500
            """
    }
]