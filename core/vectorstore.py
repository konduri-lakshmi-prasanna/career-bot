"""
vectorstore.py — FAISS vector store management.

Changes vs original:
  • build_index() now also returns `all_chunks` so the caller can pass them
    to HybridRetriever without re-loading the documents.
  • load_index() returns a (vectorstore, all_chunks) tuple — chunks are stored
    as a JSON sidecar file alongside the FAISS index.
"""

import os
import json
from typing import Optional, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from core.config import INDEX_FOLDER, EMBEDDING_MODEL
from core.loaders import load_documents
from core.chunkers import chunk_documents


# ── Sidecar path for chunk text cache ────────────────────────────────────────
_CHUNKS_CACHE = os.path.join(INDEX_FOLDER, "chunks_cache.json")


# ── Singleton-style embeddings (cached at module level) ──────────────────────
_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached embeddings model instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def _save_chunks(chunks: List[Document]) -> None:
    """Persist chunk text and metadata to a JSON sidecar file."""
    os.makedirs(INDEX_FOLDER, exist_ok=True)
    serialised = [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in chunks
    ]
    with open(_CHUNKS_CACHE, "w", encoding="utf-8") as f:
        json.dump(serialised, f, ensure_ascii=False)


def _load_chunks() -> List[Document]:
    """Load chunks from the JSON sidecar file, or return [] if absent."""
    if not os.path.exists(_CHUNKS_CACHE):
        return []
    try:
        with open(_CHUNKS_CACHE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Document(page_content=r["page_content"], metadata=r["metadata"]) for r in raw]
    except Exception:
        return []


def build_index(
    only_files: Optional[List[str]] = None,
) -> Tuple[Optional[FAISS], List[Document], list]:
    """
    Build a FAISS index from documents in the data folder.

    Args:
        only_files: If provided, only index these specific filenames.

    Returns:
        Tuple of (FAISS vectorstore or None, all_chunks, list of loading errors).
    """
    documents, errors = load_documents(only_files)

    if not documents:
        return None, [], errors

    chunks      = chunk_documents(documents)
    embeddings  = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_FOLDER)

    # Persist chunks for hybrid retrieval
    _save_chunks(chunks)

    return vectorstore, chunks, errors


def load_index() -> Tuple[Optional[FAISS], List[Document]]:
    """
    Load an existing FAISS index from disk.

    Returns:
        Tuple of (FAISS vectorstore or None, all_chunks list).
    """
    if not os.path.exists(INDEX_FOLDER):
        return None, []
    try:
        vectorstore = FAISS.load_local(
            INDEX_FOLDER,
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
        chunks = _load_chunks()
        return vectorstore, chunks
    except Exception:
        return None, []