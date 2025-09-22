import datetime as dtm

def parse_dt_safe(val):
    """Return aware UTC datetime; tolerate None/invalid formats."""
    try:
        if isinstance(val, dtm.datetime):
            return val if val.tzinfo else val.replace(tzinfo=dtm.timezone.utc)
        if not val or not isinstance(val, str):
            return dtm.datetime.now(dtm.timezone.utc)
        s = val.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return dtm.datetime.fromisoformat(s)
        except Exception:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    d = dtm.datetime.strptime(val, fmt)
                    return d.replace(tzinfo=dtm.timezone.utc)
                except Exception:
                    pass
            return dtm.datetime.now(dtm.timezone.utc)
    except Exception:
        return dtm.datetime.now(dtm.timezone.utc)