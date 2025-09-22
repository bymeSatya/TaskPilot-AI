import streamlit as st
import datetime as dtm
from services.task_manager import list_tasks, create_task
from services.utils import to_local

st.set_page_config(page_title="TaskPilot AI • All Tasks", layout="wide", initial_sidebar_state="expanded")

# ---------- Header with Create Task ----------
h1, h2 = st.columns([6,2])
with h1:
    st.markdown("## All Tasks")
    st.caption("A comprehensive list of all tasks, including open and closed items.")
with h2:
    with st.expander("Create New Task", expanded=False):
        with st.form("all_tasks_create_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="e.g. Fix login button")
            desc = st.text_area("Description", placeholder="e.g. The login button on the main page is not working on Safari.")
            btn = st.form_submit_button("Create Task", type="primary")
            if btn:
                if not (title or "").strip():
                    st.warning("Please enter a title.")
                else:
                    t = create_task(title.strip(), (desc or "").strip(), [], 5)
                    st.success(f"Task {t.get('id','')} created")
                    st.rerun()

# ---------- Helpers ----------
def age_days(created_at_iso: str) -> int:
    try:
        if not created_at_iso:
            return 0
        s = str(created_at_iso).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            d = dtm.datetime.fromisoformat(s)
        except Exception:
            d = dtm.datetime.strptime(str(created_at_iso), "%Y-%m-%d").replace(tzinfo=dtm.timezone.utc)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dtm.timezone.utc)
        return max(0, (dtm.datetime.now(dtm.timezone.utc) - d).days)
    except Exception:
        return 0

def urgency_bar(created_at_iso: str, status: str):
    days = age_days(created_at_iso)
    seg1 = min(2, max(0, days))          # 0-2 days green
    seg2 = min(2, max(0, days - 2))      # 3-4 days orange
    seg3 = min(1, max(0, days - 4))      # 5+ days red (cap 1 day)
    w1 = (seg1 / 5) * 100.0
    w2 = (seg2 / 5) * 100.0
    w3 = (seg3 / 5) * 100.0
    l2 = w1
    l3 = w1 + w2
    html = f"""
    <div style="height:10px;background:#2b3344;border-radius:8px;overflow:hidden;position:relative;">
      <div style="height:100%;width:{w1:.2f}%;background:#22c55e;position:absolute;left:0;"></div>
      <div style="height:100%;width:{w2:.2f}%;background:#f59e0b;position:absolute;left:{l2:.2f}%;"></div>
      <div style="height:100%;width:{w3:.2f}%;background:#ef4444;position:absolute;left:{l3:.2f}%;"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.caption(f"{days} days old")

def status_pill(status: str):
    colors = {
        "Open": ("#1f2a44","#60a5fa"),
        "In Progress": ("#172a3a","#93c5fd"),
        "Closed": ("#14291a","#34d399"),
        "Completed": ("#14291a","#34d399"),
    }
    bg, fg = colors.get((status or "").strip(), ("#1f2a44","#e5e7eb"))
    st.markdown(
        f"<span style='background:{bg};color:{fg};padding:4px 10px;border-radius:20px;font-size:12px'>{status or '-'}</span>",
        unsafe_allow_html=True
    )

# ---------- Load ----------
try:
    tasks = list_tasks() or []
except Exception:
    tasks = []

# ---------- Header row ----------
with st.container(border=True):
    c = st.columns([3,2,3,2,2])
    c[0].markdown("**Task**")
    c[1].markdown("**Status**")
    c[2].markdown("**Urgency**")
    c[3].markdown("**Created**")
    c[4].markdown("**Completed**")

# ---------- Rows ----------
for t in tasks:
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([3,2,3,2,2])
        title = t.get("title","Untitled")
        desc = (t.get("description") or "")[:80]
        created = t.get("created_at")
        completed = t.get("completed_at")
        status = t.get("status","Open")
        tid = t.get("id","")

        with c1:
            # Clickable title -> store in session_state and navigate (no query API conflicts)
            if st.button(title, key=f"title_{tid}", help="Open task"):
                st.session_state["selected_task_id"] = tid
                st.switch_page("pages/5_Task_Detail.py")
            if desc:
                st.caption(desc)

        with c2:
            status_pill(status)

        with c3:
            urgency_bar(created, status)

        with c4:
            try:
                st.markdown(to_local(created))
            except Exception:
                st.markdown("-")

        with c5:
            try:
                st.markdown(to_local(completed) if completed else "-")
            except Exception:
                st.markdown("-")