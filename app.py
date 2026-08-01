import streamlit as st

st.set_page_config(page_title="CareerBot")

from ui.styles import get_custom_css

st.markdown(get_custom_css(), unsafe_allow_html=True)

st.success("Styles Loaded")