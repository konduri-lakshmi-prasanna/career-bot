"""
ui_tabs.py — Logic for rendering Streamlit tabs.
"""

import streamlit as st

from prompts import (
    resume_analysis_prompt,
    interview_prep_prompt,
    career_roadmap_prompt,
    job_match_prompt,
)
from state import set_quick_result

# Quick Action Helper
def run_quick_action(query: str) -> str:
    if st.session_state.rag_chain:
        with st.spinner("Analysing your documents…"):
            return st.session_state.rag_chain.invoke(query)
    return "📂 No documents uploaded yet. Please upload your **Resume**, **Marksheet**, or **Certificates** (PDF or TXT) in the sidebar and click **⚡ Build Knowledge Base** before using this feature."


def render_career_chat_tab():
    st.markdown("""
    <div class="dash-card card-blue" style="margin-bottom: 20px;">
        <div class="card-icon">💬</div>
        <div class="card-title">COMMS LINK</div>
        <div class="card-value" style="font-size: 18px;">Chat with Your Documents</div>
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


def render_resume_score_tab():
    st.markdown("""
    <div class="dash-card card-pink" style="margin-bottom: 20px;">
        <div class="card-icon">📊</div>
        <div class="card-title">DIAGNOSTICS</div>
        <div class="card-value" style="font-size: 18px;">Resume Strength Analyser</div>
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
        query = resume_analysis_prompt()
        result = run_quick_action(query)
        set_quick_result("resume", result)

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


def render_interview_prep_tab():
    st.markdown("""
    <div class="dash-card card-orange" style="margin-bottom: 20px;">
        <div class="card-icon">🎯</div>
        <div class="card-title">SIMULATION</div>
        <div class="card-value" style="font-size: 18px;">Interview Preparation</div>
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
        query = interview_prep_prompt(interview_type, difficulty)
        result = run_quick_action(query)
        set_quick_result("interview", result)

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


def render_career_roadmap_tab():
    st.markdown("""
    <div class="dash-card card-green" style="margin-bottom: 20px;">
        <div class="card-icon">🗺️</div>
        <div class="card-title">TRAJECTORY</div>
        <div class="card-value" style="font-size: 18px;">Personalised Career Roadmap</div>
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
        query = career_roadmap_prompt(target_role, timeframe)
        result = run_quick_action(query)
        set_quick_result("roadmap", result)

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


def render_job_match_tab():
    st.markdown("""
    <div class="dash-card card-blue" style="margin-bottom: 20px;">
        <div class="card-icon">🤝</div>
        <div class="card-title">ALIGNMENT CHECK</div>
        <div class="card-value" style="font-size: 18px;">Job Description Matcher</div>
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
            query = job_match_prompt(job_description)
            result = run_quick_action(query)
            set_quick_result("jobmatch", result)

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
