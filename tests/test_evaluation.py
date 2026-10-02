import pytest
from backend.evaluation.nlp_evaluation import evaluate_nlp_intent, evaluate_nlp_sentiment, evaluate_nlp_ner
from backend.evaluation.rag_evaluation import evaluate_rag_pipeline

def test_nlp_intent_evaluation():
    res = evaluate_nlp_intent()
    assert res.total_samples > 0
    assert res.accuracy >= 0.80

def test_nlp_sentiment_evaluation():
    res = evaluate_nlp_sentiment()
    assert res.total_samples > 0
    assert res.accuracy >= 0.75

def test_rag_evaluation():
    res = evaluate_rag_pipeline()
    assert res.total_queries > 0
    assert res.recall_at_k > 0.50
