import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Ticket
from backend.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

@router.get("", response_model=List[TicketResponse])
def get_all_tickets(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve list of all support and escalation tickets."""
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return tickets

@router.post("", response_model=TicketResponse)
def create_new_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket."""
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    new_ticket = Ticket(
        id=ticket_id,
        customer_id=payload.customer_id,
        customer_name=payload.customer_name or "Customer",
        order_id=payload.order_id,
        title=payload.title,
        description=payload.description,
        intent=payload.intent or "general_faq",
        priority=payload.priority.upper(),
        status=payload.status.upper(),
        assigned_to=payload.assigned_to or "Unassigned",
        ai_recommended_action=payload.ai_recommended_action,
        escalation_reason=payload.escalation_reason,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_record(ticket_id: str, payload: TicketUpdate, db: Session = Depends(get_db)):
    """Update status, assignment, or resolution notes of a ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if payload.status:
        ticket.status = payload.status.upper()
    if payload.priority:
        ticket.priority = payload.priority.upper()
    if payload.assigned_to:
        ticket.assigned_to = payload.assigned_to
    if payload.ai_recommended_action:
        ticket.ai_recommended_action = payload.ai_recommended_action
    if payload.escalation_reason:
        ticket.escalation_reason = payload.escalation_reason

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket
