"""
sidebar.py — Sidebar components and file uploading logic.

Rendering only — pipeline orchestration is delegated to services.pipeline.
"""

import os
import streamlit as st

from core.config import DATA_FOLDER
from core.ocr import IMAGE_EXTENSIONS, is_image_file
from core.loaders import describe_file_type
from services.pipeline import rebuild_knowledge_base
from ui.state import set_chain, add_uploaded_file, clear_chat


# All file types the uploader will accept
_UPLOAD_TYPES = ["pdf", "txt"] + [ext.lstrip(".") for ext in IMAGE_EXTENSIONS]


def _has_ocr_files() -> bool:
    """Return True if any uploaded file is an image or likely a scanned PDF."""
    for fname in st.session_state.get("uploaded_files", []):
        if is_image_file(fname):
            return True
    return False


def _handle_rebuild(spinner_msg: str):
    """Shared logic for building the knowledge base with UI feedback."""
    with st.spinner(spinner_msg):
        chain, retriever, errors = rebuild_knowledge_base()
        if chain:
            set_chain(chain, retriever)
            st.success("✅ Knowledge base ready!")
        else:
            st.error("❌ No valid documents could be loaded.")
        if errors:
            with st.expander("⚠️ Loading warnings"):
                for err in errors:
                    st.caption(err)


def render_sidebar():
    with st.sidebar:
        # ── Branding
        st.markdown("""
        <div style="padding: 1.25rem 0 0.5rem;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:1.3rem;
                        font-weight:700; color:#fff; letter-spacing:2px; text-transform:uppercase;">
                <span style="color:#00FFCC;">[</span> CAREER_BOT <span style="color:#00FFCC;">]</span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:10px;
                        color:#8F95B2; margin-top:4px; letter-spacing:1px;">
                SYSTEM OVERRIDE ACTIVE
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Upload section
        st.markdown("""
        <div style="font-size:13px; font-weight:600; color:#fff; margin-bottom:0.5rem;">
            📂 Upload Documents
        </div>
        <div style="font-size:12px; color:#9EA5B5; margin-bottom:0.4rem; line-height:1.6;">
            Resume · Marksheet · Certificates · Job Descriptions<br>
            <span style="color:#00FFCC; font-weight:600;">🖼️ Images &amp; scanned PDFs supported via OCR</span>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Choose files", type=_UPLOAD_TYPES,
            accept_multiple_files=True, label_visibility="collapsed",
        )

        if uploaded:
            new_files, ocr_files = [], []
            for file in uploaded:
                save_path = os.path.join(DATA_FOLDER, file.name)
                if file.name not in st.session_state.uploaded_files:
                    file_bytes = file.read()
                    if file_bytes:
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)
                        new_files.append(file.name)
                        add_uploaded_file(file.name)
                        if is_image_file(file.name):
                            ocr_files.append(file.name)

            if new_files:
                st.info(f"Saved: {', '.join(new_files)}")
                if ocr_files:
                    st.markdown(
                        f"<div style='font-size:11px; color:#00FFCC; margin-bottom:0.4rem;'>"
                        f"🔍 OCR will be applied to: {', '.join(ocr_files)}</div>",
                        unsafe_allow_html=True,
                    )
                _handle_rebuild("Processing documents (OCR if needed)…")

        st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

        if st.button("⚡ Rebuild Knowledge Base", use_container_width=True):
            _handle_rebuild("Rebuilding index (OCR applied to images/scanned PDFs)…")

        if st.session_state.rag_chain is None:
            st.info("💡 Upload your documents — the knowledge base builds automatically.")

        st.divider()

        # ── File list
        if st.session_state.uploaded_files:
            st.markdown(
                "<div style='font-size:13px; font-weight:600; color:#fff; margin-bottom:0.5rem;'>"
                "📋 Files in Index</div>", unsafe_allow_html=True,
            )
            for fname in st.session_state.uploaded_files:
                label = describe_file_type(fname)
                display = fname[:26] + "…" if len(fname) > 28 else fname
                ocr_tag = (
                    " <span style='color:#00FFCC; font-size:10px;'>[OCR]</span>"
                    if is_image_file(fname) else ""
                )
                st.markdown(
                    f'<div class="file-chip">{label} {display}{ocr_tag}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Status bar
        if st.session_state.rag_chain:
            extra = " + OCR" if _has_ocr_files() else ""
            st.markdown(f"""
            <div class="status-bar ready">
                <div class="status-dot"></div>
                RAG Mode — Document Based{extra}
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
