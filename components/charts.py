import streamlit as st
import pandas as pd
from services.task_manager import list_tasks
from services.utils import pct_complete

def dashboard_kpis():
    tasks = list_tasks()
    total = len(tasks)
    open_ = len([t for t in tasks if t["status"].lower().startswith("open")])
    progress = round(pd.Series([pct_complete(t["created_at"], t.get("due_days",5)) for t in tasks]).mean() if tasks else 0, 1)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total)
    col2.metric("Open", open_)
    col3.metric("Closed", total - open_)
    col4.metric("Avg Progress %", progress)

def timeline_chart():
    tasks = list_tasks()
    df = pd.DataFrame([{
        "Task": t["title"],
        "Progress": pct_complete(t["created_at"], t.get("due_days",5))
    } for t in tasks])
    if df.empty:
        st.info("No tasks yet.")
        return
    st.bar_chart(df.set_index("Task"))