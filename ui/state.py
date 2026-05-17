"""
state.py — Streamlit session state management.

CHANGES:
  • init_state() loads chat history from disk on startup.
  • append_message() saves history to disk after every message.
  • clear_chat() also wipes the saved history file.
"""

import streamlit as st
from core.memory import trim_history, load_history, save_history


def init_state():
    """Initialise all session state keys with defaults."""
    defaults = {
        "messages":       load_history(),   # ← loads from disk instead of []
        "rag_chain":      None,
        "retriever":      None,
        "all_chunks":     [],
        "uploaded_files": [],
        "quick_result":   None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chat():
    st.session_state.messages     = []
    st.session_state.quick_result = None
    save_history([])                        # ← wipes the saved file too


def set_chain(chain, retriever):
    st.session_state.rag_chain = chain
    st.session_state.retriever = retriever


def add_uploaded_file(filename: str):
    if filename not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.append(filename)


def set_quick_result(tab_key: str, result: str):
    st.session_state.quick_result = (tab_key, result)


def append_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.messages = trim_history(st.session_state.messages)
    save_history(st.session_state.messages)  # ← saves to disk after every message