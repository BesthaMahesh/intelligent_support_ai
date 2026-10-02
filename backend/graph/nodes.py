import time
import json
import uuid
from typing import Dict, Any
from backend.graph.state import AgentState
from backend.nlp import analyze_customer_query
from backend.guardrails.input_guardrail import validate_input
from backend.guardrails.output_guardrail import validate_output
from backend.business_rules.rules import BusinessRuleEngine
from backend.agents.supervisor import SupervisorAgent
from backend.agents.knowledge_agent import KnowledgeAgent
from backend.agents.order_agent import OrderAgent
from backend.agents.payment_agent import PaymentAgent
from backend.agents.shipment_agent import ShipmentAgent
from backend.agents.customer_agent import CustomerAgent
from backend.agents.escalation_agent import EscalationAgent
from backend.agents.response_agent import ResponseAgent
from backend.schemas.chat import ToolCallRecord

def nlp_and_input_guardrail_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Validate input, run full NLP understanding pipeline."""
    start_time = time.time()
    raw_message = state.get("message", "")
    
    # Input Guardrails
    guard_res = validate_input(raw_message)
    sanitized = guard_res["sanitized_text"]
    
    # NLP Pipeline
    nlp_res = analyze_customer_query(sanitized or raw_message)
    nlp_latency = round((time.time() - start_time) * 1000, 2)
    
    # Check if customer explicitly gave order/customer id in state
    entities_dict = nlp_res.entities.dict()
    if state.get("customer_id") and not entities_dict.get("customer_id"):
        entities_dict["customer_id"] = state["customer_id"]

    return {
        "sanitized_message": sanitized,
        "language": nlp_res.language,
        "language_confidence": nlp_res.language_confidence,
        "intent": nlp_res.intent,
        "intent_confidence": nlp_res.intent_confidence,
        "sentiment": nlp_res.sentiment,
        "urgency": nlp_res.urgency,
        "urgency_reason": nlp_res.urgency_reason,
        "topic": nlp_res.topic,
        "entities": entities_dict,
        "guardrails": {
            "input_passed": guard_res["passed"],
            "input_violations": guard_res["violations"],
            "prompt_injection_detected": guard_res["prompt_injection_detected"]
        },
        "nlp_latency_ms": nlp_latency
    }

def supervisor_routing_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Supervisor Agent plans execution flow."""
    decision = SupervisorAgent.plan(state)
    return {
        "route_taken": decision["route_taken"],
        "required_agents": decision["required_agents"]
    }

def tool_execution_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Execute required specialized domain agents."""
    required = state.get("required_agents", [])
    tool_results = state.get("tool_results", {}).copy()
    tools_executed = state.get("tools_executed", []).copy()
    tool_latency = 0.0

    if "order_agent" in required:
        res = OrderAgent.run(state)
        tool_results.update(res["tool_results"])
        tools_executed.append(res["tool_record"])
        tool_latency += res["tool_record"].latency_ms

    if "payment_agent" in required:
        res = PaymentAgent.run(state)
        tool_results.update(res["tool_results"])
        tools_executed.append(res["tool_record"])
        tool_latency += res["tool_record"].latency_ms

    if "shipment_agent" in required:
        res = ShipmentAgent.run(state)
        tool_results.update(res["tool_results"])
        tools_executed.append(res["tool_record"])
        tool_latency += res["tool_record"].latency_ms

    if "customer_agent" in required:
        res = CustomerAgent.run(state)
        tool_results.update(res["tool_results"])
        tools_executed.append(res["tool_record"])
        tool_latency += res["tool_record"].latency_ms

    return {
        "tool_results": tool_results,
        "tools_executed": tools_executed,
        "tool_latency_ms": round(tool_latency, 2)
    }

def knowledge_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """Node 4: Execute RAG knowledge retrieval."""
    required = state.get("required_agents", [])
    if "knowledge_agent" in required:
        res = KnowledgeAgent.run(state)
        return res
    return {
        "retrieved_context": "",
        "retrieved_sources": [],
        "retrieval_latency_ms": 0.0
    }

def business_rules_node(state: AgentState) -> Dict[str, Any]:
    """Node 5: Evaluate deterministic business rules."""
    rule_res = BusinessRuleEngine.evaluate_rules(
        intent=state.get("intent", "general_faq"),
        sentiment=state.get("sentiment", "neutral"),
        urgency=state.get("urgency", "low"),
        entities=state.get("entities", {}),
        tool_results=state.get("tool_results", {})
    )

    requires_human = rule_res.get("auto_escalate", False) or state.get("route_taken") == "human_escalation"
    escalation_reason = rule_res.get("policy_guidance") if requires_human else None

    ticket_id = state.get("ticket_id")
    tools_executed = state.get("tools_executed", []).copy()

    # Automatically create escalation ticket if required
    if requires_human and not ticket_id:
        esc_res = EscalationAgent.run({
            **state,
            "escalation_reason": escalation_reason
        })
        ticket_id = esc_res["ticket_id"]
        tools_executed.append(esc_res["tool_record"])

    return {
        "business_rule_result": rule_res,
        "requires_human": requires_human,
        "escalation_reason": escalation_reason,
        "ticket_id": ticket_id,
        "tools_executed": tools_executed
    }

def response_generation_node(state: AgentState) -> Dict[str, Any]:
    """Node 6: Generate grounded response using Response Agent."""
    res = ResponseAgent.generate(state)
    llm_res = res["llm_result"]

    return {
        "response": res["response"],
        "llm_latency_ms": llm_res.latency_ms,
        "input_tokens": llm_res.prompt_tokens,
        "output_tokens": llm_res.completion_tokens,
        "total_tokens": llm_res.total_tokens,
        "cost_inr": llm_res.cost_inr,
        "model_name": llm_res.model,
        "prompt_version": res["prompt_version"]
    }

def output_guardrails_node(state: AgentState) -> Dict[str, Any]:
    """Node 7: Output Guardrail validation."""
    raw_response = state.get("response", "")
    guard_res = validate_output(
        response_text=raw_response,
        tool_results=list(state.get("tool_results", {}).values())
    )

    prev_guardrails = state.get("guardrails", {})
    prev_guardrails.update({
        "output_passed": guard_res["passed"],
        "output_violations": guard_res["violations"],
        "grounding_passed": guard_res["grounding_passed"]
    })

    return {
        "response": guard_res["sanitized_response"],
        "guardrails": prev_guardrails
    }
