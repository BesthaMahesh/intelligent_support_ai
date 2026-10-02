import re
from typing import Dict, Any, Tuple

INTENT_DEFINITIONS = {
    "human_agent_request": [
        "human", "agent", "representative", "person", "operator", "speak to someone",
        "talk to human", "manager", "supervisor", "connect me", "customer care executive",
        "real person", "escalate to human"
    ],
    "payment_pending": [
        "payment pending", "money deducted", "amount debited", "payment was deducted",
        "paid but pending", "transaction pending", "payment processing", "money cut",
        "deducted from bank", "debited from account", "paid but not confirmed",
        "amount deducted", "payment success but pending", "paise kat gaye"
    ],
    "payment_failed": [
        "payment failed", "transaction failed", "payment error", "card declined",
        "upi failed", "payment declined", "payment unsuccessful", "checkout failed"
    ],
    "refund_request": [
        "refund", "money back", "return money", "refund status", "refund my amount",
        "when will i get refund", "refund processed", "reimbursement", "reimburse",
        "panam thirumba"
    ],
    "delivery_delay": [
        "delay", "not shipped", "hasn't shipped", "not delivered", "late delivery",
        "tracking not updating", "where is my parcel", "expected dispatch",
        "order delayed", "shipment delayed", "three days ago", "not received"
    ],
    "order_status": [
        "where is my order", "order status", "track order", "track shipment",
        "where is package", "order details", "check status of order", "locate order",
        "current status"
    ],
    "return_policy": [
        "return policy", "how to return", "can i return", "return period",
        "return electronics", "return window", "return process", "return conditions",
        "days to return", "replacement policy", "replace item"
    ],
    "shipping_policy": [
        "shipping policy", "shipping charges", "delivery time", "shipping cost",
        "international shipping", "free delivery", "dispatch time", "courier partner",
        "shipping timeline"
    ],
    "cancellation": [
        "cancel order", "cancellation policy", "how to cancel", "cancel my item",
        "stop shipment", "cancel purchase"
    ],
    "product_information": [
        "warranty", "specifications", "product details", "how does it work",
        "compatible", "dimensions", "features", "stock availability", "is it original"
    ],
    "technical_support": [
        "app crashing", "login issue", "password reset", "website error",
        "otp not received", "account locked", "bug", "not working"
    ],
    "complaint": [
        "frustrated", "worst service", "nobody helped", "complaint", "terrible experience",
        "unhappy", "angry", "poor support", "ridiculous", "contacted yesterday",
        "escalate issue"
    ],
    "general_faq": [
        "hello", "hi", "help", "working hours", "support email", "contact info",
        "customer service", "office location", "thank you", "good morning"
    ]
}

def classify_intent(text: str) -> Dict[str, Any]:
    """
    Classify the customer's intent using multi-factor lexical & semantic scoring.
    Returns:
    {
        "intent": "payment_pending",
        "confidence": 0.97
    }
    """
    if not text:
        return {"intent": "general_faq", "confidence": 0.50}
    
    clean_text = text.lower()
    scores = {}
    
    # Check for strong specific patterns first
    if re.search(r'\b(human|agent|person|representative|operator|manager)\b', clean_text) and \
       re.search(r'\b(talk|speak|connect|escalate|want|need|transfer)\b', clean_text):
        return {"intent": "human_agent_request", "confidence": 0.98}

    if re.search(r'(deducted|debited|kat gaye|cut from).*?(pending|not confirmed|still pending)', clean_text) or \
       re.search(r'(paid|payment).*?(pending|not confirmed|deducted)', clean_text):
        return {"intent": "payment_pending", "confidence": 0.97}

    if re.search(r'(not shipped|hasn\'t shipped|late|delayed|three days ago).*?(ship|deliver|package|order)', clean_text):
        return {"intent": "delivery_delay", "confidence": 0.96}

    # Evaluate all intent patterns with weighted overlap
    words = set(re.findall(r'\b\w+\b', clean_text))
    
    for intent, patterns in INTENT_DEFINITIONS.items():
        score = 0.0
        for pattern in patterns:
            pattern_words = pattern.split()
            if pattern in clean_text:
                score += 2.0 * len(pattern_words)
            else:
                overlap = sum(1 for pw in pattern_words if pw in words)
                if overlap > 0:
                    score += (overlap / len(pattern_words)) * 0.8
        scores[intent] = score

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]
    
    if best_score == 0:
        return {"intent": "general_faq", "confidence": 0.55}

    # Normalize confidence to [0.65, 0.99]
    confidence = min(0.99, max(0.65, round(0.65 + (best_score / (best_score + 3.0)) * 0.34, 2)))
    return {"intent": best_intent, "confidence": confidence}
