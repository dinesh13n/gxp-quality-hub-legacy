"""Observability metrics derived deterministically from stored rows (observability-spec OBS-4, BEH-OBS-05/06; INC-07).

`samples()` computes the normative metrics that can be read from the stores that exist after INC-07; `snapshot()` writes them as insert-only
`obs_metric` rows. Counters here are totals over the stored rows (a re-computation gives the same numbers), so "intake_noop_duplicate_total
+100 after a replay of 100 items" (AC-OBS-09) is a difference of two collections. Implemented: intake_items_total, intake_noop_duplicate_total,
quarantine_depth, exception_queue_depth, decision_events_total, zone_h_attempts_total, zone_h_service_actor_rejections_total,
zone_h_service_actor_accepted, run_duration_seconds, run_backlog_remaining, run_missed_total, model_calls_total, egress_attempts_total,
search_engine. Not yet (need later increments or an anchor path): http_*, auth_failures_total, audit_chain_verify_ok, projection_mismatch_count,
exception_age_hours_p90, unmatched_reference_rate, run_finished_before_0600_local (reported by hub.runs.detector), db_busy_total,
override_total, defaulted_outputs_total (RTD-60).
"""
import json

from hub import runtime
from hub.obs import metrics as tripwire_metrics
from hub.security.canonical import canonical

TRIPWIRE_NAMES = ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted")


def _s(name, kind, labels, value):
    return {"name": name, "kind": kind, "labels": dict(labels), "value": str(value)}


def zone_h_service_actor_accepted(con):
    """ZONE_H_ATTEMPT audit records with outcome success by a non-human actor: must be 0 (FR-GATE-03, BEH-OBS-06)."""
    return con.execute("SELECT count(*) FROM audit_log WHERE action = 'ZONE_H_ATTEMPT' AND outcome = 'success' AND actor_kind <> 'human'").fetchone()[0]


def tripwires(con):
    t = tripwire_metrics.tripwires()
    return {"model_calls_total": t["model_calls_total"], "egress_attempts_total": t["egress_attempts_total"],
            "zone_h_service_actor_accepted": zone_h_service_actor_accepted(con)}


def samples(con, runs=(), missed=None):
    """runs: folded run records (hub.runs.service); missed: {job: count} from the missing-run detector (None = schedule disabled)."""
    out = []
    tables = set(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')"))
    if "intake_current" in tables:
        for src, oc, n in con.execute("SELECT r.source, o.outcome, count(*) FROM intake_current o JOIN raw_intake r ON r.raw_id = o.raw_id"
                                      " GROUP BY 1, 2 ORDER BY 1, 2"):
            out.append(_s("intake_items_total", "counter", {"source": src, "outcome": oc}, n))
        for src, n in con.execute("SELECT r.source, count(*) FROM intake_outcome o JOIN raw_intake r ON r.raw_id = o.raw_id"
                                  " WHERE o.outcome = 'NOOP_DUPLICATE' GROUP BY 1 ORDER BY 1"):
            out.append(_s("intake_noop_duplicate_total", "counter", {"source": src}, n))
        q = dict(con.execute("SELECT queue, count(*) FROM intake_current WHERE queue IS NOT NULL GROUP BY 1").fetchall())
        out.append(_s("quarantine_depth", "gauge", {"queue": "quarantine_invalid"}, q.get("quarantine_invalid", 0)))
        for name in ("revision_review", "unmatched", "ambiguous_match", "flagged_value"):
            out.append(_s("exception_queue_depth", "gauge", {"queue": name}, q.get(name, 0)))
    if "decision_events" in tables:
        for et, n in con.execute("SELECT event_type, count(*) FROM decision_events GROUP BY 1 ORDER BY 1"):
            out.append(_s("decision_events_total", "counter", {"event_type": et}, n))
    zh = {}
    for det, oc, kind in con.execute("SELECT details, outcome, actor_kind FROM audit_log WHERE action = 'ZONE_H_ATTEMPT' ORDER BY audit_seq"):
        act = json.loads(det).get("zone_h_action") or "unknown"
        zh[(act, oc)] = zh.get((act, oc), 0) + 1
        if kind != "human" and oc == "denied":
            zh[(act, "service_rejected")] = zh.get((act, "service_rejected"), 0) + 1
    for (act, oc), n in sorted(zh.items()):
        if oc == "service_rejected":
            out.append(_s("zone_h_service_actor_rejections_total", "counter", {"action": act}, n))
        else:
            out.append(_s("zone_h_attempts_total", "counter", {"action": act, "outcome": oc}, n))
    by_job = {}
    for r in runs:
        by_job.setdefault(r["job"], []).append(r)
    for job in sorted(by_job):
        done = [r for r in by_job[job] if r["outcome"] in ("finished", "failed") and r.get("duration_seconds") is not None]
        if done:
            ds = [r["duration_seconds"] for r in done]
            out.append(_s("run_duration_seconds", "histogram", {"job": job},
                          canonical({"count": len(ds), "max_s": max(ds), "sum_s": round(sum(ds), 6)})))
        fin = [r for r in by_job[job] if r["outcome"] == "finished"]
        if fin:
            out.append(_s("run_backlog_remaining", "gauge", {"job": job}, fin[-1]["backlog_remaining"]))
    if missed is not None:
        for job, n in sorted(missed.items()):
            out.append(_s("run_missed_total", "counter", {"job": job}, n))
    for name, v in sorted(tripwires(con).items()):
        out.append(_s(name, "counter", {}, v))
    out.append(_s("search_engine", "gauge", {"engine": "fts5" if runtime.fts5_available() else "fallback"}, 1))
    return sorted(out, key=lambda s: (s["name"], canonical(s["labels"])))


def insert_samples(con, clock, sample_list, run_id=None):
    """Insert the samples as obs_metric rows (insert-only) inside the caller's transaction (no commit)."""
    now = clock()
    con.executemany("INSERT INTO obs_metric(collected_at, name, kind, labels, value, run_id) VALUES (?,?,?,?,?,?)",
                    [(now, s["name"], s["kind"], canonical(s["labels"]), s["value"], run_id) for s in sample_list])
    return len(sample_list)


def snapshot(con, clock, sample_list, run_id=None):
    """insert_samples + commit. Must be called with no other open transaction."""
    n = insert_samples(con, clock, sample_list, run_id)
    con.commit()
    return n


def run_end_samples(con, job, duration_seconds, backlog_remaining):
    """Exported at the end of every run (BEH-OBS-06): the three zero-tripwires plus the run's duration and remaining backlog."""
    out = [_s(n, "counter", {}, v) for n, v in sorted(tripwires(con).items())]
    out.append(_s("run_backlog_remaining", "gauge", {"job": job}, backlog_remaining))
    out.append(_s("run_duration_seconds", "gauge", {"job": job}, duration_seconds))
    return out


def value_of(sample_list, name, **labels):
    """Sum of the numeric samples called `name` whose labels contain `labels` (test / report helper)."""
    return sum(int(s["value"]) for s in sample_list if s["name"] == name and all(s["labels"].get(k) == v for k, v in labels.items())
               and s["value"].lstrip("-").isdigit())
