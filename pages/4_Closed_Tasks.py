import streamlit as st
from services.task_manager import by_status
from components.task_card import task_card

st.title("Closed Tasks")
for t in by_status("Closed"):
    task_card(t, on_open=lambda tid=t["id"]: st.experimental_set_query_params(task=tid) or st.switch_page("pages/5_Task_Detail.py"))