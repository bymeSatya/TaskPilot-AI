import streamlit as st
from datetime import datetime, timezone
from services.task_manager import list_tasks, create_task
from services.utils import to_local

# ---------- Robust parsing ----------
def parse_iso(dt_str):
    if isinstance(dt_str, datetime):
        return dt_str if dt_str.tzinfo else dt_str.replace(tzinfo=timezone.utc)
    if not dt_str or not isinstance(dt_str, str):
        return datetime.now(timezone.utc)
    s = dt_str.strip()
    try:
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue
        return datetime.now(timezone.utc)

def ensure_state():
    for k, v in {
        "tp_show_create": False,
        "tp_new_title": "",
        "tp_new_desc": ""
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

def age_days(created_at_any) -> int:
    now = datetime.now(timezone.utc)
    dt = parse_iso(created_at_any)
    return max(0, int((now - dt).total_seconds() // 86400))

def kpi_card(title: str, value: int, subtitle: str, icon: str | None = None):
    with st.container(border=True):
        head = st.columns([4,1])
        with head[0]:
            st.markdown(f"**{title}**")
        with head[1]:
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
    st.markdown(
        """
        <div style="position:fixed; inset:0; background:rgba(0,0,0,0.55);
                    display:flex; align-items:center; justify-content:center; z-index:9999;">
          <div style="width:520px; background:#0f172a; color:#e6edf3;
                      border:1px solid rgba(255,255,255,0.06); border-radius:12px;
                      box-shadow:0 10px 30px rgba(0,0,0,0.35); padding:18px 20px;">
            <h3 style="margin:4px 0 6px 0;">Create New Task</h3>
            <div style="opacity:0.8; margin-bottom:16px;">Fill in the details below to create a new task.</div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.tp_new_title = st.text_input("Title", value=st.session_state.tp_new_title, key="tp_title", placeholder="e.g. Fix login button")
    st.session_state.tp_new_desc = st.text_area("Description", value=st.session_state.tp_new_desc, key="tp_desc", placeholder="e.g. The login button on the main page is not working on Safari.")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Cancel", key="tp_cancel", use_container_width=True, on_click=cancel_create)
    with c2:
        st.button("Create Task", key="tp_confirm", type="primary", use_container_width=True, on_click=confirm_create)
    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------- Page ----------
st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")
ensure_state()

header_left, header_right = st.columns([6,1])
with header_left:
    st.markdown("## Dashboard")
with header_right:
    st.button("+  Create Task", key="tp_open", use_container_width=True, on_click=open_create_modal)

if st.session_state.tp_show_create:
    render_create_modal()

# ---------- Data + KPIs (robust against bad data) ----------
tasks = list_tasks() or []

open_cnt = 0
closed_cnt = 0
overdue_cnt = 0
nearing_cnt = 0

for t in tasks:
    status = (t.get("status") or "").strip()
    created_raw = t.get("created_at")
    days = age_days(created_raw)
    if status in ("Closed", "Completed"):
        closed_cnt += 1
    elif status in ("Open", "In Progress"):
        open_cnt += 1
    else:
        open_cnt += 1  # treat unknown as open

    if status not in ("Closed", "Completed"):
        if days > 5:
            overdue_cnt += 1
        elif 3 <= days <= 5:
            nearing_cnt += 1

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

# ---------- Priority: Overdue ----------
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    any_overdue = False
    for t in tasks:
        status = (t.get("status") or "").strip()
        if status in ("Closed","Completed"):
            continue
        if age_days(t.get("created_at")) > 5:
            any_overdue = True
            created_raw = t.get("created_at")
            # to_local may expect ISO; guard with try
            try:
                created_disp = to_local(parse_iso(created_raw).isoformat())
            except Exception:
                created_disp = "-"
            st.markdown(f"- {t.get('title','Untitled')} • {status or 'Open'} • Created {created_disp}")
            if st.button("Open", key=f"tp_open_{t.get('id', id(t))}"):
                st.experimental_set_query_params(task=t.get("id",""))
                st.switch_page("pages/5_Task_Detail.py")
    if not any_overdue:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)