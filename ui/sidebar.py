"""
sidebar.py — Sidebar components and file uploading logic.

PERSISTENT RAG: Uploaded documents are ADDED to the existing ChromaDB index.
Previously indexed files are never deleted unless the user explicitly clears
the knowledge base. This means the bot remembers all past uploads across
app restarts.
"""

import os
import streamlit as st

from core.config import DATA_FOLDER
from core.ocr import IMAGE_EXTENSIONS, is_image_file
from core.loaders import describe_file_type
from core.vectorstore import clear_index
from services.pipeline import rebuild_knowledge_base, load_existing_knowledge_base
from ui.state import set_chain, add_uploaded_file, clear_chat

_UPLOAD_TYPES = ["pdf", "txt"] + [ext.lstrip(".") for ext in IMAGE_EXTENSIONS]

SUPPORTED_EXTS = {".pdf", ".txt"} | {e for e in IMAGE_EXTENSIONS}


def _clear_all_knowledge():
    """
    Wipe ChromaDB collection AND delete all files from the data folder.
    This is a full reset — call only when the user explicitly requests it.
    """
    # Clear ChromaDB
    clear_index()
    # Delete files from data folder
    for fname in os.listdir(DATA_FOLDER):
        if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTS:
            try:
                os.remove(os.path.join(DATA_FOLDER, fname))
            except Exception:
                pass
    st.session_state.uploaded_files = []
    st.session_state.rag_chain = None
    st.session_state.rag_retriever = None


def _has_ocr_files() -> bool:
    for fname in st.session_state.get("uploaded_files", []):
        if is_image_file(fname):
            return True
    return False


def _handle_rebuild(spinner_msg: str):
    with st.spinner(spinner_msg):
        try:
            chain, retriever, errors = rebuild_knowledge_base()
            if chain:
                set_chain(chain, retriever)
                st.success("✅ Knowledge base ready!")
            else:
                st.error("❌ No valid documents found in the data folder.")
            if errors:
                with st.expander("⚠️ Loading warnings"):
                    for err in errors:
                        st.caption(err)
        except Exception as e:
            st.error(f"❌ Error building knowledge base: {e}")


def _try_load_existing():
    """On first page load, silently restore a previously built index."""
    if st.session_state.rag_chain is not None:
        return
    try:
        chain, retriever = load_existing_knowledge_base()
        if chain:
            set_chain(chain, retriever)
            if not st.session_state.uploaded_files:
                for fname in os.listdir(DATA_FOLDER):
                    if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTS:
                        add_uploaded_file(fname)
    except Exception:
        pass


def render_sidebar():
    _try_load_existing()

    with st.sidebar:
        # ── Branding ──────────────────────────────────────────────────────────
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

        # ── Upload section ─────────────────────────────────────────────────────
        st.markdown("""
        <div style="font-size:13px; font-weight:600; color:#fff; margin-bottom:0.5rem;">
            📂 Upload Documents
        </div>
        <div style="font-size:12px; color:#9EA5B5; margin-bottom:0.4rem; line-height:1.6;">
            Resume · Marksheet · Certificates · Job Descriptions<br>
            <span style="color:#00FFCC; font-weight:600;">🖼️ Images &amp; scanned PDFs supported via OCR</span>
        </div>
        """, unsafe_allow_html=True)

        os.makedirs(DATA_FOLDER, exist_ok=True)

        uploaded = st.file_uploader(
            "Choose files",
            type=_UPLOAD_TYPES,
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded:
            # PERSISTENT: do NOT clear old files — add new ones to the existing index
            new_files, ocr_files = [], []
            for file in uploaded:
                save_path = os.path.join(DATA_FOLDER, file.name)
                file_bytes = file.read()
                if file_bytes:
                    try:
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)
                        new_files.append(file.name)
                        add_uploaded_file(file.name)
                        if is_image_file(file.name):
                            ocr_files.append(file.name)
                    except Exception as e:
                        st.error(f"❌ Could not save {file.name}: {e}")

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
            _handle_rebuild("Rebuilding index…")

        if st.button("🗑️ Clear Knowledge Base", use_container_width=True, type="secondary"):
            _clear_all_knowledge()
            st.success("✅ Knowledge base cleared. Upload new documents to start fresh.")
            st.rerun()

        if st.session_state.rag_chain is None:
            st.info("💡 Upload documents above — the knowledge base builds automatically.")

        st.divider()

        # ── File list ──────────────────────────────────────────────────────────
        if st.session_state.uploaded_files:
            st.markdown(
                "<div style='font-size:13px; font-weight:600; color:#fff; margin-bottom:0.5rem;'>"
                "📋 Files in Index</div>",
                unsafe_allow_html=True,
            )
            for fname in st.session_state.uploaded_files:
                label   = describe_file_type(fname)
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

        # ── Status bar ─────────────────────────────────────────────────────────
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
        st.caption(f"📁 `{DATA_FOLDER}`")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            clear_chat()
            st.rerun()