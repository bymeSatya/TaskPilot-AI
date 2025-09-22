# pages/1_Dashboard.py
import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks, add_task

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Dashboard")

tasks = load_tasks()
now = datetime.now()

open_tasks = [t for t in tasks if t.get("status") != "Completed"]
overdue = [t for t in open_tasks if (now - datetime.fromisoformat(t["created_at"])) > timedelta(days=5)]
nearing_deadline = [
    t for t in open_tasks
    if timedelta(days=3) <= (now - datetime.fromisoformat(t["created_at"])) <= timedelta(days=5)
]
closed = [t for t in tasks if t.get("status") == "Completed"]

# ---- KPI cards CSS ----
st.markdown(
    """
    <style>
    .kpi { background:#0f1720; border-radius:12px; padding:18px; text-align:left; color:#e6eef8; }
    .kpi-title { font-size:14px; color:#9fb4d6; margin:0 0 6px 0; }
    .kpi-value { font-size:28px; font-weight:700; margin:0; }
    .kpi-sub { font-size:12px; color:#93a3b6; margin-top:6px; }
    .top-row { display:flex; gap:12px; align-items:center; }
    </style>
    """, unsafe_allow_html=True
)

# Top header + create dropdown on right
colL, colR = st.columns([6,1])
with colL:
    st.header("Dashboard")
with colR:
    # Use an expander (dropdown) for create task
    with st.expander("➕ Create Task", expanded=False):
        title = st.text_input("Title", key="db_title")
        desc = st.text_area("Description", key="db_desc")
        if st.button("Create Task", key="db_create"):
            if not title.strip():
                st.error("Title required")
            else:
                add_task(title.strip(), desc.strip())
                st.success("Task created")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

# KPI row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="kpi"><div class="kpi-title">Open Tasks</div>'
                f'<div class="kpi-value">{len(open_tasks)}</div>'
                '<div class="kpi-sub">Tasks currently in progress or not started</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="kpi"><div class="kpi-title">Overdue</div>'
                f'<div class="kpi-value" style="color:#ff6b6b">{len(overdue)}</div>'
                '<div class="kpi-sub">Tasks older than 5 days</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="kpi"><div class="kpi-title">Nearing Deadline</div>'
                f'<div class="kpi-value" style="color:#ffb86b">{len(nearing_deadline)}</div>'
                '<div class="kpi-sub">Tasks 3–5 days old</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="kpi"><div class="kpi-title">Closed Tasks</div>'
                f'<div class="kpi-value" style="color:#7ee7a6">{len(closed)}</div>'
                '<div class="kpi-sub">Total tasks completed</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("🔥 Priority: Overdue Tasks")
st.caption("These tasks are over 5 days old and require immediate attention.")

if not overdue:
    st.success("No overdue tasks. Great job!")
else:
    for t in overdue:
        days_old = (now - datetime.fromisoformat(t["created_at"])).days
        st.markdown(
            f"<div style='background:#0b1220;padding:12px;border-radius:10px;margin-bottom:8px'>"
            f"<b>{t['id']} — {t['title']}</b> &nbsp; <span style='color:#ff6b6b'>{days_old} days old</span><br>"
            f"<div style='color:#97a6b8'>{t.get('description','')}</div>"
            f"</div>", unsafe_allow_html=True
        )
