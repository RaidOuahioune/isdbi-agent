from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..schemas.product_design import ProductDesignRequest, ProductDesignResponse
from ..services.product_design_service import ProductDesignService

# Create router
router = APIRouter(prefix="/product-design", tags=["Financial Product Design"])


@router.post("", )
async def design_financial_product(request: ProductDesignRequest) -> Dict[str, Any]:
    """
    Design a Shariah-compliant financial product based on specified requirements.
    
    This endpoint processes product requirements and returns a comprehensive
    financial product concept with Islamic contract structures, AAOIFI standards
    considerations, and Shariah compliance checkpoints.
    """
    try:
        # Convert Pydantic model to dict
        request_data = request.dict()
        
        # Remove None values
        request_data = {k: v for k, v in request_data.items() if v is not None}
        
        result = ProductDesignService.design_financial_product(request_data)
        print(result.keys(),)
        print([type(value) for value in result.values()])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
