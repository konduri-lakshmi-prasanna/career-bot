"""
core/vectorstore.py  ←  CHANGED
Only clear_index() remains. Everything else moved to rag-core.
"""

import chromadb
from core.config import INDEX_FOLDER

COLLECTION_NAME = "careerbot"


def clear_index() -> None:
    """
    Wipe the CareerBot ChromaDB collection.
    Called only when user clicks 'Clear Knowledge Base'.
    """
    try:
        client = chromadb.PersistentClient(path=INDEX_FOLDER)
        client.delete_collection(COLLECTION_NAME)
        print("[vectorstore] Collection cleared.")
    except Exception as e:
        print(f"[vectorstore] Could not clear collection: {e}")