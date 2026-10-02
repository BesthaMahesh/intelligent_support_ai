import pytest
from backend.nlp import (
    detect_language, normalize_text, detect_and_protect_pii,
    classify_intent, analyze_sentiment, extract_entities,
    classify_urgency, analyze_customer_query
)

def test_language_detection():
    # Tamil test
    res_ta = detect_language("வணக்கம் என் ஆர்டர் எங்கே உள்ளது?")
    assert res_ta["language"] == "Tamil"
    
    # Hindi test
    res_hi = detect_language("मेरा आर्डर अभी तक नहीं आया")
    assert res_hi["language"] == "Hindi"

    # English test
    res_en = detect_language("Where is my order ORD-78231?")
    assert res_en["language"] == "English"

def test_normalization():
    raw = "My ord 78231 paid ₹ 24,990"
    norm = normalize_text(raw)
    assert "ORD-78231" in norm
    assert "INR 24,990" in norm

def test_pii_detection():
    sample = "My card is 4111 1111 1111 1111 and phone is 9876543210"
    res = detect_and_protect_pii(sample)
    assert res["pii_detected"] is True
    assert "[REDACTED_CARD]" in res["redacted_text"]
    assert "[REDACTED_PHONE]" in res["redacted_text"]

def test_intent_classification():
    faq = classify_intent("What is the return policy for electronics?")
    assert faq["intent"] == "return_policy"

    pending = classify_intent("Payment was deducted but my order is still pending")
    assert pending["intent"] == "payment_pending"

    human = classify_intent("Please connect me to a human agent right now")
    assert human["intent"] == "human_agent_request"

def test_entity_extraction():
    msg = "I ordered a laptop three days ago and paid ₹72,999. Order ID ORD-91245."
    entities = extract_entities(msg)
    assert entities.order_id == "ORD-91245"
    assert entities.product == "laptop"
    assert entities.amount == 72999.0
    assert entities.currency == "INR"

def test_unified_nlp_pipeline():
    msg = "My payment was deducted for order ORD-78231"
    res = analyze_customer_query(msg)
    assert res.intent == "payment_pending"
    assert res.entities.order_id == "ORD-78231"
