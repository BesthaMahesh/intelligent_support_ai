from datetime import datetime
import json
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), default="customer") # "customer", "agent", "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(50), primary_key=True, index=True) # e.g. CONV-1001
    customer_id = Column(String(50), index=True, nullable=False)
    customer_name = Column(String(100), default="Customer")
    intent = Column(String(50), default="general_faq")
    sentiment = Column(String(30), default="neutral")
    urgency = Column(String(30), default="low")
    status = Column(String(30), default="active") # active, escalated, resolved, closed
    channel = Column(String(30), default="web_chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(50), primary_key=True, index=True)
    conversation_id = Column(String(50), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(30), nullable=False) # "customer", "ai", "agent", "system"
    content = Column(Text, nullable=False)
    language = Column(String(30), default="English")
    intent = Column(String(50), nullable=True)
    sentiment = Column(String(30), nullable=True)
    entities_json = Column(Text, default="{}")
    tool_calls_json = Column(Text, default="[]")
    guardrails_passed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String(50), primary_key=True, index=True) # e.g. TKT-458921
    customer_id = Column(String(50), index=True, nullable=False)
    customer_name = Column(String(100), default="Customer")
    order_id = Column(String(50), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    intent = Column(String(50), default="general_faq")
    priority = Column(String(30), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="OPEN") # OPEN, IN_PROGRESS, WAITING_FOR_CUSTOMER, ESCALATED, RESOLVED, CLOSED
    assigned_to = Column(String(100), default="Unassigned")
    ai_recommended_action = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(50), primary_key=True, index=True)
    request_id = Column(String(50), index=True, nullable=False)
    conversation_id = Column(String(50), index=True, nullable=False)
    user_email = Column(String(100), default="customer@support.ai")
    action = Column(String(50), default="chat_interaction")
    input_text = Column(Text, nullable=False)
    classification_json = Column(Text, default="{}")
    retrieved_docs_json = Column(Text, default="[]")
    tool_calls_json = Column(Text, default="[]")
    tool_results_json = Column(Text, default="[]")
    model = Column(String(50), default="llama-3.3-70b-versatile")
    prompt_version = Column(String(20), default="v1.0.0")
    guardrail_results_json = Column(Text, default="{}")
    final_response = Column(Text, nullable=False)
    latency_ms = Column(Float, default=0.0)
    token_usage_json = Column(Text, default="{}")
    cost_inr = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String(50), primary_key=True, index=True)
    conversation_id = Column(String(50), index=True, nullable=False)
    message_id = Column(String(50), nullable=True)
    rating = Column(Integer, default=5) # 1-5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
