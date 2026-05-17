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
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100

# ── Retrieval Settings ────────────────────────────────────────────────────────
RETRIEVER_K = 6

# ── Chat Memory ───────────────────────────────────────────────────────────────
MEMORY_WINDOW_SIZE: int = int(os.getenv("MEMORY_WINDOW_SIZE", "5"))

# ── Hybrid Search ─────────────────────────────────────────────────────────────
BM25_K: int         = int(os.getenv("BM25_K", "10"))
RRF_K_CONSTANT: int = int(os.getenv("RRF_K_CONSTANT", "60"))
RETRIEVAL_MODE: str = os.getenv("RETRIEVAL_MODE", "hybrid")