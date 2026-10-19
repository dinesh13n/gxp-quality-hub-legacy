-- M004 (Stage 15 INC-06) - docs/14-transformation/schema-migration-plan.md row M004; backlog TB-15.
-- Applied ONLY by hub.intake.schema (backup-before-migrate), recorded in intake_schema_migrations (NOT in schema_migrations:
-- same constraint as INC-04/05, see docs/15-modernization/inc06-design-notes.md D-02). Forward-only, sha256-checked.
--
-- raw_intake, intake_outcome, intake_current: from docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (SCH-RAW-INTAKE, SCH-INTAKE-OUTCOME).
-- DDL ADDENDA (the Stage 12 file is not edited in place, HAR-13):
--   intake_outcome.contract_missing  keys that failed the declared contract (BEH-INT-06: result stored on the outcome)
--   intake_outcome.conflicts_with    raw_id of the first earlier version with the same identity_key (BEH-INT-04: linked)
--   intake_outcome.reason_detail     per-reason details (field names, match candidates), JSON object
--   raw_intake_source_key index      backfill idempotency lookup (BEH-INT-10)
--   intake_item_attr                 source_* attributes and Untrusted text (BEH-INT-09); insert-only
--   intake_run_event                 run record + checkpoint storage (AD-04: offsets are hub-owned); insert-only; a subset of the
--                                    DDL run_event table, which INC-07 (F06) owns - reconcile there
-- Synthetic, unvalidated. Rollback: restore the pre-migration backup written by hub.intake.schema.

CREATE TABLE raw_intake(
  raw_id TEXT PRIMARY KEY, source TEXT NOT NULL, source_key TEXT, partner TEXT, schema_rev TEXT,
  receipt_time TEXT NOT NULL, identity_key TEXT NOT NULL, content_hash TEXT NOT NULL,
  duplicate_of TEXT, raw_bytes BLOB NOT NULL, run_id TEXT NOT NULL, adapter_version TEXT NOT NULL);
CREATE INDEX raw_intake_identity ON raw_intake(identity_key);
CREATE INDEX raw_intake_source_key ON raw_intake(source, source_key);
CREATE TRIGGER raw_intake_no_update BEFORE UPDATE ON raw_intake BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER raw_intake_no_delete BEFORE DELETE ON raw_intake BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;

CREATE TABLE intake_outcome(
  raw_id TEXT NOT NULL REFERENCES raw_intake(raw_id), outcome_seq INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('VALIDATED','VALIDATED_WITH_FLAGS','EXCEPTION','QUARANTINED','NOOP_DUPLICATE','CONFLICT_RESOLVED')),
  primary_reason TEXT, all_reasons TEXT NOT NULL DEFAULT '[]', queue TEXT CHECK(queue IN ('quarantine_invalid','revision_review','unmatched','ambiguous_match','flagged_value')),
  contract_check TEXT CHECK(contract_check IN ('pass','fail','not_bound')), counts_toward_totals INTEGER NOT NULL CHECK(counts_toward_totals IN (0,1)),
  matched_link TEXT, resolution TEXT CHECK(resolution IN ('accept_revision','keep_original','reject_both')), resolution_reason TEXT, resolved_by TEXT,
  run_id TEXT NOT NULL, decided_at TEXT NOT NULL,
  contract_missing TEXT NOT NULL DEFAULT '[]', conflicts_with TEXT REFERENCES raw_intake(raw_id), reason_detail TEXT NOT NULL DEFAULT '{}',
  PRIMARY KEY(raw_id, outcome_seq),
  CHECK(outcome <> 'CONFLICT_RESOLVED' OR (resolution IS NOT NULL AND resolution_reason IS NOT NULL AND length(resolution_reason) > 0 AND resolved_by IS NOT NULL)),
  CHECK(outcome <> 'NOOP_DUPLICATE' OR counts_toward_totals = 0));
CREATE TRIGGER intake_outcome_no_update BEFORE UPDATE ON intake_outcome BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER intake_outcome_no_delete BEFORE DELETE ON intake_outcome BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE VIEW intake_current AS
  SELECT o.* FROM intake_outcome o
  WHERE o.outcome_seq = (SELECT MAX(outcome_seq) FROM intake_outcome x WHERE x.raw_id = o.raw_id)
    AND o.outcome <> 'NOOP_DUPLICATE';

CREATE TABLE intake_item_attr(
  raw_id TEXT PRIMARY KEY REFERENCES raw_intake(raw_id),
  record_kind TEXT, ref_id TEXT, source_ts TEXT,
  source_state TEXT, source_quality_flag TEXT, source_subtype TEXT, amount_text TEXT,
  notes TEXT, notes_trust TEXT NOT NULL DEFAULT 'untrusted' CHECK(notes_trust = 'untrusted'));
CREATE TRIGGER intake_item_attr_no_update BEFORE UPDATE ON intake_item_attr BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER intake_item_attr_no_delete BEFORE DELETE ON intake_item_attr BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;

CREATE TABLE intake_run_event(
  run_id TEXT NOT NULL, run_seq INTEGER NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN ('RUN_STARTED','RUN_CHECKPOINT','RUN_FINISHED','RUN_FAILED')),
  source TEXT NOT NULL, occurred_at TEXT NOT NULL, body TEXT NOT NULL DEFAULT '{}',
  PRIMARY KEY(run_id, run_seq));
CREATE TRIGGER intake_run_event_no_update BEFORE UPDATE ON intake_run_event BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
CREATE TRIGGER intake_run_event_no_delete BEFORE DELETE ON intake_run_event BEGIN SELECT RAISE(ABORT,'E-INT-RAW-IMMUTABLE'); END;
