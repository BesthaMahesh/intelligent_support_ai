import os
from typing import List, Dict, Any

_cross_encoder = None

def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        if os.environ.get("USE_HF_RERANKER", "false").lower() == "true":
            try:
                from sentence_transformers import CrossEncoder
                _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception:
                _cross_encoder = "fallback"
        else:
            _cross_encoder = "fallback"
    return _cross_encoder

def rerank_documents(query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Rerank retrieved candidates using Cross-Encoder or lexical-semantic reciprocal fusion.
    """
    if not documents:
        return []

    # If cross-encoder is available
    ce = get_cross_encoder()
    if ce != "fallback":
        try:
            pairs = [[query, doc["content"]] for doc in documents]
            scores = ce.predict(pairs)
            for i, score in enumerate(scores):
                documents[i]["rerank_score"] = float(score)
            documents.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            return documents[:top_k]
        except Exception:
            pass

    # High-precision lexical & semantic relevance fallback scoring
    query_terms = set(query.lower().split())
    for doc in documents:
        content_lower = doc["content"].lower()
        title_lower = str(doc.get("metadata", {}).get("title", "")).lower()
        
        # Term overlap
        term_matches = sum(1 for t in query_terms if t in content_lower)
        title_matches = sum(2 for t in query_terms if t in title_lower)
        
        vec_score = doc.get("vector_score", 0.5)
        bm25_score = min(1.0, doc.get("bm25_score", 0.0) / 10.0)
        
        # Weighted hybrid reranking score
        relevance_score = (vec_score * 0.45) + (bm25_score * 0.35) + (min(1.0, (term_matches + title_matches) / max(1, len(query_terms))) * 0.20)
        doc["rerank_score"] = round(relevance_score, 4)

    documents.sort(key=lambda x: x["rerank_score"], reverse=True)
    return documents[:top_k]
