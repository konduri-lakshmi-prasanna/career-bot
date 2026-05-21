"""
core/config.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: Had EMBEDDING_MODEL, INDEX_FOLDER, RETRIEVER_K, RETRIEVAL_MODE,
        BM25_K, RRF_K_CONSTANT — all needed because vectorstore.py,
        hybrid_retriever.py, and chain.py lived inside careerbot.

AFTER:  Embedding, retrieval, and reranking are all handled by rag-core.
        Removed: EMBEDDING_MODEL, RETRIEVAL_MODE, BM25_K, RRF_K_CONSTANT.
        RETRIEVER_K is also removed — top_k is now set in CareerBotPipeline.__init__().
        INDEX_FOLDER is kept because clear_index() in vectorstore.py still
        needs it to locate the ChromaDB files on disk.
        Everything else (chunking, memory, API keys) is unchanged.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Base directory = project root (one level up from core/) ───────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Absolute paths ────────────────────────────────────────────────────────────
INDEX_FOLDER = os.path.join(BASE_DIR, "chroma_db")   # kept for clear_index()
DATA_FOLDER  = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_FOLDER,  exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# ── API Keys ──────────────────────────────────────────────────────────────────
# rag-core reads GROQ_API_KEY / GOOGLE_API_KEY directly from .env via
# rag_core.llm.factory.get_llm() — no need to re-read them here.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── LLM Settings (kept for reference / evaluate.py) ──────────────────────────
LLM_MODEL       = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.7

# ── Chunking Settings ─────────────────────────────────────────────────────────
# Used by core/chunkers.py — careerbot's semantic/section-aware chunker.
CHUNKING_MODE  : str = os.getenv("CHUNKING_MODE", "semantic")

CHUNK_MAX_CHARS: int = int(os.getenv("CHUNK_MAX_CHARS", "1200"))
CHUNK_MIN_CHARS: int = int(os.getenv("CHUNK_MIN_CHARS", "80"))
CHUNK_OVERLAP  : int = int(os.getenv("CHUNK_OVERLAP",   "100"))

# Alias so any code that still imports CHUNK_SIZE won't break
CHUNK_SIZE = CHUNK_MAX_CHARS

# ── Semantic Chunker Settings ─────────────────────────────────────────────────
# Used by core/chunkers.py when CHUNKING_MODE="semantic"
SEMANTIC_BREAKPOINT_TYPE     : str   = os.getenv("SEMANTIC_BREAKPOINT_TYPE", "percentile")
SEMANTIC_BREAKPOINT_THRESHOLD: float = float(os.getenv("SEMANTIC_BREAKPOINT_THRESHOLD", "95"))

# ── Chat Memory ───────────────────────────────────────────────────────────────
# Used by core/memory.py
MEMORY_WINDOW_SIZE: int = int(os.getenv("MEMORY_WINDOW_SIZE", "5"))