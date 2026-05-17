"""
app.py — Streamlit entrypoint for CareerBot.
"""

import streamlit as st

st.set_page_config(
    page_title="CareerBot — AI Career Guidance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from ui.styles import get_custom_css
    from ui.sidebar import render_sidebar
    from ui.tabs import (
        render_career_chat_tab,
        render_resume_score_tab,
        render_interview_prep_tab,
        render_career_roadmap_tab,
        render_job_match_tab,
    )
    from ui.state import init_state
except ImportError as e:
    st.error(f"❌ Missing dependency: {e}")
    st.info("Run:  pip install -r requirements.txt")
    st.stop()

st.markdown(get_custom_css(), unsafe_allow_html=True)

init_state()

render_sidebar()

st.markdown("""
<div class="status-dashboard">
    <div class="status-pulse"></div>
    <span class="status-text">CAREER COMMAND CENTER • AI ONLINE • SYSTEM READY</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "[ COMMS ]",
    "[ DIAGNOSTICS ]",
    "[ SIMULATION ]",
    "[ TRAJECTORY ]",
    "[ ALIGNMENT ]",
])

with tab1:
    render_career_chat_tab()

with tab2:
    render_resume_score_tab()

with tab3:
    render_interview_prep_tab()

with tab4:
    render_career_roadmap_tab()

with tab5:
    render_job_match_tab()