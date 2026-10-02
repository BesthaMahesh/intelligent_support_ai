import uuid
from typing import Dict, Any
from backend.schemas.chat import ObservabilityTrace

def initialize_trace(conversation_id: str, request_id: str = None) -> ObservabilityTrace:
    """Initialize a new observability execution trace."""
    return ObservabilityTrace(
        request_id=request_id or f"REQ-{uuid.uuid4().hex[:8].upper()}",
        conversation_id=conversation_id
    )

def finalize_trace(
    trace: ObservabilityTrace,
    nlp_latency: float = 0.0,
    retrieval_latency: float = 0.0,
    tool_latency: float = 0.0,
    llm_latency: float = 0.0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_inr: float = 0.0,
    model_name: str = "",
    prompt_version: str = "v1.2.0"
) -> ObservabilityTrace:
    """Compile final latencies and token/cost metrics."""
    total_latency = round(nlp_latency + retrieval_latency + tool_latency + llm_latency, 2)
    
    trace.nlp_latency_ms = nlp_latency
    trace.retrieval_latency_ms = retrieval_latency
    trace.tool_latency_ms = tool_latency
    trace.llm_latency_ms = llm_latency
    trace.total_latency_ms = total_latency
    trace.input_tokens = input_tokens
    trace.output_tokens = output_tokens
    trace.total_tokens = input_tokens + output_tokens
    trace.estimated_cost_inr = cost_inr
    trace.model_name = model_name
    trace.prompt_version = prompt_version
    
    return trace
