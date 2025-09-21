import streamlit as st
from services.task_manager import load_tasks
from components.task_card import render_task_card

st.title("🔓 Open Tasks")

tasks = [t for t in load_tasks() if t["status"] == "Open"]

if not tasks:
    st.info("No open tasks.")
else:
    for task in tasks:
        render_task_card(task)
