# services/task_manager.py
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "tasks.json"

def _read_all() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _write_all(tasks: List[Dict]):
    DATA_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")

def load_tasks() -> List[Dict]:
    """Return list of all tasks."""
    return _read_all()

def save_tasks(tasks: List[Dict]):
    """Overwrite tasks file."""
    _write_all(tasks)

def _next_id(tasks: List[Dict]) -> str:
    ids = []
    for t in tasks:
        tid = t.get("id", "")
        if isinstance(tid, str) and tid.startswith("TASK-"):
            try:
                ids.append(int(tid.split("-")[-1]))
            except:
                continue
    return f"TASK-{max(ids) + 1}" if ids else "TASK-1"

def add_task(title: str, description: str = "", category: str = "General", priority: str = "Medium") -> Dict:
    """Create and persist a new task. Returns the new task."""
    tasks = _read_all()
    new = {
        "id": _next_id(tasks),
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "updates": []
    }
    tasks.append(new)
    _write_all(tasks)
    return new

def get_task(task_id: str) -> Optional[Dict]:
    for t in _read_all():
        if t.get("id") == task_id:
            return t
    return None

def update_task(task_id: str, update_msg: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict]:
    tasks = _read_all()
    changed = False
    for t in tasks:
        if t.get("id") == task_id:
            if update_msg:
                t.setdefault("updates", []).append({"time": datetime.now().isoformat(), "msg": update_msg})
            if status:
                t["status"] = status
            t["updated_at"] = datetime.now().isoformat()
            changed = True
            updated = t
            break
    if changed:
        _write_all(tasks)
        return updated
    return None

def delete_task(task_id: str) -> bool:
    tasks = _read_all()
    new_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(new_tasks) == len(tasks):
        return False
    _write_all(new_tasks)
    return True
