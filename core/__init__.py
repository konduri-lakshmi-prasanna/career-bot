"""
core — Pure business logic for CareerBot.

This package contains all non-UI logic: configuration, document loading,
OCR, chunking, vector store management, prompt templates, and RAG chain
construction.  Nothing in this package imports Streamlit.
"""

from core.config import (
    GROQ_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVER_K,
    INDEX_FOLDER,
    DATA_FOLDER,
)
from core.prompts import (
    RAG_PROMPT,
    resume_analysis_prompt,
    interview_prep_prompt,
    career_roadmap_prompt,
    job_match_prompt,
)
from core.loaders import load_documents, describe_file_type, SUPPORTED_EXTENSIONS
from core.chunkers import chunk_documents
from core.vectorstore import build_index, load_index, get_embeddings
from core.chain import build_chain, get_llm
