from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class MessageRequest(BaseModel):
    """Generic message request for chat-based agents."""
    
    messages: List[Dict[str, Any]] = Field(..., description="Chat messages")
    state: Optional[Dict[str, Any]] = Field({}, description="Current chat state")


class MessageResponse(BaseModel):
    """Generic message response for chat-based agents."""
    
    messages: List[Dict[str, Any]] = Field(..., description="Updated messages")
    state: Optional[Dict[str, Any]] = Field({}, description="Updated state")
