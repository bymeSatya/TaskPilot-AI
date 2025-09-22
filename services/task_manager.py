import json
import os
from datetime import datetime

DATA_FILE = os.path.join("data", "tasks.json")

# --- Ensure data folder exists ---
os.makedirs("data", exist_ok=True)

# --- Load tasks ---
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# --- Save all tasks back ---
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# --- Add a new task ---
def save_task(task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

# --- Update a task (by ID) ---
def update_task(task_id, updates: dict):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task.update(updates)
            task["updated_at"] = datetime.now().isoformat()
            break
    save_tasks(tasks)

# --- Get a task by ID ---
def get_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None
