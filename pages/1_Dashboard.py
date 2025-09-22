import streamlit as st
from datetime import datetime, timezone
from components.sidebar import render as sidebar_render
from services.task_manager import list_tasks, create_task
from services.utils import to_local

st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")

# Left sidebar menu, default stays on Dashboard
active = sidebar_render("Dashboard")

# Top bar + Create Task
c1, c2 = st.columns([6,1])
with c1:
    st.markdown("## Dashboard")
with c2:
    with st.container():
        if st.button("+  Create Task", use_container_width=True):
            with st.dialog("Create Task", width="large"):
                title = st.text_input("Title", placeholder="e.g., Fix email diff between UCV and Siebel")
                desc = st.text_area("Description", placeholder="Short description of the task or hypothesis")
                due_days = st.number_input("Due in (days)", min_value=1, max_value=30, value=5, step=1)
                tags = st.text_input("Tags (comma separated)", placeholder="Snowflake, Matillion")
                if st.button("Save Task", type="primary"):
                    t = create_task(title.strip(), desc.strip(), [x.strip() for x in tags.split(",") if x.strip()], due_days)
                    st.success(f"Task {t['id']} created")
                    st.rerun()

# Data
tasks = list_tasks()
now = datetime.now(timezone.utc)

def age_days(created_at_iso: str) -> int:
    dt = datetime.fromisoformat(created_at_iso.replace("Z","+00:00"))
    return max(0, (now - dt).days)

open_cnt = len([t for t in tasks if t["status"] in ("Open","In Progress")])
closed_cnt = len([t for t in tasks if t["status"] == "Closed"])
overdue_cnt = len([t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] != "Closed"])
nearing_cnt = len([t for t in tasks if 3 <= age_days(t["created_at"]) <= 5 and t["status"] != "Closed"])

# KPI card component
def kpi_card(title: str, value: int, subtitle: str, icon: str | None = None):
    with st.container(border=True):
        top = st.columns([4,1])
        with top[0]:
            st.markdown(f"**{title}**")
        with top[1]:
            if icon:
                st.markdown(f"<div style='text-align:right;font-size:18px'>{icon}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:40px;line-height:1.0;padding:4px 0'>{value}</div>", unsafe_allow_html=True)
        st.caption(subtitle)

# KPI grid (2x2) matching screenshot
g1c1, g1c2 = st.columns(2)
with g1c1:
    kpi_card("Open Tasks", open_cnt, "Tasks currently in progress or not started", "◦")
with g1c2:
    kpi_card("Overdue", overdue_cnt, "Tasks older than 5 days", "⚠️")

g2c1, g2c2 = st.columns(2)
with g2c1:
    kpi_card("Nearing Deadline", nearing_cnt, "Tasks 3–5 days old", "🕒")
with g2c2:
    kpi_card("Closed Tasks", closed_cnt, "Total tasks completed", "✅")

# Priority section
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    overdue = [t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] != "Closed"]
    if not overdue:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)
    else:
        for t in overdue:
            st.markdown(f"- {t['title']} • {t['status']} • Created {to_local(t['created_at'])}")
            if st.button("Open", key=f"o_{t['id']}"):
                st.experimental_set_query_params(task=t["id"])
                st.switch_page("pages/5_Task_Detail.py")