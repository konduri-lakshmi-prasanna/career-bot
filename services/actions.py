"""
actions.py — Shared business-logic actions used by the UI tabs.

Extracted from ui_tabs.py so that tab rendering stays purely presentational.
"""

import streamlit as st


def run_quick_action(query: str) -> str:
    """
    Execute a prompt against the current RAG chain.

    Args:
        query: The fully-formed prompt string to send to the chain.

    Returns:
        The LLM response string, or a helpful fallback message if no
        knowledge base is loaded.
    """
    if st.session_state.rag_chain:
        with st.spinner("Analysing your documents…"):
            return st.session_state.rag_chain.invoke(query)

    return (
        "📂 No documents uploaded yet. Please upload your **Resume**, "
        "**Marksheet**, or **Certificates** (PDF or TXT) in the sidebar "
        "and click **⚡ Build Knowledge Base** before using this feature."
    )
