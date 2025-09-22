import streamlit as st
from services.utils import pct_complete, to_local

def task_card(t, on_open=None):
    col1, col2, col3 = st.columns([4,2,2])
    with col1:
        st.markdown(f"**{t['title']}**")
        st.caption(t["description"][:120])
        st.progress(pct_complete(t["created_at"], t.get("due_days",5))/100.0, text="Progress")
    with col2:
        st.metric("Status", t["status"])
        st.caption(f"Created {to_local(t['created_at'])}")
    with col3:
        if st.button("Open", key=f"open_{t['id']}") and on_open:
            on_open(t["id"])