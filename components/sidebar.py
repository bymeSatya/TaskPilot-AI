import streamlit as st

def render(active: str):
    st.sidebar.markdown("### TaskPilot AI")
    return st.sidebar.radio(
        "Navigation",
        ["Dashboard","All Tasks","Open Tasks","Closed Tasks","Knowledge Base","Development"],
        index=["Dashboard","All Tasks","Open Tasks","Closed Tasks","Knowledge Base","Development"].index(active),
        label_visibility="collapsed",
        key="nav_radio"
    )