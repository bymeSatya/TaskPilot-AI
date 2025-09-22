import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks

st.set_page_config(page_title="Dashboard", layout="wide")

# --- Custom CSS for KPI Cards ---
st.markdown("""
    <style>
    .kpi-card {
        border-radius: 15px;
        padding: 20px;
        background-color: #1c1f26;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin: 5px;
    }
    .kpi-title {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: bold;
        margin: 5px 0;
    }
    .kpi-desc {
        font-size: 13px;
        color: #aaa;
    }
    .green { color: #4CAF50; }
    .red { color: #FF5252; }
    .yellow { color: #FFC107; }
    .blue { color: #42A5F5; }
    </style>
""", unsafe_allow_html=True)

# --- Load Tasks ---
tasks = load_tasks()
open_tasks = [t for t in tasks if t["status"] == "Open"]
closed_tasks = [t for t in tasks if t["status"] == "Closed"]

now = datetime.now()
def task_age_days(task): return (now - datetime.fromisoformat(task["created_at"])).days

overdue_tasks = [t for t in open_tasks if task_age_days(t) > 5]
nearing_deadline_tasks = [t for t in open_tasks if 3 <= task_age_days(t) <= 5]

# --- KPIs Layout ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Open Tasks</div>
            <div class="kpi-value blue">{len(open_tasks)}</div>
            <div class="kpi-desc">Tasks currently in progress or not started</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Overdue</div>
            <div class="kpi-value red">{len(overdue_tasks)}</div>
            <div class="kpi-desc">Tasks older than 5 days</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Nearing Deadline</div>
            <div class="kpi-value yellow">{len(nearing_deadline_tasks)}</div>
            <div class="kpi-desc">Tasks 3–5 days old</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Closed Tasks</div>
            <div class="kpi-value green">{len(closed_tasks)}</div>
            <div class="kpi-desc">Total tasks completed</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Priority Section ---
st.subheader("🔥 Priority: Overdue Tasks")
st.caption("These tasks are over 5 days old and require immediate attention.")

if not overdue_tasks:
    st.success("No overdue tasks. Great job! 🎉")
else:
    for task in overdue_tasks:
        st.markdown(f"""
        <div style="padding:10px; border-radius:10px; background:#2a2e38; margin:5px 0;">
            <b>{task['title']}</b> — {task_age_days(task)} days old<br>
            <small>{task['description']}</small><br>
            <span style="color:#aaa;">🕒 Created: {task['created_at']}</span>
        </div>
        """, unsafe_allow_html=True)
