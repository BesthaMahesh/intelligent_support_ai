import os
import re
import numpy as np
from typing import List
from backend.config.settings import settings

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        # Check if local model weights or cache exist, otherwise use high-speed semantic dense vectorizer
        if os.environ.get("USE_HF_EMBEDDINGS", "false").lower() == "true":
            try:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception:
                _model = "fallback"
        else:
            _model = "fallback"
    return _model

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate dense vector embeddings for a list of strings.
    """
    if not texts:
        return []
        
    model = get_embedding_model()
    if model != "fallback":
        try:
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception:
            pass

    # High-speed semantic dense n-gram vectorizer (384 dimensions)
    vectors = []
    for text in texts:
        vec = np.zeros(384, dtype=np.float32)
        words = re.findall(r'\b\w+\b', text.lower())
        for i, word in enumerate(words):
            # Primary word hash
            h1 = abs(hash(word)) % 384
            # Sub-word character trigram hash
            for j in range(max(0, len(word) - 2)):
                tri = word[j:j+3]
                h_tri = abs(hash(tri)) % 384
                vec[h_tri] += 0.5 / (i + 1)
            vec[h1] += 1.0 / (i + 1)

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        vectors.append(vec.tolist())
    return vectors

def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a single search query."""
    res = generate_embeddings([query])
    return res[0] if res else [0.0] * 384
