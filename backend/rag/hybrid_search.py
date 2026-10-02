from typing import List, Dict, Any
from .vectorstore import vector_store
from .bm25 import bm25_engine
from .reranker import rerank_documents

def hybrid_search(query: str, top_k_vector: int = 5, top_k_bm25: int = 5, final_top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Production Hybrid Retrieval:
    1. Vector semantic search
    2. BM25 keyword search
    3. Candidate deduplication & Reciprocal Rank Fusion (RRF)
    4. Cross-Encoder reranking
    """
    vector_results = vector_store.search(query, top_k=top_k_vector)
    bm25_results = bm25_engine.search(query, top_k=top_k_bm25)

    # Candidate Fusion with Reciprocal Rank Fusion (RRF)
    # RRF score = 1 / (60 + rank)
    combined: Dict[str, Dict[str, Any]] = {}
    
    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        if doc_id not in combined:
            combined[doc_id] = doc.copy()
            combined[doc_id]["rrf_score"] = 0.0
        combined[doc_id]["rrf_score"] += 1.0 / (60.0 + rank + 1.0)
        combined[doc_id]["vector_score"] = doc.get("vector_score", 0.0)

    for rank, doc in enumerate(bm25_results):
        doc_id = doc["id"]
        if doc_id not in combined:
            combined[doc_id] = doc.copy()
            combined[doc_id]["rrf_score"] = 0.0
        combined[doc_id]["rrf_score"] += 1.0 / (60.0 + rank + 1.0)
        combined[doc_id]["bm25_score"] = doc.get("bm25_score", 0.0)

    candidates = list(combined.values())

    # Rerank top candidates
    final_ranked = rerank_documents(query, candidates, top_k=final_top_k)
    return final_ranked
