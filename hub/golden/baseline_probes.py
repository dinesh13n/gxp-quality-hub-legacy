"""Reference computations over the read-only baseline snapshots (FX-BASE125, OD-09: 125 cases, seed 4100).

These are the only "new side" values INC-02 can compute itself; every other probe's new side is the
spec-declared target (F10-2) until the owning module is built in a later increment. Fixed SQL, executed
only through the AD-01/AD-02 read-only adapters. Pure, deterministic (ORDER BY everywhere).
"""

QUERIES = {
    # DV-01 target: month_end_total sums each case once (no join fan-out)
    "month_end_total": ("legacy.sqlite3", "SELECT round(sum(amount), 2) FROM cases", "scalar"),
    # DV-08 target: per-entity evaluation -> distinct entities among the first 500 evaluated
    "distinct_entities_first_500": ("enterprise_legacy.sqlite3",
                                    "SELECT count(DISTINCT object_id) FROM (SELECT object_id FROM operational_objects "
                                    "ORDER BY object_id LIMIT 500)", "scalar"),
    # identity probe (CT-10): active policies per region
    "active_policies_per_region": ("enterprise_legacy.sqlite3",
                                   "SELECT region, count(*) FROM policy_register WHERE active = 1 GROUP BY 1 ORDER BY 1",
                                   "rows"),
}


def run(name, handles):
    store, sql, shape = QUERIES[name]
    rows = handles[store].execute(sql)
    if shape == "scalar":
        return rows[0][0]
    return [list(r) for r in rows]


def stores_needed(names):
    return sorted(set(QUERIES[n][0] for n in names))
