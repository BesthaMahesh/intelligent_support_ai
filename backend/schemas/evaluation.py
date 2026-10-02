from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IntentEvalResult(BaseModel):
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    total_samples: int
    classification_report: Dict[str, Any] = Field(default_factory=dict)

class NEREvalResult(BaseModel):
    precision: float
    recall: float
    f1: float
    total_samples: int
    entity_breakdown: Dict[str, Any] = Field(default_factory=dict)

class SentimentEvalResult(BaseModel):
    macro_f1: float
    accuracy: float
    total_samples: int

class RAGEvalResult(BaseModel):
    recall_at_k: float
    precision_at_k: float
    mrr: float # Mean Reciprocal Rank
    ndcg: float # Normalized Discounted Cumulative Gain
    faithfulness: float
    context_recall: float
    answer_groundedness: float
    answer_relevance: float
    total_queries: int
    query_details: List[Dict[str, Any]] = Field(default_factory=list)

class AgentEvalResult(BaseModel):
    task_success_rate: float
    valid_tool_call_rate: float
    policy_violation_rate: float
    avg_latency_ms: float
    avg_cost_inr: float
    total_scenarios: int

class SystemEvaluationSummary(BaseModel):
    intent_evaluation: Optional[IntentEvalResult] = None
    ner_evaluation: Optional[NEREvalResult] = None
    sentiment_evaluation: Optional[SentimentEvalResult] = None
    rag_evaluation: Optional[RAGEvalResult] = None
    agent_evaluation: Optional[AgentEvalResult] = None
    last_evaluated_at: Optional[str] = None
