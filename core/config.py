"""
config.py — Central configuration for CareerBot.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Base directory = project root (one level up from core/) ───────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Absolute paths — work regardless of where you run streamlit from ──────────
INDEX_FOLDER = os.path.join(BASE_DIR, "chroma_db")
DATA_FOLDER  = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_FOLDER,  exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Model Settings ────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL       = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.7

# ── Chunking Settings ─────────────────────────────────────────────────────────
# CHUNKING_MODE: "semantic" uses section-aware + SemanticChunker (recommended).
#                "recursive" uses the original RecursiveCharacterTextSplitter.
#                Switch to "recursive" if langchain-experimental is not installed.
CHUNKING_MODE  : str = os.getenv("CHUNKING_MODE", "semantic")

# Hard upper/lower bounds on chunk size (used by both modes).
CHUNK_MAX_CHARS: int = int(os.getenv("CHUNK_MAX_CHARS", "1200"))  # was CHUNK_SIZE=800
CHUNK_MIN_CHARS: int = int(os.getenv("CHUNK_MIN_CHARS", "80"))    # drop tiny fragments
CHUNK_OVERLAP  : int = int(os.getenv("CHUNK_OVERLAP",   "100"))

# Keep old names as aliases so any code that still imports them won't break.
CHUNK_SIZE = CHUNK_MAX_CHARS

# ── Semantic Chunker Settings (only used when CHUNKING_MODE="semantic") ───────
# SEMANTIC_BREAKPOINT_TYPE options:
#   "percentile"         — split where similarity drop > Nth percentile (default)
#   "standard_deviation" — split where drop > mean + N * std_dev
#   "interquartile"      — split where drop > Q3 + N * IQR
SEMANTIC_BREAKPOINT_TYPE     : str   = os.getenv("SEMANTIC_BREAKPOINT_TYPE", "percentile")
SEMANTIC_BREAKPOINT_THRESHOLD: float = float(os.getenv("SEMANTIC_BREAKPOINT_THRESHOLD", "95"))

# ── Retrieval Settings ────────────────────────────────────────────────────────
RETRIEVER_K = 6

# ── Chat Memory ───────────────────────────────────────────────────────────────
MEMORY_WINDOW_SIZE: int = int(os.getenv("MEMORY_WINDOW_SIZE", "5"))

# ── Hybrid Search ─────────────────────────────────────────────────────────────
BM25_K: int         = int(os.getenv("BM25_K", "10"))
RRF_K_CONSTANT: int = int(os.getenv("RRF_K_CONSTANT", "60"))
RETRIEVAL_MODE: str = os.getenv("RETRIEVAL_MODE", "hybrid")