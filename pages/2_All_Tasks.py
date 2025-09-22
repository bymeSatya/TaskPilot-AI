# pages/2_All_Tasks.py
import streamlit as st
from datetime import datetime
from services.task_manager import load_tasks, add_task, delete_task, save_tasks
from dateutil import parser

st.set_page_config(layout="wide")
st.title("📋 All Tasks")

# ---- CSS for task card / status / progress ----
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
    }
    .task-row { display:flex; gap:12px; align-items:center; width:100%; }
    .task-col { padding:4px 8px; }
    .title { font-weight:700; font-size:16px; margin-bottom:6px; }
    .desc { color:#9fb4d6; font-size:13px; margin-bottom:4px; }
    .badge { padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    .status-open { background:#243447; color:#7fb3ff; }
    .status-progress { background:#123a2b; color:#7ee7a6; }
    .status-completed { background:#122022; color:#9be7bf; }
    /* segmented progress container */
    .seg-wrap { display:flex; gap:6px; align-items:center; }
    .seg { height:12px; border-radius:8px; background:#0f1720; overflow:hidden; position:relative; }
    .seg-inner { height:100%; border-radius:8px 0 0 8px; }
    .seg2 .seg-inner { border-radius:0; }
    .seg3 .seg-inner { border-radius:0 8px 8px 0; }
    .meta { color:#9fb4d6; font-size:13px; }
    .actions { display:flex; gap:8px; }
    .small-btn { padding:6px 8px; border-radius:8px; background:#0b2a3a; color:#dff5ff; border: none; }
    </style>
    """, unsafe_allow_html=True
)

# Create task via expander (dropdown)
with st.expander("➕ Create Task", expanded=False):
    t_title = st.text_input("Title", key="all_title")
    t_desc = st.text_area("Description", key="all_desc")
    if st.button("Create Task", key="all_create"):
        if not t_title.strip():
            st.error("Title required")
        else:
            add_task(t_title.strip(), t_desc.strip())
            st.success("Task created")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

tasks = load_tasks()
now = datetime.now()

# Header row (visual)
st.markdown(
    "<div style='display:flex;gap:12px;margin-bottom:8px;padding:10px 12px;'>"
    "<div style='flex:3;font-weight:700;color:#bcd6ff;'>Task</div>"
    "<div style='flex:1;font-weight:700;color:#bcd6ff;'>Status</div>"
    "<div style='flex:2;font-weight:700;color:#bcd6ff;'>Urgency</div>"
    "<div style='width:120px;font-weight:700;color:#bcd6ff;'>Created</div>"
    "<div style='width:120px;font-weight:700;color:#bcd6ff;'>Completed</div>"
    "<div style='width:120px;'></div>"
    "</div>", unsafe_allow_html=True
)

# Helper to render segmented progress bar (5 days = 2+2+1)
def render_progress_html(days_old: int):
    # clamp days to >=0
    d = max(0, days_old)
    seg_lens = [2, 2, 1]
    # compute fill for each segment (0..seg_len)
    remaining = min(d, 5)
    fills = []
    for seg in seg_lens:
        fill = min(max(0, remaining), seg)
        fills.append(fill)
        remaining -= fill
    # convert to percent within each segment (0..100)
    fill_percents = [int((f / seg_lens[i]) * 100) for i, f in enumerate(fills)]
    # segment base width in percent of whole bar
    base_widths = [ (seg / 5) * 100 for seg in seg_lens ]  # [40,40,20]
    # HTML for segmented bar
    html = "<div class='seg-wrap'>"
    colors = ["#2ecc71", "#f39c12", "#e74c3c"]  # green, orange, red
    for i in range(3):
        html += (f"<div class='seg seg{i+1}' style='flex:{base_widths[i]}; min-width:0;'>"
                 f"<div class='seg-inner' style='width:{fill_percents[i]}%; background:{colors[i]};'></div>"
                 "</div>")
    html += f"<div style='min-width:90px;color:#9fb4d6;font-size:13px;margin-left:8px;'>{d} day(s) old</div>"
    html += "</div>"
    return html

# Render tasks as curved rectangle rows
for t in tasks:
    created_at = parser.parse(t["created_at"]) if isinstance(t["created_at"], str) else t["created_at"]
    days_old = (now - created_at).days
    completed_at = t.get("completed_at", "-")
    status = t.get("status", "Open")

    # container
    st.markdown("<div class='task-card'>", unsafe_allow_html=True)
    cols = st.columns([3, 1, 2.2, 0.9, 0.9, 1])
    # Task column
    with cols[0]:
        st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc'>{t.get('description','')}</div>", unsafe_allow_html=True)

    # Status column
    with cols[1]:
        cls = "status-open"
        if status.lower() in ("in progress", "progress"):
            cls = "status-progress"
        if status.lower() in ("completed", "closed"):
            cls = "status-completed"
        st.markdown(f"<div class='badge {cls}'>{status}</div>", unsafe_allow_html=True)

    # Urgency column (segmented progress)
    with cols[2]:
        st.markdown(render_progress_html(days_old), unsafe_allow_html=True)

    # Created
    with cols[3]:
        st.markdown(f"<div class='meta'>{created_at.strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

    # Completed
    with cols[4]:
        if status.lower() in ("completed", "closed") and completed_at != "-":
            try:
                comp_dt = parser.parse(completed_at)
                st.markdown(f"<div class='meta'>{comp_dt.strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown(f"<div class='meta'>{completed_at}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='meta'>-</div>", unsafe_allow_html=True)

    # Actions
    with cols[5]:
        if st.button("Open", key=f"open_{t['id']}"):
            st.session_state['selected_task'] = t['id']
            # route to Task Detail page if you have it
            try:
                st.switch_page("pages/5_Task_Detail.py")
            except Exception:
                # fallback: set a session flag for your Task Detail page
                st.session_state['page'] = 'task_detail'
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

        if status.lower() not in ("completed", "closed"):
            if st.button("Mark Completed", key=f"complete_{t['id']}"):
                # mark completed and set completed_at
                all_tasks = load_tasks()
                for task_obj in all_tasks:
                    if task_obj.get("id") == t["id"]:
                        task_obj["status"] = "Completed"
                        task_obj["completed_at"] = datetime.now().isoformat()
                        break
                save_tasks(all_tasks)
                st.success("Marked completed")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
        if st.button("Delete", key=f"delete_{t['id']}"):
            delete_task(t['id'])
            st.success("Deleted")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
