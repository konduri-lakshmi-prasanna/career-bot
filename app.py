import streamlit as st

st.set_page_config(page_title="CareerBot")

from ui.styles import get_custom_css

st.success("Imported")

css = get_custom_css()

st.success("CSS Generated")

st.markdown(css, unsafe_allow_html=True)

st.success("CSS Applied")