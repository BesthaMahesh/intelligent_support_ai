from typing import Dict, Any

TOPIC_MAPPINGS = {
    "Returns & Replacements": ["return_policy", "refund_request"],
    "Payments & Billing": ["payment_pending", "payment_failed"],
    "Shipping & Logistics": ["delivery_delay", "shipping_policy", "order_status"],
    "Order Management": ["cancellation"],
    "Customer Support & Complaints": ["complaint", "human_agent_request"],
    "Product Support": ["product_information", "technical_support"],
    "General & FAQ": ["general_faq"]
}

def classify_topic(intent: str, text: str = "") -> str:
    """
    Classify the overarching business topic based on intent and query content.
    """
    for topic, intents in TOPIC_MAPPINGS.items():
        if intent in intents:
            return topic
            
    return "General & FAQ"
