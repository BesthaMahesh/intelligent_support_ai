import re
from typing import List, Dict, Any, Tuple
from backend.config.settings import settings
from .hybrid_search import hybrid_search

CANONICAL_REWRITES = {
    r'(?i)return.*?(electronic|phone|laptop|headphone|device)': "electronics return policy 30 days replacement condition defective DOA",
    r'(?i)return.*?(cloth|shirt|shoe|apparel)': "clothing apparel return policy tags unworn",
    r'(?i)ship.*?(time|charge|sla|cost|how long|delay)': "shipping delivery dispatch timelines metros charges express",
    r'(?i)pay.*?(pending|deduct|debit|bank|webhook)': "payment deducted pending webhook reconciliation 15 minutes",
    r'(?i)refund.*?(time|process|status|how long)': "refund timelines UPI card netbanking financial authorization limits",
    r'(?i)warranty.*?(electronic|device|laptop)': "electronics brand manufacturer warranty service centers 1-year",
    r'(?i)panam.*?(thirumba|kedaikala)': "refund payment reconciliation failure turnaround time",
    r'(?i)paise.*?(kat|kat gaye|nahi mila)': "payment debited account deducted order pending 15 minutes"
}

def rewrite_query(query: str) -> str:
    """
    Rewrite ambiguous or multilingual conversational queries into canonical knowledge retrieval keys.
    """
    if not query:
        return ""
        
    for pattern, canonical in CANONICAL_REWRITES.items():
        if re.search(pattern, query):
            return f"{query} {canonical}"
            
    return query

def retrieve_knowledge(
    query: str,
    category_filter: str = None,
    top_k: int = 3
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Execute full production RAG retrieval:
    1. Query Rewriting
    2. Hybrid Search (Vector + BM25)
    3. Reranking
    4. Formatted Context String for LLM
    """
    rewritten_query = rewrite_query(query)
    
    ranked_chunks = hybrid_search(
        query=rewritten_query,
        top_k_vector=settings.TOP_K_RETRIEVAL + 2,
        top_k_bm25=settings.TOP_K_RETRIEVAL + 2,
        final_top_k=top_k or settings.RERANK_TOP_K
    )

    if not ranked_chunks:
        return [], ""

    # Build compressed, well-structured context for LLM grounding
    context_blocks = []
    sources = []
    
    for doc in ranked_chunks:
        meta = doc.get("metadata", {})
        title = meta.get("title", "Knowledge Base")
        sec = meta.get("section", "")
        doc_id = meta.get("document_id", "")
        content = doc.get("content", "")
        
        sources.append({
            "document_id": doc_id,
            "title": title,
            "section": sec,
            "category": meta.get("category", ""),
            "relevance_score": doc.get("rerank_score", 0.0),
            "snippet": content[:200] + "..."
        })
        
        context_blocks.append(f"--- Document: {title} ({doc_id}) [{sec}] ---\n{content}\n")

    context_str = "\n".join(context_blocks)
    return sources, context_str

class HybridRetriever:
    """Wrapper class providing object-oriented access to knowledge retrieval."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def retrieve(self, query: str, category_filter: str = None, top_k: int = 3):
        sources, context_str = retrieve_knowledge(query, category_filter=category_filter, top_k=top_k)
        return sources

