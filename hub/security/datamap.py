"""Field map of the hub store (Stage 24, DW-19 'field map', RTD-83, PIA input). Synthetic, unvalidated.

classify(table, column) -> {"class": C0..C3, "tags": [...]} for every column of every hub table. Classes are the PROPOSED C0..C3 of
docs/11-data-context/metadata-model.md M2 (Assumption A-11-02, still open): C1 internal, C2 confidential, C3 restricted. A column inherits its table's
class; a tag can only RAISE it:
  secret       credential material or a digest of a credential (password hash and salt, session / service-token digests)      -> C3
  staff_id     a pseudonymous user / actor identifier (a personal-data analogue in a real deployment, A-11-10)                -> at least C2
  free_text    human- or partner-written text that may carry anything and is Untrusted (escaped on output, never interpreted)  -> at least C2
  finance      a money amount as text (C2, docs/11 M2)
  content      the stored object itself (raw delivery bytes, search corpus body)                                               -> table class
An unknown table or a column that no rule covers raises KeyError, so tests/hub/test_tst_hub_stg24_fields.py fails the build when a column is added
without a classification. The map says NOTHING about legal status: the estate is synthetic (DU-01); who the real data subjects would be, the applicable
privacy regime and the retention period are Unknown (U-11-17, OD-30).
"""
CLASS_ORDER = ("C0", "C1", "C2", "C3")

# table -> default class. audit_log, principal, session, login_attempt, service_token(+revocation): identity / credential / access evidence = C3
# (docs/11 M2: "the audit trail"; hub.r2.protection.FIELD_CLASSES['audit'] = C3). search_doc is by access_level (C2 or C3): C3 is the safe default here.
TABLE_CLASS = {
    "audit_log": "C3", "principal": "C3", "principal_role": "C3", "session": "C3", "login_attempt": "C3", "service_token": "C3",
    "service_token_revocation": "C3", "search_doc": "C3",
    "decision_events": "C2", "evidence_record": "C2", "case_state": "C2", "crosswalk_link": "C2", "crosswalk_link_event": "C2",
    "decision_idempotency": "C2", "raw_intake": "C2", "intake_outcome": "C2", "intake_item_attr": "C2", "intake_run_event": "C2", "rule_trace": "C2",
    "flag_action": "C2", "review_draft": "C2", "consistency_finding": "C2",
    "policy_object": "C1", "policy_events": "C1", "rule_set": "C1", "rule_row": "C1", "active_ruleset": "C1", "run_event": "C1", "run_lock": "C1",
    "metric_definition": "C1", "metric_value": "C1", "obs_metric": "C1", "release_record": "C1", "release_gate_result": "C1",
    "deviation_register": "C1", "coexistence_inventory": "C1", "search_corpus_load": "C1",
    "schema_migrations": "C1", "hardening_schema_migrations": "C1", "decision_schema_migrations": "C1", "intake_schema_migrations": "C1", "policy_schema_migrations": "C1",
    "runs_schema_migrations": "C1", "web_schema_migrations": "C1", "search_schema_migrations": "C1",
}
# tag -> (columns, minimum class). A column is matched by NAME in any table, or as "table.column" for one table only.
TAGS = {
    "secret": ({"pw_hash", "pw_salt", "token_sha256"}, "C3"),
    "staff_id": ({"actor", "created_by", "recorded_by", "granted_by", "resolved_by", "attached_by", "revoked_by", "triggered_by", "creator", "owner",
                  "principal_id", "holder_check_ref", "authority_ref"}, "C2"),
    "free_text": ({"reason", "reason_detail", "resolution_reason", "notes", "body", "payload", "replacement", "documentation", "detail", "description",
                   "justification", "details", "note", "fields", "inputs", "legacy_value", "new_value", "old_value", "service_token.label"}, "C2"),
    "finance": ({"amount_text"}, "C2"),
    "content": ({"raw_bytes", "folded"}, None),
}
# identifiers, hashes, times, counters, enumerations, versions, references and labels - reviewed one by one in Stage 24 (docs/24-security-privacy/privacy-impact-assessment.md)
NEUTRAL = {
    "access_level", "access_level_given", "acted_at", "action", "action_id", "activated_event", "actor_kind", "adapter_version",
    "affects_state", "all_reasons", "applied_at", "approval_ref", "archive_items", "attached_at", "attempt_seq", "audit_seq", "authoritative",
    "basis", "body_hash", "case_id", "category", "closure_check", "code_version", "collected_at", "computed_at", "conditions", "conflicts_with",
    "content_hash", "contract_check", "contract_missing", "correlation_id", "counts_toward_totals", "created_at", "creator_kind", "cutoff_ref",
    "cycle", "data_origin", "decided_at", "definition_tag", "denominator", "detected_at", "dev_id", "doc_id", "documents", "draft_id",
    "duplicate_of", "effective_at", "effective_from", "effective_to", "errors", "ev_id", "event", "event_id", "event_type", "evidence_path",
    "evidence_refs", "exception", "exclusions", "expires_at", "finding_id", "flag_id", "flag_kind", "from_id", "from_state", "from_type", "fts",
    "function", "functions", "gate", "golden_ref", "granted_at", "hash", "heartbeat_at", "idem_key", "identity_key", "inputs_hash",
    "involves_definition", "is_default", "item_id", "job", "key_used", "kind", "label", "labels", "last_seen_at", "last_seq", "link_id",
    "load_id", "locale", "matched_link", "metric_id", "metric_version", "mode_at_write", "n", "name", "notes_trust", "null_reason",
    "object_ref", "object_refs", "occurred_at", "ocr_confidence", "ordinal", "origin", "outcome", "outcome_seq", "params", "partial", "partner",
    "policy_id", "policy_ref", "policy_status", "policy_version", "prev_hash", "primary_reason", "principal_kind", "pw_algo", "pw_iterations",
    "queue", "raw_id", "read_only", "reauth_at", "receipt_time", "record_kind", "recorded_at", "ref_id", "reference", "release_id",
    "resolution", "result", "revoked_at", "role", "row_id", "rowid", "rule_ref", "ruleset_id", "ruleset_ref", "run_id", "run_seq", "sample_id",
    "schema_rev", "seq", "sha256", "source", "source_hash", "source_key", "source_quality_flag", "source_ref", "source_state", "source_subtype",
    "source_ts", "started_at", "state", "status", "template_id", "template_version", "to_id", "to_state", "to_type", "trace_id", "trigger",
    "updated_from_event", "value", "value_id", "version", "window", "window_end", "window_start",
}
def classify(table, column):
    if table not in TABLE_CLASS:
        raise KeyError("table %r has no class in hub.security.datamap.TABLE_CLASS" % table)
    cls = TABLE_CLASS[table]
    tags = []
    for tag, (cols, floor) in sorted(TAGS.items()):
        if column in cols or (table + "." + column) in cols:
            tags.append(tag)
            if floor and CLASS_ORDER.index(floor) > CLASS_ORDER.index(cls):
                cls = floor
    if not tags and column not in NEUTRAL:
        raise KeyError("column %s.%s has no rule in hub.security.datamap (add it to TAGS or NEUTRAL after review)" % (table, column))
    return {"class": cls, "tags": tags}
