import streamlit as st
from services.task_manager import get_task, add_activity, set_status
from services.utils import to_local, pct_complete
from services.ai_assistant import groq_chat

query = st.experimental_get_query_params()
task_id = query.get("task",[None])[0]
if not task_id:
    st.error("No task selected."); st.stop()

t = get_task(task_id)
if not t:
    st.error("Task not found."); st.stop()

st.title(t["title"])
st.caption(f"Task ID: {t['id']}")

col1, col2 = st.columns([2,1])

with col1:
    with st.container(border=True):
        st.subheader("Description")
        st.write(t["description"])
    with st.container(border=True):
        st.subheader("Activity")
        for a in reversed(t.get("activity",[])):
            st.markdown(f"- {to_local(a['at'])} — **{a['who']}**: {a['text']}")
        if msg := st.text_input("Add update", key="new_update"):
            if st.button("Add Update"):
                add_activity(t["id"], "You", msg)
                st.rerun()

with col2:
    with st.container(border=True):
        st.subheader("Details")
        st.caption(f"Created At: {to_local(t['created_at'])}")
        st.caption(f"Status: {t['status']}")
        st.progress(pct_complete(t["created_at"], t.get("due_days",5))/100.0, text="Progress")
        new_status = st.selectbox("Update Status", ["Open","In Progress","Closed"], index=["Open","In Progress","Closed"].index(t["status"]))
        if st.button("Apply Status"):
            set_status(t["id"], new_status)
            st.rerun()
    with st.container(border=True):
        st.subheader("AI-Powered Guidance")
        prompt = st.text_area("Ask about Snowflake/Matillion", placeholder="e.g., How to backtrack data changes in Snowflake for table X?")
        if st.button("Get Suggestion") and prompt:
            answer = groq_chat([
                {"role":"user","content": f"Task title: {t['title']}
Description: {t['description']}
Question: {prompt}
Constraints: Prefer official docs, show SQL or Matillion steps."}
            ])
            st.write(answer)