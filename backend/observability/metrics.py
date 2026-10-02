from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.database import SessionLocal
from backend.database.models import Conversation, Message, Ticket, AuditLog

def get_dashboard_kpis() -> Dict[str, Any]:
    """
    Calculate real production KPIs from database tables.
    """
    db = SessionLocal()
    try:
        total_conversations = db.query(Conversation).count()
        if total_conversations == 0:
            return {
                "has_data": False,
                "total_conversations": 0,
                "ai_assisted_conversations": 0,
                "open_tickets": 0,
                "human_escalations": 0,
                "avg_response_time_ms": 0.0,
                "resolution_rate_pct": 0.0,
                "intents_distribution": {},
                "sentiments_distribution": {},
                "escalation_rate_pct": 0.0,
                "ai_vs_human": {"ai": 0, "human": 0}
            }

        open_tickets = db.query(Ticket).filter(Ticket.status.in_(["OPEN", "IN_PROGRESS", "ESCALATED"])).count()
        human_escalations = db.query(Conversation).filter(Conversation.status == "escalated").count()
        resolved_conversations = db.query(Conversation).filter(Conversation.status == "resolved").count()
        ai_assisted = total_conversations - human_escalations

        # Calculate average latency from audit logs
        avg_latency = db.query(func.avg(AuditLog.latency_ms)).scalar() or 0.0
        
        # Calculate resolution rate
        resolution_rate = round((resolved_conversations / max(1, total_conversations)) * 100, 1)
        escalation_rate = round((human_escalations / max(1, total_conversations)) * 100, 1)

        # Intent distribution
        intent_counts = db.query(Conversation.intent, func.count(Conversation.id)).group_by(Conversation.intent).all()
        intents_dict = {intent or "general_faq": count for intent, count in intent_counts}

        # Sentiment distribution
        sentiment_counts = db.query(Conversation.sentiment, func.count(Conversation.id)).group_by(Conversation.sentiment).all()
        sentiments_dict = {sent or "neutral": count for sent, count in sentiment_counts}

        return {
            "has_data": True,
            "total_conversations": total_conversations,
            "ai_assisted_conversations": max(0, ai_assisted),
            "open_tickets": open_tickets,
            "human_escalations": human_escalations,
            "avg_response_time_ms": round(float(avg_latency), 1),
            "resolution_rate_pct": resolution_rate,
            "escalation_rate_pct": escalation_rate,
            "intents_distribution": intents_dict,
            "sentiments_distribution": sentiments_dict,
            "ai_vs_human": {
                "AI Resolved": max(0, ai_assisted),
                "Human Escalated": human_escalations
            }
        }
    finally:
        db.close()
