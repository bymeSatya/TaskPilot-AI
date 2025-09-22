import streamlit as st
from datetime import datetime, timezone
from services.task_manager import list_tasks, create_task
from services.utils import to_local

st.title("All Tasks")
st.caption("A comprehensive list of all tasks, including open and closed items.")

# ---------- Create Task modal ----------
def create_task_modal():
    with st.popover("Create Task", use_container_width=False):  # popover looks like the screenshot
        st.markdown("### Create New Task")
        st.caption("Fill in the details below to create a new task.")
        title = st.text_input("Title", placeholder="e.g. Fix login button")
        desc = st.text_area("Description", placeholder="e.g. The login button on the main page is not working on Safari.")
        due_days = 5  # fixed per requirement
        if st.button("Create Task", type="primary"):
            if title.strip():
                t = create_task(title.strip(), desc.strip(), [], due_days)
                st.success(f"Task {t['id']} created")
                st.rerun()
            else:
                st.warning("Please enter a title.")

# Top bar with modal trigger (right side)
_, right = st.columns([6,1])
with right:
    create_task_modal()

tasks = list_tasks()
now = datetime.now(timezone.utc)

import datetime as dtm

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
    # 5-day scale: 0-2 green, 3-4 orange, 5+ red
    seg1 = min(2, max(0, days))
    seg2 = min(2, max(0, days - 2))
    seg3 = min(1, max(0, days - 4))
    # widths as percentages of full 5-day rail
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
    bg, fg = colors.get(status, ("#1f2a44","#e5e7eb"))
    st.markdown(
        f"<span style='background:{bg};color:{fg};padding:4px 10px;border-radius:20px;font-size:12px'>{status}</span>",
        unsafe_allow_html=True
    )

# ---------- Table header ----------
with st.container(border=True):
    cols = st.columns([3,2,3,2,2])
    cols[0].markdown("**All Tasks**")
    cols[1].markdown(" ")  # spacer
    cols = st.columns([3,2,3,2,2])
    cols[0].markdown("**Task**")
    cols[1].markdown("**Status**")
    cols[2].markdown("**Urgency**")
    cols[3].markdown("**Created**")
    cols[4].markdown("**Completed**")

# ---------- Rows ----------
for t in tasks:
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([3,2,3,2,2])
        with c1:
            st.markdown(f"**{t['title']}**")
            st.caption((t.get('description') or "")[:80])
        with c2:
            status_pill(t["status"])
        with c3:
            urgency_bar(t["created_at"], t["status"])
        with c4:
            st.markdown(to_local(t["created_at"]))
        with c5:
            completed_at = None
            if t["status"] in ("Closed","Completed"):
                # When status flipped to Closed, you may persist a completed_at in the JSON. If missing, show today.
                completed_at = t.get("completed_at")
                if not completed_at:
                    completed_at = now.isoformat()
            st.markdown(to_local(completed_at) if completed_at else "-")
        # Clickable row button to open details
        open_col = st.columns([0.8,0.2])[1]
        with open_col:
            if st.button("Open", key=f"open_{t['id']}"):
                st.experimental_set_query_params(task=t["id"])
                st.switch_page("pages/5_Task_Detail.py")