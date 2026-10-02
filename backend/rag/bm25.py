import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

class BM25SearchEngine:
    """
    BM25 Keyword Search Engine for Exact Match & Term Frequency Indexing.
    """
    def __init__(self):
        self.bm25 = None
        self.corpus_documents = [] # list of dicts with doc_id, text, metadata

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index a collection of documents.
        Each doc has: {"id": str, "content": str, "metadata": dict}
        """
        self.corpus_documents = documents
        tokenized_corpus = [self._tokenize(doc["content"]) for doc in documents]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search indexed corpus using BM25.
        """
        if not self.bm25 or not self.corpus_documents:
            return []
            
        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []
            
        scores = self.bm25.get_scores(tokenized_query)
        scored_docs = []
        for idx, score in enumerate(scores):
            if score > 0:
                doc = self.corpus_documents[idx].copy()
                doc["bm25_score"] = float(score)
                scored_docs.append(doc)

        scored_docs.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_docs[:top_k]

bm25_engine = BM25SearchEngine()
