import os, json
import datetime as dtm
from dateutil import tz

DATA_PATH = os.path.join("data","tasks.json")

def to_local(dt_iso: str, zone: str = "Asia/Kolkata") -> str:
    if not dt_iso:
        return "-"
    d = dtm.datetime.fromisoformat(str(dt_iso).replace("Z","+00:00"))
    return d.astimezone(tz.gettz(zone)).strftime("%b %d, %Y, %I:%M %p")