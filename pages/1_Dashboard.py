import streamlit as st
from components.charts import dashboard_kpis, timeline_chart
from services.task_manager import list_tasks
from components.task_card import task_card

st.title("Dashboard")

dashboard_kpis()
st.divider()
st.subheader("Recent Tasks")

tasks = list_tasks()[:5]
for t in tasks:
    task_card(t, on_open=lambda tid: st.switch_page("pages/5_Task_Detail.py")+"")