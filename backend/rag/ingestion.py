import os
import re
from pathlib import Path
from typing import List, Dict, Any
from backend.config.settings import settings
from .vectorstore import vector_store
from .bm25 import bm25_engine

def parse_markdown_metadata(content: str) -> Dict[str, str]:
    """Extract metadata headers from markdown files."""
    meta = {}
    lines = content.splitlines()
    for line in lines:
        if line.startswith("**Document ID**"):
            meta["document_id"] = line.split(":")[-1].strip().replace("*", "")
        elif line.startswith("**Category**"):
            meta["category"] = line.split(":")[-1].strip().replace("*", "")
        elif line.startswith("**Version**"):
            meta["version"] = line.split(":")[-1].strip().replace("*", "")
        elif line.startswith("**Last Updated**"):
            meta["last_updated"] = line.split(":")[-1].strip().replace("*", "")
        elif line.startswith("**Authoritative Source**"):
            meta["source"] = line.split(":")[-1].strip().replace("*", "")
    return meta

def chunk_document(content: str, metadata: Dict[str, Any], doc_name: str) -> List[Dict[str, Any]]:
    """
    Chunk markdown documents by headers and semantic sections.
    """
    title_match = re.search(r'^#\s+(.+)$', content, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else doc_name.replace("_", " ").title()
    
    sections = re.split(r'\n(?=##\s+)', content)
    chunks = []
    
    for idx, sec in enumerate(sections):
        sec_clean = sec.strip()
        if not sec_clean:
            continue
            
        sec_header_match = re.search(r'^##\s+(.+)$', sec_clean, flags=re.MULTILINE)
        section_title = sec_header_match.group(1).strip() if sec_header_match else "Overview"
        
        chunk_meta = {
            "document_id": metadata.get("document_id", f"DOC-{doc_name}"),
            "title": title,
            "section": section_title,
            "category": metadata.get("category", "general"),
            "version": metadata.get("version", "1.0"),
            "source": metadata.get("source", "Knowledge Base"),
            "last_updated": metadata.get("last_updated", "2026-10-01")
        }
        
        chunks.append({
            "id": f"{chunk_meta['document_id']}-CHK-{idx+1}",
            "content": f"# {title} - {section_title}\n\n{sec_clean}",
            "metadata": chunk_meta
        })
        
    return chunks

def ingest_knowledge_base(knowledge_dir: str = None) -> int:
    """
    Ingest all markdown documents from data/knowledge directory into Vector DB & BM25 index.
    """
    if knowledge_dir is None:
        knowledge_dir = str(Path(__file__).resolve().parent.parent.parent / "data" / "knowledge")
        
    if not os.path.exists(knowledge_dir):
        return 0
        
    all_chunks = []
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                    meta = parse_markdown_metadata(text)
                    doc_name = Path(file).stem
                    chunks = chunk_document(text, meta, doc_name)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error processing knowledge doc {file}: {e}")
                    
    if all_chunks:
        vector_store.add_documents(all_chunks)
        bm25_engine.index_documents(all_chunks)
        
    return len(all_chunks)
