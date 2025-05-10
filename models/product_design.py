"""
Data models for the Financial Product Design feature.

This module contains the structured models for product design requests,
Islamic contracts, and compliance assessments.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ProductRequirements(BaseModel):
    """Input requirements for designing a financial product."""
    
    product_objective: str
    risk_appetite: str  # Low, Medium, High
    investment_tenor: str  # Short-term, Medium-term, Long-term
    target_audience: str  # Retail, Corporate, HNWI, etc.
    asset_focus: Optional[str] = None  # Real estate, Commodities, etc.
    desired_features: List[str] = []
    specific_exclusions: List[str] = []
    additional_notes: Optional[str] = None


class ProductStructure(BaseModel):
    """Structure of the designed financial product."""
    
    parties_and_roles: str
    flow_of_funds: str
    profit_loss_mechanism: str
    ownership_structure: str


class StandardsConsideration(BaseModel):
    """AAOIFI standards considerations for a financial product."""
    
    standard_id: str
    key_requirements: str
    accounting_implications: str
    disclosure_requirements: str


class ComplianceAssessment(BaseModel):
    """Shariah compliance assessment for a financial product."""
    
    compliance_checkpoints: List[str]
    potential_concerns: List[str]
    risk_mitigation: str
    next_steps: List[str]
    relevant_standards: List[str]


class ProductDesign(BaseModel):
    """Complete financial product design output."""
    
    suggested_product_concept_name: str
    recommended_islamic_contracts: List[str]
    rationale_for_contract_selection: str
    proposed_product_structure_overview: str
    key_aaoifi_fas_considerations: Dict[str, Any]
    shariah_compliance_checkpoints: List[str]
    potential_areas_of_concern: List[str]
    potential_risks_and_mitigation_notes: str
    next_steps_for_detailed_design: List[str]
    original_requirements: ProductRequirements


# Contract information definitions
ISLAMIC_CONTRACTS = {
    "Mudarabah": {
        "description": "A partnership where one party provides capital and the other provides expertise/management.",
        "risk_profile": "Medium to High",
        "suitable_for": ["Investment products", "Fund management", "Project financing"],
        "primary_standard": "FAS 4"
    },
    "Musharakah": {
        "description": "A partnership where all parties contribute capital and share profits/losses based on agreed ratios.",
        "risk_profile": "Medium to High",
        "suitable_for": ["Joint ventures", "Real estate development", "Business financing"],
        "primary_standard": "FAS 4"
    },
    "Diminishing Musharakah": {
        "description": "A form of partnership where one partner's share diminishes over time as the other partner gradually purchases it.",
        "risk_profile": "Medium",
        "suitable_for": ["Home financing", "Equipment financing", "Business acquisition"],
        "primary_standard": "FAS 4"
    },
    "Ijarah": {
        "description": "A lease agreement where the lessor retains ownership of the asset while the lessee has the right to use it.",
        "risk_profile": "Low to Medium",
        "suitable_for": ["Equipment leasing", "Vehicle financing", "Property rental"],
        "primary_standard": "FAS 32"
    },
    "Ijarah Muntahia Bittamleek": {
        "description": "A lease ending with ownership, where the asset is transferred to the lessee at the end of the lease term.",
        "risk_profile": "Low to Medium",
        "suitable_for": ["Home financing", "Auto financing", "Equipment financing"],
        "primary_standard": "FAS 32"
    },
    "Murabaha": {
        "description": "A cost-plus sale where the seller discloses the cost and profit margin to the buyer.",
        "risk_profile": "Low",
        "suitable_for": ["Trade financing", "Asset acquisition", "Working capital"],
        "primary_standard": "FAS 28"
    },
    "Istisna'a": {
        "description": "A manufacturing contract where one party agrees to produce a specific item for the other.",
        "risk_profile": "Medium",
        "suitable_for": ["Construction financing", "Manufacturing", "Infrastructure projects"],
        "primary_standard": "FAS 10"
    },
    "Parallel Istisna'a": {
        "description": "Two Istisna'a contracts where an institution acts as buyer in one and seller in another.",
        "risk_profile": "Medium",
        "suitable_for": ["Construction financing", "Project financing", "Manufacturing"],
        "primary_standard": "FAS 10"
    },
    "Salam": {
        "description": "An advance purchase agreement where payment is made upfront for future delivery of goods.",
        "risk_profile": "Medium to High",
        "suitable_for": ["Agricultural financing", "Commodity trading", "Manufacturing inputs"],
        "primary_standard": "FAS 7"
    },
    "Parallel Salam": {
        "description": "Two Salam contracts where an institution acts as buyer in one and seller in another.",
        "risk_profile": "Medium",
        "suitable_for": ["Agricultural financing", "Commodity trading", "Liquidity management"],
        "primary_standard": "FAS 7"
    },
    "Wakalah": {
        "description": "An agency arrangement where one party acts on behalf of another for a fee.",
        "risk_profile": "Varies (depends on underlying arrangement)",
        "suitable_for": ["Investment management", "Fund administration", "Payment services"],
        "primary_standard": "Multiple (depends on application)"
    },
    "Sukuk": {
        "description": "Islamic certificates representing ownership in an underlying asset, usufruct, or project.",
        "risk_profile": "Varies based on underlying structure",
        "suitable_for": ["Capital raising", "Infrastructure financing", "Government funding"],
        "primary_standard": "Multiple (depends on underlying structure)"
    }
}

# Feature options for product design
PRODUCT_FEATURE_OPTIONS = [
    "Asset-backed",
    "Profit-sharing",
    "Fixed periodic payments",
    "Tradable/Securitizable",
    "Capital protection features",
    "Early termination option",
    "Staged funding",
    "Collateralized"
]

# Risk appetite levels
RISK_APPETITE_LEVELS = ["Low", "Medium", "High"]

# Investment tenor options
INVESTMENT_TENOR_OPTIONS = [
    "Short-term (up to 1 year)",
    "Medium-term (1-5 years)",
    "Long-term (5+ years)"
]

# Target audience options
TARGET_AUDIENCE_OPTIONS = [
    "Retail investors",
    "High Net Worth Individuals",
    "Corporates",
    "SMEs",
    "Financial institutions",
    "Government entities"
]

# Asset focus options
ASSET_FOCUS_OPTIONS = [
    "No specific preference",
    "Real estate",
    "Commodities",
    "Equity",
    "Trade receivables",
    "Infrastructure",
    "Vehicles/Equipment",
    "Technology"
]

# Contract to standard mapping
CONTRACT_TO_STANDARDS = {
    "Mudarabah": ["4"],
    "Musharakah": ["4"],
    "Diminishing Musharakah": ["4"],
    "Ijarah": ["32"],
    "Ijarah Muntahia Bittamleek": ["32"],
    "Murabaha": ["28"],
    "Istisna'a": ["10"],
    "Parallel Istisna'a": ["10"],
    "Salam": ["7"],
    "Parallel Salam": ["7"],
    "Wakalah": ["4", "32"],
    "Sukuk": ["32", "4", "10"]
} 