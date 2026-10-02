from fastapi import APIRouter
from backend.schemas.evaluation import SystemEvaluationSummary
from backend.evaluation.llm_evaluation import run_full_system_evaluation, get_latest_evaluation_summary

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])

@router.get("", response_model=SystemEvaluationSummary)
def get_evaluation_metrics():
    """Retrieve the latest comprehensive evaluation metrics across NLP, RAG, and Agent layers."""
    summary = get_latest_evaluation_summary()
    return summary

@router.post("/run", response_model=SystemEvaluationSummary)
def run_evaluation_suite():
    """Trigger a fresh live run of the full evaluation framework against benchmark datasets."""
    summary = run_full_system_evaluation()
    return summary
