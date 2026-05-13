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
