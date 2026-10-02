from typing import Dict, Any, List, Optional

class BusinessRuleEngine:
    """
    Deterministic Enterprise Business Rule Engine.
    Enforces rigid business policies that cannot be overridden by LLM reasoning.
    """

    @staticmethod
    def evaluate_rules(
        intent: str,
        sentiment: str,
        urgency: str,
        entities: Dict[str, Any],
        tool_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate business rules and return decisions:
        - action_required: str
        - auto_escalate: bool
        - rule_applied: str
        - policy_guidance: str
        """
        order_info = tool_results.get("order_status", {})
        payment_info = tool_results.get("payment_status", {})
        shipment_info = tool_results.get("shipment_status", {})
        customer_info = tool_results.get("customer_history", {})

        # Rule 1 & 2: Payment Deducted / Success but Order Pending
        p_status = payment_info.get("payment_status") or order_info.get("payment_status")
        o_status = order_info.get("order_status")

        if p_status == "SUCCESS" and o_status == "PAYMENT_PENDING":
            minutes_elapsed = payment_info.get("minutes_since_payment", 30) # mock or actual elapsed
            if minutes_elapsed <= 15:
                return {
                    "auto_escalate": False,
                    "rule_applied": "BR-PAY-01: Payment Pending within 15min Reconciliation Window",
                    "action_required": "INFORM_PAYMENT_RECONCILIATION",
                    "policy_guidance": "Payment was received successfully. Bank webhook reconciliation takes up to 15 minutes. No manual intervention required yet."
                }
            else:
                return {
                    "auto_escalate": True,
                    "rule_applied": "BR-PAY-02: Payment Pending Beyond Allowed Reconciliation SLA",
                    "action_required": "CREATE_PAYMENT_RECONCILIATION_TICKET",
                    "policy_guidance": "Payment was successful over 15 minutes ago but order remains pending. Automatically initiate an investigation ticket."
                }

        # Rule 3: Shipping Delay with Past Expected Dispatch + Prior Unresolved Ticket
        if shipment_info.get("shipment_status") == "NOT_SHIPPED" and shipment_info.get("is_dispatch_overdue", False):
            prev_tickets = customer_info.get("previous_tickets", 0)
            if prev_tickets > 0 or sentiment in ["negative", "highly_negative"]:
                return {
                    "auto_escalate": True,
                    "rule_applied": "BR-LOG-03: Delayed Shipment with Prior Customer Escalation",
                    "action_required": "ESCALATE_TO_LOGISTICS_LEAD",
                    "policy_guidance": "Order has not shipped past the committed dispatch date and customer has prior open touchpoints. Priority escalation required."
                }

        # Rule 4: High Value Refund Safety Guard (> ₹10,000)
        amount = entities.get("amount") or order_info.get("amount") or 0
        if intent == "refund_request" and float(amount) > 10000:
            return {
                "auto_escalate": True,
                "rule_applied": "BR-FIN-04: High Value Refund Verification (> INR 10,000)",
                "action_required": "FINANCIAL_SUPERVISOR_REVIEW",
                "policy_guidance": f"Refund of INR {amount} exceeds automated authorization limit. Human supervisor authorization is mandatory."
            }

        # Rule 5: Critical Urgency / Legal Threat / Severe Hostility
        if urgency == "critical" or sentiment == "highly_negative":
            return {
                "auto_escalate": True,
                "rule_applied": "BR-ESC-05: Critical Customer Risk / Escalation Threshold",
                "action_required": "IMMEDIATE_HUMAN_HANDOFF",
                "policy_guidance": "Customer sentiment or urgency meets critical threshold. Route directly to senior support agent."
            }

        # Default standard flow
        return {
            "auto_escalate": False,
            "rule_applied": "BR-STD-00: Standard AI Resolution Flow",
            "action_required": "STANDARD_RESOLUTION",
            "policy_guidance": "Process inquiry using verified tool data and knowledge base grounding."
        }
