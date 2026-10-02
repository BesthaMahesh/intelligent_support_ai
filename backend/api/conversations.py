import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Conversation, Message
from backend.schemas.conversation import ConversationResponse, MessageResponse

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationResponse])
def get_all_conversations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all active and historical support conversations."""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    results = []
    for c in conversations:
        msgs = []
        for m in c.messages:
            msgs.append(MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender=m.sender,
                content=m.content,
                language=m.language or "English",
                intent=m.intent,
                sentiment=m.sentiment,
                entities=json.loads(m.entities_json) if m.entities_json else {},
                tool_calls=json.loads(m.tool_calls_json) if m.tool_calls_json else [],
                guardrails_passed=m.guardrails_passed,
                created_at=m.created_at
            ))
        results.append(ConversationResponse(
            id=c.id,
            customer_id=c.customer_id,
            customer_name=c.customer_name,
            intent=c.intent,
            sentiment=c.sentiment,
            urgency=c.urgency,
            status=c.status,
            channel=c.channel,
            created_at=c.created_at,
            updated_at=c.updated_at,
            messages=msgs
        ))
    return results

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_by_id(conversation_id: str, db: Session = Depends(get_db)):
    """Retrieve details and full message history for a specific conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    msgs = []
    for m in conv.messages:
        msgs.append(MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            sender=m.sender,
            content=m.content,
            language=m.language or "English",
            intent=m.intent,
            sentiment=m.sentiment,
            entities=json.loads(m.entities_json) if m.entities_json else {},
            tool_calls=json.loads(m.tool_calls_json) if m.tool_calls_json else [],
            guardrails_passed=m.guardrails_passed,
            created_at=m.created_at
        ))
    return ConversationResponse(
        id=conv.id,
        customer_id=conv.customer_id,
        customer_name=conv.customer_name,
        intent=conv.intent,
        sentiment=conv.sentiment,
        urgency=conv.urgency,
        status=conv.status,
        channel=conv.channel,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=msgs
    )

@router.patch("/{conversation_id}/status")
def update_conversation_status(conversation_id: str, status: str, db: Session = Depends(get_db)):
    """Update status of a conversation (active, escalated, resolved, closed)."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.status = status
    db.commit()
    return {"id": conv.id, "status": conv.status}
