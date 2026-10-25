"""Table disposition register (Stage 24, DW-19 'RETAINED_TABLES gap'; RF-02 of docs/25-governance/evidence-retention-policy.md).

Every table the hub creates (M000 .. M007 and the five per-component ledgers) has exactly one disposition here:

  retained    insert-only evidence / record / ledger: a BEFORE DELETE trigger aborts (E-SEC-RETAINED), product code has no delete or drop statement for it, and
              hub.security.scan.RETAINED_TABLES lists it (so the deletion-path grep and the trigger check cover it);
  mutable     rows are legitimately removed or rewritten by product code - the reviewed places are named in `reason` and in REVIEWED_DELETE_SITES (so a new place is a finding);
  derived     rebuildable from other tables; no insert-only trigger by design (rollback = rebuild / drop-index).

`RETAINED` is the single source for scan.RETAINED_TABLES. tests/hub/test_tst_hub_stg24_tables.py proves the register equals the live store: every table
in a fully migrated store (M001..M007) has a disposition, every `retained` table has an aborting BEFORE DELETE trigger, no other table has one, and the
reviewed delete sites are the only delete statements in hub/. A new table therefore fails the build until it is classified.
Assumption (A-S24-TBL-1, Engagement lead Dinesh Naik): this disposition is a proposal; the retention PERIOD stays hold-all (OD-30 / OD-S12-09).
"""

RETAINED, MUTABLE, DERIVED = "retained", "mutable", "derived"

TABLES = {
    # M000 / M001 (hub.store)
    "schema_migrations": (RETAINED, "core migration ledger: insert-only since the Stage 27 hardening migration H001 (hub/store/hardening/); drift is also "
                                    "detected by sha256 comparison (hub.store.migrate.check); closes RS-12 for this table"),
    "hardening_schema_migrations": (RETAINED, "H001 ledger (hub/store/hardening.py)"),
    "coexistence_inventory": (RETAINED, "inventory of legacy items (M000), update and delete aborted"),
    "deviation_register": (RETAINED, "DV register (M000/M001), delete aborted; status may move forward by a recorded decision"),
    "audit_log": (RETAINED, "hash-chained audit trail"),
    "principal": (RETAINED, "users and service principals; no deletion, status change only"),
    "principal_role": (RETAINED, "role grants"),
    "session": (RETAINED, "login sessions; revocation sets revoked_at, rows are never deleted"),
    "login_attempt": (RETAINED, "login attempts (lockout evidence)"),
    "release_record": (RETAINED, "release status; no downgrade"),
    "release_gate_result": (RETAINED, "G1..G10 results"),
    # M002 policy
    "policy_object": (RETAINED, "policy objects"), "policy_events": (RETAINED, "policy lifecycle events"),
    "rule_set": (RETAINED, "versioned rule sets"), "rule_row": (RETAINED, "rule rows"),
    "active_ruleset": (MUTABLE, "the pointer to the active rule set: hub/policy/service.py deactivate / replace (two delete statements, both audited by "
                                "a policy event); history is in policy_events"),
    "policy_schema_migrations": (RETAINED, "M002 ledger"),
    # M003 decision / crosswalk
    "decision_events": (RETAINED, "case decision events (hash chain per case)"), "evidence_record": (RETAINED, "evidence records"),
    "case_state": (DERIVED, "projection of decision_events; hub/decision/service.py rebuilds it (one delete statement); verify-projection "
                            "compares it with the events"),
    "crosswalk_link": (RETAINED, "crosswalk links"), "crosswalk_link_event": (RETAINED, "link events"),
    "decision_idempotency": (RETAINED, "idempotency keys of decision writes"), "decision_schema_migrations": (RETAINED, "M003 ledger"),
    # M004 intake
    "raw_intake": (RETAINED, "raw deliveries, byte-exact"), "intake_outcome": (RETAINED, "intake outcomes"),
    "intake_item_attr": (RETAINED, "item attributes"), "intake_run_event": (RETAINED, "intake run events"),
    "intake_schema_migrations": (RETAINED, "M004 ledger"),
    # M005 runs / metrics
    "run_event": (RETAINED, "run events"), "run_lock": (MUTABLE, "single-flight lock: hub/runs/service.py releases it (three delete statements); "
                                                              "run history is in run_event"),
    "metric_definition": (RETAINED, "metric definitions"), "metric_value": (RETAINED, "computed metric values"),
    "obs_metric": (RETAINED, "observability samples"), "runs_schema_migrations": (RETAINED, "M005 ledger"),
    # M006 web / gate / review
    "service_token": (RETAINED, "service token digests"), "service_token_revocation": (RETAINED, "revocations"),
    "rule_trace": (RETAINED, "rule evaluation traces"), "flag_action": (RETAINED, "reviewer flag actions"),
    "web_schema_migrations": (RETAINED, "M006 ledger"),
    # M007 search / R2
    "search_doc": (DERIVED, "derived corpus: hub/search/corpus.py clears and reloads it (two delete statements); `python -m hub.search drop-index` is the "
                            "rollback; provenance is search_corpus_load"),
    "search_corpus_load": (RETAINED, "corpus load / drop provenance"), "consistency_finding": (RETAINED, "consistency findings"),
    "review_draft": (RETAINED, "template drafts"), "search_schema_migrations": (RETAINED, "M007 ledger"),
}
# SQLite internals and the derived FTS5 objects (created only when the runtime offers FTS5, dropped by drop-index) are outside the register.
IGNORED_PREFIXES = ("sqlite_", "search_fts", "search_tri")
# Reviewed product-code delete / drop-table sites: (file relative to hub/, table) -> expected number of statements.
REVIEWED_DELETE_SITES = {
    ("decision/service.py", "case_state"): 1,
    ("policy/service.py", "active_ruleset"): 2,
    ("runs/service.py", "run_lock"): 3,
    ("search/corpus.py", "search_doc"): 2,
}
RETAINED_TABLES = tuple(sorted(t for t, (d, _) in TABLES.items() if d == RETAINED))


def disposition(table):
    return TABLES[table][0] if table in TABLES else None


def ignored(name):
    return name.startswith(IGNORED_PREFIXES)
