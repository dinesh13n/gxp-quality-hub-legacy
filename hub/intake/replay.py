"""Replay-safety check (gate G2, AC-INT-04, AC-NFR-11, rollback rehearsal TST-CO-09): re-deliver the same items and prove nothing changed.

`replay_safety` ingests `deliveries` again as a NORMAL run (every delivery is stored again) and compares the queue snapshot (sizes, ages,
per-reason counts, totals) before and after: it must be identical, every re-delivery must be a NOOP_DUPLICATE with counts_toward_totals = 0,
and the raw count must grow by exactly the number of re-deliveries (nothing silently dropped, nothing overwritten).
"""


def replay_safety(svc, source, deliveries, run_id, as_of, correlation_id="replay-safety", targets=None):
    before, c0 = svc.queue_snapshot(as_of), svc.counts()
    rep = svc.ingest(source, deliveries, run_id, correlation_id, targets=targets)
    after, c1 = svc.queue_snapshot(as_of), svc.counts()
    n = len(deliveries)
    checks = {
        "queues_totals_identical": before == after,
        "all_noop_duplicate": rep["outcomes"] == ({"NOOP_DUPLICATE": n} if n else {}),
        "raw_grew_by_n": c1["raw"] - c0["raw"] == n,
        "noop_counted_out": c1["noop_duplicate"] - c0["noop_duplicate"] == n,
        "no_conflicts": rep["revised_conflict"] == 0,
    }
    return {"ok": all(checks.values()), "checks": checks, "redelivered": n, "report": rep}
