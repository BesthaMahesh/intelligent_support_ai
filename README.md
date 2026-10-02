# Intelligent Support AI

> **Enterprise Customer Support Intelligence Platform**  
> Production-Scale NLP, RAG, Multi-Agent Orchestration, Guardrails & Human-in-the-Loop Architecture.

---

## 🌟 Overview & Philosophy

**Intelligent Support AI** is NOT a generic chatbot clone. It is an enterprise-grade AI customer support intelligence platform engineered to strictly distinguish between:
1. **Informational Inquiries** (e.g., *"What is your return policy for electronics?"*) → High-precision Hybrid RAG Retrieval (Vector + BM25 + Cross-Encoder Reranker).
2. **Transactional Inquiries** (e.g., *"My payment was deducted but my order is still showing Payment Pending. Order ID ORD-78231."*) → Safe Business API Tool Orchestration.
3. **Complex Escalation Scenarios** (e.g., *"I ordered a laptop 3 days ago and paid ₹72,999. The payment was successful but order hasn't shipped. Nobody helped me."*) → Multi-Agent Supervisor + Deterministic Business Rules + Automated Incident Ticket Creation + Human Review Queue.

### Critical Production Principle
**THE LLM IS NOT THE SOURCE OF TRUTH FOR BUSINESS DATA.**
- **Payment Status**: Verified Payment Gateway & Ledger API
- **Order Status**: Order Management Microservice
- **Shipment Status**: Real-Time Logistics Telemetry
- **Customer History**: Enterprise CRM
- **Policies**: Authoritative Hybrid RAG Knowledge Base

---

## 🏛️ High-Level System Architecture

```
                       CUSTOMER
                           │
                           ▼
                ENTERPRISE CHAT UI (Streamlit)
                           │
                           ▼
                  INPUT GATEWAY (FastAPI)
                           │
                           ▼
               INPUT GUARDRAILS & PII SAFETY
                           │
                           ▼
                 NLP UNDERSTANDING LAYER
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
         Intent        Sentiment        Entities
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                 SUPERVISOR ROUTER
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
        FAQ / RAG     BUSINESS TOOLS   HUMAN ESCALATION
     (Vector + BM25)   (Order/Pay/Ship)  (Desk Queue)
           │               │
           └───────┬───────┘
                   │
                   ▼
         BUSINESS RULES ENGINE (Deterministic)
                   │
                   ▼
         RESPONSE AGENT (Groq / Llama 3.3 70B)
                   │
                   ▼
            OUTPUT GUARDRAILS
                   │
           ┌───────┴───────┐
           ▼               ▼
      AI RESPONSE    HUMAN REVIEW
           │
           ▼
     OBSERVABILITY & AUDIT TRAIL (Tokens, INR Cost, Latency, Traces)
```

---

## 🛠️ Technology Stack

- **Primary Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Agent Orchestration**: LangGraph, LangChain
- **Frontend / Enterprise UI**: Streamlit with Role-Based Access Control (Admin, Agent, Customer)
- **NLP & Language Layer**: Custom Multilingual Engine (English, Tamil, Hindi, Telugu, etc.), Regex PII Redaction, Token Normalizers
- **RAG & Retrieval**: ChromaDB, Rank-BM25, Sentence Transformers (`all-MiniLM-L6-v2`), Cross-Encoder Reranker
- **LLM Provider**: Groq API (`llama-3.3-70b-versatile`) with multi-provider abstraction and deterministic fallback
- **Database & Persistence**: SQLite (Production-ready SQLAlchemy ORM schema)
- **Evaluation & Benchmarking**: Scikit-learn (Accuracy, Macro-F1, Precision, Recall, MRR, NDCG, Groundedness)

---

## 🚀 Getting Started

### 1. Installation
```bash
# Clone or navigate to the project directory
cd intelligent_support_ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Create a `.env` file from `.env.example`:
```env
APP_NAME="Intelligent Support AI"
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
SECRET_KEY=enterprise-support-ai-super-secret-jwt-key-2026-production-ready
```

### 3. Run the Applications

**Run the Streamlit Enterprise UI**:
```bash
streamlit run app.py
```

**Run the FastAPI Backend**:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 👥 Default Demo Credentials

| Role | Email | Password | Access / View |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@support.ai` | `admin123` | Full AI Operations, Evaluation, Audit, Latency & Cost Analytics |
| **Support Specialist** | `agent@support.ai` | `agent123` | Human Review Queue, Conversations, Tickets, AI Assistant |
| **Customer** | `customer@support.ai` | `customer123` | Customer Support Workspace, Order Tracking, Knowledge Base |

---

## 🧪 Running Automated Tests

Run the full pytest test suite:
```bash
pytest
```
Tests cover authentication, NLP classification, RAG retrieval, business tools, security guardrails, LangGraph orchestration, and evaluation benchmarks.
