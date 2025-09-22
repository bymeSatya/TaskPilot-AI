# pages/1_Dashboard.py
import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks, add_task, save_tasks

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Dashboard")

# --- Load tasks ---
tasks = load_tasks()

# --- KPI calculations ---
now = datetime.now()
open_tasks = [t for t in tasks if t.get("status") != "Closed"]
overdue = [
    t for t in tasks 
    if (now - datetime.fromisoformat(t["created_at"])) > timedelta(days=5) and t["status"] != "Closed"
]
nearing_deadline = [
    t for t in tasks 
    if timedelta(days=3) <= (now - datetime.fromisoformat(t["created_at"])) <= timedelta(days=5)
    and t["status"] != "Closed"
]
closed = [t for t in tasks if t.get("status") == "Closed"]

# --- KPI Display ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown("### Open Tasks")
    st.metric(label="Tasks currently in progress or not started", value=len(open_tasks))
with kpi2:
    st.markdown("### Overdue")
    st.metric(label="Tasks older than 5 days", value=len(overdue))
with kpi3:
    st.markdown("### Nearing Deadline")
    st.metric(label="Tasks 3-5 days old", value=len(nearing_deadline))
with kpi4:
    st.markdown("### Closed Tasks")
    st.metric(label="Total tasks completed", value=len(closed))

# --- Create Task Button (opens modal-like form) ---
if "show_create_task" not in st.session_state:
    st.session_state.show_create_task = False

st.markdown(
    """
    <style>
    .create-btn {
        position: absolute;
        top: 90px;
        right: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button("➕ Create Task", key="open_modal"):
    st.session_state.show_create_task = True

# --- Modal-like Create Task Form ---
if st.session_state.show_create_task:
    with st.container():
        st.markdown(
            """
            <div style="
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background-color: rgba(0,0,0,0.6);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;">
            <div style="background-color: #1e1e1e; padding: 2rem; border-radius: 10px; width: 400px;">
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Create New Task")
        title = st.text_input("Task Title", key="modal_title")
        desc = st.text_area("Description", key="modal_desc")
        cat = st.selectbox("Category", ["Snowflake", "Matillion", "General"], index=0, key="modal_cat")
        pri = st.selectbox("Priority", ["Low", "Medium", "High"], index=1, key="modal_pri")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save Task", key="save_modal"):
                if not title.strip():
                    st.error("Title required")
                else:
                    add_task(title.strip(), desc.strip(), category=cat, priority=pri)
                    st.success("Task created successfully!")
                    st.session_state.show_create_task = False
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_modal"):
                st.session_state.show_create_task = False
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

# --- Priority Section ---
st.markdown("### 🚨 Priority: Overdue Tasks")
if overdue:
    for t in overdue:
        st.warning(f"**{t['id']} - {t['title']}** · Created {t['created_at'][:10]}")
else:
    st.success("No overdue tasks. Great job!")
