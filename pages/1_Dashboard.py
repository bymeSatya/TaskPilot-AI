import streamlit as st
from datetime import datetime, timezone
from services.task_manager import list_tasks, create_task
from services.utils import to_local

# ---- Page config (keeps the same dark/light theme from .streamlit/config.toml) ----
st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---- Header row: title on left, Create button on right ----
left, right = st.columns([6,1])
with left:
    st.markdown("## Dashboard")
with right:
    # Cute popup box to create a task (uses popover for clean UX)
    with st.popover("Create Task", use_container_width=False):
        st.markdown("### Create New Task")
        st.caption("Fill in the details below to create a new task.")
        title = st.text_input("Title", placeholder="e.g. Fix login button")
        desc = st.text_area("Description", placeholder="e.g. The login button on the main page is not working on Safari.")
        # Per requirements: every task defaults to a 5-day window
        due_days = 5
        cols = st.columns([1,1])
        with cols[0]:
            if st.button("Cancel", use_container_width=True):
                st.experimental_rerun()
        with cols[1]:
            if st.button("Create Task", type="primary", use_container_width=True):
                if title.strip():
                    t = create_task(title.strip(), desc.strip(), [], due_days)
                    st.success(f"Task {t['id']} created")
                    st.rerun()
                else:
                    st.warning("Please enter a title before creating.")

# ---- Load tasks and compute metrics ----
tasks = list_tasks()
now = datetime.now(timezone.utc)

def age_days(created_at_iso: str) -> int:
    dt = datetime.fromisoformat(created_at_iso.replace("Z","+00:00"))
    return max(0, (now - dt).days)

open_cnt = len([t for t in tasks if t["status"] in ("Open", "In Progress")])
closed_cnt = len([t for t in tasks if t["status"] in ("Closed", "Completed")])
overdue_cnt = len([t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] not in ("Closed","Completed")])
nearing_cnt = len([t for t in tasks if 3 <= age_days(t["created_at"]) <= 5 and t["status"] not in ("Closed","Completed")])

# ---- Small KPI card component (matches screenshot look) ----
def kpi_card(title: str, value: int, subtitle: str, icon: str | None = None):
    with st.container(border=True):
        top = st.columns([4,1])
        with top[0]:
            st.markdown(f"**{title}**")
        with top[1]:
            if icon:
                st.markdown(f"<div style='text-align:right;font-size:18px'>{icon}</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:40px;line-height:1.0;padding:4px 0'>%s</div>" % value, unsafe_allow_html=True)
        st.caption(subtitle)

# ---- KPI grid (2x2) ----
row1c1, row1c2 = st.columns(2)
with row1c1:
    kpi_card("Open Tasks", open_cnt, "Tasks currently in progress or not started", "◦")
with row1c2:
    kpi_card("Overdue", overdue_cnt, "Tasks older than 5 days", "⚠️")

row2c1, row2c2 = st.columns(2)
with row2c1:
    kpi_card("Nearing Deadline", nearing_cnt, "Tasks 3–5 days old", "🕒")
with row2c2:
    kpi_card("Closed Tasks", closed_cnt, "Total tasks completed", "✅")

# ---- Priority: Overdue section ----
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    overdue = [t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] not in ("Closed","Completed")]
    if not overdue:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)
    else:
        for t in overdue:
            st.markdown(f"- {t['title']} • {t['status']} • Created {to_local(t['created_at'])}")
            if st.button("Open", key=f"open_{t['id']}"):
                st.experimental_set_query_params(task=t["id"])
                st.switch_page("pages/5_Task_Detail.py")