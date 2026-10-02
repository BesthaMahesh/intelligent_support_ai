import json
import os
from pathlib import Path
from typing import Dict, Any
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from backend.nlp.intent_classifier import classify_intent
from backend.nlp.sentiment import analyze_sentiment
from backend.nlp.entity_extraction import extract_entities
from backend.schemas.evaluation import IntentEvalResult, NEREvalResult, SentimentEvalResult

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def evaluate_nlp_intent() -> IntentEvalResult:
    """Evaluate Intent Classification accuracy, precision, recall, and macro F1."""
    test_file = BASE_DIR / "data" / "evaluation" / "intent_test.json"
    if not os.path.exists(test_file):
        return IntentEvalResult(accuracy=0.0, precision_macro=0.0, recall_macro=0.0, f1_macro=0.0, total_samples=0)

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    y_true = []
    y_pred = []

    for item in data:
        text = item["text"]
        expected = item["expected_intent"]
        pred_res = classify_intent(text)
        
        y_true.append(expected)
        y_pred.append(pred_res["intent"])

    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

    return IntentEvalResult(
        accuracy=round(float(acc), 4),
        precision_macro=round(float(p), 4),
        recall_macro=round(float(r), 4),
        f1_macro=round(float(f1), 4),
        total_samples=len(data)
    )

def evaluate_nlp_sentiment() -> SentimentEvalResult:
    """Evaluate Sentiment Classification accuracy and macro F1."""
    test_file = BASE_DIR / "data" / "evaluation" / "sentiment_test.json"
    if not os.path.exists(test_file):
        return SentimentEvalResult(macro_f1=0.0, accuracy=0.0, total_samples=0)

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    y_true = []
    y_pred = []

    for item in data:
        text = item["text"]
        expected = item["expected_sentiment"]
        pred = analyze_sentiment(text)
        y_true.append(expected)
        y_pred.append(pred["sentiment"])

    acc = accuracy_score(y_true, y_pred)
    _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

    return SentimentEvalResult(
        accuracy=round(float(acc), 4),
        macro_f1=round(float(f1), 4),
        total_samples=len(data)
    )

def evaluate_nlp_ner() -> NEREvalResult:
    """Evaluate Named Entity Recognition precision, recall, and F1."""
    test_file = BASE_DIR / "data" / "evaluation" / "ner_test.json"
    if not os.path.exists(test_file):
        return NEREvalResult(precision=0.0, recall=0.0, f1=0.0, total_samples=0)

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for item in data:
        text = item["text"]
        expected = item["expected_entities"]
        pred_entities = extract_entities(text).dict()

        for k, v in expected.items():
            if pred_entities.get(k) == v or (isinstance(v, float) and abs(float(pred_entities.get(k) or 0) - v) < 1.0):
                true_positives += 1
            else:
                false_negatives += 1

        for k, v in pred_entities.items():
            if v is not None and v != {} and k not in expected:
                false_positives += 1

    prec = true_positives / max(1, true_positives + false_positives)
    rec = true_positives / max(1, true_positives + false_negatives)
    f1 = (2 * prec * rec) / max(0.0001, prec + rec)

    return NEREvalResult(
        precision=round(float(prec), 4),
        recall=round(float(rec), 4),
        f1=round(float(f1), 4),
        total_samples=len(data)
    )
