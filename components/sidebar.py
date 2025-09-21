import streamlit as st

def render_sidebar():
    st.sidebar.title("TaskPilot AI")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/1_Dashboard.py", label="🏠 Dashboard")
    st.sidebar.page_link("pages/2_All_Tasks.py", label="📋 All Tasks")
    st.sidebar.page_link("pages/3_Open_Tasks.py", label="🔓 Open Tasks")
    st.sidebar.page_link("pages/4_Closed_Tasks.py", label="✅ Closed Tasks")
    st.sidebar.page_link("pages/6_Knowledge_Base.py", label="📚 Knowledge Base")
