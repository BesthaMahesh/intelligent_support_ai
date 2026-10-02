from .chat import router as chat_router
from .conversations import router as conversations_router
from .tickets import router as tickets_router
from .knowledge import router as knowledge_router
from .evaluation import router as evaluation_router
from .metrics import router as metrics_router
from .health import router as health_router
from .auth import router as auth_router

__all__ = [
    "chat_router",
    "conversations_router",
    "tickets_router",
    "knowledge_router",
    "evaluation_router",
    "metrics_router",
    "health_router",
    "auth_router"
]
