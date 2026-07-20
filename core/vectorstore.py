"""
core/vectorstore.py  ←  CHANGED
Only clear_index() remains. Everything else moved to rag-core.
"""

from rag_core.db.chromadb_store import get_client

COLLECTION_NAME = "careerbot"


def clear_index() -> None:
    """
    Wipe the CareerBot ChromaDB collection ONLY.
    Does not touch any files in the data folder.

    Called:
      • automatically, right before every re-embed (new resume upload)
      • manually, when user clicks 'Clear Knowledge Base' (via _clear_all_knowledge,
        which also deletes the files)

    Reuses rag_core's client singleton (same one used to build the index)
    instead of opening a second PersistentClient on the same path, which
    can otherwise cause SQLite locking issues.
    """
    try:
        client = get_client()
        client.delete_collection(COLLECTION_NAME)
        print("[vectorstore] Collection cleared.")
    except Exception as e:
        # Collection may not exist yet on first run — that's fine.
        print(f"[vectorstore] Could not clear collection: {e}")