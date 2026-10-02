from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    language: str = "English"
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    guardrails_passed: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    intent: str
    sentiment: str
    urgency: str
    status: str
    channel: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
