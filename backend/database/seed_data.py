import uuid
from datetime import datetime, timedelta
from backend.database.database import SessionLocal, init_db
from backend.database.models import User, Conversation, Message, Ticket, AuditLog
from backend.auth.authentication import seed_default_users
from backend.rag.ingestion import ingest_knowledge_base
from backend.api.chat import process_chat_message
from backend.schemas.chat import ChatRequest

def seed_sample_enterprise_data():
    """
    Populate realistic enterprise customer conversations and tickets for immediate demonstration.
    """
    init_db()
    seed_default_users()
    ingest_knowledge_base()
    
    db = SessionLocal()
    try:
        conv_count = db.query(Conversation).count()
        if conv_count > 0:
            return # Data already exists

        print("Seeding initial enterprise conversation scenarios...")

        # Scenario 1: Electronics Return FAQ
        req1 = ChatRequest(
            customer_id="CUS-8821",
            customer_name="Rajesh Kumar",
            message="What is the return policy for electronics products?",
            user_email="customer@support.ai"
        )
        process_chat_message(req1, db)

        # Scenario 2: Transactional Payment Pending Inquiry
        req2 = ChatRequest(
            customer_id="CUS-8821",
            customer_name="Rajesh Kumar",
            message="My payment was deducted but my order is still showing Payment Pending. Order ID is ORD-78231.",
            user_email="customer@support.ai"
        )
        process_chat_message(req2, db)

        # Scenario 3: Complex Multi-Agent Delay & Escalation
        req3 = ChatRequest(
            customer_id="CUS-8821",
            customer_name="Rajesh Kumar",
            message="I ordered a laptop three days ago and paid ₹72,999. The payment was successful but the order hasn't shipped. I contacted support yesterday and nobody helped me. Order ID ORD-91245.",
            user_email="customer@support.ai"
        )
        process_chat_message(req3, db)

        # Scenario 4: Multilingual / Tamil Inquiry
        req4 = ChatRequest(
            customer_id="CUS-7712",
            customer_name="Anand Venkatesh",
            message="வணக்கம் என் ஆர்டர் ORD-78231 எங்கே உள்ளது?",
            user_email="anand.v@example.com"
        )
        process_chat_message(req4, db)

        print("Successfully seeded 4 enterprise customer scenarios.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_enterprise_data()
