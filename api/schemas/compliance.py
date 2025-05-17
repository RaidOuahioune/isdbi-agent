from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ComplianceVerificationRequest(BaseModel):
    """Schema for the compliance verification request."""
    document_content: str = Field(..., description="The content of the financial report to verify")
    document_name: str = Field("Uploaded Document", description="The name of the document")


class ComplianceCheckpoint(BaseModel):
    """Schema for a compliance checkpoint in the structured report."""
    standard: str
    requirement: str
    status: str
    status_code: str
    comments: str


class ComplianceVerificationResponse(BaseModel):
    """Schema for the compliance verification response."""
    document_name: str
    timestamp: str
    compliance_report: str
    structured_report: List[ComplianceCheckpoint]
    document: str
