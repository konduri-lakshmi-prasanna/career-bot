"""
state.py — Streamlit session state management.

Changes vs original:
  • init_state() adds `all_chunks` key for hybrid retriever.
  • trim_messages() enforces the memory window on every new message.
  • set_chain() accepts the optional all_chunks list.
"""

import streamlit as st
from core.memory import trim_history


def init_state():
    """Initialise all session state keys with defaults."""
    defaults = {
        "messages":       [],
        "rag_chain":      None,
        "retriever":      None,
        "all_chunks":     [],          # NEW — needed by HybridRetriever
        "uploaded_files": [],
        "quick_result":   None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chat():
    st.session_state.messages     = []
    st.session_state.quick_result = None


def set_chain(chain, retriever):
    st.session_state.rag_chain = chain
    st.session_state.retriever = retriever


def add_uploaded_file(filename: str):
    if filename not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.append(filename)


def set_quick_result(tab_key: str, result: str):
    st.session_state.quick_result = (tab_key, result)


def append_message(role: str, content: str):
    """
    Append a message and trim the history to the configured memory window.
    Call this instead of st.session_state.messages.append() directly.
    """
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.messages = trim_history(st.session_state.messages)