"""
state.py — Streamlit session state management.
"""

import streamlit as st


def init_state():
    """Initialise all session state keys with defaults."""
    defaults = {
        "messages":       [],
        "rag_chain":      None,
        "retriever":      None,
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
