from datetime import datetime
from typing import Optional
from backend.schemas.evaluation import SystemEvaluationSummary
from .nlp_evaluation import evaluate_nlp_intent, evaluate_nlp_sentiment, evaluate_nlp_ner
from .rag_evaluation import evaluate_rag_pipeline
from .agent_evaluation import evaluate_agent_scenarios

_last_summary: Optional[SystemEvaluationSummary] = None

def run_full_system_evaluation() -> SystemEvaluationSummary:
    """
    Run complete empirical evaluation across NLP, RAG, and Agentic AI layers.
    """
    global _last_summary
    
    intent_res = evaluate_nlp_intent()
    ner_res = evaluate_nlp_ner()
    sentiment_res = evaluate_nlp_sentiment()
    rag_res = evaluate_rag_pipeline()
    agent_res = evaluate_agent_scenarios()

    _last_summary = SystemEvaluationSummary(
        intent_evaluation=intent_res,
        ner_evaluation=ner_res,
        sentiment_evaluation=sentiment_res,
        rag_evaluation=rag_res,
        agent_evaluation=agent_res,
        last_evaluated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    return _last_summary

def get_latest_evaluation_summary() -> Optional[SystemEvaluationSummary]:
    """Retrieve last cached evaluation results or run if empty."""
    global _last_summary
    if _last_summary is None:
        return run_full_system_evaluation()
    return _last_summary
