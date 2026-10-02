from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.database.database import init_db
from backend.auth.authentication import seed_default_users
from backend.rag.ingestion import ingest_knowledge_base
from backend.api import (
    chat_router,
    conversations_router,
    tickets_router,
    knowledge_router,
    evaluation_router,
    metrics_router,
    health_router,
    auth_router
)

app = FastAPI(
    title="Intelligent Support AI API",
    description="Enterprise Customer Support NLP & Generative AI Platform",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend and enterprise clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(tickets_router)
app.include_router(knowledge_router)
app.include_router(evaluation_router)
app.include_router(metrics_router)

@app.on_event("startup")
def on_startup():
    """Initialize database tables, seed default credentials, and ingest knowledge."""
    init_db()
    seed_default_users()
    ingested_chunks = ingest_knowledge_base()
    print(f"[{settings.APP_NAME}] Startup complete. Ingested {ingested_chunks} knowledge chunks into Vector DB & BM25.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
