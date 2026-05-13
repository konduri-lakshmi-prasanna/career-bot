import streamlit as st

from ui_styles import get_custom_css
from ui_sidebar import render_sidebar
from ui_tabs import (
    render_career_chat_tab,
    render_resume_score_tab,
    render_interview_prep_tab,
    render_career_roadmap_tab,
    render_job_match_tab,
)
from state import init_state

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerBot — AI Career Guidance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INITIALISE STATE
# ─────────────────────────────────────────────────────────────────────────────
init_state()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
render_sidebar()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────────────────────────────────────
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