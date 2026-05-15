"""
vectorstore.py — FAISS vector store management.
Handles building, saving, and loading the FAISS index.
"""

import os
from typing import Optional, List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from core.config import INDEX_FOLDER, EMBEDDING_MODEL
from core.loaders import load_documents
from core.chunkers import chunk_documents


# ── Singleton-style embeddings (cached at module level) ──────────────────────
_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached embeddings model instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def build_index(only_files: Optional[List[str]] = None):
    """
    Build a FAISS index from documents in the data folder.

    Args:
        only_files: If provided, only index these specific filenames.

    Returns:
        Tuple of (FAISS vectorstore or None, list of loading errors).
    """
    documents, errors = load_documents(only_files)

    if not documents:
        return None, errors

    chunks      = chunk_documents(documents)
    embeddings  = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_FOLDER)

    return vectorstore, errors


def load_index():
    """
    Load an existing FAISS index from disk.

    Returns:
        FAISS vectorstore or None if not found / corrupted.
    """
    if not os.path.exists(INDEX_FOLDER):
        return None
    try:
        return FAISS.load_local(
            INDEX_FOLDER,
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    except Exception:
        return None
