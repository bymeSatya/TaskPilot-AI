# app.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from dateutil import parser
import openai
import requests

# ---------------------------
# Config / Storage
# ---------------------------
st.set_page_config(page_title="TaskPilot AI", layout="wide", initial_sidebar_state="expanded")

TASK_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)

# ---------------------------
# Utilities
# ---------------------------
def new_task_id(tasks):
    if not tasks: return "TASK-1"
    nums = [int(t["id"].split("-")[-1]) for t in tasks if t.get("id","").startswith("TASK-")]
    return f"TASK-{max(nums)+1}" if nums else "TASK-1"

def days_old(created_str):
    try:
        created = parser.parse(created_str) if isinstance(created_str, str) else created_str
    except:
        created = datetime.now()
    return (datetime.now() - created).days

def init_openai_from_secrets():
    key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
    if key:
        openai.api_key = key
        return True
    return False

def openai_suggest(prompt, model="gpt-4o-mini"):
    if not init_openai_from_secrets():
        return "OpenAI key not configured. Add OPENAI_API_KEY in Streamlit secrets."
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=600
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"OpenAI error: {e}"

def groq_search(query):
    """Call user-provided Groq API to deep-dive documents.
       Provide GROQ_API_URL and GROQ_API_KEY in streamlit secrets.
    """
    url = st.secrets.get("GROQ_API_URL")
    key = st.secrets.get("GROQ_API_KEY")
    if not url or not key:
        return "Groq API not configured. Add GROQ_API_URL and GROQ_API_KEY to secrets."
    try:
        resp = requests.post(url, json={"query": query}, headers={"Authorization": f"Bearer {key}"}, timeout=12)
        if resp.status_code == 200:
            return resp.json()
        return f"Groq API returned {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"Groq API call error: {e}"

# ---------------------------
# Styling (dark/light)
# ---------------------------
# Minimal custom CSS to mimic the visual style in screenshots
def local_css(theme="dark"):
    if theme == "dark":
        primary_bg = "#071025"
        panel_bg = "#0b1220"
        text_color = "#cfe7ff"
        muted = "#94a3b8"
        accent = "#6ee7b7"
    else:
        primary_bg = "#f7fafc"
        panel_bg = "#ffffff"
        text_color = "#0b1220"
        muted = "#475569"
        accent = "#0ea5a4"

    css = f"""
    <style>
      .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
      .sidebar .sidebar-content {{ background-color: {panel_bg}; }}
      .css-1d391kg {{ color: {text_color}; }}
      .task-card {{ background:{panel_bg}; border-radius:10px; padding:16px; margin-bottom:12px; }}
      .metric-card {{ background:{panel_bg}; border-radius:10px; padding:18px; }}
      .small-muted {{ color:{muted}; font-size:0.92em; }}
      .accent-badge {{ background:{accent}; color:#021; padding:6px 8px; border-radius:8px; font-weight:600; }}
      .sidebar .css-1d391kg {{ color: {text_color}; }}
      .stButton>button {{ border-radius:8px; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------------
# Page state & Navigation
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

tasks = load_tasks()

# Sidebar (Left)
with st.sidebar:
    local_css(st.session_state.theme)
    st.markdown("### 🤖 TaskPilot AI", unsafe_allow_html=True)
    st.markdown("---")
    st.session_state.theme = st.radio("Theme", ("dark","light"), index=0 if st.session_state.theme=="dark" else 1, horizontal=True)
    st.button("Refresh", on_click=lambda: st.experimental_rerun())
    st.markdown("---")

    menu = st.radio("Menu",
                    ["Dashboard", "All Tasks", "Open Tasks", "Closed Tasks", "Knowledge Base", "Development"],
                    index=["Dashboard", "All Tasks", "Open Tasks", "Closed Tasks", "Knowledge Base", "Development"].index(st.session_state.page) if st.session_state.page in ["Dashboard","All Tasks","Open Tasks","Closed Tasks","Knowledge Base","Development"] else 0)
    st.session_state.page = menu

    st.markdown("---")
    st.markdown("### Quick Create")
    with st.form("quick_create", clear_on_submit=True):
        qtitle = st.text_input("Title")
        qcat = st.selectbox("Category", ["Snowflake", "Matillion", "General"], index=0)
        qprio = st.selectbox("Priority", ["Low","Medium","High"], index=1)
        qdetails = st.text_area("Short details")
        if st.form_submit_button("Create"):
            t = {
                "id": new_task_id(tasks),
                "title": qtitle or "Untitled Task",
                "category": qcat,
                "priority": qprio,
                "details": qdetails or "",
                "status": "Open",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "updates": []
            }
            tasks.append(t)
            save_tasks(tasks)
            st.success(f"Task {t['id']} created.")
            st.session_state.selected_task = t["id"]
            st.session_state.page = "All Tasks"
            st.experimental_rerun()

# Main layout (Right)
st.markdown(f"# {st.session_state.page}" if st.session_state.page else "# Dashboard")

# Reminder modal: morning/evening when opened (simple)
now_hr = datetime.now().hour
if "reminded" not in st.session_state:
    if now_hr in (9, 18):  # basic morning/evening
        with st.modal("Daily Check-in"):
            if now_hr == 9:
                st.write("🌞 Good morning! Here are your open tasks.")
            else:
                st.write("🌇 Evening check-in: Please update your tasks if any progress.")
            st.button("Got it", on_click=lambda: st.session_state.update({"reminded": True}))
    st.session_state.reminded = True

# --- Dashboard page ---
if st.session_state.page == "Dashboard":
    open_tasks = [t for t in tasks if t["status"].lower() != "completed" and t["status"].lower() != "closed"]
    closed_tasks = [t for t in tasks if t["status"].lower() in ["completed","closed"]]
    overdue = [t for t in open_tasks if days_old(t["created_at"]) > 5]
    nearing = [t for t in open_tasks if 3 <= days_old(t["created_at"]) <= 5]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Tasks", len(open_tasks))
    c2.metric("Overdue", len(overdue))
    c3.metric("Nearing Deadline (3-5d)", len(nearing))
    c4.metric("Closed Tasks", len(closed_tasks))

    st.markdown("---")
    st.subheader("Progress Overview")
    # Show each open task with progress bar proportionally to age (0 to 7 days)
    for t in open_tasks:
        age = days_old(t["created_at"])
        pct = min(100, int((age / 7) * 100))
        cols = st.columns([4,1,2])
        with cols[0]:
            st.markdown(f"**{t['title']}**  —  <span class='small-muted'>{t['category']} · {t['priority']}</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-muted'>Created: {parser.parse(t['created_at']).strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
        with cols[1]:
            st.progress(pct)
        with cols[2]:
            st.markdown(f"<div class='accent-badge'>{age} day(s)</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Priority: Overdue Tasks")
    if overdue:
        for t in overdue:
            st.warning(f"{t['id']} — {t['title']} ({days_old(t['created_at'])} days old)")
    else:
        st.info("No overdue tasks. Great job!")

# --- All Tasks page ---
elif st.session_state.page == "All Tasks":
    st.markdown("A comprehensive list of all tasks including open and closed.")
    for t in tasks:
        col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
        with col1:
            st.markdown(f"**{t['id']} - {t['title']}**")
            st.markdown(f"<div class='small-muted'>{t.get('category','-')} · {t.get('priority','-')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-muted'>{t.get('details','')}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{t['status']}**")
        with col3:
            st.markdown(f"{days_old(t['created_at'])}d old")
        with col4:
            if st.button("Open", key=f"open_{t['id']}"):
                st.session_state.selected_task = t["id"]
                st.session_state.page = "task_detail"
                st.experimental_rerun()
        with col5:
            if st.button("Delete", key=f"del_{t['id']}"):
                tasks[:] = [x for x in tasks if x["id"] != t["id"]]
                save_tasks(tasks)
                st.experimental_rerun()

# --- Open Tasks page ---
elif st.session_state.page == "Open Tasks":
    open_list = [t for t in tasks if t["status"].lower() not in ["completed","closed"]]
    st.markdown("Open tasks currently in progress or not started.")
    for t in open_list:
        st.markdown(f"- **{t['id']}** {t['title']} — {t.get('category','-')} — {days_old(t['created_at'])} day(s)")
        if st.button("Open", key=f"open_open_{t['id']}"):
            st.session_state.page = "task_detail"
            st.session_state.selected_task = t["id"]
            st.experimental_rerun()

# --- Closed Tasks page ---
elif st.session_state.page == "Closed Tasks":
    closed_list = [t for t in tasks if t["status"].lower() in ["completed","closed"]]
    st.markdown("Tasks that are completed.")
    for t in closed_list:
        st.markdown(f"- **{t['id']}** {t['title']} — Completed on: {t.get('completed_at','-')}")

# --- Knowledge Base page ---
elif st.session_state.page == "Knowledge Base":
    st.markdown("Knowledge Base (Snowflake & Matillion resources).")
    st.markdown("- Add your most used doc links here.")
    st.markdown("- You can configure a Groq API in Streamlit secrets and use the 'Deep Dive' feature inside each task to search your docs.")
    if st.button("Open docs example (Snowflake)"):
        st.markdown("Snowflake docs: https://docs.snowflake.com/")
    st.markdown("---")
    st.markdown("You can add your curated links or upload a document for indexing in your external Groq index.")

# --- Development page ---
elif st.session_state.page == "Development":
    st.markdown("Development / Roadmap")
    st.markdown("- Add Slack/Teams push notifications")
    st.markdown("- Integrate directly with Matillion APIs")
    st.markdown("- Sync job failures from Snowflake alert feeds")

# --- Task detail page ---
elif st.session_state.page in ["task_detail", "Task", "task"]:
    sel = st.session_state.selected_task
    task = next((t for t in tasks if t["id"] == sel), None)
    if not task:
        st.error("Selected task not found.")
    else:
        left, right = st.columns([3,1])
        with left:
            st.markdown(f"## {task['title']}  <small class='small-muted'>{task['id']}</small>", unsafe_allow_html=True)
            st.markdown(f"**Status:** {task['status']}")
            st.markdown("### Description")
            st.write(task.get("details", ""))
            st.markdown("### Activity")
            for upd in task.get("updates", []):
                st.info(f"{upd.get('time','-')} — {upd.get('text','')}")
            st.markdown("---")
            st.markdown("### Add Update")
            with st.form(f"update_form_{task['id']}", clear_on_submit=True):
                new_text = st.text_area("Write update (raw notes).")
                quick_suggest = st.checkbox("Also get AI-suggested manager-style update", value=True)
                if st.form_submit_button("Add Update"):
                    final_text = new_text
                    if quick_suggest:
                        prompt = f"Rewrite the following raw task note into a concise manager-friendly status update and suggested next steps:\n\n{new_text}\n\nKeep it short, 2-3 sentences + 1 recommended next step."
                        final_text = openai_suggest(prompt)
                    task.setdefault("updates", []).append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": final_text})
                    task["updated_at"] = datetime.now().isoformat()
                    save_tasks(tasks)
                    st.success("Update saved.")
                    st.experimental_rerun()
        with right:
            st.markdown("### Details")
            st.markdown(f"- **Category:** {task.get('category','-')}")
            st.markdown(f"- **Priority:** {task.get('priority','-')}")
            st.markdown(f"- **Created:** {parser.parse(task['created_at']).strftime('%b %d, %Y, %I:%M %p')}")
            st.markdown(f"- **Last Updated:** {parser.parse(task['updated_at']).strftime('%b %d, %Y, %I:%M %p')}")
            st.markdown("---")
            st.markdown("### Actions")
            if st.button("Mark Completed"):
                task["status"] = "Completed"
                task["completed_at"] = datetime.now().isoformat()
                save_tasks(tasks)
                st.experimental_rerun()
            if st.button("Close Task"):
                task["status"] = "Closed"
                task["closed_at"] = datetime.now().isoformat()
                save_tasks(tasks)
                st.experimental_rerun()
            if st.button("Delete Task"):
                tasks[:] = [x for x in tasks if x["id"] != task["id"]]
                save_tasks(tasks)
                st.session_state.page = "All Tasks"
                st.experimental_rerun()
            st.markdown("---")
            st.markdown("### AI Chat / Assistant")
            user_q = st.text_input("Ask your AI assistant about this task (e.g., 'What next step should I take?')", key=f"aiq_{task['id']}")
            if st.button("Get Suggestion", key=f"getsug_{task['id']}"):
                prompt = f"You are an AI assistant specialized in Snowflake and Matillion. Task title: {task['title']}. Details: {task.get('details','')}. Updates: {task.get('updates',[])}. User question: {user_q}\n\nProvide a concise, actionable answer and recommended next steps."
                sug = openai_suggest(prompt)
                st.success("AI Suggestion:")
                st.write(sug)
                # Offer optional deep-dive with Groq
                if st.button("Deep Dive in Docs (Groq)", key=f"deep_{task['id']}"):
                    qres = groq_search(f"{task['title']} {task.get('details','')} {user_q}")
                    st.write(qres)

# Footer / Save tasks on each run
save_tasks(tasks)
