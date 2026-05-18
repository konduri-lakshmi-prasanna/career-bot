"""
pipeline.py — refactored to use CareerBotPipeline from rag-core.

Before: careerbot built its own chain, vectorstore, retriever here.
After:  all of that is delegated to CareerBotPipeline which extends
        the shared rag-core IRagPipeline interface.

Low coupling: ui/sidebar.py and ui/tabs.py never touch RAG logic directly.
"""

from core.careerbot_pipeline import CareerBotPipeline

# Singleton — one pipeline instance for the whole app
_pipeline = None


def get_pipeline() -> CareerBotPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = CareerBotPipeline()
    return _pipeline


def rebuild_knowledge_base():
    """Called by sidebar when user uploads documents."""
    pipeline = get_pipeline()
    errors = pipeline.rebuild()
    chain = pipeline._chain
    retriever = pipeline._retriever
    return chain, retriever, errors


def load_existing_knowledge_base():
    """Called on app startup to restore existing index."""
    pipeline = get_pipeline()
    return pipeline._chain, pipeline._retriever