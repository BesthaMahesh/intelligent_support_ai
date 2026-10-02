from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    order_id: Optional[str] = None
    customer_id: Optional[str] = None
    product: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    payment_status: Optional[str] = None
    shipping_status: Optional[str] = None
    date: Optional[str] = None
    issue: Optional[str] = None
    custom_entities: Dict[str, Any] = Field(default_factory=dict)

class NLPAnalysisResult(BaseModel):
    language: str = "English"
    language_confidence: float = 1.0
    normalized_text: str = ""
    intent: str = "general_faq"
    intent_confidence: float = 1.0
    sentiment: str = "neutral" # positive, neutral, negative, highly_negative
    sentiment_confidence: float = 1.0
    urgency: str = "low" # low, medium, high, critical
    urgency_reason: str = ""
    topic: str = "General"
    entities: EntitySchema = Field(default_factory=EntitySchema)
    pii_detected: bool = False
    redacted_text: str = ""

class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success" # success, error, blocked_by_guardrails
    latency_ms: float = 0.0

class GuardrailEvaluation(BaseModel):
    passed: bool = True
    input_safety_passed: bool = True
    output_grounding_passed: bool = True
    pii_protected: bool = True
    prompt_injection_detected: bool = False
    violations: List[str] = Field(default_factory=list)

class ObservabilityTrace(BaseModel):
    request_id: str
    conversation_id: str
    total_latency_ms: float = 0.0
    nlp_latency_ms: float = 0.0
    retrieval_latency_ms: float = 0.0
    tool_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_inr: float = 0.0
    model_name: str = ""
    prompt_version: str = "v1.0.0"

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = "CUS-8821"
    customer_name: Optional[str] = "Rajesh Kumar"
    message: str
    user_email: Optional[str] = "customer@support.ai"
    channel: Optional[str] = "web_chat"

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    language: str = "English"
    intent: str
    intent_confidence: float
    sentiment: str
    urgency: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    route_taken: str # rag, business_tool, multi_tool, human_escalation
    requires_human: bool = False
    escalation_reason: Optional[str] = None
    ticket_id: Optional[str] = None
    retrieved_sources: List[Dict[str, Any]] = Field(default_factory=list)
    tools_executed: List[ToolCallRecord] = Field(default_factory=list)
    guardrails: GuardrailEvaluation = Field(default_factory=GuardrailEvaluation)
    observability: ObservabilityTrace
