import numpy as np
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.database import SessionLocal
from backend.database.models import AuditLog

def get_token_and_cost_analytics() -> Dict[str, Any]:
    """
    Retrieve real token usage, cost analytics, and latency distributions (P50, P95).
    """
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).all()
        if not logs:
            return {
                "has_data": False,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "avg_tokens_per_interaction": 0,
                "total_cost_inr": 0.0,
                "total_llm_calls": 0,
                "latency_p50_ms": 0.0,
                "latency_p95_ms": 0.0,
                "latency_avg_ms": 0.0
            }

        total_input = 0
        total_output = 0
        total_cost = 0.0
        latencies = []

        import json
        for log in logs:
            try:
                tok_data = json.loads(log.token_usage_json) if log.token_usage_json else {}
                total_input += tok_data.get("input_tokens", 0)
                total_output += tok_data.get("output_tokens", 0)
            except Exception:
                pass
            
            total_cost += (log.cost_inr or 0.0)
            if log.latency_ms:
                latencies.append(float(log.latency_ms))

        total_tokens = total_input + total_output
        llm_calls = len(logs)
        avg_tokens = round(total_tokens / max(1, llm_calls), 1)

        p50 = round(float(np.percentile(latencies, 50)), 2) if latencies else 0.0
        p95 = round(float(np.percentile(latencies, 95)), 2) if latencies else 0.0
        avg_lat = round(float(np.mean(latencies)), 2) if latencies else 0.0

        return {
            "has_data": True,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "avg_tokens_per_interaction": avg_tokens,
            "total_cost_inr": round(total_cost, 2),
            "total_llm_calls": llm_calls,
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "latency_avg_ms": avg_lat
        }
    finally:
        db.close()
