"""
ui_sidebar.py — Sidebar components and file uploading logic.
"""

import os
import streamlit as st

from config import DATA_FOLDER
from vectorstore import build_index
from chain import build_chain
from state import set_chain, add_uploaded_file, clear_chat

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1.25rem 0 0.5rem;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:1.3rem; font-weight:700; color:#fff; letter-spacing: 2px; text-transform: uppercase;">
                <span style="color:#00FFCC;">[</span> CAREER_BOT <span style="color:#00FFCC;">]</span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:10px; color:#8F95B2; margin-top:4px; letter-spacing: 1px;">
                SYSTEM OVERRIDE ACTIVE
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        <div style="font-size:13px; font-weight:600; color:#fff; margin-bottom:0.75rem;">
            📂 Upload Documents
        </div>
        <div style="font-size:12px; color:#9EA5B5; margin-bottom:0.75rem; line-height:1.6;">
            Upload your <strong style="color:#C8CADB;">Resume</strong>,
            <strong style="color:#C8CADB;">Marksheet</strong>,
            <strong style="color:#C8CADB;">Certificates</strong>, or
            <strong style="color:#C8CADB;">Job Descriptions</strong> as PDF or TXT.
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Choose files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded:
            new_files = []
            for file in uploaded:
                save_path = os.path.join(DATA_FOLDER, file.name)
                if file.name not in st.session_state.uploaded_files:
                    file_bytes = file.read()
                    if file_bytes:
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)
                        new_files.append(file.name)
                        add_uploaded_file(file.name)
            if new_files:
                st.info(f"Saved: {', '.join(new_files)}")
                # Auto-rebuild index whenever new files are uploaded
                with st.spinner("Building knowledge base from your documents…"):
                    vectorstore, _ = build_index()
                    if vectorstore:
                        chain, retriever = build_chain(vectorstore)
                        set_chain(chain, retriever)
                        st.success("✅ Knowledge base rebuilt with new documents!")

        st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

        if st.button("⚡ Rebuild Knowledge Base", use_container_width=True):
            with st.spinner("Rebuilding index from all documents…"):
                vectorstore, _ = build_index()
                if vectorstore:
                    chain, retriever = build_chain(vectorstore)
                    set_chain(chain, retriever)
                    st.success("✅ Knowledge base ready!")
                else:
                    st.error("❌ No valid documents found in the data folder.")

        # Only show hint if no documents have been uploaded yet
        if st.session_state.rag_chain is None:
            st.info("💡 Upload your documents above — the knowledge base will be built automatically.")

        st.divider()

        if st.session_state.uploaded_files:
            st.markdown("<div style='font-size:13px; font-weight:600; color:#fff; margin-bottom:0.5rem;'>📋 Files in Index</div>", unsafe_allow_html=True)
            for fname in st.session_state.uploaded_files:
                ext  = "📄" if fname.endswith(".pdf") else "📝"
                name = fname[:28] + "…" if len(fname) > 30 else fname
                st.markdown(f'<div class="file-chip">{ext} {name}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.rag_chain:
            st.markdown("""
            <div class="status-bar ready">
                <div class="status-dot"></div>
                RAG Mode — Document Based
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-bar idle">
                <div class="status-dot"></div>
                No knowledge base loaded
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            clear_chat()
            st.rerun()
