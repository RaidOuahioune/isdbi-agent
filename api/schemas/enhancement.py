from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class EnhancementRequest(BaseModel):
    """Request schema for standards enhancement."""
    
    standard_id: str = Field(..., description="The ID of the standard to enhance (e.g., '10' for FAS 10)")
    trigger_scenario: str = Field(..., description="The scenario that triggers the need for enhancement")
    include_cross_standard_analysis: bool = Field(True, description="Whether to include cross-standard impact analysis")


class EnhancementResponse(BaseModel):
    """Response schema for standards enhancement."""
    
    standard_id: str = Field(..., description="The ID of the enhanced standard")
    trigger_scenario: str = Field(..., description="The scenario that triggered the enhancement")
    review: str = Field(..., description="Review analysis of the standard")
    proposal: str = Field(..., description="Enhancement proposal")
    validation: str = Field(..., description="Validation results")
    original_text: Optional[str] = Field(None, description="Original text from the standard")
    proposed_text: Optional[str] = Field(None, description="Proposed enhanced text")
    cross_standard_analysis: Optional[str] = Field(None, description="Cross-standard impact analysis")
    compatibility_matrix: Optional[Dict[str, Any]] = Field(None, description="Compatibility matrix with other standards")