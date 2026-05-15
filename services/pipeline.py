"""
pipeline.py — Knowledge-base build pipeline.

Changes vs original:
  • build_index() now returns (vectorstore, all_chunks, errors).
  • rebuild_knowledge_base() passes all_chunks to build_chain() so the
    HybridRetriever can be constructed in one go.
"""

from typing import Optional, Tuple, List

from langchain_core.documents import Document

from core.vectorstore import build_index, load_index
from core.chain import build_chain


def rebuild_knowledge_base() -> Tuple[Optional[object], Optional[object], list]:
    """
    Full pipeline: rebuild the FAISS index from all documents in the data
    folder, then construct a fresh RAG chain (with hybrid retrieval).

    Returns:
        (chain, retriever, errors)
        chain     — the LangChain RAG chain, or None on failure
        retriever — HybridRetriever or FAISS retriever, or None on failure
        errors    — list of human-readable warning / error strings
    """
    vectorstore, all_chunks, errors = build_index()

    if vectorstore is None:
        return None, None, errors

    chain, retriever = build_chain(vectorstore, all_chunks)
    return chain, retriever, errors


def load_existing_knowledge_base() -> Tuple[Optional[object], Optional[object]]:
    """
    Load an already-built index and wire up the chain without re-indexing.

    Returns:
        (chain, retriever) — both None if no index found.
    """
    vectorstore, all_chunks = load_index()
    if vectorstore is None:
        return None, None

    chain, retriever = build_chain(vectorstore, all_chunks)
    return chain, retriever


if __name__ == "__main__":
    # CLI entry-point for manual re-indexing
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