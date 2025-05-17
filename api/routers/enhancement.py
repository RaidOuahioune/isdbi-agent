from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from ..schemas.enhancement import EnhancementRequest, EnhancementResponse
from ..services.enhancement_service import EnhancementService

# Create router
router = APIRouter(prefix="/enhancement", tags=["Standards Enhancement"])


@router.post("/standards", response_model=EnhancementResponse)
async def enhance_standards(request: EnhancementRequest) -> Dict[str, Any]:
    """
    Generate standards enhancement proposals based on a trigger scenario.
    
    This endpoint processes a trigger scenario for a specific standard and
    returns enhancement proposals, validation results, and optional
    cross-standard impact analysis.
    """
    try:
        result = EnhancementService.run_standards_enhancement(
            standard_id=request.standard_id,
            trigger_scenario=request.trigger_scenario,
            include_cross_standard_analysis=request.include_cross_standard_analysis
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))