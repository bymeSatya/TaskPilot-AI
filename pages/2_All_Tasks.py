# pages/2_All_Tasks.py
import streamlit as st
from datetime import datetime
from services.task_manager import load_tasks, add_task, save_tasks
from dateutil import parser

st.set_page_config(layout="wide")
st.title("📋 All Tasks")

# ---- CSS ----
st.markdown(
    """
    <style>
    .task-card {
      background: linear-gradient(180deg, #071226 0%, #0b1620 100%);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      color: #dbe9ff;
      box-shadow: 0 6px 18px rgba(2,6,22,0.6);
      cursor:pointer;
      transition: background 0.2s ease;
    }
    .task-card:hover { background:#102030; }
    .title { font-weight:700; font-size:16px; margin-bottom:6px; color:#7fb3ff; }
    .desc { color:#9fb4d6; font-size:13px; margin-bottom:4px; }
    .badge { padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    .status-open { background:#243447; color:#7fb3ff; }
    .status-progress { background:#123a2b; color:#7ee7a6; }
    .status-completed { background:#122022; color:#9be7bf; }
    .seg-wrap { display:flex; gap:6px; align-items:center; }
    .seg { height:12px; border-radius:8px; background:#0f1720; overflow:hidden; }
    .seg-inner { height:100%; }
    .seg2 .seg-inner { border-radius:0; }
    .seg3 .seg-inner { border-radius:0 8px 8px 0; }
    .meta { color:#9fb4d6; font-size:13px; }
    </style>
    """, unsafe_allow_html=True
)

# Create task dropdown
with st.expander("➕ Create Task", expanded=False):
    t_title = st.text_input("Title", key="all_title")
    t_desc = st.text_area("Description", key="all_desc")
    if st.button("Create Task", key="all_create"):
        if not t_title.strip():
            st.error("Title required")
        else:
            add_task(t_title.strip(), t_desc.strip())
            st.success("Task created")
            st.rerun()

tasks = load_tasks()
now = datetime.now()

# Header
st.markdown(
    "<div style='display:flex;gap:12px;margin-bottom:8px;padding:10px 12px;'>"
    "<div style='flex:3;font-weight:700;color:#bcd6ff;'>Task</div>"
    "<div style='flex:1;font-weight:700;color:#bcd6ff;'>Status</div>"
    "<div style='flex:2;font-weight:700;color:#bcd6ff;'>Urgency</div>"
    "<div style='width:120px;font-weight:700;color:#bcd6ff;'>Created</div>"
    "<div style='width:120px;font-weight:700;color:#bcd6ff;'>Completed</div>"
    "</div>", unsafe_allow_html=True
)

# Urgency segmented progress bar
def render_progress_html(days_old: int):
    seg_lens = [2, 2, 1]
    remaining = min(max(0, days_old), 5)
    fills, colors = [], ["#2ecc71", "#f39c12", "#e74c3c"]
    for seg in seg_lens:
        fills.append(min(remaining, seg))
        remaining -= min(remaining, seg)
    html = "<div class='seg-wrap'>"
    for i, seg in enumerate(seg_lens):
        perc = int((fills[i]/seg)*100)
        html += (f"<div class='seg seg{i+1}' style='flex:{seg};'>"
                 f"<div class='seg-inner' style='width:{perc}%; background:{colors[i]};'></div></div>")
    html += f"<div style='min-width:90px;color:#9fb4d6;font-size:13px;margin-left:8px;'>{days_old} day(s) old</div></div>"
    return html

# Render tasks
for t in tasks:
    created_at = parser.parse(t["created_at"]) if isinstance(t["created_at"], str) else t["created_at"]
    days_old = (now - created_at).days
    completed_at = t.get("completed_at")
    status = t.get("status", "Open")

    # Wrap card in a clickable link to Task Detail
    link = f"""<a href="/Task_Detail?task_id={t['id']}" target="_self" style="text-decoration:none;">"""
    st.markdown(link, unsafe_allow_html=True)

    cols = st.columns([3,1,2.2,0.9,0.9])
    with cols[0]:
        st.markdown(f"<div class='task-card'><div class='title'>{t['title']}</div>"
                    f"<div class='desc'>{t.get('description','')}</div></div>"
