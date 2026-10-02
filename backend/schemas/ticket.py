from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TicketCreate(BaseModel):
    customer_id: str
    customer_name: Optional[str] = "Customer"
    order_id: Optional[str] = None
    title: str
    description: str
    intent: Optional[str] = "general_faq"
    priority: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "OPEN"
    assigned_to: Optional[str] = "Unassigned"
    ai_recommended_action: Optional[str] = None
    escalation_reason: Optional[str] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    ai_recommended_action: Optional[str] = None
    escalation_reason: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    order_id: Optional[str] = None
    title: str
    description: str
    intent: str
    priority: str
    status: str
    assigned_to: str
    ai_recommended_action: Optional[str] = None
    escalation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
