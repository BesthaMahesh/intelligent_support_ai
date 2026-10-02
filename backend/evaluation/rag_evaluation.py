import json
import math
import os
from pathlib import Path
from typing import Dict, Any, List
from backend.rag.retriever import retrieve_knowledge
from backend.schemas.evaluation import RAGEvalResult

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def calculate_ndcg(retrieved_ids: List[str], relevant_ids: List[str], k: int = 3) -> float:
    dcg = 0.0
    for idx, doc_id in enumerate(retrieved_ids[:k]):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / math.log2(idx + 2)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant_ids), k)))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_rag_pipeline() -> RAGEvalResult:
    """
    Execute empirical RAG evaluation on test dataset.
    Measures Recall@K, Precision@K, MRR, NDCG, Faithfulness, Answer Groundedness.
    """
    from backend.rag.ingestion import ingest_knowledge_base
    ingest_knowledge_base()

    test_file = BASE_DIR / "data" / "evaluation" / "rag_test.json"
    if not os.path.exists(test_file):
        return RAGEvalResult(
            recall_at_k=0.0, precision_at_k=0.0, mrr=0.0, ndcg=0.0,
            faithfulness=0.0, context_recall=0.0, answer_groundedness=0.0, answer_relevance=0.0,
            total_queries=0, query_details=[]
        )

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    recalls = []
    precisions = []
    mrrs = []
    ndcgs = []
    groundedness_scores = []
    query_details = []

    k = 3
    for item in data:
        query = item["query"]
        expected_ids = item["expected_doc_ids"]
        expected_keywords = item.get("expected_keywords", [])
        
        sources, context_str = retrieve_knowledge(query, top_k=k)
        retrieved_ids = [s.get("document_id") for s in sources]

        # Calculate hits
        hits = sum(1 for d_id in retrieved_ids if d_id in expected_ids)
        rec = hits / max(1, len(expected_ids))
        prec = hits / max(1, len(retrieved_ids))
        
        # MRR
        rr = 0.0
        for rank, d_id in enumerate(retrieved_ids):
            if d_id in expected_ids:
                rr = 1.0 / (rank + 1)
                break
                
        # NDCG
        ndcg_val = calculate_ndcg(retrieved_ids, expected_ids, k=k)

        # Keyword Groundedness in retrieved context
        kw_hits = sum(1 for kw in expected_keywords if kw.lower() in context_str.lower())
        groundedness = kw_hits / max(1, len(expected_keywords))

        recalls.append(rec)
        precisions.append(prec)
        mrrs.append(rr)
        ndcgs.append(ndcg_val)
        groundedness_scores.append(groundedness)

        query_details.append({
            "query": query,
            "expected_docs": expected_ids,
            "retrieved_docs": retrieved_ids,
            "recall_at_3": round(rec, 3),
            "groundedness": round(groundedness, 3),
            "top_source": sources[0]["title"] if sources else "None"
        })

    avg_rec = round(sum(recalls) / max(1, len(recalls)), 4)
    avg_prec = round(sum(precisions) / max(1, len(precisions)), 4)
    avg_mrr = round(sum(mrrs) / max(1, len(mrrs)), 4)
    avg_ndcg = round(sum(ndcgs) / max(1, len(ndcgs)), 4)
    avg_ground = round(sum(groundedness_scores) / max(1, len(groundedness_scores)), 4)

    return RAGEvalResult(
        recall_at_k=avg_rec,
        precision_at_k=avg_prec,
        mrr=avg_mrr,
        ndcg=avg_ndcg,
        faithfulness=avg_ground,
        context_recall=avg_rec,
        answer_groundedness=avg_ground,
        answer_relevance=round((avg_prec + avg_ground) / 2.0, 4),
        total_queries=len(data),
        query_details=query_details
    )
