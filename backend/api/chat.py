import uuid
import time
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Conversation, Message
from backend.schemas.chat import (
    ChatRequest, ChatResponse, NLPAnalysisResult,
    ObservabilityTrace, GuardrailEvaluation, ToolCallRecord
)
from backend.graph.workflow import support_graph
from backend.observability.tracing import initialize_trace, finalize_trace
from backend.observability.audit import record_audit_log

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def process_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Primary Enterprise Support Chat Endpoint.
    Executes complete pipeline: Input Gateway -> NLP -> Router -> Agents/RAG/Tools -> Guardrails -> Audit.
    """
    request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    start_total_time = time.time()
    
    # 1. Manage Conversation Record
    conv_id = request.conversation_id
    cust_id = request.customer_id or "CUS-8821"
    cust_name = request.customer_name or "Valued Customer"
    conversation = None
    if conv_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.customer_id == cust_id
        ).first()
    
    if not conversation:
        # Check if requested conv_id is already taken by another user; if so or if none provided, generate a unique one
        if not conv_id or db.query(Conversation).filter(Conversation.id == conv_id).first():
            conv_id = f"CONV-{uuid.uuid4().hex[:6].upper()}"
        conversation = Conversation(
            id=conv_id,
            customer_id=cust_id,
            customer_name=cust_name,
            intent="general_faq",
            sentiment="neutral",
            urgency="low",
            status="active",
            channel=request.channel or "web_chat",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Record Customer Message in DB
    customer_msg = Message(
        id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
        conversation_id=conversation.id,
        sender="customer",
        content=request.message,
        language="English",
        created_at=datetime.utcnow()
    )
    db.add(customer_msg)
    db.commit()

    # 3. Build LangGraph Initial State
    initial_state = {
        "request_id": request_id,
        "conversation_id": conversation.id,
        "customer_id": conversation.customer_id,
        "customer_name": conversation.customer_name,
        "user_email": request.user_email or "customer@support.ai",
        "message": request.message,
        "sanitized_message": request.message,
        "tool_results": {},
        "tools_executed": [],
        "retrieved_context": "",
        "retrieved_sources": [],
        "entities": {},
        "requires_human": False,
        "escalation_reason": None,
        "ticket_id": None,
        "response": "",
        "guardrails": {},
        "observability": {},
        "audit": {}
    }

    # 4. Invoke Multi-Agent StateGraph Workflow
    try:
        final_state = support_graph.invoke(initial_state)
    except Exception as e:
        print(f"Error in support graph execution: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    # 5. Extract results
    nlp_latency = final_state.get("nlp_latency_ms", 10.0)
    retrieval_latency = final_state.get("retrieval_latency_ms", 15.0)
    tool_latency = final_state.get("tool_latency_ms", 20.0)
    llm_latency = final_state.get("llm_latency_ms", 250.0)
    in_tokens = final_state.get("input_tokens", 150)
    out_tokens = final_state.get("output_tokens", 80)
    cost_inr = final_state.get("cost_inr", 0.04)
    model_name = final_state.get("model_name", "llama-3.3-70b-versatile")
    prompt_version = final_state.get("prompt_version", "v1.2.0")

    trace = initialize_trace(conversation.id, request_id)
    trace = finalize_trace(
        trace=trace,
        nlp_latency=nlp_latency,
        retrieval_latency=retrieval_latency,
        tool_latency=tool_latency,
        llm_latency=llm_latency,
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        cost_inr=cost_inr,
        model_name=model_name,
        prompt_version=prompt_version
    )

    # 6. Update Conversation Record
    conversation.intent = final_state.get("intent", "general_faq")
    conversation.sentiment = final_state.get("sentiment", "neutral")
    conversation.urgency = final_state.get("urgency", "low")
    if final_state.get("requires_human"):
        conversation.status = "escalated"
    conversation.updated_at = datetime.utcnow()
    db.commit()

    # 7. Record AI Message in DB
    tool_records = []
    for t in final_state.get("tools_executed", []):
        if hasattr(t, "dict"):
            tool_records.append(t.dict())
        elif isinstance(t, dict):
            tool_records.append(t)

    ai_msg = Message(
        id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
        conversation_id=conversation.id,
        sender="ai",
        content=final_state.get("response", ""),
        language=final_state.get("language", "English"),
        intent=final_state.get("intent"),
        sentiment=final_state.get("sentiment"),
        entities_json=json.dumps(final_state.get("entities", {})),
        tool_calls_json=json.dumps(tool_records),
        guardrails_passed=final_state.get("guardrails", {}).get("output_passed", True),
        created_at=datetime.utcnow()
    )
    db.add(ai_msg)
    db.commit()

    # 8. Record Audit Trail
    classification_payload = {
        "language": final_state.get("language"),
        "intent": final_state.get("intent"),
        "sentiment": final_state.get("sentiment"),
        "urgency": final_state.get("urgency"),
        "entities": final_state.get("entities")
    }
    
    record_audit_log(
        request_id=request_id,
        conversation_id=conversation.id,
        user_email=request.user_email or "customer@support.ai",
        input_text=request.message,
        classification=classification_payload,
        retrieved_docs=final_state.get("retrieved_sources", []),
        tools_executed=tool_records,
        tool_results=final_state.get("tool_results", {}),
        model=model_name,
        prompt_version=prompt_version,
        guardrails=final_state.get("guardrails", {}),
        final_response=final_state.get("response", ""),
        latency_ms=trace.total_latency_ms,
        token_usage={"input_tokens": in_tokens, "output_tokens": out_tokens, "total_tokens": in_tokens + out_tokens},
        cost_inr=cost_inr
    )

    # 9. Format response
    guardrails_eval = GuardrailEvaluation(
        passed=final_state.get("guardrails", {}).get("output_passed", True),
        input_safety_passed=final_state.get("guardrails", {}).get("input_passed", True),
        output_grounding_passed=final_state.get("guardrails", {}).get("grounding_passed", True),
        pii_protected=True,
        prompt_injection_detected=final_state.get("guardrails", {}).get("prompt_injection_detected", False),
        violations=final_state.get("guardrails", {}).get("input_violations", []) + final_state.get("guardrails", {}).get("output_violations", [])
    )

    tools_formatted = []
    for tr in tool_records:
        tools_formatted.append(ToolCallRecord(
            tool_name=tr.get("tool_name", "unknown_tool"),
            arguments=tr.get("arguments", {}),
            result=tr.get("result", {}),
            status=tr.get("status", "success"),
            latency_ms=tr.get("latency_ms", 0.0)
        ))

    return ChatResponse(
        conversation_id=conversation.id,
        response=final_state.get("response", ""),
        language=final_state.get("language", "English"),
        intent=final_state.get("intent", "general_faq"),
        intent_confidence=final_state.get("intent_confidence", 1.0),
        sentiment=final_state.get("sentiment", "neutral"),
        urgency=final_state.get("urgency", "low"),
        entities=final_state.get("entities", {}),
        route_taken=final_state.get("route_taken", "rag"),
        requires_human=final_state.get("requires_human", False),
        escalation_reason=final_state.get("escalation_reason"),
        ticket_id=final_state.get("ticket_id"),
        retrieved_sources=final_state.get("retrieved_sources", []),
        tools_executed=tools_formatted,
        guardrails=guardrails_eval,
        observability=trace
    )
