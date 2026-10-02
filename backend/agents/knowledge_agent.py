import time
from typing import Dict, Any
from backend.rag.retriever import retrieve_knowledge

class KnowledgeAgent:
    """
    Knowledge Agent: Performs hybrid retrieval, reranking, and context preparation.
    """
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        query = state.get("sanitized_message", "")
        
        sources, context_str = retrieve_knowledge(query=query)
        latency = round((time.time() - start) * 1000, 2)

        return {
            "retrieved_context": context_str,
            "retrieved_sources": sources,
            "retrieval_latency_ms": latency
        }
