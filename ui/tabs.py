"""
ui/tabs.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: render_career_chat_tab() called ask(chain, retriever, question, messages)
        — pulling chain and retriever out of session_state.
        _show_source_chunks() pulled st.session_state.retriever directly.

AFTER:  render_career_chat_tab() calls run_query(user_input) — one call,
        all 6 rag-core stages run internally.
        _show_source_chunks() calls pipeline.retrieve(query) directly to
        show the same chunks the pipeline used.
        All st.session_state.rag_chain / .retriever references removed.
        Replaced with st.session_state.kb_ready (bool) checks only.
        UI layout, markdown, widgets — all unchanged.
"""

import streamlit as st

from core.prompts import (
    resume_analysis_prompt,
    interview_prep_prompt,
    career_roadmap_prompt,
    job_match_prompt,
)
from services.pipeline import get_pipeline, run_query
from services.actions import run_quick_action
from ui.state import set_quick_result, append_message


# ── Helpers ───────────────────────────────────────────────────────────────────

def _show_source_chunks(query: str):
    """Show retrieved chunks. Uses pipeline.retrieve() — same Stage 2 the
    pipeline used — so displayed chunks are always consistent with the answer."""
    with st.expander("📄 Source chunks used"):
        if not st.session_state.kb_ready:
            st.warning("No knowledge base loaded.")
            return
        pipeline = get_pipeline()
        raw_chunks = pipeline.retrieve(query)        # list[dict] from rag-core
        if raw_chunks:
            for i, chunk in enumerate(raw_chunks[:6], 1):
                src = chunk.get("metadata", {}).get(
                    "source_file",
                    chunk.get("metadata", {}).get("source", "unknown")
                )
                st.markdown(f"**Chunk {i}** _(from {src})_: {chunk['text'][:300]}…")
        else:
            st.warning("No relevant content found in uploaded documents.")


# ── Tab renderers ─────────────────────────────────────────────────────────────

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
        with st.chat_message("user"):
            st.markdown(user_input)

        append_message("user", user_input)

        with st.chat_message("assistant"):
            if st.session_state.kb_ready:
                with st.spinner("Retrieving from your documents…"):
                    response = run_query(user_input)   # ← all 6 rag-core stages
                    st.markdown(response)
                _show_source_chunks(user_input)
            else:
                response = (
                    "📂 No knowledge base found. Please upload your **Resume**, "
                    "**Marksheet**, or **Certificates** (PDF/TXT) in the sidebar "
                    "to enable document-based answers."
                )
                st.warning(response)

        append_message("assistant", response)


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
        result = run_quick_action(resume_analysis_prompt())
        set_quick_result("resume", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "resume":
        st.divider()
        st.markdown(st.session_state.quick_result[1])
        _show_source_chunks("resume skills experience education")


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
        result = run_quick_action(interview_prep_prompt(interview_type, difficulty))
        set_quick_result("interview", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "interview":
        st.divider()
        st.markdown(st.session_state.quick_result[1])
        _show_source_chunks("skills projects experience technologies")


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
        result = run_quick_action(career_roadmap_prompt(target_role, timeframe))
        set_quick_result("roadmap", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "roadmap":
        st.divider()
        st.markdown(st.session_state.quick_result[1])
        _show_source_chunks("education skills subjects marks experience")


def render_job_match_tab():
    st.markdown("""
    <div class="dash-card card-blue" style="margin-bottom: 20px;">
        <div class="card-icon">🤝</div>
        <div class="card-title">ALIGNMENT CHECK</div>
        <div class="card-value" style="font-size: 18px;">Job Description Matcher</div>
    </div>
    """, unsafe_allow_html=True)

    job_description = st.text_area(
        "Paste the Job Description here", height=220,
        placeholder="Paste the full job description here — requirements, responsibilities, and skills needed…",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🤝 Check My Job Match Score", use_container_width=True, key="jobmatch_btn"):
        if not job_description.strip():
            st.warning("⚠️ Please paste a job description above before checking.")
        else:
            result = run_quick_action(job_match_prompt(job_description))
            set_quick_result("jobmatch", result)

    if st.session_state.quick_result and st.session_state.quick_result[0] == "jobmatch":
        st.divider()
        st.markdown(st.session_state.quick_result[1])
        _show_source_chunks("skills experience projects technologies")