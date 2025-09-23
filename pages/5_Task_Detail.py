import streamlit as st
from services.task_manager import get_task, add_activity, set_status, delete_task
from services.utils import to_local
from services.ai_assistant import groq_chat

st.set_page_config(page_title="TaskPilot AI • Task", layout="wide", initial_sidebar_state="expanded")

# Get selected task id from session
task_id = st.session_state.get("selected_task_id")
if not task_id:
    st.error("No task selected."); st.stop()

task = get_task(task_id)
if not task:
    st.error("Task not found."); st.stop()

# Top bar
top_l, _, top_r = st.columns([6,1,1])
with top_l:
    if st.button("← Back to all tasks"):
        st.switch_page("pages/2_All_Tasks.py")
    st.markdown(f"### {task['title']}")
    st.caption(f"Task ID: {task['id']}")
with top_r:
    if st.button("Delete Task"):
        delete_task(task["id"])
        st.success("Task deleted")
        st.session_state.pop("selected_task_id", None)
        st.switch_page("pages/2_All_Tasks.py")

left, right = st.columns([2,1])

# Left: Description, Activity, AI Chat
with left:
    # Description
    with st.container(border=True):
        st.subheader("Description")
        st.write(task.get("description") or "-")

    # Activity
    with st.container(border=True):
        st.subheader("Activity")
        acts = list(reversed(task.get("activity", [])))
        if not acts:
            st.caption("No updates yet.")
        else:
            for a in acts:
                st.markdown(f"- {to_local(a['at'])} — **{a['who']}**: {a['text']}")
        new_note = st.text_input("Add update", key="td_add_update")
        if st.button("Add Update", key="td_btn_add"):
            if new_note.strip():
                add_activity(task["id"], "You", new_note.strip())
                st.rerun()
            else:
                st.warning("Please type an update first.")

    # AI Chat
    with st.container(border=True):
        st.subheader("AI Chat")
        st.caption("Ask questions about this task; AI will use the activity history as context.")
        # Build a single-line history string safely
        activity_lines = [f"{a['who']}: {a['text']}" for a in task.get("activity", [])]
        history = "
".join(activity_lines[-10:])
        user_q = st.text_area("Message", placeholder="e.g., What was the last update on this task?")
        if st.button("Send", key="td_ai_chat"):
            prompt = (
                "You are an assistant for data engineering tasks, specialized in Snowflake, Matillion, SQL, and Python. "
                "Answer concisely with steps and relevant SQL/examples.

"
                f"Task Title: {task['title']}
"
                f"Task Description: {task.get('description','')}
"
                f"Recent Activity:
{history}

"
                f"User Question: {user_q}"
            )
            ans = groq_chat([{"role":"user","content": prompt}])
            st.write(ans)

# Right: Details, Update Status, AI Guidance
with right:
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
        new_status = st.selectbox(
            "Select status",
            ["Open","In Progress","Closed"],
            index=["Open","In Progress","Closed"].index(task["status"])
        )
        note = st.text_input("Add a comment (optional)", key="td_status_note")
        if st.button("Apply", key="td_btn_apply"):
            set_status(task["id"], new_status)
            msg = f"Status set to {new_status}."
            if note.strip():
                msg += f" {note.strip()}"
            add_activity(task["id"], "You", msg)
            st.rerun()

    # AI-Powered Guidance
    with st.container(border=True):
        st.subheader("AI-Powered Guidance")
        st.caption("Focused suggestions for Snowflake/Matillion/SQL/Python, using this task's context.")
        guide_q = st.text_area("Question", placeholder="e.g., How to backtrack changes in Snowflake for this table?")
        if st.button("Get Suggestion", key="td_ai_suggest"):
            acts = "
".join([f"- {a['who']}: {a['text']}" for a in task.get("activity", [])][-10:])
            prompt = (
                "Act as a senior data engineer specialized in Snowflake and Matillion. "
                "Based on the task description and recent activity, propose next steps with SQL and Matillion job hints, "
                "and point to relevant official docs.

"
                f"Task: {task['title']}
Description: {task.get('description','')}
"
                f"Recent Activity:
{acts}

"
                f"Question: {guide_q}"
            )
            ans = groq_chat([{"role":"user","content": prompt}])
            st.write(ans)