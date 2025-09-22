from __future__ import annotations
import json, os, uuid
from datetime import datetime, timedelta, timezone
from dateutil import tz

DATA_PATH = os.path.join("data", "tasks.json")

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def to_local(dt: str, zone: str = "Asia/Kolkata") -> str:
    d = datetime.fromisoformat(dt.replace("Z","+00:00"))
    return d.astimezone(tz.gettz(zone)).strftime("%b %d, %Y, %I:%M %p")

def load_json(path: str = DATA_PATH):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path,"w") as f: json.dump([], f)
    with open(path) as f: return json.load(f)

def save_json(data, path: str = DATA_PATH):
    with open(path,"w") as f: json.dump(data, f, indent=2)

def new_id(prefix="TASK") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:4].upper()}"

def default_due(created_at: datetime, days: int = 5) -> datetime:
    return created_at + timedelta(days=days)

def pct_complete(created_at_iso: str, days: int = 5) -> float:
    start = datetime.fromisoformat(created_at_iso.replace("Z","+00:00"))
    end = default_due(start, days)
    total = (end - start).total_seconds()
    spent = (now_utc() - start).total_seconds()
    if total <= 0: return 100.0
    return max(0.0, min(100.0, 100.0 * spent / total))