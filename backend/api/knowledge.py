import os
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.rag.retriever import retrieve_knowledge
from backend.rag.ingestion import ingest_knowledge_base, parse_markdown_metadata

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

class SearchKnowledgeRequest(BaseModel):
    query: str
    top_k: int = 4

@router.get("")
def list_knowledge_documents():
    """List all knowledge base documents with categories and version metadata."""
    knowledge_dir = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge"
    if not os.path.exists(knowledge_dir):
        return []

    docs = []
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith((".md", ".txt")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
                    meta = parse_markdown_metadata(text)
                    doc_id = meta.get("document_id", f"DOC-{Path(file).stem}")
                    title_line = text.splitlines()[0].replace("#", "").strip() if text else Path(file).stem
                    docs.append({
                        "document_id": doc_id,
                        "title": title_line,
                        "category": meta.get("category", Path(root).name),
                        "version": meta.get("version", "1.0"),
                        "last_updated": meta.get("last_updated", "2026-10-01"),
                        "source": meta.get("source", "Standard Policy"),
                        "file_name": file,
                        "content_preview": text[:300] + "..."
                    })
                except Exception:
                    pass
    return docs

@router.post("/search")
def search_knowledge_base(payload: SearchKnowledgeRequest):
    """Execute hybrid vector + BM25 search across enterprise knowledge documents."""
    sources, context_str = retrieve_knowledge(payload.query, top_k=payload.top_k)
    return {
        "query": payload.query,
        "sources": sources,
        "context_str": context_str
    }

@router.post("/ingest")
def trigger_knowledge_ingestion():
    """Re-index all documents in data/knowledge into ChromaDB and BM25 index."""
    chunks_indexed = ingest_knowledge_base()
    return {
        "status": "success",
        "chunks_indexed": chunks_indexed,
        "message": f"Successfully indexed {chunks_indexed} knowledge chunks."
    }
