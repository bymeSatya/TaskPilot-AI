import streamlit as st
import datetime as dtm
from services.task_manager import get_task, add_activity, set_status, list_tasks
from services.task_manager import create_task  # optional reuse
from services.utils import to_local
from services.ai_assistant import groq_chat

st.set_page_config(page_title="TaskPilot AI • Task", layout="wide", initial_sidebar_state="expanded")

qid = st.experimental_get_query_params().get("task", [None])[0]
if not qid:
    st.error("No task selected."); st.stop()

task = get_task(qid)
if not task:
    st.error("Task not found."); st.stop()

# Top bar: Back + Title + Status pill + Delete
c_top = st.columns([6,1,1])
with c_top[0]:
    if st.button("← Back to all tasks"):
        st.switch_page("pages/2_All_Tasks.py")
    st.markdown(f"### {task['title']}")
    st.caption(f"Task ID: {task['id']}")
with c_top[2]:
    # Delete Task
    if st.button("Delete Task", type="secondary"):
        # simple delete
        tasks = [t for t in list_tasks() if t.get("id") != task["id"]]
        import json, os
        os.makedirs("data", exist_ok=True)
        with open("data/tasks.json","w") as f: json.dump(tasks, f, indent=2)
        st.success("Task deleted")
        st.experimental_set_query_params()
        st.switch_page("pages/2_All_Tasks.py")

left, right = st.columns([2,1])

# ------------- Left: Description + Activity + AI Chat -------------
with left:
    with st.container(border=True):
        st.subheader("Description")
        st.write(task.get("description") or "-")

    with st.container(border=True):
        st.subheader("Activity")
        acts = list(reversed(task.get("activity", [])))
        if not acts:
            st.caption("No updates yet.")
        else:
            for a in acts:
                st.markdown(f"- {to_local(a['at'])} — **{a['who']}**: {a['text']}")

        new_note = st.text_input("Add update", key="add_update")
        if st.button("Add Update", key="btn_add_update"):
            if new_note.strip():
                add_activity(task["id"], "You", new_note.strip())
                st.rerun()
            else:
                st.warning("Please type an update first.")

    with st.container(border=True):
        st.subheader("AI Chat")
        st.caption("Ask questions about this task; AI will use the activity history as context.")
        history = "
".join([f"{a['who']}: {a['text']}" for a in task.get("activity", [])][-10:])
        user_q = st.text_area("Message", placeholder="e.g., What was the last update on this task?")
        if st.button("Send", key="btn_ai_chat"):
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

# ------------- Right: Details + Update Status + AI Guidance -------------
with right:
    with st.container(border=True):
        st.subheader("Details")
        st.caption(f"Created: {to_local(task['created_at'])}")
        st.caption(f"Status: {task['status']}")
        if task.get("completed_at"):
            st.caption(f"Completed: {to_local(task['completed_at'])}")

    with st.container(border=True):
        st.subheader("Update Status")
        new_status = st.selectbox(
            "Select status",
            ["Open","In Progress","Closed"],
            index=["Open","In Progress","Closed"].index(task["status"])
        )
        note = st.text_input("Add a comment (optional)", key="status_note")
        if st.button("Apply", key="btn_apply_status"):
            set_status(task["id"], new_status)
            if note.strip():
                add_activity(task["id"], "You", f"Status set to {new_status}. {note.strip()}")
            else:
                add_activity(task["id"], "You", f"Status set to {new_status}.")
            st.rerun()

    with st.container(border=True):
        st.subheader("AI-Powered Guidance")
        st.caption("Focused suggestions for Snowflake/Matillion/SQL/Python, using this task's context.")
        guide_q = st.text_area("Question", placeholder="e.g., How to backtrack changes in Snowflake for this table?")
        if st.button("Get Suggestion", key="btn_ai_suggest"):
            acts = "
".join([f"- {a['who']}: {a['text']}" for a in task.get("activity", [])][-10:])
            prompt = (
                "Act as a senior data engineer specialized in Snowflake and Matillion. "
                "Based on the task description and recent activity, propose next steps with SQL, Matillion job hints, "
                "and links to relevant official docs.

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