from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

from retreiver import retriever


@tool
def search_standards(query: str) -> str:
    """
    Search for information within AAOIFI standards.
    
    Args:
        query: The search query to find information in AAOIFI standards.
        
    Returns:
        str: Relevant information from the standards.
    """
    # Use the retriever to get relevant chunks from standards
    retrieved_nodes = retriever.retrieve(query)
    
    # If no results found, return a message
    if not retrieved_nodes:
        return "No relevant information found in AAOIFI standards for this query."
    
    # Extract text content from retrieved nodes
    results = []
    for node in retrieved_nodes[:10]:  # Limiting to top 10 results for clarity
        results.append(f"- {node.text}")
    
    # Combine all results
    return "\n\n".join(results)


@tool
def get_standard_info(standard_id: str) -> str:
    """
    Get detailed information about a specific AAOIFI standard.
    
    Args:
        standard_id: The ID of the standard (e.g., "4" for FAS 4, "28" for FAS 28)
        
    Returns:
        str: Detailed information about the specified standard.
    """
    # Map of standard IDs to their full names
    standard_names = {
        "4": "FAS 4 - Mudarabah Financing",
        "7": "FAS 7 - Musharakah Financing",
        "10": "FAS 10 - Istisna'a and Parallel Istisna'a",
        "28": "FAS 28 - Murabaha and Other Deferred Payment Sales",
        "32": "FAS 32 - Ijarah"
    }
    
    # Check if standard ID is valid
    if standard_id not in standard_names:
        return f"Invalid standard ID: {standard_id}. Available standards: 4, 7, 10, 28, 32."
    
    # Use the retriever to get information about this specific standard
    query = f"FAS {standard_id} standard full details"
    retrieved_nodes = retriever.retrieve(query)
    
    # Extract text content from retrieved nodes
    results = [f"# {standard_names[standard_id]}\n"]
    for node in retrieved_nodes[:15]:  # Get more details for a specific standard
        results.append(f"{node.text}")
    
    # Combine all results
    return "\n\n".join(results)


@tool
def analyze_financial_scenario(scenario: str) -> str:
    """
    Analyze a financial scenario and determine which AAOIFI standards apply.
    
    Args:
        scenario: The financial scenario or transaction to analyze.
        
    Returns:
        str: Analysis of the scenario and applicable standards.
    """
    # Use the retriever to get relevant standards for this scenario
    retrieved_nodes = retriever.retrieve(scenario)
    
    # Extract text content from retrieved nodes
    context = "\n\n".join([node.text for node in retrieved_nodes[:7]])
    
    return f"""
Analysis based on AAOIFI standards:

{context}
    """


@tool
def generate_journal_entries(
    transaction_type: str, 
    amount: float, 
    details: Dict[str, Any]
) -> str:
    """
    Generate journal entries for a specific Islamic finance transaction.
    
    Args:
        transaction_type: Type of transaction (e.g., "murabaha", "ijarah", "musharakah")
        amount: The principal amount of the transaction
        details: Additional details specific to the transaction type
        
    Returns:
        str: Journal entries for the transaction
    """
    transaction_type = transaction_type.lower()
    
    # Based on transaction type, generate appropriate journal entries
    if transaction_type == "murabaha":
        # Example Murabaha journal entries
        cost_price = amount
        selling_price = amount + (amount * details.get("profit_rate", 0.05))
        
        return f"""
## Murabaha Journal Entries (FAS 28)

1. **Purchase of Asset by Islamic Bank**
   - Dr. Murabaha Assets: ${cost_price:,.2f}
   - Cr. Cash/Payables: ${cost_price:,.2f}

2. **Sale of Asset to Customer**
   - Dr. Murabaha Receivables: ${selling_price:,.2f}
   - Cr. Murabaha Assets: ${cost_price:,.2f}
   - Cr. Deferred Profit: ${selling_price - cost_price:,.2f}

3. **Collection of Installments** (each period)
   - Dr. Cash/Bank: [Installment Amount]
   - Cr. Murabaha Receivables: [Installment Amount]
   
4. **Recognition of Profit** (each period)
   - Dr. Deferred Profit: [Profit portion for this period]
   - Cr. Income from Murabaha: [Profit portion for this period]
"""
    
    elif transaction_type == "ijarah":
        # Example Ijarah journal entries
        asset_cost = amount
        lease_term = details.get("lease_term", 5)  # years
        rental_amount = (asset_cost / lease_term) * (1 + details.get("profit_rate", 0.05))
        
        return f"""
## Ijarah Journal Entries (FAS 32)

1. **Acquisition of Asset by Islamic Bank**
   - Dr. Ijarah Assets: ${asset_cost:,.2f}
   - Cr. Cash/Payables: ${asset_cost:,.2f}

2. **Recognition of Rental Income** (each period)
   - Dr. Ijarah Rental Receivables: ${rental_amount:,.2f}
   - Cr. Ijarah Revenue: ${rental_amount:,.2f}

3. **Collection of Rental**
   - Dr. Cash/Bank: ${rental_amount:,.2f}
   - Cr. Ijarah Rental Receivables: ${rental_amount:,.2f}

4. **Depreciation of Ijarah Asset** (each period)
   - Dr. Depreciation Expense: ${asset_cost / lease_term:,.2f}
   - Cr. Accumulated Depreciation: ${asset_cost / lease_term:,.2f}
"""
    
    elif transaction_type == "musharakah":
        # Example Musharakah journal entries
        bank_contribution = amount
        partner_contribution = details.get("partner_contribution", amount)
        total_capital = bank_contribution + partner_contribution
        profit_ratio_bank = details.get("profit_ratio_bank", 0.5)  # 50% to bank
        
        return f"""
## Musharakah Journal Entries (FAS 7)

1. **Bank's Capital Contribution**
   - Dr. Musharakah Investment: ${bank_contribution:,.2f}
   - Cr. Cash/Bank: ${bank_contribution:,.2f}

2. **Recognition of Partner's Contribution** (memo entry)
   - Total Musharakah Capital: ${total_capital:,.2f}
   - Bank's Share: {bank_contribution / total_capital * 100:.1f}%
   - Partner's Share: {partner_contribution / total_capital * 100:.1f}%

3. **Recognition of Profit**
   - Dr. Cash/Receivables: [Bank's Share of Profit]
   - Cr. Musharakah Income: [Bank's Share of Profit]
Due from financial institutions
4. **Recognition of Loss** (if applicable)
   - Dr. Provision for Musharakah Losses: [Bank's Share of Loss]
   - Cr. Musharakah Investment: [Bank's Share of Loss]
"""
    
    elif transaction_type == "mudarabah":
        # Example Mudarabah journal entries
        investment_amount = amount
        profit_share_bank = details.get("profit_share_bank", 0.4)  # 40% to bank
        
        return f"""
## Mudarabah Journal Entries (FAS 4)

1. **Investment by Bank (Rab-ul-Mal)**
   - Dr. Mudarabah Investment: ${investment_amount:,.2f}
   - Cr. Cash/Bank: ${investment_amount:,.2f}

2. **Recognition of Profit**
   - Dr. Cash/Receivables: [Bank's Share of Profit]
   - Cr. Mudarabah Income: [Bank's Share of Profit]

3. **Recognition of Loss** (if applicable)
   - Dr. Provision for Mudarabah Losses: [Loss Amount]
   - Cr. Mudarabah Investment: [Loss Amount]

4. **Return of Capital at End of Mudarabah**
   - Dr. Cash/Bank: [Remaining Investment]
   - Cr. Mudarabah Investment: [Remaining Investment]
"""
    
    elif transaction_type == "istisna":
        # Example Istisna'a journal entries
        contract_price = amount
        manufacturing_cost = details.get("manufacturing_cost", amount * 0.8)
        profit = contract_price - manufacturing_cost
        
        return f"""
## Istisna'a Journal Entries (FAS 10)

1. **Execution of Istisna'a Contract**
   - Dr. Istisna'a Receivables: ${contract_price:,.2f}
   - Cr. Istisna'a Revenue: ${contract_price:,.2f}

2. **Recognition of Costs**
   - Dr. Istisna'a Costs: ${manufacturing_cost:,.2f}
   - Cr. Cash/Payables: ${manufacturing_cost:,.2f}

3. **Recognition of Profit**
   - Dr. Work-in-Process: ${profit:,.2f}
   - Cr. Deferred Profit: ${profit:,.2f}

4. **Receipt of Payment**
   - Dr. Cash/Bank: ${contract_price:,.2f}
   - Cr. Istisna'a Receivables: ${contract_price:,.2f}
"""
    
    else:
        return f"Transaction type '{transaction_type}' is not recognized. Supported types: murabaha, ijarah, musharakah, mudarabah, istisna."


@tool
def identify_transaction_type(description: str) -> str:
    """
    Identify the Islamic finance transaction type based on a description.
    
    Args:
        description: Description of the financial transaction or scenario
        
    Returns:
        str: Identified transaction type and applicable AAOIFI standard
    """
    # Use the retriever to identify the transaction type
    retrieved_nodes = retriever.retrieve(description)
    context = "\n\n".join([node.text for node in retrieved_nodes[:5]])
    
    # Simple keyword matching for demo purposes
    # In production, this would be more sophisticated
    transaction_types = {
        "murabaha": {
            "keywords": ["murabaha", "cost plus", "mark-up", "deferred payment sale"],
            "standard": "FAS 28 - Murabaha and Other Deferred Payment Sales"
        },
        "ijarah": {
            "keywords": ["ijarah", "lease", "leasing", "rental"],
            "standard": "FAS 32 - Ijarah"
        },
        "musharakah": {
            "keywords": ["musharakah", "joint venture", "partnership", "equity participation"],
            "standard": "FAS 7 - Musharakah Financing"
        },
        "mudarabah": {
            "keywords": ["mudarabah", "profit sharing", "investment management"],
            "standard": "FAS 4 - Mudarabah Financing"
        },
        "istisna": {
            "keywords": ["istisna", "manufacturing", "construction", "made-to-order"],
            "standard": "FAS 10 - Istisna'a and Parallel Istisna'a"
        }
    }
    
    description_lower = description.lower()
    
    # Check for keyword matches
    matches = []
    for tx_type, info in transaction_types.items():
        for keyword in info["keywords"]:
            if keyword in description_lower:
                matches.append((tx_type, info["standard"]))
                break
    
    if matches:
        result = "Transaction identified as:\n\n"
        for match in matches:
            result += f"- Type: {match[0].capitalize()}\n"
            result += f"- Standard: {match[1]}\n\n"
        return result
    else:
        return "Transaction type could not be clearly identified. Please provide more details about the transaction."


# List of tools available to agents
tools = [
    search_standards,
    get_standard_info,
    analyze_financial_scenario,
    generate_journal_entries,
    identify_transaction_type
]