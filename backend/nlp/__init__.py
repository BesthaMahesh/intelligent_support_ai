from .language_detection import detect_language
from .normalization import normalize_text
from .pii_detection import detect_and_protect_pii
from .intent_classifier import classify_intent
from .sentiment import analyze_sentiment
from .entity_extraction import extract_entities
from .urgency import classify_urgency
from .topic_classifier import classify_topic
from backend.schemas.chat import NLPAnalysisResult

def analyze_customer_query(text: str) -> NLPAnalysisResult:
    """
    Unified NLP pipeline execution:
    1. Language Detection
    2. Text Normalization
    3. PII Detection & Redaction
    4. Intent Classification
    5. Sentiment Analysis
    6. Entity Extraction
    7. Urgency Classification
    8. Topic Classification
    """
    # 1. Detect language
    lang_info = detect_language(text)
    
    # 2. Normalize text
    norm_text = normalize_text(text)
    
    # 3. PII Detection
    pii_info = detect_and_protect_pii(norm_text)
    safe_text = pii_info["redacted_text"] if pii_info["pii_detected"] else norm_text
    
    # 4. Intent Classification
    intent_info = classify_intent(safe_text)
    
    # 5. Sentiment Analysis
    sentiment_info = analyze_sentiment(safe_text)
    
    # 6. Entity Extraction (from normalized text to catch order/customer patterns safely)
    entities = extract_entities(norm_text)
    
    # 7. Urgency Classification
    urgency_info = classify_urgency(safe_text, sentiment=sentiment_info["sentiment"], intent=intent_info["intent"])
    
    # 8. Topic Classification
    topic = classify_topic(intent_info["intent"], safe_text)

    return NLPAnalysisResult(
        language=lang_info["language"],
        language_confidence=lang_info["confidence"],
        normalized_text=norm_text,
        intent=intent_info["intent"],
        intent_confidence=intent_info["confidence"],
        sentiment=sentiment_info["sentiment"],
        sentiment_confidence=sentiment_info["confidence"],
        urgency=urgency_info["urgency"],
        urgency_reason=urgency_info["reason"],
        topic=topic,
        entities=entities,
        pii_detected=pii_info["pii_detected"],
        redacted_text=safe_text
    )

__all__ = [
    "detect_language", "normalize_text", "detect_and_protect_pii",
    "classify_intent", "analyze_sentiment", "extract_entities",
    "classify_urgency", "classify_topic", "analyze_customer_query"
]
