import re
from typing import Dict, Any

def classify_urgency(text: str, sentiment: str = "neutral", intent: str = "general_faq") -> Dict[str, Any]:
    """
    Classify customer query urgency into: low, medium, high, critical.
    Provides clear business reasoning.
    """
    if not text:
        return {"urgency": "low", "reason": "Standard inquiry"}

    lower = text.lower()

    # 1. Critical urgency
    if "fraud" in lower or "sue" in lower or "legal" in lower or "police" in lower or "cheated" in lower:
        return {"urgency": "critical", "reason": "Severe legal or fraud risk detected"}

    if sentiment == "highly_negative" and ("deducted" in lower or "not shipped" in lower or "nobody helped" in lower):
        return {"urgency": "high", "reason": "High customer frustration with unresolved transaction delay"}

    # 2. High urgency
    if intent in ["payment_pending", "payment_failed", "refund_request"]:
        return {"urgency": "high", "reason": "Financial transaction concern requires prompt verification"}

    if "three days ago" in lower or "nobody helped" in lower or "unresolved" in lower or "urgent" in lower or "emergency" in lower:
        return {"urgency": "high", "reason": "Repeated contact or substantial delay reported"}

    if intent == "delivery_delay" or "delayed" in lower:
        return {"urgency": "medium", "reason": "Logistics inquiry regarding order delivery"}

    # 3. Medium urgency
    if intent in ["order_status", "cancellation", "technical_support"]:
        return {"urgency": "medium", "reason": "Active order management or technical inquiry"}

    # 4. Low urgency
    return {"urgency": "low", "reason": "Informational or standard policy inquiry"}
