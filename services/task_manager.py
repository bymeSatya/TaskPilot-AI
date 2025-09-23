from __future__ import annotations
from typing import List, Dict, Any
import os, json, datetime as dtm

DATA_PATH = os.path.join("data", "tasks.json")

def _ensure_store():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump([], f)

def _load() -> List[Dict[str,Any]]:
    _ensure_store()
    with open(DATA_PATH) as f:
        return json.load(f)

def _save(tasks: List[Dict[str,Any]]):
    _ensure_store()
    with open(DATA_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def list_tasks() -> List[Dict[str,Any]]:
    return _load()

def get_task(task_id: str) -> Dict[str,Any] | None:
    for t in _load():
        if t.get("id") == task_id:
            return t
    return None

def _new_id() -> str:
    return f"TASK-{int(dtm.datetime.now(dtm.timezone.utc).timestamp())%10000000}"

def create_task(title: str, description: str, tags=None, due_days: int = 5) -> Dict[str,Any]:
    tasks = _load()
    t = {
        "id": _new_id(),
        "title": title,
        "description": description,
        "status": "Open",
        "created_at": dtm.datetime.now(dtm.timezone.utc).isoformat(),
        "due_days": due_days,
        "activity": [],
        "tags": tags or []
    }
    tasks.append(t)
    _save(tasks)
    return t

def set_status(task_id: str, status: str):
    tasks = _load()
    for t in tasks:
        if t.get("id") == task_id:
            t["status"] = status
            if status in ("Closed","Completed") and not t.get("completed_at"):
                t["completed_at"] = dtm.datetime.now(dtm.timezone.utc).isoformat()
            elif status not in ("Closed","Completed"):
                t.pop("completed_at", None)
            break
    _save(tasks)

def add_activity(task_id: str, who: str, text: str):
    tasks = _load()
    for t in tasks:
        if t.get("id") == task_id:
            t.setdefault("activity", []).append({
                "at": dtm.datetime.now(dtm.timezone.utc).isoformat(),
                "who": who, "text": text
            })
            break
    _save(tasks)

def delete_task(task_id: str):
    tasks = [t for t in _load() if t.get("id") != task_id]
    _save(tasks)