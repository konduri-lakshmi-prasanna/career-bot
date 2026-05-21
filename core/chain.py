"""
core/chain.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: This file owned the LLM singleton (get_llm), the LangChain chain
        (build_chain), and the ask() function which manually did:
            retriever.invoke(query) → _format_docs() → chain.invoke({...})
        tabs.py and actions.py both imported from here.

AFTER:  The LLM singleton is no longer needed in careerbot — rag-core's
        rag_core.llm.factory.get_llm() handles it (reads GROQ_API_KEY
        or GOOGLE_API_KEY from .env automatically).
        build_chain() and ask() are gone — pipeline.run(query) replaces them.

        Only _format_docs() is kept because evaluate.py still uses it
        to pretty-print retrieved documents during RAGAS evaluation.
        If evaluate.py is also refactored, this entire file can be deleted.
"""

from langchain_core.documents import Document
from typing import List


def _format_docs(docs: List[Document]) -> str:
    """
    Format a list of LangChain Document objects into a labelled context string.
    Used by evaluate.py for RAGAS evaluation display.

    Args:
        docs: List of LangChain Document objects.

    Returns:
        A formatted string with each document labelled by source.
    """
    if not docs:
        return "[NO DOCUMENTS]"
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
        parts.append(f"[Document {i} — {source}]:\n{doc.page_content}")
    return "\n\n".join(parts)