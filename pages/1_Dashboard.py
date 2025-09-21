import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks

st.title("📊 Dashboard")

tasks = load_tasks()

# --- Categorize tasks ---
open_tasks = [t for t in tasks if t["status"] == "Open"]
closed_tasks = [t for t in tasks if t["status"] == "Closed"]

now = datetime.now()

def task_age_days(task):
    return (now - datetime.fromisoformat(task["created_at"])).days

overdue_tasks = [t for t in open_tasks if task_age_days(t) > 5]
nearing_deadline_tasks = [t for t in open_tasks if 3 <= task_age_days(t) <= 5]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔓 Open Tasks", len(open_tasks))
col2.metric("⚠️ Overdue", len(overdue_tasks))
col3.metric("⏳ Nearing Deadline", len(nearing_deadline_tasks))
col4.metric("✅ Closed", len(closed_tasks))

st.markdown("---")

# --- Priority Section ---
st.subheader("🔥 Priority: Overdue Tasks")
if not overdue_tasks:
    st.success("No overdue tasks! 🎉")
else:
    for task in overdue_tasks:
        st.markdown(f"**{task['title']}** — Created {task_age_days(task)} days ago")
        st.caption(task["description"])
        st.write(f"🕒 Created: {task['created_at']}")
        st.markdown("---")
