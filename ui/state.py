"""
ui/state.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: Session state held rag_chain and retriever as separate objects.
        set_chain(chain, retriever) was called after every rebuild.

AFTER:  rag_chain and retriever are completely removed from session state.
        Replaced with kb_ready (bool) — the only thing the UI needs to know.
        set_kb_ready(bool) replaces set_chain(chain, retriever).
        The pipeline singleton in services/pipeline.py owns all RAG state.
"""

import streamlit as st
from core.memory import trim_history, load_history, save_history


def init_state():
    """Initialise all session state keys with defaults."""
    defaults = {
        "messages":           load_history(),   # loaded from disk on startup
        "kb_ready":           False,            # True once KB is confirmed loaded
        "uploaded_files":     [],
        "quick_result":       None,
        "web_search_enabled": True,             # Web search enabled by default
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chat():
    st.session_state.messages     = []
    st.session_state.quick_result = None
    save_history([])                        # wipes the saved file too


def set_kb_ready(ready: bool):
    """Called by sidebar after a successful rebuild or on startup load."""
    st.session_state.kb_ready = ready


def add_uploaded_file(filename: str):
    if filename not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.append(filename)


def set_quick_result(tab_key: str, result: str):
    st.session_state.quick_result = (tab_key, result)


def append_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.messages = trim_history(st.session_state.messages)
    save_history(st.session_state.messages)  # saves to disk after every message