"""DM-1: backfill of the shipped legacy cases (OD-09: 125 cases, seed 4100) into the decision record (INC-05, TB-14).

Reads ONLY the hash-gated read-only snapshot adapter (AD-01, `mode=ro&immutable=1`, pinned sha256): the working-tree
`data/` is never opened (the sandbox guard refuses a source inside the repository or the backup). For every case:
  seq 1  CASE_IMPORTED  from_state null, to_state = snapshot status, basis "legacy snapshot", actor legacy-backfill (system)
  seq 2  FACT_RECEIVED  occurred_at = cases.created_at (proxy, Assumption A-12-F01-1)
Both events carry occurred_at = cases.created_at and recorded_at = the import time; payload has source_db_sha256 and the legacy
version. No history is invented: the legacy `events` rows are not imported, and the 8 REOPENED cases (no reopen event in the
legacy data) carry marker LEGACY_UNEVIDENCED_REOPEN. One transaction, one audit record: all cases or none (rollback L1). The
run is idempotent on (source_db_sha256, case_id): a second run writes only a NOOP audit record. Gate G4: imported count equals
the source count and `verify_projection` reports 0 mismatches, else E-DEC-BACKFILL-MISMATCH and nothing is written.
"""
import collections
import json

from hub.adapters import legacy_sqlite
from hub.decision import settings as dsettings
from hub.decision.errors import BackfillMismatch
from hub.decision.service import LEGACY_REOPEN_MARKER, norm_ts
from hub.security import audit

ACTOR = "legacy-backfill"
BASIS = "legacy snapshot"
EXPECTED_CASES = 125  # OD-09 baseline (seed 4100)
PRIORITY_RULESET = "as-found-python@1"


def read_cases(handle):
    rows = handle.execute("SELECT id, status, created_at, version FROM cases ORDER BY id")
    return [{"id": r[0], "status": r[1], "created_at": r[2], "version": r[3]} for r in rows]


def priority_distribution(handle, policy_service):
    """CT-02: priority of every case through the INC-04 as-found Python rule set (explicit ref, still inactive)."""
    rows = handle.execute("SELECT status, severity, amount FROM cases ORDER BY id")
    res = policy_service.evaluate_many("PRIORITY", [{"status": r[0], "severity": r[1], "amount": r[2]} for r in rows], PRIORITY_RULESET)
    return dict(sorted(collections.Counter(r["outcome"] for r in res).items()))


def run(svc, legacy_root, run_dir, correlation_id="backfill", expected=EXPECTED_CASES, policy_service=None):
    """Backfill through DecisionService `svc`. Returns the report dict."""
    handle = legacy_sqlite.open_snapshot(legacy_root, "legacy.sqlite3", run_dir, pinned=True)
    try:
        cases = read_cases(handle)
        sha = handle.provenance["source_sha256"]
        priority = None
        if policy_service is not None:
            priority = priority_distribution(handle, policy_service)
    finally:
        handle.close()
    for c in cases:
        if c["status"] not in dsettings.VOCAB:
            raise BackfillMismatch({"reason": "status outside the case_status vocabulary", "case_id": c["id"]})
    done = {}
    for (cid, payload) in svc.con.execute("SELECT case_id, payload FROM decision_events WHERE event_type = 'CASE_IMPORTED'"):
        done[cid] = json.loads(payload).get("source_db_sha256")
    foreign = sorted(c for c, h in done.items() if h != sha)
    if foreign:
        raise BackfillMismatch({"reason": "cases already imported from a different snapshot", "case_ids": foreign[:10]})
    todo = [c for c in cases if c["id"] not in done]
    now = svc.clock()
    written = 0
    with audit.change(svc.con, svc.clock, anchor=svc.anchor, actor=ACTOR, actor_kind="system", action="BACKFILL_RUN",
                      outcome="success", correlation_id=correlation_id, object_ref="backfill:legacy.sqlite3", details={}) as ctx:
        for c in todo:
            occ = norm_ts(c["created_at"], "created_at")
            payload = {"source": "legacy.sqlite3", "source_db_sha256": sha, "legacy_version": c["version"],
                       "legacy_status": c["status"]}
            if c["status"] == dsettings.REOPENED_LABEL:
                payload["marker"] = LEGACY_REOPEN_MARKER
            svc._insert_event(c["id"], "CASE_IMPORTED", ACTOR, "system", occ, now, BASIS, to_state=c["status"], from_state=None,
                              affects_state=True, payload=payload)
            svc._insert_event(c["id"], "FACT_RECEIVED", ACTOR, "system", occ, now, "", payload={"proxy": "cases.created_at"})
            written += 2
        proj = svc.verify_projection()
        total = svc.con.execute("SELECT count(*) FROM decision_events WHERE event_type = 'CASE_IMPORTED'").fetchone()[0]
        if proj["mismatches"] != 0 or total != len(cases) or (expected is not None and total != expected):
            raise BackfillMismatch({"imported_total": total, "source_cases": len(cases), "expected": expected, "projection": proj})
        ctx.fields["details"] = {"source_db_sha256": sha, "cases_in_source": len(cases), "imported_now": len(todo),
                                 "already_imported": len(cases) - len(todo), "events_written": written,
                                 "projection_mismatches": proj["mismatches"]}
    chain = svc.verify_chain()
    states = collections.Counter(r[0] for r in svc.con.execute("SELECT state FROM case_state"))
    return {"source_db_sha256": sha, "cases_in_source": len(cases), "imported_now": len(todo),
            "already_imported": len(cases) - len(todo), "events_written": written, "state_counts": dict(sorted(states.items())),
            "marked_legacy_reopen": svc.reopen_invariant_internal()["marked_count"], "projection": proj, "chain": chain,
            "priority_distribution": priority, "priority_ruleset": PRIORITY_RULESET if priority is not None else None}
