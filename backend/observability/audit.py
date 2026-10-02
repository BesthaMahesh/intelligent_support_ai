import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database.database import SessionLocal
from backend.database.models import AuditLog

def record_audit_log(
    request_id: str,
    conversation_id: str,
    user_email: str,
    input_text: str,
    classification: Dict[str, Any],
    retrieved_docs: List[Dict[str, Any]],
    tools_executed: List[Dict[str, Any]],
    tool_results: Dict[str, Any],
    model: str,
    prompt_version: str,
    guardrails: Dict[str, Any],
    final_response: str,
    latency_ms: float,
    token_usage: Dict[str, Any],
    cost_inr: float
) -> str:
    """
    Persist immutable audit record for enterprise compliance.
    """
    log_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
    
    db = SessionLocal()
    try:
        audit_entry = AuditLog(
            id=log_id,
            request_id=request_id,
            conversation_id=conversation_id,
            user_email=user_email,
            action="support_interaction",
            input_text=input_text,
            classification_json=json.dumps(classification),
            retrieved_docs_json=json.dumps(retrieved_docs),
            tool_calls_json=json.dumps(tools_executed),
            tool_results_json=json.dumps(tool_results),
            model=model,
            prompt_version=prompt_version,
            guardrail_results_json=json.dumps(guardrails),
            final_response=final_response,
            latency_ms=latency_ms,
            token_usage_json=json.dumps(token_usage),
            cost_inr=cost_inr,
            created_at=datetime.utcnow()
        )
        db.add(audit_entry)
        db.commit()
        return log_id
    finally:
        db.close()

def get_audit_trail_for_conversation(conversation_id: str) -> List[Dict[str, Any]]:
    """Retrieve audit trail logs for a conversation."""
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).filter(AuditLog.conversation_id == conversation_id).order_by(AuditLog.created_at.desc()).all()
        return [
            {
                "id": l.id,
                "request_id": l.request_id,
                "conversation_id": l.conversation_id,
                "user_email": l.user_email,
                "action": l.action,
                "input_text": l.input_text,
                "classification": json.loads(l.classification_json) if l.classification_json else {},
                "retrieved_docs": json.loads(l.retrieved_docs_json) if l.retrieved_docs_json else [],
                "tool_calls": json.loads(l.tool_calls_json) if l.tool_calls_json else [],
                "tool_results": json.loads(l.tool_results_json) if l.tool_results_json else {},
                "model": l.model,
                "prompt_version": l.prompt_version,
                "guardrail_results": json.loads(l.guardrail_results_json) if l.guardrail_results_json else {},
                "final_response": l.final_response,
                "latency_ms": l.latency_ms,
                "token_usage": json.loads(l.token_usage_json) if l.token_usage_json else {},
                "cost_inr": l.cost_inr,
                "created_at": l.created_at.isoformat() if l.created_at else ""
            }
            for l in logs
        ]
    finally:
        db.close()
