import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Intelligent Support AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # LLM Settings
    LLM_PROVIDER: str = Field(default="groq", description="Provider: groq, openai, gemini, mock")
    GROQ_API_KEY: str = Field(default=os.getenv("GROQ_API_KEY", ""))
    GROQ_MODEL: str = Field(default="openai/gpt-oss-120b")
    
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Security
    SECRET_KEY: str = "enterprise-support-ai-super-secret-jwt-key-2026-production-ready"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/support_ai.db"
    
    # RAG
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    TOP_K_RETRIEVAL: int = 4
    RERANK_TOP_K: int = 3
    
    # Guardrails
    ENABLE_GUARDRAILS: bool = True
    MAX_INPUT_CHARS: int = 2000
    CONFIDENCE_THRESHOLD: float = 0.65

    # Cost Tracking (INR rates)
    INR_PER_USD: float = 86.50
    GROQ_INPUT_COST_PER_1K: float = 0.005
    GROQ_OUTPUT_COST_PER_1K: float = 0.007
    OPENAI_INPUT_COST_PER_1K: float = 0.013
    OPENAI_OUTPUT_COST_PER_1K: float = 0.052

    # LangSmith / Observability
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "intelligent-support-ai"

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
