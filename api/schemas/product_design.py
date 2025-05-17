from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ProductDesignRequest(BaseModel):
    """Schema for the product design request."""
    product_objective: str = Field(..., description="The objective of the financial product")
    risk_appetite: str = Field(..., description="The risk appetite level")
    investment_tenor: str = Field(..., description="The investment tenor")
    target_audience: str = Field(..., description="The target audience for the product")
    asset_focus: Optional[str] = Field(None, description="The asset focus for the product")
    desired_features: List[str] = Field(default_factory=list, description="List of desired features")
    specific_exclusions: List[str] = Field(default_factory=list, description="List of specific exclusions")
    additional_notes: Optional[str] = Field(None, description="Additional requirements or notes")


class ProductDesignResponse(BaseModel):
    """Schema for the product design response."""
    suggested_product_concept_name: str
    recommended_islamic_contracts: List[str]
    original_requirements: Dict[str, Any]
    rationale_for_contract_selection: str
    proposed_product_structure_overview: str
    key_aaoifi_fas_considerations: Dict[str, str]
    shariah_compliance_checkpoints: List[str]
    potential_areas_of_concern: List[str]
    potential_risks_and_mitigation_notes: str
    next_steps_for_detailed_design: List[str]
