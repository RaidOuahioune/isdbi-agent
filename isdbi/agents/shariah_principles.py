"""
Shariah Principles Knowledge Base

This module defines core Shariah principles and standards-specific guidelines
for validating proposed standard enhancements. This serves as a reference
for the Validator Agent when evaluating compliance.
"""

# Core Islamic finance principles applicable across all standards
CORE_PRINCIPLES = [
    {
        "principle": "Prohibition of Riba (Interest)",
        "description": "Any predetermined, fixed return on capital is prohibited. Financial transactions must not involve interest-based returns.",
        "examples": ["Fixed interest payments", "Compounding of interest", "Late payment penalties that accumulate over time"]
    },
    {
        "principle": "Prohibition of Gharar (Excessive Uncertainty)",
        "description": "Contracts must have clarity in fundamental terms and conditions. Excessive uncertainty in key contract elements is forbidden.",
        "examples": ["Undefined subject matter", "Unknown price", "Uncertain delivery date", "Ambiguous contract terms"]
    },
    {
        "principle": "Prohibition of Maysir (Gambling)",
        "description": "Speculative transactions with no underlying economic activity or asset are prohibited.",
        "examples": ["Pure speculation", "Zero-sum games", "Betting on future prices without actual ownership"]
    },
    {
        "principle": "Asset-Backing",
        "description": "Financial transactions must be linked to real economic activity and tangible assets.",
        "examples": ["Each sukuk must represent ownership in real assets", "Financing must be tied to specific assets", "Credit cannot be pure monetary exchange"]
    },
    {
        "principle": "Risk-Sharing",
        "description": "Profits and losses should be shared according to pre-agreed ratios based on capital contribution and/or effort.",
        "examples": ["Mudarabah profit-sharing", "Musharakah partnership", "Investment risk must be proportionate to potential returns"]
    },
    {
        "principle": "Ethical Investment",
        "description": "Investments must avoid prohibited industries (haram) such as alcohol, gambling, pork, pornography, etc.",
        "examples": ["Screening for haram activities", "Avoiding companies with excessive conventional debt", "Environmental and social governance concerns"]
    },
    {
        "principle": "Transparency and Fairness",
        "description": "All parties must have clear information about the transaction. Exploitation, fraud, and deception are forbidden.",
        "examples": ["Full disclosure of costs", "Clear contract terms", "Informed consent of all parties"]
    }
]

# Standard-specific Shariah principles for FAS 4 (Musharakah and Mudarabah)
FAS_4_PRINCIPLES = [
    {
        "principle": "Capital Recognition",
        "description": "Mudarabah capital must be clearly identifiable and segregated from the entity's own funds. Capital contributions in Musharakah must be properly measured and recognized.",
        "related_clauses": ["Capital measurement", "Entity's own investments", "Capital contributions"]
    },
    {
        "principle": "Loss Attribution",
        "description": "In Mudarabah, financial losses are borne solely by the capital provider (Rab al-Mal), not the manager (Mudarib), unless caused by misconduct or negligence.",
        "related_clauses": ["Loss recognition", "Capital impairment", "Manager's liability"]
    },
    {
        "principle": "Profit Distribution",
        "description": "Profits must be distributed according to pre-agreed ratios, not as a fixed amount or percentage of capital.",
        "related_clauses": ["Profit recognition", "Profit allocation", "Distribution methods"]
    },
    {
        "principle": "Investment Management Separation",
        "description": "A clear distinction must be maintained between the entity's role as manager (Mudarib) and its role as principal in its own investments.",
        "related_clauses": ["Off-balance sheet recognition", "Accounting separation", "Disclosure requirements"]
    }
]

# Standard-specific Shariah principles for FAS 10 (Istisna'a and Parallel Istisna'a)
FAS_10_PRINCIPLES = [
    {
        "principle": "Specification of Subject Matter",
        "description": "The subject matter of Istisna'a must be precisely specified in terms of attributes, specifications, and characteristics.",
        "related_clauses": ["Subject matter definition", "Specifications clarity", "Manufacturing requirements"]
    },
    {
        "principle": "Fixed Price",
        "description": "The contract price in Istisna'a must be fixed and known at contract inception, though payment may be deferred or in installments.",
        "related_clauses": ["Price determination", "Payment terms", "Cost calculations"]
    },
    {
        "principle": "Delivery Terms",
        "description": "The delivery date or period must be specified, though some flexibility is permitted.",
        "related_clauses": ["Delivery specifications", "Timing requirements", "Implementation timeline"]
    },
    {
        "principle": "Parallel Istisna'a Independence",
        "description": "In parallel Istisna'a, each contract must be independent of the other, with no contingency between them.",
        "related_clauses": ["Contract independence", "Risk management", "Sub-contracting provisions"]
    },
    {
        "principle": "Liability and Risk",
        "description": "The manufacturer (sani') bears liability for defects and non-conformity to specifications until delivery.",
        "related_clauses": ["Risk transfer", "Liability recognition", "Quality assurance"]
    }
]

# Standard-specific Shariah principles for FAS 32 (Ijarah and Ijarah Muntahia Bittamleek)
FAS_32_PRINCIPLES = [
    {
        "principle": "Ownership Risk",
        "description": "The lessor must bear the ownership risks of the leased asset, including maintenance of the asset's usability.",
        "related_clauses": ["Risk distribution", "Maintenance obligations", "Insurance requirements"]
    },
    {
        "principle": "Identifiable Usufruct",
        "description": "The usufruct (benefit) of the leased asset must be clearly identifiable and transferable to the lessee.",
        "related_clauses": ["Asset identification", "Usufruct definition", "Lease terms"]
    },
    {
        "principle": "Rental Determination",
        "description": "Rental payments must be clearly specified for the entire lease term, though variable rentals based on a clear benchmark are permitted.",
        "related_clauses": ["Rent calculation", "Payment terms", "Variable components"]
    },
    {
        "principle": "Transfer of Ownership",
        "description": "In Ijarah Muntahia Bittamleek, the transfer of ownership must be executed through a separate contract (gift, sale, etc.) after the Ijarah is completed.",
        "related_clauses": ["Ownership transfer", "Gift contract", "Sale agreement", "Option to purchase"]
    },
    {
        "principle": "Lease Term and Asset Life",
        "description": "The lease term must be reasonable in relation to the useful life of the asset.",
        "related_clauses": ["Term specifications", "Asset depreciation", "Useful life calculations"]
    }
]

# Mapping standard IDs to their specific principles
STANDARD_PRINCIPLES = {
    "4": FAS_4_PRINCIPLES,
    "10": FAS_10_PRINCIPLES,
    "32": FAS_32_PRINCIPLES,
    # Add others as needed
}

def get_principles_for_standard(standard_id: str) -> list:
    """
    Get both core principles and standard-specific principles for a given standard.
    
    Args:
        standard_id: The ID of the standard (e.g., "4" for FAS 4)
        
    Returns:
        List of principles applicable to the standard
    """
    principles = CORE_PRINCIPLES.copy()
    
    if standard_id in STANDARD_PRINCIPLES:
        principles.extend(STANDARD_PRINCIPLES[standard_id])
        
    return principles

def format_principles_for_validation(standard_id: str) -> str:
    """
    Format principles as a string for use in validation prompts.
    
    Args:
        standard_id: The ID of the standard (e.g., "4" for FAS 4)
        
    Returns:
        Formatted string with relevant principles
    """
    principles = get_principles_for_standard(standard_id)
    
    formatted = "# SHARIAH PRINCIPLES FOR VALIDATION\n\n"
    formatted += "## Core Islamic Finance Principles\n"
    
    for i, principle in enumerate(CORE_PRINCIPLES, 1):
        formatted += f"{i}. {principle['principle']}: {principle['description']}\n"
    
    if standard_id in STANDARD_PRINCIPLES:
        formatted += f"\n## FAS {standard_id} Specific Principles\n"
        for i, principle in enumerate(STANDARD_PRINCIPLES[standard_id], 1):
            formatted += f"{i}. {principle['principle']}: {principle['description']}\n"
    
    return formatted 