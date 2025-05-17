from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from ..schemas.use_case import (
    UseCaseRequest, 
    UseCaseResponse, 
   
)
from ..services.use_case_service import UseCaseService, StandardsService

# Create router
router = APIRouter(prefix="/use-case", tags=["Use Cases"])


@router.post("/process", response_model=UseCaseResponse)
async def process_use_case(request: UseCaseRequest) -> Dict[str, Any]:


    # dummy data for testing
    #return {
    #        "scenario": 'Financial transaction involving a sale of goods', 
    #        "accounting_guidance": 'The transaction should be recorded as a sale in the financial statements, recognizing revenue at the point of sale. The cost of goods sold should also be recognized at this time, impacting the income statement. Any applicable taxes should be calculated and recorded accordingly.'
    #    }
    #"""Process a financial use case and provide accounting guidance."""
    try:
        result = UseCaseService.process_use_case(
            scenario=request.scenario,
            standards_info=request.standards_info
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

