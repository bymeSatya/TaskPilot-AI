import streamlit as st
import datetime as dtm  # alias module to avoid name collisions
from services.task_manager import list_tasks, create_task
from services.utils import to_local

# ---------- helpers ----------
def ensure_state():
    defaults = {
        "tp_show_create": False,
        "tp_new_title": "",
        "tp_new_desc": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def parse_any_datetime(val):
    """Return timezone-aware UTC dt for wide variety inputs; never crash."""
    try:
        # already a datetime
        if isinstance(val, dtm.datetime):
            return val if val.tzinfo else val.replace(tzinfo=dtm.timezone.utc)
        # null or non-string
        if not val or not isinstance(val, str):
            return dtm.datetime.now(dtm.timezone.utc)
        s = val.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return dtm.datetime.fromisoformat(s)
        except Exception:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    d = dtm.datetime.strptime(val, fmt)
                    return d.replace(tzinfo=dtm.timezone.utc)
                except Exception:
                    pass
            return dtm.datetime.now(dtm.timezone.utc)
    except Exception:
        return dtm.datetime.now(dtm.timezone.utc)

def age_days(created_any) -> int:
    now = dtm.datetime.now(dtm.timezone.utc)
    d = parse_any_datetime(created_any)
    return max(0, int((now - d).total_seconds() // 86400))

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
    try:
        t = create_task(title, desc, [], 5)
        st.success(f"Task {t.get('id','')} created")
    except Exception as e:
        st.error(f"Could not create task: {e}")
    finally:
        cancel_create()
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

# ---------- page ----------
st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")
ensure_state()

left, right = st.columns([6,1])
with left:
    st.markdown("## Dashboard")
with right:
    st.button("+  Create Task", key="tp_open_btn", use_container_width=True, on_click=open_create_modal)

if st.session_state.tp_show_create:
    render_create_modal()

# ---------- load data + KPIs (defensive) ----------
try:
    tasks = list_tasks() or []
except Exception:
    tasks = []

open_cnt = 0
closed_cnt = 0
overdue_cnt = 0
nearing_cnt = 0

for t in tasks:
    status = (t.get("status") or "").strip()
    days = age_days(t.get("created_at"))
    if status in ("Closed", "Completed"):
        closed_cnt += 1
    else:
        open_cnt += 1
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

# ---------- priority: overdue ----------
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    listed = False
    for t in tasks:
        status = (t.get("status") or "").strip()
        if status in ("Closed", "Completed"):
            continue
        if age_days(t.get("created_at")) > 5:
            listed = True
            try:
                created_disp = to_local(parse_any_datetime(t.get("created_at")).isoformat())
            except Exception:
                created_disp = "-"
            st.markdown(f"- {t.get('title','Untitled')} • {status or 'Open'} • Created {created_disp}")
            if st.button("Open", key=f"tp_open_{t.get('id', id(t))}"):
                st.experimental_set_query_params(task=t.get("id",""))
                st.switch_page("pages/5_Task_Detail.py")
    if not listed:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)