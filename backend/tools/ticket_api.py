import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database.database import SessionLocal
from backend.database.models import Ticket

def create_escalation_ticket(
    customer_id: str = "CUS-8821",
    customer_name: str = "Rajesh Kumar",
    order_id: Optional[str] = None,
    title: str = "Customer Support Escalation",
    description: str = "",
    intent: str = "general_faq",
    priority: str = "HIGH",
    ai_recommended_action: Optional[str] = None,
    escalation_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a verified support escalation ticket with audit traceability.
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    
    db = SessionLocal()
    try:
        new_ticket = Ticket(
            id=ticket_id,
            customer_id=customer_id,
            customer_name=customer_name,
            order_id=order_id,
            title=title,
            description=description,
            intent=intent,
            priority=priority.upper(),
            status="OPEN",
            assigned_to="Tier-2 Support Queue",
            ai_recommended_action=ai_recommended_action,
            escalation_reason=escalation_reason,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        return {
            "ticket_id": new_ticket.id,
            "status": new_ticket.status,
            "priority": new_ticket.priority,
            "customer_id": new_ticket.customer_id,
            "order_id": new_ticket.order_id,
            "created_at": new_ticket.created_at.isoformat(),
            "ai_recommended_action": new_ticket.ai_recommended_action,
            "escalation_reason": new_ticket.escalation_reason
        }
    finally:
        db.close()

def list_all_tickets() -> List[Dict[str, Any]]:
    """Retrieve all tickets from the database."""
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "customer_id": t.customer_id,
                "customer_name": t.customer_name,
                "order_id": t.order_id,
                "title": t.title,
                "description": t.description,
                "intent": t.intent,
                "priority": t.priority,
                "status": t.status,
                "assigned_to": t.assigned_to,
                "ai_recommended_action": t.ai_recommended_action,
                "escalation_reason": t.escalation_reason,
                "created_at": t.created_at.isoformat() if t.created_at else "",
                "updated_at": t.updated_at.isoformat() if t.updated_at else ""
            }
            for t in tickets
        ]
    finally:
        db.close()
