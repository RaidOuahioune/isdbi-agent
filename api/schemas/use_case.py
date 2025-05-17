from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class UseCaseRequest(BaseModel):
    """Request schema for use case processing."""
    
    scenario: str = Field(..., description="The financial scenario to analyze")
    standards_info: Optional[Dict[str, Any]] = Field(
        None, description="Optional standards information to include as context"
    )


class UseCaseResponse(BaseModel):
    """Response schema for use case processing."""
    
    scenario: str = Field(..., description="The original financial scenario")
    accounting_guidance: str = Field(..., description="The verified accounting guidance")




class TransactionRequest(BaseModel):
    """Request schema for transaction analysis."""
    
    transaction_details: str = Field(..., description="Details of the transaction to analyze")
    additional_context: Optional[str] = Field(None, description="Additional context for analysis")


class TransactionResponse(BaseModel):
    """Response schema for transaction analysis."""
    
    analysis: str = Field(..., description="Analysis of the transaction")
    compliant: bool = Field(..., description="Whether the transaction is compliant")
    rationale: Optional[str] = Field(None, description="Rationale for the compliance assessment")
