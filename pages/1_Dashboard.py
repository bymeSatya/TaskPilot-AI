import streamlit as st
import datetime as dtm
from services.task_manager import list_tasks, create_task
from services.utils import to_local #parse_dt_safe

st.set_page_config(page_title="TaskPilot AI • Dashboard", layout="wide", initial_sidebar_state="expanded")

# --------- Header + Create Task (stable form) ---------
h1, h2 = st.columns([6,2])
with h1:
    st.markdown("## Dashboard")
with h2:
    with st.expander("Create New Task", expanded=False):
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="e.g. Fix login button")
            desc = st.text_area("Description", placeholder="e.g. The login button on the main page is not working on Safari.")
            submit = st.form_submit_button("Create Task", type="primary")
            if submit:
                if not (title or "").strip():
                    st.warning("Please enter a title.")
                else:
                    t = create_task(title.strip(), (desc or "").strip(), [], 5)
                    st.success(f"Task {t.get('id','')} created")
                    st.experimental_rerun()

# --------- Load tasks safely ---------
try:
    tasks = list_tasks() or []
except Exception:
    tasks = []

def age_days_safe(any_dt) -> int:
    now = dtm.datetime.now(dtm.timezone.utc)
    d = parse_dt_safe(any_dt)
    return max(0, int((now - d).total_seconds() // 86400))

# --------- KPIs ---------
open_cnt = 0
closed_cnt = 0
overdue_cnt = 0
nearing_cnt = 0

for t in tasks:
    status = (t.get("status") or "").strip()
    days = age_days_safe(t.get("created_at"))
    if status in ("Closed", "Completed"):
        closed_cnt += 1
    else:
        open_cnt += 1
        if days > 5:
            overdue_cnt += 1
        elif 3 <= days <= 5:
            nearing_cnt += 1

def kpi_card(title, value, subtitle, icon=None):
    with st.container(border=True):
        c1, c2 = st.columns([4,1])
        with c1: st.markdown(f"**{title}**")
        with c2:
            if icon: st.markdown(f"<div style='text-align:right;font-size:18px'>{icon}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:40px;line-height:1.0;padding:4px 0'>{value}</div>", unsafe_allow_html=True)
        st.caption(subtitle)

c1, c2 = st.columns(2)
with c1: kpi_card("Open Tasks", open_cnt, "Tasks currently in progress or not started", "◦")
with c2: kpi_card("Overdue", overdue_cnt, "Tasks older than 5 days", "⚠️")
c3, c4 = st.columns(2)
with c3: kpi_card("Nearing Deadline", nearing_cnt, "Tasks 3–5 days old", "🕒")
with c4: kpi_card("Closed Tasks", closed_cnt, "Total tasks completed", "✅")

# --------- Priority: Overdue ---------
with st.container(border=True):
    st.markdown("**Priority: Overdue Tasks**")
    st.caption("These tasks are over 5 days old and require immediate attention.")
    any_overdue = False
    for t in tasks:
        status = (t.get("status") or "").strip()
        if status in ("Closed", "Completed"):
            continue
        if age_days_safe(t.get("created_at")) > 5:
            any_overdue = True
            try:
                created_disp = to_local(parse_dt_safe(t.get("created_at")).isoformat())
            except Exception:
                created_disp = "-"
            st.markdown(f"- {t.get('title','Untitled')} • {status or 'Open'} • Created {created_disp}")
            if st.button("Open", key=f"tp_open_{t.get('id', id(t))}"):
                st.experimental_set_query_params(task=t.get("id",""))
                st.switch_page("pages/5_Task_Detail.py")
    if not any_overdue:
        st.markdown("<div style='padding:24px;text-align:center;color:#9aa4b2'>No overdue tasks. Great job!</div>", unsafe_allow_html=True)