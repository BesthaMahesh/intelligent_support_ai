import time
from fastapi import APIRouter
from backend.config.settings import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
def check_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "timestamp": time.time()
    }
