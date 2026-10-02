import pytest
from backend.rag.ingestion import ingest_knowledge_base
from backend.rag.retriever import retrieve_knowledge, rewrite_query

def test_knowledge_ingestion():
    chunks_count = ingest_knowledge_base()
    assert chunks_count > 0

def test_query_rewriting():
    q = "What is the return policy for electronics?"
    rewritten = rewrite_query(q)
    assert "return" in rewritten.lower()

def test_hybrid_retrieval():
    ingest_knowledge_base()
    sources, context = retrieve_knowledge("Electronics return policy 30 days")
    assert len(sources) > 0
    assert "Electronics" in context or "Return" in context
