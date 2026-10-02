from typing import Dict, Any, Tuple

# Allowed tools and their strict schemas
ALLOWED_TOOLS = {
    "get_order_status": {"required": ["order_id"], "optional": []},
    "get_payment_status": {"required": ["order_id"], "optional": []},
    "get_shipment_status": {"required": ["order_id"], "optional": []},
    "get_customer_history": {"required": ["customer_id"], "optional": []},
    "create_escalation_ticket": {"required": ["priority", "reason"], "optional": ["order_id", "customer_id", "customer_name"]},
    "check_refund_eligibility": {"required": ["order_id"], "optional": ["amount", "reason"]},
    "request_refund_authorization": {"required": ["order_id", "amount", "reason"], "optional": ["override_code"]}
}

FORBIDDEN_DIRECT_TOOLS = ["direct_bank_transfer", "bypass_refund_limit", "delete_customer_records"]

def validate_tool_request(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that:
    1. The requested tool exists and is permitted
    2. Required parameters are present and well-formed
    3. Direct financial disbursement is blocked from direct AI execution
    """
    if tool_name in FORBIDDEN_DIRECT_TOOLS:
        return False, f"Direct tool execution for '{tool_name}' is prohibited by Enterprise Financial Safety Policy."

    if tool_name not in ALLOWED_TOOLS:
        return False, f"Unknown or unpermitted tool: '{tool_name}'."

    spec = ALLOWED_TOOLS[tool_name]
    for req in spec["required"]:
        if req not in arguments or arguments[req] is None or str(arguments[req]).strip() == "":
            return False, f"Missing required parameter '{req}' for tool '{tool_name}'."

    # Specific guardrail: direct refund amount authorization cannot exceed automated threshold
    if tool_name == "request_refund_authorization":
        amount = float(arguments.get("amount", 0))
        if amount > 10000.0 and not arguments.get("override_code"):
            return False, f"Refund amount ₹{amount} exceeds automated limit (₹10,000). Requires human supervisor escalation."

    return True, "Tool validation passed."
