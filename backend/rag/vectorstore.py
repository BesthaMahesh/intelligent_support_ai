import os
import numpy as np
from typing import List, Dict, Any, Optional
from backend.config.settings import settings
from .embeddings import generate_embeddings, generate_query_embedding

class VectorStoreManager:
    """
    Vector Store Manager with ChromaDB and in-memory cosine similarity fallback.
    """
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.in_memory_docs = [] # fallback
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.chroma_client = None
            self.collection = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Store chunks in Vector DB.
        doc: {"id": str, "content": str, "metadata": dict}
        """
        if not documents:
            return
            
        texts = [d["content"] for d in documents]
        embeddings = generate_embeddings(texts)
        ids = [d["id"] for d in documents]
        metadatas = [d["metadata"] for d in documents]

        # Clean metadata values for chroma compatibility (strings/ints/floats)
        clean_metas = []
        for m in metadatas:
            clean = {k: str(v) if not isinstance(v, (int, float, bool, str)) else v for k, v in m.items()}
            clean_metas.append(clean)

        if self.collection:
            try:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=clean_metas
                )
            except Exception:
                pass

        # Also populate in-memory list for fast fallback
        self.in_memory_docs = []
        for i in range(len(documents)):
            self.in_memory_docs.append({
                "id": ids[i],
                "content": texts[i],
                "metadata": clean_metas[i],
                "embedding": np.array(embeddings[i], dtype=np.float32)
            })

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Vector similarity search.
        """
        query_vec = generate_query_embedding(query)

        if self.collection:
            try:
                res = self.collection.query(
                    query_embeddings=[query_vec],
                    n_results=top_k
                )
                results = []
                if res and res["ids"] and len(res["ids"][0]) > 0:
                    for i in range(len(res["ids"][0])):
                        dist = res["distances"][0][i] if "distances" in res and res["distances"] else 0.5
                        sim = 1.0 - dist if dist <= 1.0 else 0.5
                        results.append({
                            "id": res["ids"][0][i],
                            "content": res["documents"][0][i],
                            "metadata": res["metadatas"][0][i],
                            "vector_score": float(sim)
                        })
                    return results
            except Exception:
                pass

        # In-memory cosine search fallback
        if not self.in_memory_docs:
            return []

        q_arr = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 0:
            q_arr = q_arr / q_norm

        scored = []
        for doc in self.in_memory_docs:
            d_arr = doc["embedding"]
            d_norm = np.linalg.norm(d_arr)
            score = float(np.dot(q_arr, d_arr / d_norm)) if d_norm > 0 else 0.0
            scored.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "vector_score": score
            })

        scored.sort(key=lambda x: x["vector_score"], reverse=True)
        return scored[:top_k]

vector_store = VectorStoreManager()
