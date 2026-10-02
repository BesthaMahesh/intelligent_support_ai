from typing import List, Dict, Any
from fastapi import APIRouter
from backend.observability.metrics import get_dashboard_kpis
from backend.observability.cost import get_token_and_cost_analytics
from backend.observability.audit import get_audit_trail_for_conversation

router = APIRouter(prefix="/api/metrics", tags=["Metrics & Observability"])

@router.get("")
def get_system_kpis():
    """Retrieve high-level support operations and KPI metrics."""
    return get_dashboard_kpis()

@router.get("/cost")
def get_cost_and_token_metrics():
    """Retrieve token consumption, INR cost analytics, and P50/P95 latency telemetry."""
    return get_token_and_cost_analytics()

@router.get("/audit/{conversation_id}")
def get_conversation_audit_trail(conversation_id: str):
    """Retrieve full audit trace for a specific conversation."""
    return get_audit_trail_for_conversation(conversation_id)
