import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerBot — AI Career Guidance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Professional Dark-Accent Design
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@600;700&display=swap');

:root {
    --brand:        #5C6CF2;
    --brand-light:  #E8EAFF;
    --brand-dark:   #3B48CC;
    --accent:       #F26B5C;
    --accent-light: #FEF0EE;
    --success:      #27AE60;
    --success-bg:   #EAFAF1;
    --warning:      #F39C12;
    --warning-bg:   #FEF9E7;
    --danger:       #E74C3C;
    --danger-bg:    #FDEDEC;
    --surface:      #FFFFFF;
    --surface-2:    #F8F9FC;
    --surface-3:    #EFF1F8;
    --border:       #E3E6F0;
    --text-primary: #1A1D2E;
    --text-secondary: #5A6070;
    --text-muted:   #9EA5B5;
    --radius-sm:    8px;
    --radius-md:    12px;
    --radius-lg:    16px;
    --radius-xl:    24px;
    --shadow-sm:    0 1px 3px rgba(26,29,46,0.08);
    --shadow-md:    0 4px 16px rgba(26,29,46,0.10);
    --shadow-lg:    0 8px 32px rgba(26,29,46,0.14);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    color: var(--text-primary);
}
.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1200px;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

[data-testid="stSidebar"] {
    background: var(--text-primary);
    border-right: 1px solid #2A2D3E;
}
[data-testid="stSidebar"] * { color: #C8CADB !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stButton > button {
    background: var(--brand) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(92,108,242,0.35) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--brand-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(92,108,242,0.45) !important;
}
[data-testid="stSidebar"] .uploadedFile {
    background: #2A2D3E !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid #3A3D4E !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #252836 !important;
    border: 1.5px dashed #4A4D5E !important;
    border-radius: var(--radius-md) !important;
    padding: 0.8rem !important;
}
[data-testid="stSidebar"] .stDivider { border-color: #2A2D3E !important; }
[data-testid="stSidebar"] .stSuccess > div {
    background: #1A3A2A !important;
    color: #4ADE80 !important;
    border: 1px solid #2D6A4F !important;
}
[data-testid="stSidebar"] .stWarning > div {
    background: #3A2A1A !important;
    color: #FCD34D !important;
    border: 1px solid #92400E !important;
}
[data-testid="stSidebar"] .stInfo > div {
    background: #1A2A3A !important;
    color: #93C5FD !important;
    border: 1px solid #1D4ED8 !important;
}

.hero-block {
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 60%, #2D1B8A 100%);
    border-radius: var(--radius-xl);
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}
.hero-block::before {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.hero-block::after {
    content: "";
    position: absolute;
    bottom: -60px; left: 10%;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.75);
    margin: 0;
    line-height: 1.6;
    max-width: 560px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 12px;
    color: #FFFFFF;
    font-weight: 500;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-2);
    border-radius: var(--radius-lg);
    padding: 6px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-md) !important;
    padding: 0.55rem 1.2rem !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--surface) !important;
    color: var(--text-primary) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--brand) !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

.stButton > button {
    background: var(--brand) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 3px 10px rgba(92,108,242,0.3) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--brand-dark) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(92,108,242,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

[data-testid="stChatMessage"] {
    border-radius: var(--radius-lg) !important;
    margin-bottom: 0.75rem !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: var(--brand-light) !important;
    border-color: #C5CAFF !important;
}
[data-testid="stChatMessage"][data-testid*="assistant"] { background: var(--surface) !important; }
.stChatInput textarea {
    border-radius: var(--radius-lg) !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    background: var(--surface) !important;
    transition: border-color 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 0.8rem 1rem !important;
}
.stChatInput textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(92,108,242,0.12) !important;
}

.stSelectbox [data-baseweb="select"] > div:first-child,
.stTextInput input,
.stTextArea textarea {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s ease !important;
}
.stSelectbox [data-baseweb="select"] > div:first-child:focus-within,
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(92,108,242,0.1) !important;
}

.stExpander {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
    box-shadow: none !important;
    background: var(--surface-2) !important;
}
.stExpander > div:first-child {
    background: var(--surface-2) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}

.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
}
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.4rem;
}
.section-icon {
    width: 36px; height: 36px;
    border-radius: var(--radius-sm);
    background: var(--brand-light);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}
.section-subtitle {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin: 0 0 1.25rem;
    padding-left: 46px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-success { background: var(--success-bg); color: var(--success); }
.badge-warning { background: var(--warning-bg); color: var(--warning); }
.badge-info    { background: var(--brand-light); color: var(--brand); }
.badge-error   { background: var(--danger-bg); color: var(--danger); }

.status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.6rem 1rem;
    border-radius: var(--radius-md);
    font-size: 13px;
    font-weight: 500;
    margin-top: 1rem;
}
.status-bar.ready {
    background: var(--success-bg);
    color: var(--success);
    border: 1px solid #A9DFC0;
}
.status-bar.idle {
    background: var(--warning-bg);
    color: var(--warning);
    border: 1px solid #F9D78A;
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pulse 2s infinite;
}
.ready .status-dot { background: var(--success); }
.idle  .status-dot { background: var(--warning); animation: none; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

.file-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #252836;
    border: 1px solid #3A3D4E;
    border-radius: var(--radius-sm);
    padding: 6px 12px;
    font-size: 13px;
    color: #C8CADB;
    margin-bottom: 6px;
}

.stAlert > div {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
}
.stSpinner > div { border-top-color: var(--brand) !important; }

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

[data-testid="column"] { padding: 0 0.5rem !important; }
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child  { padding-right: 0 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #C5C8D8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9EA5B5; }

@media (max-width: 768px) {
    .hero-title { font-size: 1.6rem; }
    .hero-block { padding: 1.5rem; }
    .main .block-container { padding: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
INDEX_FOLDER = "faiss_index"
DATA_FOLDER  = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# CACHED RESOURCES
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@st.cache_resource
def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
    )

# ─────────────────────────────────────────────────────────────────────────────
# FAISS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def build_index(only_files=None):
    """Build FAISS index. If only_files is given, index only those filenames."""
    embeddings = get_embeddings()
    documents  = []
    splitter   = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    target_files = only_files or os.listdir(DATA_FOLDER)
    for filename in target_files:
        filepath = os.path.join(DATA_FOLDER, filename)
        if not os.path.exists(filepath):
            continue
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            elif filename.endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            else:
                continue
            loaded = loader.load()
            # Tag each doc with source filename for transparency
            for doc in loaded:
                doc.metadata["source_file"] = filename
            documents += loaded
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not load **{filename}**: {e}")

    if not documents:
        return None

    chunks      = splitter.split_documents(documents)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_FOLDER)
    return vectorstore


def load_index():
    embeddings = get_embeddings()
    if os.path.exists(INDEX_FOLDER):
        try:
            return FAISS.load_local(
                INDEX_FOLDER, embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception:
            return None
    return None

# ─────────────────────────────────────────────────────────────────────────────
# RAG CHAIN  ← STRICT: refuses to answer if context is empty
# ─────────────────────────────────────────────────────────────────────────────
def build_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    llm       = get_llm()

    prompt_template = """You are CareerBot — an AI career guidance assistant.

You MUST answer ONLY using the document excerpts provided below in the CONTEXT section.
Do NOT use your own training knowledge. Do NOT guess or fabricate any information.

RULES:
- If CONTEXT is empty or says "[NO DOCUMENTS]", reply: "📂 No relevant information found in your uploaded documents. Please upload documents and rebuild the knowledge base."
- If CONTEXT exists but doesn't have enough info for the question, say so honestly and suggest uploading more documents.
- Quote or paraphrase directly from the CONTEXT. Cite which document section you are referencing.
- Use structured formatting with markdown headers and bullet points.

--- CONTEXT FROM UPLOADED DOCUMENTS ---
{context}
--- END CONTEXT ---

User Question: {question}

Answer (based strictly on the above context):"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )

    def format_docs(docs):
        if not docs:
            return "[NO DOCUMENTS]"
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
            parts.append(f"[Document {i} — {source}]:\n{doc.page_content}")
        return "\n\n".join(parts)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


# ─────────────────────────────────────────────────────────────────────────────
# QUICK ACTION HELPER
# ─────────────────────────────────────────────────────────────────────────────
def run_quick_action(query: str) -> str:
    if st.session_state.rag_chain:
        with st.spinner("Analysing your documents…"):
            return st.session_state.rag_chain.invoke(query)
    # ── CHANGED: clear no-document message ──────────────────────────────────
    return "📂 No documents uploaded yet. Please upload your **Resume**, **Marksheet**, or **Certificates** (PDF or TXT) in the sidebar and click **⚡ Build Knowledge Base** before using this feature."

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "messages":       [],
    "rag_chain":      None,
    "retriever":      None,
    "uploaded_files": [],
    "quick_result":   None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 0 0.5rem;">
        <div style="font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:700; color:#fff; letter-spacing:-0.01em;">
            🎯 CareerBot
        </div>
        <div style="font-size:12px; color:#6B7280; margin-top:4px;">
            AI-Powered Career Guidance
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
                if file_bytes:  # Guard against empty read
                    with open(save_path, "wb") as f:
                        f.write(file_bytes)
                    new_files.append(file.name)
                    st.session_state.uploaded_files.append(file.name)
        if new_files:
            st.info(f"Saved: {', '.join(new_files)}")
            # Auto-rebuild index whenever new files are uploaded
            with st.spinner("Building knowledge base from your documents…"):
                vectorstore = build_index()
                if vectorstore:
                    chain, retriever = build_chain(vectorstore)
                    st.session_state.rag_chain  = chain
                    st.session_state.retriever  = retriever
                    st.success("✅ Knowledge base rebuilt with new documents!")

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    if st.button("⚡ Rebuild Knowledge Base", use_container_width=True):
        with st.spinner("Rebuilding index from all documents…"):
            vectorstore = build_index()
            if vectorstore:
                chain, retriever = build_chain(vectorstore)
                st.session_state.rag_chain  = chain
                st.session_state.retriever  = retriever
                st.success("✅ Knowledge base ready!")
            else:
                st.error("❌ No valid documents found in the data folder.")

    # Auto-load existing index only if no chain exists and no new uploads happened
    if st.session_state.rag_chain is None:
        vectorstore = load_index()
        if vectorstore:
            chain, retriever = build_chain(vectorstore)
            st.session_state.rag_chain  = chain
            st.session_state.retriever  = retriever
        else:
            st.info("💡 Upload documents above — the knowledge base will be built automatically.")

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
        st.session_state.messages     = []
        st.session_state.quick_result = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-block">
    <div class="hero-badge">✨ AI-Powered · RAG Technology · India-Focused</div>
    <div class="hero-title">Your Personal Career Guidance AI</div>
    <p class="hero-sub">
        Upload your resume, marksheets, or certificates and get deep personalised
        career insights, interview preparation, salary benchmarks, and step-by-step
        roadmaps — all grounded in your actual documents.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬  Career Chat",
    "📊  Resume Score",
    "🎯  Interview Prep",
    "🗺️  Career Roadmap",
    "🤝  Job Match",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Career Chat
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon">💬</div>
            <h3 class="section-title">Chat with Your Documents</h3>
        </div>
        <p class="section-subtitle">
            Ask anything about your career — based entirely on the documents you have uploaded.
        </p>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask me anything — e.g. What career suits me based on my resume?")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            if st.session_state.rag_chain:
                # Send the user's question directly — the prompt template handles grounding
                with st.spinner("Retrieving from your documents…"):
                    response = st.session_state.rag_chain.invoke(user_input)
                    st.markdown(response)

                with st.expander("📄 Source chunks retrieved from your documents"):
                    source_docs = st.session_state.retriever.invoke(user_input)
                    if source_docs:
                        for i, doc in enumerate(source_docs, 1):
                            src = doc.metadata.get("source_file", doc.metadata.get("source", ""))
                            st.markdown(f"**Chunk {i}** _(from {src})_: {doc.page_content[:400]}…")
                    else:
                        st.warning("No relevant chunks found in your documents for this query.")
            else:
                response = "📂 No knowledge base found. Please upload your **Resume**, **Marksheet**, or **Certificates** (PDF/TXT) in the sidebar to enable document-based answers."
                st.warning(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Resume Score
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon">📊</div>
            <h3 class="section-title">Resume Strength Analyser</h3>
        </div>
        <p class="section-subtitle">
            Get a detailed score, improvement tips, and a rewritten version of your weak sections.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        run_resume = st.button("🔍 Analyse My Resume", use_container_width=True, key="resume_btn")
    with col_info:
        st.markdown("""
        <div style="padding: 0.5rem 0; font-size:13px; color:var(--text-secondary); line-height:1.7;">
            ✅ Scores your resume out of 100 &nbsp;·&nbsp; ✅ Flags missing sections
            &nbsp;·&nbsp; ✅ Rewrites weak bullet points
        </div>""", unsafe_allow_html=True)

    if run_resume:
        query = """Analyse ONLY the resume content from the uploaded documents and provide:

1. 📊 Overall Resume Score out of 100

2. ✅ Strong Points (what is good in this resume)

3. ❌ Weak Points (what is missing or needs improvement)

4. 💡 Specific Improvement Suggestions:
   - Give exact lines from the resume that need to be rewritten
   - Show the improved version of each line

5. 🎯 Projected score after improvements

6. 📋 Missing Sections (e.g. LinkedIn, GitHub, achievements, metrics, summary)

IMPORTANT: Base everything ONLY on the actual content of the uploaded resume. Do not use outside knowledge."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("resume", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "resume":
        st.divider()
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume chunks used for analysis"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("resume skills experience education")
                if docs:
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}…")
                else:
                    st.warning("No resume content found in uploaded documents.")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Interview Prep
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon">🎯</div>
            <h3 class="section-title">Interview Preparation</h3>
        </div>
        <p class="section-subtitle">
            Interview questions generated from YOUR resume — not generic templates.
            Every question is specific to your background.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        interview_type = st.selectbox(
            "Interview Type",
            ["Technical Interview", "HR Interview", "Both Technical + HR"],
        )
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Fresher Level", "Mid Level (2-4 yrs)", "Senior Level (5+ yrs)"],
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🎯 Generate My Interview Questions", use_container_width=True, key="interview_btn"):
        query = f"""Read ONLY the uploaded resume document and generate {interview_type} questions at {difficulty} for this specific candidate.

Generate exactly:

1. 🔧 5 Technical Questions
   - Directly based on the skills, projects, and technologies in THEIR uploaded resume
   - Provide the ideal answer for each

2. 🤝 5 HR / Behavioural Questions
   - Based on their specific experience and background from the document
   - Provide the ideal STAR-format answer for each

3. ⭐ 3 Deep-Dive Tricky Questions
   - Questions that test deep understanding of their own listed experience
   - Provide the ideal answer for each

For every question, mention which part of the uploaded document it comes from.
IMPORTANT: Only use information from the uploaded documents. Do not generate generic questions."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("interview", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "interview":
        st.divider()
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume sections used for questions"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("skills projects experience technologies")
                if docs:
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}…")
                else:
                    st.warning("No relevant content found in uploaded documents.")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — Career Roadmap
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon">🗺️</div>
            <h3 class="section-title">Personalised Career Roadmap</h3>
        </div>
        <p class="section-subtitle">
            A step-by-step career plan built from your actual profile,
            with salary projections and target companies.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        target_role = st.text_input(
            "Dream Job Role (optional)",
            placeholder="e.g. Data Scientist, Product Manager",
        )
    with col2:
        timeframe = st.selectbox("Roadmap Duration", ["6 Months", "1 Year", "2 Years", "3 Years"])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗺️ Generate My Career Roadmap", use_container_width=True, key="roadmap_btn"):
        dream_job_text = (
            f"Their stated dream job is: {target_role}."
            if target_role
            else "Suggest the best career path based ONLY on their uploaded profile."
        )

        query = f"""Read ONLY the uploaded document (resume or marksheet) and generate a personalised career roadmap.

{dream_job_text}
Timeframe: {timeframe}

Structure your roadmap as follows (use ONLY information from the uploaded documents):

1. 📊 Current Profile Assessment
   - Strongest skills and subjects from the document
   - Current level based on uploaded content

2. 🗺️ Month-by-Month / Quarter-by-Quarter Roadmap for {timeframe}
   - Specific tasks for each period based on their profile

3. 📚 Specific Courses and Certifications relevant to their background

4. 🏫 Higher Education Options relevant to their field

5. 💰 Salary Progression Forecast (in ₹/month) based on their domain

6. 🏢 Target Companies (Tier-wise) relevant to their skills

7. ⚠️ Skill Gaps to Fill based on uploaded document content

IMPORTANT: Base the entire roadmap ONLY on the uploaded document content. Do not use outside knowledge."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("roadmap", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "roadmap":
        st.divider()
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Document sections used for roadmap"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("education skills subjects marks experience")
                if docs:
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}…")
                else:
                    st.warning("No relevant content found in uploaded documents.")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — Job Match
# ═══════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon">🤝</div>
            <h3 class="section-title">Job Description Matcher</h3>
        </div>
        <p class="section-subtitle">
            Paste any job description and get a precise match score, gap analysis,
            and a tailored resume rewrite guide.
        </p>
    </div>
    """, unsafe_allow_html=True)

    job_description = st.text_area(
        "Paste the Job Description here",
        height=220,
        placeholder="Paste the full job description here — requirements, responsibilities, and skills needed…",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🤝 Check My Job Match Score", use_container_width=True, key="jobmatch_btn"):
        if not job_description.strip():
            st.warning("⚠️ Please paste a job description above before checking.")
        else:
            query = f"""Compare ONLY my uploaded resume against this job description and give a detailed match analysis.

JOB DESCRIPTION:
{job_description}

Provide (using ONLY my uploaded resume content):

1. 🎯 Overall Match Score (X / 100) based on skills found in my resume vs JD requirements

2. ✅ Skills I Have That Match the JD
   - List each matching skill found in my uploaded resume

3. ❌ Skills I Am Missing
   - List each required JD skill NOT found in my uploaded resume
   - Mark each as High / Medium / Low priority

4. 📚 How to Fill the Skill Gaps
   - Specific course or certification for each missing skill
   - Estimated time to learn each

5. 💡 How to Rewrite My Resume for This Specific Job
   - Exact lines from my uploaded resume to change or strengthen
   - Keywords from the JD to incorporate

6. 🏆 Final Verdict
   - Should I apply now or prepare more?
   - If prepare — give realistic timeline

IMPORTANT: Only use content from the uploaded resume. Do not guess or fabricate skills."""

            result = run_quick_action(query)
            st.session_state.quick_result = ("jobmatch", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "jobmatch":
        st.divider()
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume sections compared with JD"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("skills experience projects technologies")
                if docs:
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}…")
                else:
                    st.warning("No relevant resume content found in uploaded documents.")