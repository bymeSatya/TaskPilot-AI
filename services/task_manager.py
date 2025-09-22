import json
from datetime import datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            # convert dates back to datetime
            for task in tasks:
                task["created"] = datetime.fromisoformat(task["created"])
                if task.get("completed_date"):
                    task["completed_date"] = datetime.fromisoformat(task["completed_date"])
            return tasks
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_task(tasks):
    for task in tasks:
        task["created"] = task["created"].isoformat()
        if task.get("completed_date"):
            task["completed_date"] = task["completed_date"].isoformat()
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)
    # convert them back for session usage
    for task in tasks:
        task["created"] = datetime.fromisoformat(task["created"])
        if task.get("completed_date"):
            task["completed_date"] = datetime.fromisoformat(task["completed_date"])
