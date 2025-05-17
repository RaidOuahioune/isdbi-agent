from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..schemas.compliance import ComplianceVerificationRequest, ComplianceVerificationResponse
from ..services.compliance_service import ComplianceService

# Create router
router = APIRouter(prefix="/compliance", tags=["Compliance Verification"])


@router.post("/verify", response_model=ComplianceVerificationResponse)
async def verify_document_compliance(request: ComplianceVerificationRequest) -> Dict[str, Any]:
    """
    Verify compliance of a financial report with AAOIFI standards.
    
    This endpoint processes a document's content and verifies its compliance with
    AAOIFI standards, returning a detailed compliance report with structured 
    verification results.
    """
    try:
        result = ComplianceService.verify_document_compliance(
            document_content=request.document_content,
            document_name=request.document_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
