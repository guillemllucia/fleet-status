import streamlit as st
from src.i18n import TEXT

st.set_page_config(
    page_title=TEXT["page_config_home_title"],
    page_icon=TEXT["page_config_icon"],
    layout="wide"
)

st.title(TEXT["welcome_title"])
st.sidebar.success(TEXT["sidebar_select_page"])
st.write(TEXT["welcome_instructions"])
