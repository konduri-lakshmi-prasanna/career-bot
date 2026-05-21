"""
services/actions.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: Directly accessed st.session_state.rag_chain and
        st.session_state.retriever. Called retriever.invoke(query)
        then chain.invoke({context, question, history}) manually.
        UI layer was tightly coupled to LangChain internals.

AFTER:  Calls run_query(prompt) — one call that runs all 6 rag-core
        stages and returns the final answer string.
        No chain, no retriever, no session_state RAG objects needed here.
"""

import streamlit as st
from services.pipeline import load_existing_knowledge_base, run_query


def run_quick_action(query: str) -> str:
    """
    Execute a fully-formed prompt through the 6-stage RAG pipeline.

    Args:
        query: The fully-formed prompt string (built by prompts.py).

    Returns:
        The LLM response string, or a fallback if no KB is loaded.
    """
    if not load_existing_knowledge_base():
        return (
            "📂 No documents uploaded yet. Please upload your **Resume**, "
            "**Marksheet**, or **Certificates** (PDF or TXT) in the sidebar "
            "and click **⚡ Build Knowledge Base** before using this feature."
        )

    with st.spinner("Analysing your documents…"):
        return run_query(query)