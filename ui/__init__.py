"""
ui — Streamlit presentation layer for CareerBot.

All Streamlit-specific rendering lives here. Business logic is delegated
to the `services` and `core` packages.
"""

from ui.state import init_state, clear_chat, set_kb_ready, add_uploaded_file, set_quick_result
from ui.styles import get_custom_css
from ui.sidebar import render_sidebar
from ui.tabs import (
    render_career_chat_tab,
    render_resume_score_tab,
    render_interview_prep_tab,
    render_career_roadmap_tab,
    render_job_match_tab,
)