import streamlit as st
from datetime import datetime, timezone
from services.task_manager import list_tasks, create_task
from services.utils import to_local

st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------------- Modal helpers (version-safe) ----------------
if "show_create_modal" not in st.session_state:
    st.session_state.show_create_modal = False
if "new_title" not in st.session_state:
    st.session_state.new_title = ""
if "new_desc" not in st.session_state:
    st.session_state.new_desc = ""

def open_modal():
    st.session_state.show_create_modal = True

def close_modal():
    st.session_state.show_create_modal = False
    st.session_state.new_title = ""
    st.session_state.new_desc = ""

def render_modal():
    with st.container():
        st.markdown(
            """
            <div style="
                position:fixed; inset:0; background:rgba(0,0,0,0.55);
                display:flex; align-items:center; justify-content:center;
                z-index: 9999;">
              <div style="
                width:520px; background:#0f172a; color:#e6edf3;
                border:1px solid rgba(255,255,255,0.06); border-radius:12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35); padding:18px 20px;">
                <h3 style="margin:4px 0 6px 0;">Create New Task</h3>
                <div style="opacity:0.8; margin-bottom:16px;">
                  Fill in the details below to create a new task.
                </div>
            """,
            unsafe_allow_html=True,
        )
        # Use unique keys; no experimental APIs
        st.session_state.new_title = st.text_input(
            "Title", value=st.session_state.new_title, key="create_title_input",
            placeholder="e.g. Fix login button"
        )
        st.session_state.new_desc = st.text_area(
            "Description", value=st.session_state.new_desc, key="create_desc_area",
            placeholder="e.g. The login button on the main page is not working on Safari."
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Cancel", key="create_cancel_btn", use_container_width=True):
                close_modal()
                st.rerun()
        with col_b:
            if st.button("Create Task", key="create_confirm_btn", type="primary", use_container_width=True):
                title = st.session_state.new_title.strip()
                desc = st.session_state.new_desc.strip()
                if not title:
                    st.warning("Please enter a title.")
                else:
                    t = create_task(title, desc, [], 5)
                    close_modal()
                    st.success(f"Task {t['id']} created")
                    st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------- Header ----------------
left, right = st.columns([6,1])
with left:
    st.markdown("## Dashboard")
with right:
    st.button("+  Create Task", key="open_create_modal_btn", use_container_width=True, on_click=open_modal)

# Render modal after header so it overlays content
if st.session_state.show_create_modal:
    render_modal()

# ---------------- Data ----------------
tasks = list_tasks()
now = datetime.now(timezone.utc)

def age_days(created_at_iso: str) -> int:
    dt = datetime.fromisoformat(created_at_iso.replace("Z","+00:00"))
    return max(0, (now - dt).days)

open_cnt = len([t for t in tasks if t["status"] in ("Open", "In Progress")])
closed_cnt = len([t for t in tasks if t["status"] in ("Closed", "Completed")])
overdue_cnt = len([t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] not in ("Closed","Completed")])
nearing_cnt = len([t for t in tasks if 3 <= age_days(t["created_at"]) <= 5 and t["status"] not in ("Closed","Completed")])

# ---------------- KPI cards ----------------
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

c1, c2 = st.columns(2)
with c1:
    kpi_card("Open Tasks", open_cnt, "Tasks currently in progress or not started", "◦")
with c2:
    kpi_card("Overdue", overdue_cnt, "Tasks older than 5 days", "⚠️")

c3, c4 = st.columns(2)
with c3:
    kpi_card("Nearing Deadline", nearing_cnt, "Tasks 3–5 days old", "🕒")
with c4:
    kpi_card("Closed Tasks", closed_cnt, "Total tasks completed", "✅")

# ---------------- Priority overdue ----------------
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