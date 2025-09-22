# pages/2_All_Tasks.py
import streamlit as st
from services.task_manager import load_tasks, add_task, delete_task
from components.modal import show_create_task_modal

st.title("📋 All Tasks")

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

# --- Task list ---
tasks = load_tasks()
if not tasks:
    st.info("No tasks yet.")
else:
    for t in tasks:
        cols = st.columns([4,1])
        with cols[0]:
            st.markdown(f"**{t['id']} - {t['title']}**")
            st.caption(t.get("description",""))
        with cols[1]:
            if st.button("🗑️ Delete", key=f"del_{t['id']}"):
                delete_task(t['id'])
                st.success("Deleted.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
