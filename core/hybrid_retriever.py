"""
hybrid_retriever.py — Hybrid (vector + keyword) retrieval for CareerBot.

CHANGES vs original:
  • Import changed from FAISS → Chroma.
  • Type hints updated from FAISS → Chroma.
  • All logic (BM25, RRF, invoke) is IDENTICAL to the original.

Combines:
  • Chroma dense-vector similarity search  (semantic meaning)
  • BM25 sparse keyword search             (exact term matching)

The two result sets are merged using Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

from typing import List, Optional

# CHANGED: langchain_chroma instead of langchain_community.vectorstores.FAISS
from langchain_chroma import Chroma
from langchain_core.documents import Document

from core.config import RETRIEVER_K, BM25_K, RRF_K_CONSTANT


# ── Optional BM25 import (graceful fallback) ──────────────────────────────────
try:
    from rank_bm25 import BM25Okapi
    _BM25_AVAILABLE = True
except ImportError:
    _BM25_AVAILABLE = False


class HybridRetriever:
    """
    Merges Chroma vector retrieval and BM25 keyword retrieval via RRF.

    Usage:
        retriever = HybridRetriever(vectorstore, all_chunks)
        docs = retriever.invoke("What programming languages do I know?")
    """

    def __init__(
        self,
        vectorstore: Chroma,          # CHANGED: was FAISS
        all_chunks: List[Document],
        k: int = RETRIEVER_K,
    ):
        self._vectorstore = vectorstore
        self._chunks      = all_chunks
        self._k           = k
        self._bm25        = self._build_bm25(all_chunks) if _BM25_AVAILABLE else None

    # ── Public API ─────────────────────────────────────────────────────────────

    def invoke(self, query: str) -> List[Document]:
        """Return the top-k most relevant documents for *query*."""
        vector_hits = self._vector_search(query)

        if self._bm25 is None:
            return vector_hits

        bm25_hits = self._bm25_search(query)
        return self._rrf_merge(vector_hits, bm25_hits)

    # LangChain BaseRetriever compatibility shim
    def get_relevant_documents(self, query: str) -> List[Document]:
        return self.invoke(query)

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _build_bm25(chunks: List[Document]) -> Optional["BM25Okapi"]:
        """Tokenise all chunks and build a BM25 index."""
        if not chunks:
            return None
        tokenised = [doc.page_content.lower().split() for doc in chunks]
        return BM25Okapi(tokenised)

    def _vector_search(self, query: str) -> List[Document]:
        """Dense retrieval from ChromaDB."""
        try:
            return self._vectorstore.similarity_search(query, k=self._k * 2)
        except Exception:
            return []

    def _bm25_search(self, query: str) -> List[Document]:
        """Sparse BM25 retrieval over stored chunks."""
        if not self._bm25 or not self._chunks:
            return []
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)

        ranked = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )
        top_indices = [idx for idx, _ in ranked[: self._k * 2]]
        return [self._chunks[i] for i in top_indices]

    def _rrf_merge(
        self,
        vector_hits: List[Document],
        bm25_hits: List[Document],
    ) -> List[Document]:
        """
        Reciprocal Rank Fusion.
        score(d) = Σ  1 / (RRF_K_CONSTANT + rank_in_list)
        """
        scores: dict[str, float] = {}
        doc_map: dict[str, Document] = {}

        def _add_list(hits: List[Document]) -> None:
            for rank, doc in enumerate(hits, start=1):
                key = doc.page_content[:120]
                scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K_CONSTANT + rank)
                doc_map[key] = doc

        _add_list(vector_hits)
        _add_list(bm25_hits)

        ranked_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
        return [doc_map[k] for k in ranked_keys[: self._k]]


def build_hybrid_retriever(
    vectorstore: Chroma,              # CHANGED: was FAISS
    all_chunks: List[Document],
    k: int = RETRIEVER_K,
) -> HybridRetriever:
    """
    Factory function — the only public import other modules need.

    Args:
        vectorstore: Built Chroma index.
        all_chunks:  Full list of Document chunks (same ones indexed).
        k:           Number of results to return per query.

    Returns:
        A ready-to-use HybridRetriever instance.
    """
    return HybridRetriever(vectorstore, all_chunks, k=k)
