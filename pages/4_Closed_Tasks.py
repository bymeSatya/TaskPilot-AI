import streamlit as st
from services.task_manager import load_tasks
from components.task_card import render_task_card

st.title("✅ Closed Tasks")

tasks = [t for t in load_tasks() if t["status"] == "Closed"]

if not tasks:
    st.info("No closed tasks.")
else:
    for task in tasks:
        render_task_card(task)
