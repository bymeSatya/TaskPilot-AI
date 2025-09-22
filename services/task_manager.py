from __future__ import annotations
from typing import List, Dict, Any
from .utils import load_json, save_json, now_utc, new_id

def list_tasks() -> List[Dict[str,Any]]:
    return load_json()

def get_task(task_id: str) -> Dict[str,Any] | None:
    for t in list_tasks():
        if t["id"] == task_id:
            return t
    return None

def create_task(title: str, description: str, tags=None, due_days: int = 5) -> Dict[str,Any]:
    tasks = list_tasks()
    task = {
        "id": new_id(),
        "title": title,
        "description": description,
        "status": "Open",
        "created_at": now_utc().isoformat(),
        "due_days": due_days,
        "activity": [],
        "tags": tags or []
    }
    tasks.append(task)
    save_json(tasks)
    return task

def add_activity(task_id: str, who: str, text: str):
    tasks = list_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t.setdefault("activity", []).append({"at": now_utc().isoformat(), "who": who, "text": text})
            break
    save_json(tasks)

def set_status(task_id: str, status: str):
    tasks = list_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = status
            break
    save_json(tasks)

def by_status(status: str) -> List[Dict[str,Any]]:
    return [t for t in list_tasks() if t.get("status","").lower().startswith(status.lower())]