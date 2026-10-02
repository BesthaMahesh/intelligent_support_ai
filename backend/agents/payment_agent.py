import time
from typing import Dict, Any
from backend.tools.payment_api import get_payment_status, check_refund_eligibility
from backend.guardrails.tool_guardrail import validate_tool_request
from backend.schemas.chat import ToolCallRecord

class PaymentAgent:
    """Payment Agent: Interacts with Payment Gateway and refund services."""
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        entities = state.get("entities", {})
        order_id = entities.get("order_id") or "ORD-78231"
        intent = state.get("intent", "")
        
        tool_name = "get_payment_status"
        args = {"order_id": order_id}
        
        is_valid, reason = validate_tool_request(tool_name, args)
        if not is_valid:
            record = ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result={"error": reason},
                status="blocked_by_guardrails",
                latency_ms=0.0
            )
            return {"tool_results": {"payment_status": {"error": reason}}, "tool_record": record}

        res = get_payment_status(order_id)
        
        # If refund request, check eligibility
        if intent == "refund_request":
            eligibility = check_refund_eligibility(order_id, entities.get("amount"))
            res["refund_eligibility"] = eligibility

        latency = round((time.time() - start) * 1000, 2)
        
        record = ToolCallRecord(
            tool_name=tool_name,
            arguments=args,
            result=res,
            status="success",
            latency_ms=latency
        )
        
        return {
            "tool_results": {"payment_status": res},
            "tool_record": record
        }
