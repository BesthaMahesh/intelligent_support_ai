from typing import TypedDict, List, Dict, Any, Optional
from backend.schemas.chat import NLPAnalysisResult, ToolCallRecord, GuardrailEvaluation, ObservabilityTrace

class AgentState(TypedDict):
    request_id: str
    conversation_id: str
    customer_id: str
    customer_name: str
    user_email: str
    message: str
    sanitized_message: str
    
    # NLP Classifications
    language: str
    language_confidence: float
    intent: str
    intent_confidence: float
    sentiment: str
    urgency: str
    urgency_reason: str
    topic: str
    entities: Dict[str, Any]
    
    # Routing & Flow
    route_taken: str # rag, business_tool, multi_tool, human_escalation
    required_agents: List[str]
    
    # Context & Tools
    retrieved_context: str
    retrieved_sources: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    tools_executed: List[ToolCallRecord]
    
    # Business Rules & Decision
    business_rule_result: Dict[str, Any]
    requires_human: bool
    escalation_reason: Optional[str]
    ticket_id: Optional[str]
    
    # Output & Observability
    response: str
    guardrails: Dict[str, Any]
    observability: Dict[str, Any]
    audit: Dict[str, Any]
