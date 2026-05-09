import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Career Guidance Bot", page_icon="🎯", layout="centered")
st.title("🎯 Career Guidance Chatbot")
st.markdown("**Tell me your skills or interests — I'll suggest career paths!**")
st.divider()

INDEX_FOLDER = "faiss_index"
DATA_FOLDER  = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ── Embeddings (cached) ───────────────────────────────────────────────────────
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ── LLM (cached) ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7
    )

# ── Build / rebuild FAISS index from data/ folder ─────────────────────────────
def build_index():
    embeddings = get_embeddings()
    documents  = []
    splitter   = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for filename in os.listdir(DATA_FOLDER):
        filepath = os.path.join(DATA_FOLDER, filename)
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            elif filename.endswith(".txt"):
                loader = TextLoader(filepath)
            else:
                continue
            documents += loader.load()
        except Exception as e:
            st.sidebar.warning(f"Could not load {filename}: {e}")

    if not documents:
        return None

    chunks      = splitter.split_documents(documents)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_FOLDER)
    return vectorstore

# ── Load existing FAISS index ─────────────────────────────────────────────────
def load_index():
    embeddings = get_embeddings()
    if os.path.exists(INDEX_FOLDER):
        return FAISS.load_local(
            INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True
        )
    return None

# ── Build RAG chain from vectorstore ─────────────────────────────────────────
def build_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm       = get_llm()

    prompt_template = """You are a friendly career guidance counselor for students in India.
Use the context provided below (retrieved from a career knowledge base) to answer accurately.
If the context does not have enough info, use your general knowledge but stay focused on Indian career guidance.

Context from knowledge base:
{context}

Student's question: {question}

Provide your answer in this structured format:

1. 🎯 Top 3 Career Paths that suit them

2. 📚 Key Skills needed for each career path

3. 🏫 Courses or Degrees to pursue (mention Indian universities/boards where relevant)

4. 💰 Realistic Monthly Salary Range in ₹:
   - Fresher salary AND experienced salary separately
   - Use realistic current Indian market figures

5. 🏢 Top Indian Companies or Sectors that hire for each career

6. 💡 One motivational tip tailored for Indian students

Keep the tone friendly, encouraging, and practical."""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever

# ── Session state init ────────────────────────────────────────────────────────
if "messages"       not in st.session_state:
    st.session_state.messages       = []
if "rag_chain"      not in st.session_state:
    st.session_state.rag_chain      = None
if "retriever"      not in st.session_state:
    st.session_state.retriever      = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Knowledge Base")
    st.markdown("Upload PDF or TXT files for accurate answers.\n\n*Without documents, the bot uses general knowledge.*")

    uploaded = st.file_uploader(
        "Upload career documents",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded:
        new_files = []
        for file in uploaded:
            save_path = os.path.join(DATA_FOLDER, file.name)
            if file.name not in st.session_state.uploaded_files:
                with open(save_path, "wb") as f:
                    f.write(file.read())
                new_files.append(file.name)
                st.session_state.uploaded_files.append(file.name)
        if new_files:
            st.info(f"📄 Saved: {', '.join(new_files)}")

    # ── Build index button ────────────────────────────────────────────────────
    if st.button("⚡ Build / Rebuild Knowledge Base", use_container_width=True):
        with st.spinner("Building index... please wait"):
            vectorstore = build_index()
            if vectorstore:
                chain, retriever = build_chain(vectorstore)
                st.session_state.rag_chain  = chain
                st.session_state.retriever  = retriever
                st.success("✅ Knowledge base ready!")
            else:
                st.error("❌ No valid documents found in data/ folder.")

    st.divider()

    # ── Auto-load existing index on startup ───────────────────────────────────
    if st.session_state.rag_chain is None:
        vectorstore = load_index()
        if vectorstore:
            chain, retriever = build_chain(vectorstore)
            st.session_state.rag_chain = chain
            st.session_state.retriever = retriever
            st.success("✅ Existing knowledge base loaded!")
        else:
            st.info("💡 No knowledge base loaded — bot will use general knowledge.\nUpload documents for more accurate answers.")

    # ── Show uploaded files ───────────────────────────────────────────────────
    if st.session_state.uploaded_files:
        st.markdown("**📋 Uploaded Files:**")
        for fname in st.session_state.uploaded_files:
            st.markdown(f"- {fname}")

    # ── Current mode indicator ────────────────────────────────────────────────
    st.divider()
    if st.session_state.rag_chain:
        st.success("🟢 Mode: RAG (Document-based)")
    else:
        st.info("🔵 Mode: General Knowledge (No documents)")

    # ── Clear chat button ─────────────────────────────────────────────────────
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Tell me your skills or interests (e.g. I love math and computers)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your profile..."):

            if st.session_state.rag_chain:
                # ── RAG MODE — uses uploaded documents ────────────────────────
                response = st.session_state.rag_chain.invoke(user_input)
                st.markdown(response)

                with st.expander("📄 Sources used from knowledge base"):
                    source_docs = st.session_state.retriever.invoke(user_input)
                    for i, doc in enumerate(source_docs, 1):
                        st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")

            else:
                # ── FALLBACK MODE — uses LLM general knowledge ─────────────────
                llm = get_llm()
                messages = [
                    SystemMessage(content="""You are a friendly career guidance counselor for students in India.
When a student shares their skills or interests, provide:

1. 🎯 Top 3 Career Paths that suit them
2. 📚 Key Skills needed for each career path
3. 🏫 Courses or Degrees to pursue (mention Indian universities/boards where relevant, e.g., IIT, NIT, IGNOU)
4. 💰 Realistic Monthly Salary Range in ₹:
   - Always give salary in ₹/month
   - Mention fresher salary AND experienced salary separately
   - Use realistic current Indian market figures
5. 🏢 Top Indian Companies or Sectors that hire for each career
6. 💡 One motivational tip tailored for Indian students

Keep the tone friendly, encouraging, and practical for Indian students."""),
                    HumanMessage(content=user_input)
                ]
                result   = llm.invoke(messages)
                response = result.content
                st.markdown(response)
                st.caption("💡 Answering from general knowledge — upload documents for more accurate answers.")

    st.session_state.messages.append({"role": "assistant", "content": response})