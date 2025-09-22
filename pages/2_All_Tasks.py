import streamlit as st
from services.task_manager import list_tasks
from components.task_card import task_card

st.title("All Tasks")
for t in list_tasks():
    task_card(t, on_open=lambda tid=t["id"]: st.experimental_set_query_params(task=tid) or st.switch_page("pages/5_Task_Detail.py"))