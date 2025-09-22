import streamlit as st
from components.sidebar import render as sidebar_render

st.set_page_config(page_title="TaskPilot AI", layout="wide", initial_sidebar_state="expanded")

# Ensure default page selection is Dashboard
if "nav_radio" not in st.session_state:
    st.session_state["nav_radio"] = "Dashboard"

active = sidebar_render(st.session_state["nav_radio"])
st.session_state["nav_radio"] = active

# Redirect to the selected page (Streamlit multipage style)
if active != "Dashboard":
    st.switch_page(f"pages/{['Dashboard','All Tasks','Open Tasks','Closed Tasks','Knowledge Base','Development'].index(active)+1}_{active.replace(' ','_')}.py")
else:
    st.switch_page("pages/1_Dashboard.py")