"""
pipeline.py — Knowledge-base build pipeline.

Replaces the old standalone ingest.py and the inline orchestration that was
previously scattered across ui_sidebar.py.  This module is the single place
that coordinates:  load → chunk → embed → index → chain.
"""

from typing import Optional, Tuple

from core.vectorstore import build_index
from core.chain import build_chain


def rebuild_knowledge_base() -> Tuple[Optional[object], Optional[object], list]:
    """
    Full pipeline: rebuild the FAISS index from all documents in the data
    folder, then construct a fresh RAG chain.

    Returns:
        (chain, retriever, errors)
        chain     — the LangChain RAG chain, or None on failure
        retriever — the FAISS retriever, or None on failure
        errors    — list of human-readable warning / error strings
    """
    vectorstore, errors = build_index()

    if vectorstore is None:
        return None, None, errors

    chain, retriever = build_chain(vectorstore)
    return chain, retriever, errors


if __name__ == "__main__":
    # CLI entry-point for manual re-indexing (replaces old ingest.py)
    print("🚀 Rebuilding knowledge base…")
    chain, retriever, errors = rebuild_knowledge_base()
    if chain:
        print("✨ Knowledge base is ready!")
    else:
        print("❌ No valid documents could be loaded.")
    if errors:
        print("⚠️  Warnings:")
        for err in errors:
            print(f"   • {err}")
