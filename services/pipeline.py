"""
services/pipeline.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: rebuild_knowledge_base() returned (chain, retriever, errors).
        load_existing_knowledge_base() returned (chain, retriever).
        Callers stored chain + retriever in session_state manually.

AFTER:  rebuild_knowledge_base() returns only errors.
        load_existing_knowledge_base() returns a bool.
        run_query(query) is the single entry point for all chat queries —
        it calls pipeline.run() which executes all 6 rag-core stages.
        No chain or retriever ever leaks into the UI layer.
"""

from core.careerbot_pipeline import CareerBotPipeline
from rag_core.db.chromadb_store import get_collection

_pipeline: CareerBotPipeline | None = None


def get_pipeline() -> CareerBotPipeline:
    """Return (or create) the singleton CareerBotPipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = CareerBotPipeline()
    return _pipeline


def rebuild_knowledge_base() -> list:
    """
    Rebuild the knowledge base. Returns list of error strings.
    """
    pipeline = get_pipeline()
    return pipeline.rebuild()


def load_existing_knowledge_base() -> bool:
    """
    Returns True if the ChromaDB collection exists and has documents.
    """
    try:
        collection = get_collection(CareerBotPipeline.COLLECTION)
        return collection.count() > 0
    except Exception:
        return False


def run_query(query: str) -> str:
    """
    Run the full 6-stage RAG pipeline for a user query.
    Stages: rewrite → retrieve → rerank → refine → generate
    """
    pipeline = get_pipeline()
    return pipeline.run(query)