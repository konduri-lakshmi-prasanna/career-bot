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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Career Guidance Bot",
    page_icon="🎯",
    layout="wide"
)

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

# ── Build FAISS index ─────────────────────────────────────────────────────────
def build_index():
    embeddings = get_embeddings()
    documents  = []
    splitter   = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )

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
            INDEX_FOLDER, embeddings,
            allow_dangerous_deserialization=True
        )
    return None

# ── Build RAG chain ───────────────────────────────────────────────────────────
def build_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm       = get_llm()

    prompt_template = """You are a friendly career guidance counselor for students in India.
Use the context provided below (retrieved from the student's uploaded documents) to answer accurately.
Always base your answer on what is in the document.

Context from uploaded documents:
{context}

Question: {question}

Answer clearly and in a structured format."""

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

# ── Quick action using RAG chain ──────────────────────────────────────────────
def run_quick_action(query):
    if st.session_state.rag_chain:
        with st.spinner("Analyzing your documents..."):
            response = st.session_state.rag_chain.invoke(query)
            return response
    else:
        return "⚠️ Please upload documents and build the knowledge base first."

# ── Session state init ────────────────────────────────────────────────────────
if "messages"       not in st.session_state:
    st.session_state.messages       = []
if "rag_chain"      not in st.session_state:
    st.session_state.rag_chain      = None
if "retriever"      not in st.session_state:
    st.session_state.retriever      = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "quick_result"   not in st.session_state:
    st.session_state.quick_result   = None
if "active_tab"     not in st.session_state:
    st.session_state.active_tab     = "💬 Career Chat"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Your Documents")
    st.markdown("Upload your **Resume**, **Marksheet**, **Certificates**, or **Job Description** PDFs.")

    uploaded = st.file_uploader(
        "Choose files",
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
    if st.button("⚡ Build Knowledge Base", use_container_width=True):
        with st.spinner("Building index from your documents..."):
            vectorstore = build_index()
            if vectorstore:
                chain, retriever = build_chain(vectorstore)
                st.session_state.rag_chain  = chain
                st.session_state.retriever  = retriever
                st.success("✅ Knowledge base ready!")
            else:
                st.error("❌ No valid documents found.")

    # ── Auto load existing index ──────────────────────────────────────────────
    if st.session_state.rag_chain is None:
        vectorstore = load_index()
        if vectorstore:
            chain, retriever = build_chain(vectorstore)
            st.session_state.rag_chain = chain
            st.session_state.retriever = retriever
            st.success("✅ Knowledge base loaded!")
        else:
            st.info("💡 Upload documents and click Build Knowledge Base.")

    st.divider()

    # ── Uploaded files list ───────────────────────────────────────────────────
    if st.session_state.uploaded_files:
        st.markdown("**📋 Uploaded Files:**")
        for fname in st.session_state.uploaded_files:
            st.markdown(f"- 📄 {fname}")

    st.divider()

    # ── Mode indicator ────────────────────────────────────────────────────────
    if st.session_state.rag_chain:
        st.success("🟢 RAG Mode — Document Based")
    else:
        st.warning("🔴 No Knowledge Base Loaded")

    # ── Clear chat ────────────────────────────────────────────────────────────
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages     = []
        st.session_state.quick_result = None
        st.rerun()

# ── Main Title ────────────────────────────────────────────────────────────────
st.title("🎯 Career Guidance RAG Chatbot")
st.markdown("**Upload your documents and get personalized career guidance powered by AI**")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Career Chat",
    "📊 Resume Score",
    "🎯 Interview Prep",
    "🗺️ Career Roadmap",
    "🤝 Job Match"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Career Chat
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("💬 Chat With Your Documents")
    st.markdown("Ask anything about your career based on your uploaded documents.")

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(
        "Ask me anything — e.g. What career suits me based on my resume?"
    )

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving from your documents..."):
                if st.session_state.rag_chain:
                    query = f"""Based on the uploaded documents, answer this question for an Indian student:
{user_input}

Provide your answer in this structured format:
1. 🎯 Top 3 Career Paths that suit them
2. 📚 Key Skills needed for each career path
3. 🏫 Courses or Degrees to pursue (mention Indian universities)
4. 💰 Realistic Monthly Salary Range in ₹ (fresher AND experienced separately)
5. 🏢 Top Indian Companies or Sectors that hire
6. 💡 One motivational tip for Indian students"""

                    response = st.session_state.rag_chain.invoke(query)
                    st.markdown(response)

                    with st.expander("📄 Sources retrieved from your documents"):
                        source_docs = st.session_state.retriever.invoke(user_input)
                        for i, doc in enumerate(source_docs, 1):
                            st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")
                else:
                    response = "⚠️ Please upload your documents and click **Build Knowledge Base** in the sidebar first."
                    st.warning(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Resume Score
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Resume Strength Analyzer")
    st.markdown("Upload your **Resume PDF** and get a detailed score with improvement tips.")

    if st.button("🔍 Analyze My Resume", use_container_width=True, key="resume_btn"):
        query = """Analyze the resume from the uploaded document carefully and provide:

1. 📊 Overall Resume Score out of 100

2. ✅ Strong Points (what is good in this resume)

3. ❌ Weak Points (what is missing or needs improvement)

4. 💡 Specific Improvement Suggestions:
   - Give exact lines from resume that need to be rewritten
   - Show the improved version of each line

5. 🎯 What score it can become after improvements

6. 📋 Missing Sections (e.g. LinkedIn, GitHub, achievements, metrics)

Be very specific and base everything on the actual content of the uploaded resume."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("resume", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "resume":
        st.markdown("---")
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume chunks used for analysis"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("resume skills experience education")
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Interview Prep
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🎯 Interview Preparation")
    st.markdown("Get interview questions generated **specifically from your resume**.")

    col1, col2 = st.columns(2)
    with col1:
        interview_type = st.selectbox(
            "Select Interview Type",
            ["Technical Interview", "HR Interview", "Both Technical + HR"]
        )
    with col2:
        difficulty = st.selectbox(
            "Select Difficulty",
            ["Fresher Level", "Mid Level", "Senior Level"]
        )

    if st.button("🎯 Generate My Interview Questions", use_container_width=True, key="interview_btn"):
        query = f"""Read the uploaded resume carefully and generate {interview_type} questions at {difficulty} for this specific person.

Generate exactly:

1. 🔧 5 Technical Questions
   - Based on the specific skills, projects, and technologies mentioned in THEIR resume
   - Give the ideal answer for each question

2. 🤝 5 HR Questions
   - Based on their specific experience and background from the resume
   - Give the ideal answer for each question

3. ⭐ 3 Tricky Questions
   - Questions that test deep understanding of what they have mentioned
   - Give the ideal answer for each question

Important: Every question must be specific to THIS person's resume — not generic questions.
Mention which part of their resume each question is based on."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("interview", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "interview":
        st.markdown("---")
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume sections used for questions"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("skills projects experience technologies")
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Career Roadmap
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🗺️ Personalized Career Roadmap")
    st.markdown("Upload your **Marksheet or Resume** and get a step by step career roadmap.")

    col1, col2 = st.columns(2)
    with col1:
        target_role = st.text_input(
            "Your Dream Job (optional)",
            placeholder="e.g. Data Scientist, Software Engineer"
        )
    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            ["1 Year", "2 Years", "3 Years", "4 Years"]
        )

    if st.button("🗺️ Generate My Career Roadmap", use_container_width=True, key="roadmap_btn"):
        dream_job_text = f"Their dream job is: {target_role}." if target_role else "Suggest the best career based on their profile."

        query = f"""Read the uploaded document carefully (resume or marksheet) and generate a personalized career roadmap for this Indian student.

{dream_job_text}
Timeframe: {timeframe}

Provide:

1. 📊 Current Profile Assessment
   - Their strongest subjects or skills from the document
   - Their current level

2. 🗺️ Month by Month Roadmap for {timeframe}
   - Specific actions for each month or quarter
   - What to learn, what to build, what certifications to get

3. 📚 Specific Courses and Certifications
   - Free resources (YouTube, NPTEL, Coursera free)
   - Paid resources worth investing in

4. 🏫 College or Further Education Recommendations
   - Based on their current profile
   - Indian universities and entrance exams

5. 💰 Expected Salary Progression
   - Starting salary in ₹
   - After 1 year, 3 years, 5 years

6. 🏢 Target Companies to Apply
   - Based on their profile and dream job
   - Tier 1, Tier 2, and startup options

7. ⚠️ Gaps to Fill
   - What is missing from their profile right now
   - Priority order to fill those gaps

Base everything on their actual document content."""

        result = run_quick_action(query)
        st.session_state.quick_result = ("roadmap", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "roadmap":
        st.markdown("---")
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Document sections used for roadmap"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("education skills subjects marks experience")
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Job Match
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🤝 Job Description Matcher")
    st.markdown("Upload your **Resume PDF** + paste a **Job Description** to see how well you match.")

    job_description = st.text_area(
        "Paste the Job Description here",
        height=200,
        placeholder="Paste the full job description here — requirements, skills, responsibilities..."
    )

    if st.button("🤝 Check My Job Match", use_container_width=True, key="jobmatch_btn"):
        if not job_description.strip():
            st.warning("⚠️ Please paste a job description first.")
        else:
            query = f"""I have uploaded my resume. Compare it against this job description and tell me how well I match.

JOB DESCRIPTION:
{job_description}

Provide a detailed analysis:

1. 🎯 Overall Match Score out of 100%

2. ✅ Skills I Have That Match the JD
   - List each matching skill found in my resume

3. ❌ Skills I Am Missing
   - List each required skill from JD not in my resume
   - How important each missing skill is (High/Medium/Low)

4. 📚 How to Fill the Skill Gap
   - Specific courses or certifications for each missing skill
   - Time needed to learn each skill

5. 💡 How to Rewrite My Resume for This Job
   - Specific lines to change or add
   - Keywords from JD to include

6. 🏆 Final Verdict
   - Should I apply now or prepare more?
   - If prepare — give exact timeline

Base the match analysis on my actual uploaded resume content."""

            result = run_quick_action(query)
            st.session_state.quick_result = ("jobmatch", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "jobmatch":
        st.markdown("---")
        st.markdown(st.session_state.quick_result[1])

        with st.expander("📄 Resume sections compared with JD"):
            if st.session_state.retriever:
                docs = st.session_state.retriever.invoke("skills experience projects technologies")
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**Chunk {i}:** {doc.page_content[:300]}...")
