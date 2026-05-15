"""
config.py — Central configuration for CareerBot.
All paths, model names, and tunable parameters live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
INDEX_FOLDER = "faiss_index"
DATA_FOLDER  = "data"

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# ── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Model Settings ───────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL       = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.7

# ── Chunking Settings ────────────────────────────────────────────────────────
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100

# ── Retrieval Settings ───────────────────────────────────────────────────────
RETRIEVER_K = 6

# ── Week 1 — Chat Memory ─────────────────────────────────────────────────────
# Number of conversation *pairs* (user + assistant) to keep in context.
# 5 pairs = 10 messages — enough context without bloating the prompt.
MEMORY_WINDOW_SIZE: int = int(os.getenv("MEMORY_WINDOW_SIZE", "5"))

# ── Week 1 — Hybrid Search ───────────────────────────────────────────────────
# Number of BM25 candidate documents before RRF merge
BM25_K: int = int(os.getenv("BM25_K", "10"))

# Reciprocal Rank Fusion constant — higher = smoother rank fusion, lower = more top-heavy
# 60 is the standard value from the original RRF paper
RRF_K_CONSTANT: int = int(os.getenv("RRF_K_CONSTANT", "60"))

# Set to "hybrid" to use BM25+vector fusion; "vector" for original FAISS-only
RETRIEVAL_MODE: str = os.getenv("RETRIEVAL_MODE", "hybrid")