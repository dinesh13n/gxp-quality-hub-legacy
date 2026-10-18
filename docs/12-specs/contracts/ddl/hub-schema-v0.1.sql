-- hub-schema-v0.1.sql  (Stage 12 specification artifact; NOT executed against repo data)
-- Logical DDL for the NEW hub store (hub.sqlite3, ADR-004 option B). SQLite >= 3.25 (window functions not required).
-- Status: DRAFT. Source of truth for semantics: docs/12-specs/schema-specifications.md.
PRAGMA foreign_keys = ON;

CREATE TABLE decision_events(
  event_id        TEXT PRIMARY KEY,
  case_id         TEXT NOT NULL,
  seq             INTEGER NOT NULL CHECK(seq >= 1),
  event_type      TEXT NOT NULL CHECK(event_type IN (
    'CASE_CREATED','CASE_IMPORTED','STATUS_CHANGE','REOPEN','EVIDENCE_ATTACHED',
    'FACT_RECEIVED','FACT_OPS_CLOSED','FACT_EVIDENCE_COMPLETE','CLOSE_EXCEPTION',
    'DISPOSITION_RECORDED','DISPOSITION_REFERENCED','QA_RELEASE_RECORDED','ESIGNATURE_RECORDED',
    'OVERRIDE_RECORDED','CORRECTION')),
  from_state      TEXT,
  to_state        TEXT,
  affects_state   INTEGER NOT NULL CHECK(affects_state IN (0,1)),
  actor           TEXT NOT NULL,
  actor_kind      TEXT NOT NULL CHECK(actor_kind IN ('human','rule','system')),
  occurred_at     TEXT NOT NULL,
  recorded_at     TEXT NOT NULL,
  basis           TEXT NOT NULL CHECK(length(basis) <= 2000),
  evidence_refs   TEXT NOT NULL DEFAULT '[]',
  cycle           INTEGER NOT NULL DEFAULT 1 CHECK(cycle >= 1),
  exception       INTEGER NOT NULL DEFAULT 0 CHECK(exception IN (0,1)),
  closure_check   TEXT CHECK(closure_check IN ('passed','exception','not_configured')),
  mode_at_write   TEXT CHECK(mode_at_write IN ('event','external_ref')),
  policy_version  TEXT,
  holder_check_ref TEXT,
  payload         TEXT NOT NULL DEFAULT '{}',
  prev_hash       TEXT NOT NULL,
  hash            TEXT NOT NULL,
  UNIQUE(case_id, seq),
  CHECK(affects_state = 0 OR to_state IS NOT NULL)
);
CREATE TRIGGER decision_events_no_update BEFORE UPDATE ON decision_events
BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER decision_events_no_delete BEFORE DELETE ON decision_events
BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER decision_events_zone_h BEFORE INSERT ON decision_events
WHEN NEW.event_type IN ('CLOSE_EXCEPTION','DISPOSITION_RECORDED','DISPOSITION_REFERENCED','QA_RELEASE_RECORDED','ESIGNATURE_RECORDED')
 AND (NEW.actor_kind <> 'human' OR NEW.holder_check_ref IS NULL)
BEGIN SELECT RAISE(ABORT,'E-GATE-NOT-AUTHORISED'); END;

CREATE TABLE evidence_record(
  ev_id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('document','intake_item','crosswalk_object','external_ref')),
  source TEXT NOT NULL, source_ref TEXT NOT NULL, source_hash TEXT, access_level TEXT NOT NULL DEFAULT 'restricted',
  attached_by TEXT NOT NULL, attached_at TEXT NOT NULL);

CREATE TABLE case_state(          -- projection, rebuildable from decision_events
  case_id TEXT PRIMARY KEY, state TEXT NOT NULL, cycle INTEGER NOT NULL, last_seq INTEGER NOT NULL, updated_from_event TEXT NOT NULL);

CREATE TABLE policy_object(
  policy_id TEXT NOT NULL, version INTEGER NOT NULL CHECK(version >= 1),
  kind TEXT NOT NULL CHECK(kind IN ('DEFINITION','CLOCK','CLOSURE','CONSISTENCY','CUTOFF')),
  name TEXT NOT NULL, definition_tag TEXT, body TEXT NOT NULL, owner TEXT NOT NULL DEFAULT 'unassigned',
  effective_from TEXT, effective_to TEXT,
  status TEXT NOT NULL CHECK(status IN ('candidate','adopted','accepted-open')),
  created_by TEXT NOT NULL, created_at TEXT NOT NULL,
  PRIMARY KEY(policy_id, version));
CREATE TRIGGER policy_object_no_update BEFORE UPDATE ON policy_object BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER policy_object_no_delete BEFORE DELETE ON policy_object BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE policy_events(
  event_id TEXT PRIMARY KEY, policy_ref TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN ('POLICY_VERSION_CREATED','POLICY_ADOPTED','POLICY_ACCEPTED_OPEN','POLICY_WITHDRAWN','RULE_ROW_CHANGED','RULESET_ACTIVATED','RULESET_DEACTIVATED','EXCEPTION_RULE_ACCEPTED','CLOSURE_ACTIVATED','DISPOSITION_MODE_CHANGED','SCHEDULE_CHANGED','CONTRACT_BINDING_CHANGED')),
  actor TEXT NOT NULL, occurred_at TEXT NOT NULL, old_value TEXT, new_value TEXT,
  authority_ref TEXT NOT NULL CHECK(length(authority_ref) > 0), holder_check_ref TEXT);
CREATE TRIGGER policy_events_no_update BEFORE UPDATE ON policy_events BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER policy_events_no_delete BEFORE DELETE ON policy_events BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE rule_set(
  ruleset_id TEXT NOT NULL, version INTEGER NOT NULL, name TEXT NOT NULL,
  origin TEXT NOT NULL CHECK(origin IN ('as-found','custom')), read_only INTEGER NOT NULL CHECK(read_only IN (0,1)),
  functions TEXT NOT NULL, PRIMARY KEY(ruleset_id, version));
CREATE TABLE rule_row(
  ruleset_id TEXT NOT NULL, version INTEGER NOT NULL, row_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
  conditions TEXT NOT NULL, outcome TEXT NOT NULL, effective_from TEXT, effective_to TEXT, owner TEXT, is_default INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(ruleset_id, version, row_id),
  FOREIGN KEY(ruleset_id, version) REFERENCES rule_set(ruleset_id, version));
CREATE TABLE active_ruleset(function TEXT PRIMARY KEY, ruleset_id TEXT NOT NULL, version INTEGER NOT NULL, activated_event TEXT NOT NULL);

CREATE TABLE raw_intake(
  raw_id TEXT PRIMARY KEY, source TEXT NOT NULL, source_key TEXT, partner TEXT, schema_rev TEXT,
  receipt_time TEXT NOT NULL, identity_key TEXT NOT NULL, content_hash TEXT NOT NULL,
  duplicate_of TEXT, raw_bytes BLOB NOT NULL, run_id TEXT NOT NULL, adapter_version TEXT NOT NULL);
CREATE INDEX raw_intake_identity ON raw_intake(identity_key);
CREATE TRIGGER raw_intake_no_update BEFORE UPDATE ON raw_intake BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER raw_intake_no_delete BEFORE DELETE ON raw_intake BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;

CREATE TABLE intake_outcome(
  raw_id TEXT NOT NULL REFERENCES raw_intake(raw_id), outcome_seq INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('VALIDATED','VALIDATED_WITH_FLAGS','EXCEPTION','QUARANTINED','NOOP_DUPLICATE','CONFLICT_RESOLVED')),
  primary_reason TEXT, all_reasons TEXT NOT NULL DEFAULT '[]', queue TEXT CHECK(queue IN ('quarantine_invalid','revision_review','unmatched','ambiguous_match','flagged_value')),
  contract_check TEXT CHECK(contract_check IN ('pass','fail','not_bound')), counts_toward_totals INTEGER NOT NULL CHECK(counts_toward_totals IN (0,1)),
  matched_link TEXT, resolution TEXT CHECK(resolution IN ('accept_revision','keep_original','reject_both')), resolution_reason TEXT, resolved_by TEXT,
  run_id TEXT NOT NULL, decided_at TEXT NOT NULL,
  PRIMARY KEY(raw_id, outcome_seq),
  CHECK(outcome <> 'CONFLICT_RESOLVED' OR (resolution IS NOT NULL AND resolution_reason IS NOT NULL AND length(resolution_reason) > 0 AND resolved_by IS NOT NULL)));
CREATE TRIGGER intake_outcome_no_update BEFORE UPDATE ON intake_outcome BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER intake_outcome_no_delete BEFORE DELETE ON intake_outcome BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE VIEW intake_current AS
  SELECT o.* FROM intake_outcome o
  WHERE o.outcome_seq = (SELECT MAX(outcome_seq) FROM intake_outcome x WHERE x.raw_id = o.raw_id)
    AND o.outcome <> 'NOOP_DUPLICATE';

CREATE TABLE crosswalk_link(
  link_id TEXT PRIMARY KEY, from_type TEXT NOT NULL, from_id TEXT NOT NULL, to_type TEXT NOT NULL, to_id TEXT NOT NULL,
  key_used TEXT NOT NULL, creator_kind TEXT NOT NULL CHECK(creator_kind IN ('rule','human')), creator TEXT NOT NULL,
  created_at TEXT NOT NULL, reason TEXT, run_id TEXT,
  CHECK(creator_kind = 'rule' OR (reason IS NOT NULL AND length(reason) > 0)),
  CHECK(NOT (from_type = to_type AND from_id = to_id)));
CREATE TABLE crosswalk_link_event(
  event_id TEXT PRIMARY KEY, link_id TEXT NOT NULL REFERENCES crosswalk_link(link_id),
  event_type TEXT NOT NULL CHECK(event_type IN ('LINK_CREATED_RULE','LINK_CREATED_HUMAN','LINK_RETRACTED')),
  actor TEXT NOT NULL, occurred_at TEXT NOT NULL, reason TEXT);
CREATE TRIGGER crosswalk_link_no_update BEFORE UPDATE ON crosswalk_link BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER crosswalk_link_no_delete BEFORE DELETE ON crosswalk_link BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE run_event(
  run_id TEXT NOT NULL, run_seq INTEGER NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN ('RUN_STARTED','RUN_CHECKPOINT','RUN_FINISHED','RUN_FAILED','RUN_ABANDONED','RUN_REFUSED')),
  job TEXT NOT NULL, trigger TEXT NOT NULL CHECK(trigger IN ('manual','scheduled')), triggered_by TEXT NOT NULL,
  occurred_at TEXT NOT NULL, body TEXT NOT NULL DEFAULT '{}', PRIMARY KEY(run_id, run_seq));
CREATE TRIGGER run_event_no_update BEFORE UPDATE ON run_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER run_event_no_delete BEFORE DELETE ON run_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE metric_definition(
  metric_id TEXT NOT NULL, version INTEGER NOT NULL, name TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('time','count','money','rate','age')),
  definition_tag TEXT, involves_definition INTEGER NOT NULL CHECK(involves_definition IN (0,1)),
  window TEXT NOT NULL, denominator TEXT NOT NULL, exclusions TEXT NOT NULL, cutoff_ref TEXT,
  basis TEXT NOT NULL CHECK(basis IN ('event_derived','modelled')), documentation TEXT NOT NULL,
  PRIMARY KEY(metric_id, version),
  CHECK(involves_definition = 0 OR definition_tag IS NOT NULL));
CREATE TABLE metric_value(
  value_id TEXT PRIMARY KEY, metric_id TEXT NOT NULL, metric_version INTEGER NOT NULL, definition_tag TEXT, policy_version TEXT,
  value TEXT, n INTEGER NOT NULL, partial INTEGER NOT NULL DEFAULT 0, window_start TEXT, window_end TEXT,
  denominator TEXT NOT NULL, exclusions TEXT NOT NULL, basis TEXT NOT NULL, data_origin TEXT NOT NULL CHECK(data_origin IN ('synthetic','production')),
  label TEXT NOT NULL, inputs_hash TEXT NOT NULL, code_version TEXT NOT NULL, computed_at TEXT NOT NULL,
  CHECK(data_origin <> 'synthetic' OR label = 'synthetic, unvalidated'));

CREATE TABLE audit_log(
  audit_seq INTEGER PRIMARY KEY, occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
  actor_kind TEXT NOT NULL CHECK(actor_kind IN ('human','service','rule','system')),
  action TEXT NOT NULL, object_ref TEXT, outcome TEXT NOT NULL CHECK(outcome IN ('success','denied','error')),
  reason TEXT, correlation_id TEXT NOT NULL, details TEXT NOT NULL DEFAULT '{}',
  prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TRIGGER audit_log_no_update BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER audit_log_no_delete BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
