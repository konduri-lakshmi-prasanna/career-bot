"""
vectorstore.py — ChromaDB vector store management.

REPLACES: FAISS-based vectorstore.py
CHANGES:
  • Uses Chroma instead of FAISS for persistent, file-based storage.
  • No more chunks_cache.json sidecar — chunks are loaded directly from Chroma.
  • build_index() and load_index() return identical signatures to the original,
    so pipeline.py, chain.py, and hybrid_retriever.py need minimal changes.
  • Chroma auto-persists on every write — no manual save_local() needed.
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from typing import Optional, List, Tuple


from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from core.config import INDEX_FOLDER, EMBEDDING_MODEL
from core.loaders import load_documents
from core.chunkers import chunk_documents

# Collection name inside ChromaDB
COLLECTION_NAME = "careerbot"

# ── Singleton embeddings (cached at module level) ─────────────────────────────
_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached embeddings model instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def build_index(
    only_files: Optional[List[str]] = None,
) -> Tuple[Optional[Chroma], List[Document], list]:
    """
    Persistently index documents into ChromaDB.

    - If the collection already exists, NEW files are ADDED to it (not wiped).
    - Already-indexed files (same source_file metadata) are skipped to avoid
      duplicates.
    - Chroma auto-persists on every write — no manual save needed.

    Args:
        only_files: If provided, only index these specific filenames.

    Returns:
        Tuple of (Chroma vectorstore or None, all_chunks, list of loading errors).
    """
    documents, errors = load_documents(only_files)

    if not documents:
        # Even if no new docs, return existing vectorstore if it exists
        vectorstore, all_chunks = load_index()
        return vectorstore, all_chunks, errors

    chunks = chunk_documents(documents)

    # Open (or create) the persistent collection
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=INDEX_FOLDER,
    )

    # Find which source files are already indexed — skip them to avoid duplicates
    already_indexed = _get_indexed_sources(vectorstore)
    new_chunks = [
        c for c in chunks
        if c.metadata.get("source_file", c.metadata.get("source", "")) not in already_indexed
    ]

    if new_chunks:
        vectorstore.add_documents(new_chunks)

    # Return ALL chunks (old + new) for BM25 hybrid search
    results = vectorstore.get(include=["documents", "metadatas"])
    all_chunks = [
        Document(page_content=text, metadata=meta or {})
        for text, meta in zip(results["documents"], results["metadatas"])
    ]

    return vectorstore, all_chunks, errors


def load_index() -> Tuple[Optional[Chroma], List[Document]]:
    """
    Load an existing ChromaDB index from disk.

    Chunks are fetched directly from Chroma — no sidecar JSON needed.

    Returns:
        Tuple of (Chroma vectorstore or None, all_chunks list).
    """
    if not os.path.exists(INDEX_FOLDER):
        return None, []

    try:
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=INDEX_FOLDER,
        )

        # Verify the collection actually has documents
        count = vectorstore._collection.count()
        if count == 0:
            return None, []

        # Retrieve all stored chunks for BM25 hybrid search
        results = vectorstore.get(include=["documents", "metadatas"])
        chunks = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(results["documents"], results["metadatas"])
        ]

        return vectorstore, chunks

    except Exception as e:
        print(f"[vectorstore] Failed to load ChromaDB index: {e}")
        return None, []


def add_documents(new_chunks: List[Document]) -> bool:
    """
    Incrementally add new documents to an existing Chroma collection.
    Returns True on success, False on failure.
    """
    try:
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=INDEX_FOLDER,
        )
        vectorstore.add_documents(new_chunks)
        return True
    except Exception as e:
        print(f"[vectorstore] Failed to add documents: {e}")
        return False


# ── Private helpers ────────────────────────────────────────────────────────────

def _get_indexed_sources(vectorstore: Chroma) -> set:
    """Return a set of source filenames already present in the collection."""
    try:
        results = vectorstore.get(include=["metadatas"])
        sources = set()
        for meta in results["metadatas"]:
            if meta:
                src = meta.get("source_file") or meta.get("source", "")
                if src:
                    sources.add(src)
        return sources
    except Exception:
        return set()


def clear_index() -> None:
    """
    Completely wipe the ChromaDB collection.
    Call this only when you explicitly want to start fresh.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=INDEX_FOLDER)
        client.delete_collection(COLLECTION_NAME)
        print("[vectorstore] Collection cleared.")
    except Exception:
        pass