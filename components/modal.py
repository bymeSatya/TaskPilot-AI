# components/modal.py
import streamlit as st

def show_create_task_modal():
    """Display a centered modal to create a new task. Returns (title, desc, submitted, cancelled)."""
    st.markdown(
        """
        <style>
        .modal-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal-box {
            background: #1e1e1e;
            padding: 2rem;
            border-radius: 12px;
            width: 420px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="modal-overlay"><div class="modal-box">', unsafe_allow_html=True)

        st.subheader("Create New Task")
        st.caption("Fill in the details below to create a new task.")

        title = st.text_input("Title", placeholder="e.g. Fix login button", key="modal_title")
        desc = st.text_area("Description", placeholder="e.g. The login button is not working on Safari.", key="modal_desc")

        col1, col2 = st.columns(2)
        cancel = col1.button("Cancel", key="cancel_modal")
        submit = col2.button("Create Task", key="submit_modal")

        st.markdown('</div></div>', unsafe_allow_html=True)

    return title, desc, submit, cancel
