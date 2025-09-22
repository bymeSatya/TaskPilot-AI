# pages/2_All_Tasks.py
import streamlit as st
from services.task_manager import load_tasks, add_task, save_tasks, delete_task

st.title("📋 All Tasks")

# Create new task form
with st.expander("➕ Create New Task"):
    title = st.text_input("Task Title", key="new_title")
    desc = st.text_area("Description", key="new_desc")
    cat = st.selectbox("Category", ["Snowflake", "Matillion", "General"], index=0, key="new_cat")
    pri = st.selectbox("Priority", ["Low", "Medium", "High"], index=1, key="new_pri")
    if st.button("Add Task"):
        if not title.strip():
            st.error("Please enter a title.")
        else:
            new = add_task(title.strip(), desc.strip(), category=cat, priority=pri)
            st.success(f"Task {new['id']} created.")
            # set state so Task Detail page can pick it up
            st.session_state['selected_task'] = new['id']
            st.session_state['page'] = 'task_detail'
            # trigger rerun in a way that supports older/newer Streamlit
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

# Show all tasks
tasks = load_tasks()

if not tasks:
    st.info("No tasks yet. Use the form above to create one.")
else:
    for t in tasks:
        cols = st.columns([4,1,1])
        with cols[0]:
            st.markdown(f"**{t['id']} - {t['title']}**")
            st.caption(f"{t.get('category','-')} · {t.get('priority','-')}")
            st.write(t.get('description',''))
        with cols[1]:
            if st.button("Open", key=f"open_{t['id']}"):
                st.session_state['selected_task'] = t['id']
                st.session_state['page'] = 'task_detail'
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        with cols[2]:
            if st.button("Delete", key=f"delete_{t['id']}"):
                deleted = delete_task(t['id'])
                if deleted:
                    st.success("Deleted.")
                else:
                    st.error("Could not delete.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
