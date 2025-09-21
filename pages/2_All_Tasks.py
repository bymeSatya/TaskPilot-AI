import streamlit as st
from services.task_manager import load_tasks, add_task
from components.task_card import render_task_card

st.title("📋 All Tasks")

tasks = load_tasks()

with st.expander("➕ Create New Task"):
    title = st.text_input("Task Title")
    desc = st.text_area("Description")
    if st.button("Add Task"):
        if title:
            add_task(title, desc)
            st.success("Task added! Refresh page.")
        else:
            st.error("Please enter a title.")

for task in tasks:
    render_task_card(task)
