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
    Build a ChromaDB index from documents in the data folder.

    Chroma persists automatically to INDEX_FOLDER — no manual save needed.
    If the collection already exists it is deleted and rebuilt from scratch.

    Args:
        only_files: If provided, only index these specific filenames.

    Returns:
        Tuple of (Chroma vectorstore or None, all_chunks, list of loading errors).
    """
    documents, errors = load_documents(only_files)

    if not documents:
        return None, [], errors

    chunks = chunk_documents(documents)

    # Delete existing collection so rebuild is clean
    _delete_existing_collection()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=INDEX_FOLDER,
    )

    return vectorstore, chunks, errors


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
    This is a bonus over FAISS — no full rebuild needed.

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

def _delete_existing_collection() -> None:
    """Delete the Chroma collection if it exists, for a clean rebuild."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=INDEX_FOLDER)
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # Collection doesn't exist yet — that's fine
