from typing import Dict, Any
from backend.tools.ticket_api import create_escalation_ticket
from backend.schemas.chat import ToolCallRecord

class EscalationAgent:
    """
    Escalation Agent: Handles case escalation and ticket creation when human review is required.
    """
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = state.get("customer_id", "CUS-8821")
        customer_name = state.get("customer_name", "Rajesh Kumar")
        entities = state.get("entities", {})
        order_id = entities.get("order_id")
        intent = state.get("intent", "general_faq")
        urgency = state.get("urgency", "high")
        escalation_reason = state.get("escalation_reason") or state.get("urgency_reason") or "Customer escalation required."

        priority = "HIGH" if urgency in ["high", "critical"] else "MEDIUM"
        title = f"Escalation: {intent.replace('_', ' ').title()} - {order_id or customer_id}"
        description = f"Customer Query: {state.get('sanitized_message', '')}\nReason: {escalation_reason}"
        ai_recommendation = f"Investigate order {order_id or 'account'} and contact customer."

        ticket_res = create_escalation_ticket(
            customer_id=customer_id,
            customer_name=customer_name,
            order_id=order_id,
            title=title,
            description=description,
            intent=intent,
            priority=priority,
            ai_recommended_action=ai_recommendation,
            escalation_reason=escalation_reason
        )

        record = ToolCallRecord(
            tool_name="create_escalation_ticket",
            arguments={"order_id": order_id, "priority": priority, "reason": escalation_reason},
            result=ticket_res,
            status="success",
            latency_ms=10.0
        )

        return {
            "ticket_id": ticket_res["ticket_id"],
            "requires_human": True,
            "escalation_reason": escalation_reason,
            "tool_record": record
        }
