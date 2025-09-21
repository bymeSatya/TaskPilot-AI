import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path("data/tasks.json")

def load_tasks():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(title, description, category="General"):
    tasks = load_tasks()
    new_task = {
        "id": f"TASK-{len(tasks)+1}",
        "title": title,
        "description": description,
        "category": category,
        "status": "Open",
        "created_at": datetime.now().isoformat(),
        "updates": [],
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def get_task_by_id(task_id):
    tasks = load_tasks()
    return next((t for t in tasks if t["id"] == task_id), None)

def update_task(task_id, update_msg, status=None):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["updates"].append(
                {"time": datetime.now().isoformat(), "msg": update_msg}
            )
            if status:
                task["status"] = status
    save_tasks(tasks)
