"""Read-only reports (observability-spec OBS-6, BEH-OBS-03/04/05/08; INC-07): health, latency, kpi-coverage, queues, selfcheck.

Every report carries the label 'synthetic, unvalidated' while data_origin = synthetic and enforces nothing: `latency` prints p50 / p95 per operation and
no pass / fail (PNFR-06 target Unknown, OPD-14). Alerts are manual in R1: `health` prints red / amber items (BEH-OBS-08)."""
from hub import runtime
from hub.obs import collect
from hub.runs import detector
from hub.runs.flag import schedule_state
from hub.security import audit, settings as sec_settings
from hub.security.canonical import parse

LABEL = "synthetic, unvalidated"


def health(run_service, as_of, anchor_path=None):
    """Every run is listed; abandoned (also a stale run not yet closed), failed runs, missed runs, non-zero tripwires, a broken audit chain."""
    con, rs = run_service.con, run_service.rs
    runs = run_service.list_runs()
    det = detector.missing(con, rs, as_of)
    trip = collect.tripwires(con)
    items = []
    for r in runs:
        if r["outcome"] == "abandoned":
            items.append({"level": "amber", "code": "RUN_ABANDONED", "run_id": r["run_id"], "job": r["job"], "closed_in_store": bool(r["reaped"])})
        elif r["outcome"] == "failed":
            items.append({"level": "red", "code": "RUN_FAILED", "run_id": r["run_id"], "job": r["job"],
                          "errors": [e.get("code") for e in r["errors"]]})
    if det["run_missed_total"]:
        items.append({"level": "red", "code": "RUN_MISSED", "count": det["run_missed_total"]})
    for k, v in sorted(trip.items()):
        if v:
            items.append({"level": "red", "code": "TRIPWIRE_NON_ZERO", "metric": k, "value": v})
    if anchor_path is not None:
        rep = audit.verify(con, anchor_path)
        if rep["status"] != "ok":
            items.append({"level": "red", "code": "AUDIT_CHAIN_BROKEN", "first_broken_seq": rep.get("first_broken_seq")})
    counts = {}
    for r in runs:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    return {"runs": [dict((k, r[k]) for k in ("run_id", "job", "trigger", "triggered_by", "started_at", "ended_at", "outcome", "inputs_seen",
                                               "limit_reached", "backlog_remaining", "reaped")) for r in runs],
            "run_counts": dict(sorted(counts.items())), "schedule": det, "tripwires": trip, "items": items, "label": LABEL}


def _rank(sorted_vals, q):
    n = len(sorted_vals)
    return sorted_vals[min(n, max(1, -(-q * n // 100))) - 1]


def latency(ops, calls, clock):
    """ops: {name: zero-argument callable}. Runs each `calls` times and prints p50 / p95 (nearest rank) in milliseconds; no threshold, no verdict."""
    rows = []
    for name in sorted(ops):
        ms = []
        for _ in range(calls):
            t0 = parse(clock())
            ops[name]()
            ms.append((parse(clock()) - t0).total_seconds() * 1000.0)
        ms.sort()
        rows.append({"operation": name, "calls": calls, "p50_ms": round(_rank(ms, 50), 3), "p95_ms": round(_rank(ms, 95), 3)})
    return {"operations": rows, "verdict": None, "note": "measure only: no target exists (PNFR-06, OPD-14)", "label": LABEL}


def selfcheck(cfg, s, con=None, floor=None):
    """BEH-OBS-03: Python, SQLite, FTS5, config hash and gate status (mode, holders count, schedule flag)."""
    rt = runtime.check(None, None, floor or cfg.get("runtime", {}).get("floor", "3.10"))
    return {"runtime": {"python": rt["python"], "sqlite": rt["sqlite"], "fts5": rt["fts5"], "floor": rt["floor"]},
            "config_hash": sec_settings.config_hash(cfg),
            "gate": {"disposition_mode": cfg.get("disposition", {}).get("mode", "none"), "holders_configured": len(s["zone_h"]["holders"]),
                     "schedule_enabled": None if con is None else schedule_state(con)["enabled"]},
            "data_origin": cfg.get("data_origin", "synthetic"), "label": LABEL}
