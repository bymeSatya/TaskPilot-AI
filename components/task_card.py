import streamlit as st
from datetime import datetime

def render_task_card(task):
    st.markdown(f"### {task['title']}")
    st.write(task["description"])
    st.write(f"**Status:** {task['status']}")
    created_at = datetime.fromisoformat(task["created_at"])
    st.write(f"**Created At:** {created_at.strftime('%b %d, %Y')}")
    if st.button("Open Task", key=f"open_{task['id']}"):
        st.session_state["selected_task"] = task["id"]
        st.switch_page("pages/5_Task_Detail.py")
