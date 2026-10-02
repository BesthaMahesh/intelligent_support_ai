import os
import streamlit as st

def get_api_base_url() -> str:
    """Retrieve dynamic API Base URL from Streamlit secrets, env vars, or local defaults."""
    try:
        if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
            base = st.secrets["BACKEND_URL"].rstrip("/")
            return f"{base}/api" if not base.endswith("/api") else base
    except Exception:
        pass

    env_url = os.getenv("BACKEND_URL") or os.getenv("API_BASE_URL")
    if env_url:
        base = env_url.rstrip("/")
        return f"{base}/api" if not base.endswith("/api") else base

    return f"http://localhost:{settings.PORT}/api"

API_BASE_URL = get_api_base_url()


class EnterpriseAPIClient:
    """Client for Intelligent Support AI backend services."""
    
    @staticmethod
    def send_chat_message(
        message: str,
        conversation_id: Optional[str] = None,
        customer_id: str = "CUS-8821",
        customer_name: str = "Rajesh Kumar",
        user_email: str = "customer@support.ai"
    ) -> Dict[str, Any]:
        """Send chat message to backend pipeline."""
        # Try REST API first, if server is running standalone, or invoke local graph directly
        try:
            resp = requests.post(
                f"{API_BASE_URL}/chat",
                json={
                    "message": message,
                    "conversation_id": conversation_id,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "user_email": user_email
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # In-process direct execution fallback for seamless standalone Streamlit execution
        from backend.api.chat import process_chat_message
        from backend.schemas.chat import ChatRequest
        from backend.database.database import SessionLocal
        
        db = SessionLocal()
        try:
            req = ChatRequest(
                message=message,
                conversation_id=conversation_id,
                customer_id=customer_id,
                customer_name=customer_name,
                user_email=user_email
            )
            res = process_chat_message(req, db)
            return res.dict()
        finally:
            db.close()

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        from backend.observability.metrics import get_dashboard_kpis
        return get_dashboard_kpis()

    @staticmethod
    def get_customer_dashboard_data(customer_id: str = "CUS-8821") -> Dict[str, Any]:
        """Fetch customer-specific metrics and recent activity from real database records."""
        from backend.database.database import SessionLocal
        from backend.database.models import Ticket, Conversation, Message
        from backend.tools.order_api import MOCK_ORDERS
        
        db = SessionLocal()
        try:
            # Tickets for customer (or recent if customer matches)
            tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
            customer_tickets = [t for t in tickets if t.customer_id == customer_id or not customer_id]
            if not customer_tickets:
                customer_tickets = tickets[:5]

            # Conversations for customer
            conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
            customer_convs = [c for c in conversations if c.customer_id == customer_id or not customer_id]
            if not customer_convs:
                customer_convs = conversations[:5]

            # Customer Orders
            orders_list = [v for v in MOCK_ORDERS.values() if v.get("customer_id") == customer_id]
            if not orders_list:
                orders_list = list(MOCK_ORDERS.values())

            # Counts
            active_requests_count = len([t for t in customer_tickets if t.status in ["OPEN", "IN_PROGRESS", "WAITING_FOR_CUSTOMER", "ESCALATED"]])
            open_tickets_count = len([t for t in customer_tickets if t.status in ["OPEN", "ESCALATED"]])
            orders_in_progress = len([o for o in orders_list if o.get("order_status") in ["PAYMENT_PENDING", "CONFIRMED", "PROCESSING", "SHIPPED"]])
            pending_actions_count = len([t for t in customer_tickets if t.status == "WAITING_FOR_CUSTOMER"]) + (1 if any(o.get("order_status") == "PAYMENT_PENDING" for o in orders_list) else 0)
            resolved_count = len([t for t in customer_tickets if t.status in ["RESOLVED", "CLOSED"]]) + len([c for c in customer_convs if c.status == "resolved"])

            # Format recent requests
            recent_requests = []
            for t in customer_tickets[:4]:
                recent_requests.append({
                    "id": t.id,
                    "subject": t.title,
                    "status": t.status.replace("_", " ").title(),
                    "priority": t.priority.capitalize(),
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "Recently",
                    "updated_at": t.updated_at.strftime("%Y-%m-%d %H:%M") if t.updated_at else "Recently",
                    "category": t.intent.replace("_", " ").title() if t.intent else "General Support"
                })

            # Format recent conversations
            recent_conversations = []
            for c in customer_convs[:4]:
                last_msg = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).first()
                preview = (last_msg.content[:80] + "...") if last_msg and last_msg.content else "No messages yet."
                recent_conversations.append({
                    "id": c.id,
                    "title": f"Inquiry: {c.intent.replace('_', ' ').title() if c.intent else 'General Support'}",
                    "date": c.updated_at.strftime("%b %d, %Y") if c.updated_at else "Today",
                    "status": c.status.capitalize(),
                    "last_message": preview,
                    "unread": False
                })

            # Recommended Help Articles from Knowledge Base
            recommended_articles = [
                {"id": "ART-101", "title": "How do I track my order & courier dispatch?", "category": "Orders & Delivery", "read_time": "2 min read"},
                {"id": "ART-102", "title": "Standard 30-Day Return & Replacement Policy", "category": "Returns & Refunds", "read_time": "4 min read"},
                {"id": "ART-103", "title": "Resolving payment debited but order pending status", "category": "Payments", "read_time": "3 min read"},
                {"id": "ART-104", "title": "Electronics warranty registration & claim guide", "category": "Products & Warranty", "read_time": "5 min read"}
            ]

            return {
                "has_data": True,
                "active_requests_count": active_requests_count,
                "open_tickets_count": open_tickets_count,
                "orders_in_progress_count": orders_in_progress,
                "pending_actions_count": pending_actions_count,
                "resolved_count": resolved_count,
                "avg_response_time": "< 3 mins",
                "recent_requests": recent_requests,
                "recent_conversations": recent_conversations,
                "recent_orders": orders_list[:3],
                "recommended_articles": recommended_articles
            }
        except Exception as e:
            return {"has_data": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def get_customer_orders(customer_id: str = "CUS-8821") -> List[Dict[str, Any]]:
        """Retrieve orders for the customer."""
        from backend.tools.order_api import MOCK_ORDERS
        orders = [v for v in MOCK_ORDERS.values() if v.get("customer_id") == customer_id]
        if not orders:
            orders = list(MOCK_ORDERS.values())
        return orders

    @staticmethod
    def get_customer_tickets(customer_id: str = "CUS-8821") -> List[Dict[str, Any]]:
        """Retrieve support requests/tickets for the customer."""
        from backend.database.database import SessionLocal
        from backend.database.models import Ticket
        db = SessionLocal()
        try:
            tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
            res = []
            for t in tickets:
                res.append({
                    "id": t.id,
                    "customer_id": t.customer_id,
                    "customer_name": t.customer_name,
                    "order_id": t.order_id or "—",
                    "title": t.title,
                    "description": t.description,
                    "intent": t.intent.replace("_", " ").title() if t.intent else "General",
                    "priority": t.priority,
                    "status": t.status,
                    "assigned_to": t.assigned_to or "Support Desk",
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "Recently",
                    "updated_at": t.updated_at.strftime("%Y-%m-%d %H:%M") if t.updated_at else "Recently"
                })
            return res
        finally:
            db.close()

    @staticmethod
    def get_customer_conversations(customer_id: str = "CUS-8821") -> List[Dict[str, Any]]:
        """Retrieve customer conversations and message history."""
        from backend.database.database import SessionLocal
        from backend.database.models import Conversation, Message
        db = SessionLocal()
        try:
            convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
            result = []
            for c in convs:
                msgs = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.asc()).all()
                result.append({
                    "id": c.id,
                    "customer_id": c.customer_id,
                    "customer_name": c.customer_name,
                    "intent": c.intent.replace("_", " ").title() if c.intent else "General",
                    "status": c.status,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "",
                    "updated_at": c.updated_at.strftime("%Y-%m-%d %H:%M") if c.updated_at else "",
                    "messages": [
                        {
                            "id": m.id,
                            "sender": m.sender,
                            "content": m.content,
                            "created_at": m.created_at.strftime("%H:%M") if m.created_at else ""
                        }
                        for m in msgs
                    ]
                })
            return result
        finally:
            db.close()

    @staticmethod
    def get_cost_and_tokens() -> Dict[str, Any]:
        from backend.observability.cost import get_token_and_cost_analytics
        return get_token_and_cost_analytics()

    @staticmethod
    def list_tickets() -> List[Dict[str, Any]]:
        from backend.tools.ticket_api import list_all_tickets
        return list_all_tickets()

    @staticmethod
    def get_audit_trail(conversation_id: str) -> List[Dict[str, Any]]:
        from backend.observability.audit import get_audit_trail_for_conversation
        return get_audit_trail_for_conversation(conversation_id)

    @staticmethod
    def run_evaluation() -> Dict[str, Any]:
        from backend.evaluation.llm_evaluation import run_full_system_evaluation
        summary = run_full_system_evaluation()
        return summary.dict()
