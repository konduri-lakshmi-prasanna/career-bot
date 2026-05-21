"""
chunkers.py — Semantic + section-aware chunking for CareerBot.

Strategy (three-tier, in priority order):

  1. SECTION-AWARE  — detects resume/marksheet section headers (Education,
                       Skills, Experience, …) and hard-splits on those
                       boundaries first.  Each section is then passed to the
                       semantic splitter independently so a section never
                       straddles a chunk boundary.

  2. SEMANTIC        — uses LangChain's SemanticChunker to find natural
                       paragraph-level breakpoints via embedding cosine
                       similarity.  Falls back gracefully if the embeddings
                       model is not yet loaded.

  3. RECURSIVE       — original RecursiveCharacterTextSplitter used as the
                       final safety net to enforce the hard token ceiling
                       (CHUNK_MAX_CHARS).  No chunk ever exceeds this limit
                       regardless of semantic boundaries.
"""

from __future__ import annotations

import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import (
    CHUNK_MAX_CHARS,
    CHUNK_MIN_CHARS,
    CHUNK_OVERLAP,
    CHUNKING_MODE,
    SEMANTIC_BREAKPOINT_THRESHOLD,
    SEMANTIC_BREAKPOINT_TYPE,
)


# ── Section header patterns (resume + marksheet) ──────────────────────────────
_SECTION_PATTERN = re.compile(
    r"^\s*(?:#{1,3}\s*)?("
    r"education|academic|qualifications?|certifications?|certificates?"
    r"|experience|work\s+experience|employment|internship"
    r"|skills?|technical\s+skills?|core\s+competenc"
    r"|projects?|personal\s+projects?"
    r"|achievements?|awards?|honors?"
    r"|summary|objective|profile|about\s+me"
    r"|publications?|research|papers?"
    r"|languages?|hobbies|interests?|extracurricular"
    r"|contact|references?"
    r")\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Main entry point. Called by careerbot_pipeline.py after loading documents.

    Args:
        documents: Full-length LangChain Document objects from loaders.py.

    Returns:
        List of smaller Document chunks with enriched metadata.
    """
    if CHUNKING_MODE == "semantic":
        return _semantic_chunk(documents)
    return _recursive_chunk(documents)


# ── Tier 1 + 2: Section-aware → Semantic ─────────────────────────────────────

def _semantic_chunk(documents: List[Document]) -> List[Document]:
    """
    Split each document by section headers first, then apply semantic
    chunking within each section. Falls back to recursive if the
    semantic splitter cannot be initialised.
    """
    try:
        from langchain_experimental.text_splitter import SemanticChunker
        from rag_core.db.chromadb_store import get_embeddings  # shared singleton

        semantic_splitter = SemanticChunker(
            embeddings=get_embeddings(),
            breakpoint_threshold_type=SEMANTIC_BREAKPOINT_TYPE,
            breakpoint_threshold_amount=SEMANTIC_BREAKPOINT_THRESHOLD,
        )
    except ImportError:
        print(
            "[chunkers] langchain-experimental not found — "
            "falling back to recursive chunking. "
            "Run: pip install langchain-experimental"
        )
        return _recursive_chunk(documents)
    except Exception as exc:
        print(f"[chunkers] Semantic splitter init failed ({exc}) — using recursive fallback.")
        return _recursive_chunk(documents)

    ceiling_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_MAX_CHARS,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Document] = []

    for doc in documents:
        sections = _split_into_sections(doc)

        for section_doc in sections:
            try:
                sem_chunks = semantic_splitter.create_documents(
                    texts=[section_doc.page_content],
                    metadatas=[section_doc.metadata],
                )
            except Exception:
                sem_chunks = [section_doc]

            for chunk in sem_chunks:
                if len(chunk.page_content) > CHUNK_MAX_CHARS:
                    sub = ceiling_splitter.split_documents([chunk])
                    all_chunks.extend(sub)
                else:
                    all_chunks.append(chunk)

    return _filter_and_enrich(all_chunks)


# ── Tier 3: Recursive fallback ────────────────────────────────────────────────

def _recursive_chunk(documents: List[Document]) -> List[Document]:
    """RecursiveCharacterTextSplitter — used as fallback."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_MAX_CHARS,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return _filter_and_enrich(chunks)


# ── Section detection ─────────────────────────────────────────────────────────

def _split_into_sections(doc: Document) -> List[Document]:
    """
    Split a document at detected section-header lines.
    Returns the original document unchanged if no headers are found.
    """
    text = doc.page_content
    matches = list(_SECTION_PATTERN.finditer(text))

    if not matches:
        return [doc]

    sections: List[Document] = []
    boundaries = [m.start() for m in matches] + [len(text)]

    preamble = text[: boundaries[0]].strip()
    if preamble:
        sections.append(Document(
            page_content=preamble,
            metadata={**doc.metadata, "section": "header"},
        ))

    for i, match in enumerate(matches):
        section_name = match.group(1).strip().lower()
        section_text = text[boundaries[i]: boundaries[i + 1]].strip()
        if section_text:
            sections.append(Document(
                page_content=section_text,
                metadata={**doc.metadata, "section": section_name},
            ))

    return sections if sections else [doc]


# ── Post-processing ───────────────────────────────────────────────────────────

def _filter_and_enrich(chunks: List[Document]) -> List[Document]:
    """
    Drop chunks that are too short and add chunk_index to metadata.
    """
    result: List[Document] = []
    for i, chunk in enumerate(chunks):
        content = chunk.page_content.strip()
        if len(content) < CHUNK_MIN_CHARS:
            continue
        chunk.page_content = content
        chunk.metadata["chunk_index"] = i
        result.append(chunk)
    return result