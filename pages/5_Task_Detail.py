import streamlit as st
from services.task_manager import (
    get_task,
    add_activity,
    set_status,
    delete_task,
)
from services.utils import to_local
from services.ai_assistant import groq_chat

# Page config
st.set_page_config(
    page_title="TaskPilot AI • Task",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Selected task id comes from session_state (set in All Tasks page)
task_id = st.session_state.get("selected_task_id")
if not task_id:
    st.error("No task selected.")
    st.stop()

task = get_task(task_id)
if not task:
    st.error("Task not found.")
    st.stop()

# ---------------- Top bar ----------------
top_left, _, top_right = st.columns([6, 1, 1])

with top_left:
    if st.button("← Back to all tasks"):
        st.switch_page("pages/2_All_Tasks.py")
    st.markdown(f"### {task['title']}")
    st.caption(f"Task ID: {task['id']}")

with top_right:
    if st.button("Delete Task"):
        delete_task(task["id"])
        st.success("Task deleted")
        st.session_state.pop("selected_task_id", None)
        st.switch_page("pages/2_All_Tasks.py")

left_col, right_col = st.columns([2, 1])

# ---------------- Left column ----------------
with left_col:
    # Description
    with st.container(border=True):
        st.subheader("Description")
        st.write(task.get("description") or "-")

    # Activity
    with st.container(border=True):
        st.subheader("Activity")
        activity = list(reversed(task.get("activity", [])))
        if activity:
            for a in activity:
                st.markdown(f"- {to_local(a['at'])} — **{a['who']}**: {a['text']}")
        else:
            st.caption("No updates yet.")

        new_note = st.text_input("Add update", key="td_add_update")
        if st.button("Add Update", key="td_btn_add"):
            note = (new_note or "").strip()
            if note:
                add_activity(task["id"], "You", note)
                st.rerun()
            else:
                st.warning("Please type an update first.")

    # AI Chat
    with st.container(border=True):
        st.subheader("AI Chat")
        st.caption("Ask questions about this task; AI uses recent activity as context.")
        # Build history safely (no raw triple-quoted literals)
        history_lines = [f"{a['who']}: {a['text']}" for a in task.get("activity", [])]
        history = "
".join(history_lines[-10:])

        user_q = st.text_area("Message", placeholder="e.g., What was the last update on this task?")
        if st.button("Send", key="td_ai_chat"):
            parts = [
                "You are an assistant for data engineering tasks, specialized in Snowflake, Matillion, SQL, and Python.",
                "Answer concisely with steps and relevant SQL/examples.",
                "",
                f"Task Title: {task['title']}",
                f"Task Description: {task.get('description','')}",
                "Recent Activity:",
                history,
                "",
                f"User Question: {user_q}",
            ]
            prompt = "
".join(parts)
            answer = groq_chat([{"role": "user", "content": prompt}])
            st.write(answer)

# ---------------- Right column ----------------
with right_col:
    # Details
    with st.container(border=True):
        st.subheader("Details")
        st.caption(f"Created: {to_local(task['created_at'])}")
        st.caption(f"Status: {task['status']}")
        if task.get("completed_at"):
            st.caption(f"Completed: {to_local(task['completed_at'])}")

    # Update Status
    with st.container(border=True):
        st.subheader("Update Status")
        options = ["Open", "In Progress", "Closed"]
        idx = options.index(task["status"]) if task.get("status") in options else 0
        new_status = st.selectbox("Select status", options, index=idx)
        note = st.text_input("Add a comment (optional)", key="td_status_note")
        if st.button("Apply", key="td_btn_apply"):
            set_status(task["id"], new_status)
            msg = f"Status set to {new_status}."
            note_clean = (note or "").strip()
            if note_clean:
                msg += f" {note_clean}"
            add_activity(task["id"], "You", msg)
            st.rerun()

    # AI-Powered Guidance
    with st.container(border=True):
        st.subheader("AI-Powered Guidance")
        st.caption("Guidance for Snowflake/Matillion/SQL/Python using this task's context.")
        guide_q = st.text_area("Question", placeholder="e.g., How to backtrack changes in Snowflake for this table?")
        if st.button("Get Suggestion", key="td_ai_suggest"):
            acts = [f"- {a['who']}: {a['text']}" for a in task.get("activity", [])]
            recent = "
".join(acts[-10:])
            parts = [
                "Act as a senior data engineer specialized in Snowflake and Matillion.",
                "Given the task details and recent activity, propose next steps with SQL and Matillion job hints.",
                "",
                f"Task: {task['title']}",
                f"Description: {task.get('description','')}",
                "Recent Activity:",
                recent,
                "",
                f"Question: {guide_q}",
            ]
            prompt = "
".join(parts)
            answer = groq_chat([{"role": "user", "content": prompt}])
            st.write(answer)