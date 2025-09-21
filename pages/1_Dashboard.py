import streamlit as st
from services.task_manager import load_tasks

st.title("📊 Dashboard")

tasks = load_tasks()
open_tasks = [t for t in tasks if t["status"] == "Open"]
closed_tasks = [t for t in tasks if t["status"] == "Closed"]

col1, col2 = st.columns(2)
col1.metric("Open Tasks", len(open_tasks))
col2.metric("Closed Tasks", len(closed_tasks))

st.write("### Task Progress Overview")
if not tasks:
    st.info("No tasks yet. Go to **All Tasks** to add one.")
else:
    for task in tasks:
        st.progress(len(task["updates"]) * 10 % 100, text=task["title"])
