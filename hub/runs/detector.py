"""Missing-run detector and timeliness record (BEH-RUN-08, BEH-RUN-09, AC-RUN-15, AC-OBS-03; INC-07). Read-only; no scheduler.

With the schedule flag OFF the detector reports 'schedule disabled' - never failures. With it ON it lists every expected run (from
configuration `schedule.expected`, daily at HH:MM in site.timezone) that is due (expected time + grace passed) and has no RUN_STARTED row
with trigger 'scheduled' in its slot [expected - grace, expected + 24 h - grace). Only runs after the moment the flag was switched on count.
`timeliness` answers 'finished before 06:00 local business time' per run; site.timezone is Unknown (U-12-F06-1): UTC unless a fixed offset is
configured, and the answer is labelled accordingly.
"""
import datetime

from hub.runs.flag import schedule_state
from hub.runs.settings import tz_offset_minutes
from hub.security.canonical import fmt, parse

LABEL = "synthetic, unvalidated"
DEADLINE_DEFAULT = "06:00"


def _expected(rs, since, until):
    off = datetime.timedelta(minutes=tz_offset_minutes(rs["site"]["timezone"]))
    day = (since + off).date() - datetime.timedelta(days=1)
    last = (until + off).date() + datetime.timedelta(days=1)
    out = []
    while day <= last:
        for e in rs["schedule"]["expected"]:
            hh, mm = int(e["at"][:2]), int(e["at"][3:])
            t = datetime.datetime(day.year, day.month, day.day, hh, mm, tzinfo=datetime.timezone.utc) - off
            if since <= t:
                out.append((e["job"], t))
        day += datetime.timedelta(days=1)
    return sorted(out, key=lambda x: (x[1], x[0]))


def missing(con, rs, as_of):
    st = schedule_state(con)
    tz = rs["site"]["timezone"]
    if not st["enabled"]:
        return {"schedule": "disabled", "message": "schedule disabled", "expected_checked": 0, "missed": [], "run_missed_total": 0,
                "by_job": {}, "timezone": tz, "label": LABEL}
    until = parse(as_of)
    grace = datetime.timedelta(minutes=rs["schedule"]["grace_minutes"])
    day = datetime.timedelta(hours=24)
    missed, checked = [], 0
    for job, t in _expected(rs, parse(st["since"]), until):
        if t + grace > until:
            continue
        checked += 1
        hit = con.execute("SELECT 1 FROM run_event WHERE job = ? AND event_type = 'RUN_STARTED' AND trigger = 'scheduled'"
                          " AND occurred_at >= ? AND occurred_at < ?", (job, fmt(t - grace), fmt(t + day - grace))).fetchone()
        if hit is None:
            missed.append({"job": job, "expected_at": fmt(t)})
    by_job = {}
    for m in missed:
        by_job[m["job"]] = by_job.get(m["job"], 0) + 1
    return {"schedule": "enabled", "schedule_since": st["since"], "expected_checked": checked, "missed": missed,
            "run_missed_total": len(missed), "by_job": dict(sorted(by_job.items())), "timezone": tz, "label": LABEL}


def timeliness(records, rs, deadline=DEADLINE_DEFAULT, triggers=("scheduled",)):
    """records: folded run records. One row per finished run with a trigger in `triggers`."""
    tz = rs["site"]["timezone"]
    off = datetime.timedelta(minutes=tz_offset_minutes(tz))
    hh, mm = int(deadline[:2]), int(deadline[3:])
    rows = []
    for r in records:
        if r["outcome"] != "finished" or r["trigger"] not in triggers:
            continue
        start, end = parse(r["started_at"]) + off, parse(r["ended_at"]) + off
        limit = datetime.datetime(start.year, start.month, start.day, hh, mm, tzinfo=datetime.timezone.utc)
        rows.append({"run_id": r["run_id"], "job": r["job"], "ended_at": r["ended_at"], "ended_local": end.strftime("%Y-%m-%dT%H:%M:%S"),
                     "deadline_local": limit.strftime("%Y-%m-%dT%H:%M:%S"), "finished_before_deadline": 1 if end <= limit else 0})
    note = ("site.timezone = %s; the business time zone is Unknown (U-12-F06-1) until configured" % tz) if tz == "UTC" else "site.timezone = %s" % tz
    return {"deadline": deadline, "timezone": tz, "timezone_note": note, "runs": rows, "label": LABEL}
