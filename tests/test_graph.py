import pytest
from backend.graph.workflow import support_graph

def test_full_graph_faq():
    initial_state = {
        "request_id": "TEST-REQ-01",
        "conversation_id": "TEST-CONV-01",
        "customer_id": "CUS-8821",
        "customer_name": "Rajesh Kumar",
        "user_email": "test@support.ai",
        "message": "What is your return policy for electronics?",
        "sanitized_message": "What is your return policy for electronics?",
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

    result = support_graph.invoke(initial_state)
    assert result is not None
    assert result["route_taken"] in ["rag", "business_tool"]
    assert len(result["response"]) > 0

def test_full_graph_complex_scenario():
    complex_msg = "I ordered a laptop three days ago and paid ₹72,999. The payment was successful but the order hasn't shipped. I contacted support yesterday and nobody helped me. Order ID ORD-91245."
    initial_state = {
        "request_id": "TEST-REQ-02",
        "conversation_id": "TEST-CONV-02",
        "customer_id": "CUS-8821",
        "customer_name": "Rajesh Kumar",
        "user_email": "test@support.ai",
        "message": complex_msg,
        "sanitized_message": complex_msg,
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

    result = support_graph.invoke(initial_state)
    assert result is not None
    assert result["requires_human"] is True
    assert result["ticket_id"] is not None
