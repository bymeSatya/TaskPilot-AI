import streamlit as st
from datetime import datetime, timedelta
from services.task_manager import load_tasks, save_task

def render_progress_bar(created_date, status):
    # Progress stages
    total_days = 5
    days_passed = (datetime.now() - created_date).days

    if days_passed < 2:
        progress = 0.33
        color = "green"
    elif days_passed < 4:
        progress = 0.66
        color = "orange"
    else:
        progress = 1.0
        color = "red"

    if status == "Completed":
        progress = 1.0
        color = "gray"

    st.progress(progress, text=f"{days_passed} days old")
    st.markdown(f"<div style='color:{color}; font-size:12px;'>Urgency</div>", unsafe_allow_html=True)

def show_all_tasks():
    st.title("All Tasks")
    st.write("A comprehensive list of all tasks, including open and closed items.")

    tasks = load_tasks()

    if not tasks:
        st.info("No tasks found. Create one to get started!")
        return

    for idx, task in enumerate(tasks):
        with st.container():
            st.markdown(
                """
                <div style="
                    border: 1px solid #444;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                    background-color: #111;">
                """,
                unsafe_allow_html=True,
            )

            cols = st.columns([2, 1, 2, 1, 1])
            with cols[0]:
                if st.button(task["title"], key=f"task_{idx}", help="Click to open details"):
                    st.session_state["open_task"] = idx
            with cols[1]:
                st.markdown(f"**{task['status']}**")
            with cols[2]:
                render_progress_bar(task["created"], task["status"])
            with cols[3]:
                st.markdown(task["created"].strftime("%b %d, %Y"))
            with cols[4]:
                if task["status"] == "Completed" and task.get("completed_date"):
                    st.markdown(task["completed_date"].strftime("%b %d, %Y"))
                else:
                    st.markdown("-")

            st.markdown("</div>", unsafe_allow_html=True)

    # Task details page
    if "open_task" in st.session_state:
        task = tasks[st.session_state["open_task"]]
        st.subheader(f"Task Details: {task['title']}")
        st.write(task["description"])

        if st.button("✅ Mark as Completed", key="mark_done"):
            task["status"] = "Completed"
            task["completed_date"] = datetime.now()
            save_task(tasks)
            st.success("Task marked as completed.")
            del st.session_state["open_task"]
            st.rerun()

        if st.button("🗑 Delete Task", key="delete_task"):
            tasks.pop(st.session_state["open_task"])
            save_task(tasks)
            st.warning("Task deleted.")
            del st.session_state["open_task"]
            st.rerun()

