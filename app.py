import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(page_title="TaskPilot AI", layout="wide")

# Sidebar
render_sidebar()

st.title("🚀 TaskPilot AI")
st.write("Welcome! Use the sidebar to navigate.")
