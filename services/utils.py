import os, json
import datetime as dtm

DATA_PATH = os.path.join("data","tasks.json")

def load_json(path: str = DATA_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path,"w") as f: json.dump([], f)
    with open(path) as f: return json.load(f)

def save_json(data, path: str = DATA_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f: json.dump(data, f, indent=2)

def to_local(dt_iso: str, zone: str = "Asia/Kolkata") -> str:
    from dateutil import tz
    if not dt_iso: return "-"
    d = dtm.datetime.fromisoformat(dt_iso.replace("Z","+00:00"))
    return d.astimezone(tz.gettz(zone)).strftime("%b %d, %Y")

def parse_dt_safe(val):
    import datetime as _dt
    try:
        if isinstance(val, _dt.datetime):
            return val if val.tzinfo else val.replace(tzinfo=_dt.timezone.utc)
        if not val or not isinstance(val, str):
            return _dt.datetime.now(_dt.timezone.utc)
        s = val.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return _dt.datetime.fromisoformat(s)
        except Exception:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    d = _dt.datetime.strptime(val, fmt)
                    return d.replace(tzinfo=_dt.timezone.utc)
                except Exception:
                    pass
            return _dt.datetime.now(_dt.timezone.utc)
    except Exception:
        return _dt.datetime.now(_dt.timezone.utc)