import re
from typing import Dict, Any

HIGHLY_NEGATIVE_WORDS = [
    "furious", "terrible", "worst", "horrible", "fraud", "cheated", "sue",
    "legal action", "extremely frustrating", "disgusted", "useless", "scam",
    "nobody helped", "ridiculous", "harassment", "pathetic", "unacceptable"
]

NEGATIVE_WORDS = [
    "frustrated", "angry", "disappointed", "annoyed", "delay", "delayed", "late",
    "broken", "damaged", "failed", "pending", "not working", "problem", "issue",
    "wrong", "bad", "slow", "error", "missing", "cancel", "refund"
]

POSITIVE_WORDS = [
    "thank you", "thanks", "great", "excellent", "awesome", "helpful", "good",
    "appreciated", "satisfied", "wonderful", "perfect", "resolved", "fast"
]

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze customer sentiment into positive, neutral, negative, highly_negative.
    Returns:
    {
        "sentiment": "negative",
        "confidence": 0.94
    }
    """
    if not text:
        return {"sentiment": "neutral", "confidence": 0.95}

    clean_text = text.lower()
    
    # Check for highly negative cues
    highly_neg_matches = sum(1 for phrase in HIGHLY_NEGATIVE_WORDS if phrase in clean_text)
    if highly_neg_matches >= 1:
        conf = min(0.99, round(0.88 + (highly_neg_matches * 0.05), 2))
        return {"sentiment": "highly_negative", "confidence": conf}

    # Check negative count
    neg_matches = sum(1 for phrase in NEGATIVE_WORDS if phrase in clean_text)
    pos_matches = sum(1 for phrase in POSITIVE_WORDS if phrase in clean_text)

    if neg_matches > pos_matches:
        conf = min(0.98, round(0.75 + ((neg_matches - pos_matches) * 0.07), 2))
        return {"sentiment": "negative", "confidence": conf}
    elif pos_matches > neg_matches:
        conf = min(0.98, round(0.75 + ((pos_matches - neg_matches) * 0.07), 2))
        return {"sentiment": "positive", "confidence": conf}
    else:
        return {"sentiment": "neutral", "confidence": 0.85}
