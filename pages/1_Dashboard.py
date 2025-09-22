import streamlit as st
from datetime import datetime, timezone
from services.task_manager import list_tasks, create_task
from services.utils import to_local

# ---------- Helpers (define BEFORE any widget calls) ----------
def ensure_state():
    defaults = {
        "tp_show_create": False,
        "tp_new_title": "",
        "tp_new_desc": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def age_days(created_at_iso: str) -> int:
    now = datetime.now(timezone.utc)
    dt = datetime.fromisoformat(created_at_iso.replace("Z","+00:00"))
    return max(0, (now - dt).days)

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

def open_create_modal():
    st.session_state.tp_show_create = True

def cancel_create():
    st.session_state.tp_show_create = False
    st.session_state.tp_new_title = ""
    st.session_state.tp_new_desc = ""

def confirm_create():
    title = (st.session_state.tp_new_title or "").strip()
    desc = (st.session_state.tp_new_desc or "").strip()
    if not title:
        st.warning("Please enter a title.")
        return
    t = create_task(title, desc, [], 5)
    cancel_create()
    st.success(f"Task {t['id']} created")
    st.rerun()

def render_create_modal():
    # Fullscreen overlay + centered card (pure HTML/CSS + normal widgets)
    st.markdown(
        """
        <div id="tp_overlay" style="
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
    st.session_state.tp_new_title = st.text_input(
        "Title", value=st.session_state.tp_new_title, key="tp_title",
        placeholder="e.g. Fix login button"
    )
    st.session_state.tp_new_desc = st.text_area(
        "Description", value=st.session_state.tp_new_desc, key="tp_desc",
        placeholder="e.g. The login button on the main page is not working on Safari."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.button("Cancel", key="tp_cancel", use_container_width=True, on_click=cancel_create)
    with c2:
        st.button("Create Task", key="tp_confirm", type="primary", use_container_width=True, on_click=confirm_create)
    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------- Page setup ----------
st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")
ensure_state()

# ---------- Header with create button ----------
left, right = st.columns([6,1])
with left:
    st.markdown("## Dashboard")
with right:
    st.button("+  Create Task", key="tp_open", use_container_width=True, on_click=open_create_modal)

# Render modal after header so it overlays properly
if st.session_state.tp_show_create:
    render_create_modal()

# ---------- Data + KPIs ----------
tasks = list_tasks()
open_cnt = len([t for t in tasks if t["status"] in ("Open", "In Progress")])
closed_cnt = len([t for t in tasks if t["status"] in ("Closed", "Completed")])
overdue_cnt = len([t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] not in ("Closed","Completed")])
nearing_cnt = len([t for t in tasks if 3 <= age_days(t["created_at"]) <= 5 and t["status"] not in ("Closed","Completed")])

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

# ---------- Priority section ----------
from services.utils import to_local  # late import OK but explicit
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    overdue = [t for t in tasks if age_days(t["created_at"]) > 5 and t["status"] not in ("Closed","Completed")]
    if not overdue:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)
    else:
        for t in overdue:
            st.markdown(f"- {t['title']} • {t['status']} • Created {to_local(t['created_at'])}")
            if st.button("Open", key=f"tp_open_{t['id']}"):
                st.experimental_set_query_params(task=t["id"])
                st.switch_page("pages/5_Task_Detail.py")