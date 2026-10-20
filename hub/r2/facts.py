"""Read-only entity facts from the legacy snapshot (AD-01: pinned sha256, mode=ro&immutable=1 copy in a guarded run directory; the working-tree
data/ is never opened). Loaded once into memory so a long-running server holds no legacy handle. Used by the joined view (fields) and the
consistency check (per-vocabulary values, never mapped - BEH-ID-08)."""
from hub.adapters import legacy_sqlite
from hub.r2 import divergence

_Q = {
    "case": "SELECT id, account_id, site, amount FROM cases",
    "batch": "SELECT batch_id, qa_status, batch_site FROM batch_records",
    "deviation": "SELECT deviation_id, status FROM deviations",
    "capa": "SELECT capa_id, state, action_owner FROM capa_actions",
}
_K = {"case": ("case_id", "account_id", "site", "amount"), "batch": ("batch_id", "qa_status", "batch_site"),
      "deviation": ("deviation_id", "status"), "capa": ("capa_id", "state", "action_owner")}


def load(legacy_root, run_dir):
    """-> (facts(type, id) -> dict | None, case_inputs list)."""
    data = {}
    with legacy_sqlite.open_snapshot(legacy_root, "legacy.sqlite3", run_dir, pinned=True) as h:
        for t, q in _Q.items():
            data[t] = dict((r[0], dict(zip(_K[t], r))) for r in h.execute(q))
        cases = divergence.legacy_case_inputs(h)

    def facts(t, i):
        rec = data.get(t, {}).get(i)
        return None if rec is None else dict(rec)
    return facts, cases
