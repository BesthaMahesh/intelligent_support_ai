import sys
import os

# Add root directory to sys.path for test resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.database import init_db
from backend.rag.ingestion import ingest_knowledge_base

# Initialize database and knowledge base for test environment
init_db()
ingest_knowledge_base()
