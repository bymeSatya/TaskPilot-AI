import streamlit as st
from services.task_manager import get_task_by_id, update_task
from services.ai_assistant import ask_ai

task_id = st.session_state.get("selected_task")
if not task_id:
    st.error("No task selected. Go back to All Tasks.")
    st.stop()

task = get_task_by_id(task_id)

st.title(task["title"])
st.write(task["description"])
st.write(f"**Status:** {task['status']}")

st.subheader("Activity")
for u in task["updates"]:
    st.markdown(f"- {u['time']}: {u['msg']}")

st.subheader("Update Status")
update_msg = st.text_area("Add update")
if st.button("Save Update"):
    if update_msg:
        update_task(task_id, update_msg, status="Open")
        st.success("Update saved! Refresh page.")
    else:
        st.warning("Please enter something.")

st.subheader("🤖 AI Guidance")
q = st.text_input("Ask AI about this task")
if st.button("Get Suggestion"):
    if q:
        suggestion = ask_ai(q, session_id=task_id)
        st.info(suggestion)
    else:
        st.warning("Enter a question first.")
