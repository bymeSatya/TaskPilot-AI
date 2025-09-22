# pages/1_Dashboard.py
import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks, add_task
from components.modal import show_create_task_modal

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Dashboard")

tasks = load_tasks()
now = datetime.now()

open_tasks = [t for t in tasks if t.get("status") != "Closed"]
overdue = [t for t in open_tasks if (now - datetime.fromisoformat(t["created_at"])) > timedelta(days=5)]
nearing_deadline = [
    t for t in open_tasks
    if timedelta(days=3) <= (now - datetime.fromisoformat(t["created_at"])) <= timedelta(days=5)
]
closed = [t for t in tasks if t.get("status") == "Closed"]

# --- KPI cards styled ---
def kpi_card(title, value, subtitle, color="white"):
    st.markdown(
        f"""
        <div style="background-color:#1e1e1e; border-radius:12px; padding:1rem; 
                    text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.25);">
            <h3 style="margin:0; color:{color};">{value}</h3>
            <p style="margin:0; font-weight:bold;">{title}</p>
            <small style="color:gray;">{subtitle}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Open Tasks", len(open_tasks), "In progress or not started")
with c2: kpi_card("Overdue", len(overdue), "Older than 5 days", color="red")
with c3: kpi_card("Nearing Deadline", len(nearing_deadline), "3–5 days old", color="orange")
with c4: kpi_card("Closed Tasks", len(closed), "Completed", color="lightgreen")

# --- Create Task Button ---
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

if st.button("➕ Create Task"):
    st.session_state.show_modal = True

if st.session_state.show_modal:
    title, desc, submit, cancel = show_create_task_modal()
    if submit:
        if not title.strip():
            st.error("Title is required")
        else:
            add_task(title.strip(), desc.strip())
            st.success("Task created successfully!")
            st.session_state.show_modal = False
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
    if cancel:
        st.session_state.show_modal = False
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

# --- Priority Section ---
st.markdown("### 🚨 Priority: Overdue Tasks")
if overdue:
    for t in overdue:
        st.warning(f"**{t['id']} - {t['title']}** · Created {t['created_at'][:10]}")
else:
    st.success("No overdue tasks. Great job!")
