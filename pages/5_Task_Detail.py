# pages/5_Task_Detail.py
import streamlit as st
from datetime import datetime
from services.task_manager import load_tasks, save_tasks, delete_task
from dateutil import parser

st.set_page_config(layout="centered", page_title="Task Detail")

task_id = st.query_params.get("task_id", [None])[0] if "task_id" in st.query_params else None
if not task_id:
    st.error("No task selected.")
    st.stop()

tasks = load_tasks()
task = next((t for t in tasks if str(t["id"]) == str(task_id)), None)
if not task:
    st.error("Task not found.")
    st.stop()

# ---- Render Task Details ----
st.header(task["title"])
st.caption(task.get("description", ""))

status = task.get("status", "Open")
st.write("**Status:**", status)

created_at = parser.parse(task["created_at"]) if isinstance(task["created_at"], str) else task["created_at"]
st.write("**Created:**", created_at.strftime("%b %d, %Y"))

if task.get("completed_at"):
    completed_at = parser.parse(task["completed_at"])
    st.write("**Completed:**", completed_at.strftime("%b %d, %Y"))
else:
    st.write("**Completed:** -")

# Urgency (reuse segmented progress)
days_old = (datetime.now() - created_at).days
def render_progress(days_old: int):
    segs = [2,2,1]
    rem = min(max(0, days_old), 5)
    fills, colors = [], ["#2ecc71", "#f39c12", "#e74c3c"]
    for seg in segs:
        fills.append(min(rem, seg))
        rem -= min(rem, seg)
    html = "<div style='display:flex;gap:6px;'>"
    for i, seg in enumerate(segs):
        perc = int((fills[i]/seg)*100)
        html += f"<div style='flex:{seg};background:#0f1720;height:14px;border-radius:6px;'>"
        html += f"<div style='width:{perc}%;background:{colors[i]};height:100%;'></div></div>"
    html += f"<span style='color:#9fb4d6;margin-left:8px'>{days_old} day(s) old</span></div>"
    return html
st.markdown("**Urgency:**", unsafe_allow_html=True)
st.markdown(render_progress(days_old), unsafe_allow_html=True)

# ---- Actions ----
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if status.lower() not in ("completed", "closed"):
        if st.button("✅ Mark Completed"):
            task["status"] = "Completed"
            task["completed_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            st.success("Task marked completed")
            st.rerun()
with col2:
    if st.button("🗑️ Delete Task"):
        delete_task(task["id"])
        st.success("Task deleted")
        st.switch_page("pages/2_All_Tasks.py")
