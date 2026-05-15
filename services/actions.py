"""
actions.py — Shared business-logic actions used by the UI tabs.

Changes vs original:
  • run_quick_action() now retrieves docs manually and passes the full
    {context, question, history} dict that the updated PromptTemplate expects.
    Quick-action tabs (resume score, interview prep, etc.) don't use chat
    history, so history is passed as an empty string.
"""

import streamlit as st
from core.chain import _format_docs


def run_quick_action(query: str) -> str:
    """
    Execute a prompt against the current RAG chain.

    Args:
        query: The fully-formed prompt string to send to the chain.

    Returns:
        The LLM response string, or a helpful fallback message if no
        knowledge base is loaded.
    """
    if not st.session_state.rag_chain:
        return (
            "📂 No documents uploaded yet. Please upload your **Resume**, "
            "**Marksheet**, or **Certificates** (PDF or TXT) in the sidebar "
            "and click **⚡ Build Knowledge Base** before using this feature."
        )

    retriever = st.session_state.retriever

    with st.spinner("Analysing your documents…"):
        # Retrieve relevant chunks
        if retriever:
            docs = (
                retriever.invoke(query)
                if hasattr(retriever, "invoke")
                else retriever.get_relevant_documents(query)
            )
        else:
            docs = []

        context = _format_docs(docs)

        # Quick actions don't have chat history — pass empty string
        return st.session_state.rag_chain.invoke({
            "context":  context,
            "question": query,
            "history":  "",
        })