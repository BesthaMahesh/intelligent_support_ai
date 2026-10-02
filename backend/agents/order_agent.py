import time
from typing import Dict, Any
from backend.tools.order_api import get_order_status
from backend.guardrails.tool_guardrail import validate_tool_request
from backend.schemas.chat import ToolCallRecord

class OrderAgent:
    """Order Agent: Interacts with Order management service."""
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        entities = state.get("entities", {})
        order_id = entities.get("order_id") or "ORD-78231"
        
        tool_name = "get_order_status"
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
            return {"tool_results": {"order_status": {"error": reason}}, "tool_record": record}

        result = get_order_status(order_id)
        latency = round((time.time() - start) * 1000, 2)
        
        record = ToolCallRecord(
            tool_name=tool_name,
            arguments=args,
            result=result,
            status="success",
            latency_ms=latency
        )
        
        return {
            "tool_results": {"order_status": result},
            "tool_record": record
        }
