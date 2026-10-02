import time
from typing import Dict, Any
from backend.tools.crm_api import get_customer_history
from backend.guardrails.tool_guardrail import validate_tool_request
from backend.schemas.chat import ToolCallRecord

class CustomerAgent:
    """Customer CRM Agent: Retrieves customer profile, prior tickets, and tier."""
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        customer_id = state.get("customer_id") or "CUS-8821"
        
        tool_name = "get_customer_history"
        args = {"customer_id": customer_id}
        
        is_valid, reason = validate_tool_request(tool_name, args)
        if not is_valid:
            record = ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result={"error": reason},
                status="blocked_by_guardrails",
                latency_ms=0.0
            )
            return {"tool_results": {"customer_history": {"error": reason}}, "tool_record": record}

        result = get_customer_history(customer_id)
        latency = round((time.time() - start) * 1000, 2)
        
        record = ToolCallRecord(
            tool_name=tool_name,
            arguments=args,
            result=result,
            status="success",
            latency_ms=latency
        )
        
        return {
            "tool_results": {"customer_history": result},
            "tool_record": record
        }
