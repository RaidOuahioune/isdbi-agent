from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from ui.utils.transaction_utils import analyze_transaction

from ..schemas.use_case import TransactionRequest, TransactionResponse
from ..services.transaction_service import TransactionService
# Import the service with its class
from ..services.transaction_analyzer_service import transaction_analyzer

# Create router
router = APIRouter(prefix="/transaction", tags=["Transactions"])


@router.post("/analyze", response_model=TransactionResponse)
async def analyze_transaction_handler(request: TransactionRequest) -> Dict[str, Any]:
    """Analyze a financial transaction and determine compliance."""
    try:
        result = analyze_transaction(
            transaction_details=request.transaction_details,
            use_api=False
          
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



