"""The schedule flag (OD-S12-10, OD-19): the latest SCHEDULE_CHANGED policy event written through Zone H ZH-09; default OFF.

Kept in its own gate-free module so the runner and the jobs can READ the flag without any import path to the gate (AC-RUN-12)."""
import json


def schedule_state(con):
    row = con.execute("SELECT event_id, new_value, occurred_at FROM policy_events WHERE event_type = 'SCHEDULE_CHANGED'"
                      " AND policy_ref = 'schedule' ORDER BY rowid DESC LIMIT 1").fetchone()
    if row is None:
        return {"enabled": False, "event_id": None, "since": None, "origin": "default"}
    return {"enabled": bool(json.loads(row[1]).get("enabled")), "event_id": row[0], "since": row[2], "origin": "zone_h_event"}
