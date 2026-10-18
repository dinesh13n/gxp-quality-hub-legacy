-- M003 (Stage 15 INC-05) - docs/14-transformation/schema-migration-plan.md row M003; backlog TB-13 / TB-14.
-- Applied ONLY by hub.decision.schema (backup-before-migrate), recorded in decision_schema_migrations (NOT in
-- schema_migrations: see docs/15-modernization/inc05-design-notes.md D-02 / DEV-42). Forward-only, sha256-checked.
--
-- decision_events, evidence_record, case_state, crosswalk_link, crosswalk_link_event: verbatim from
-- docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (SCH-DEC-EVENT, SCH-EVIDENCE, SCH-CASE-STATE, SCH-CROSSWALK).
-- DDL ADDENDUM (Stage 12 file not edited in place, HAR-13): decision_events gapless-seq trigger (BEH-DEC-01);
-- insert-only triggers on evidence_record and crosswalk_link_event (hold-all, OD-S12-09 / OD-15);
-- decision_idempotency (BEH-DEC-09). case_state is a rebuildable projection: its rows are replaced by the service.
-- Synthetic, unvalidated. Rollback: restore the pre-migration backup written by hub.decision.schema.

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
-- addendum: seq is gapless per case, starting at 1 (BEH-DEC-01); a concurrent writer with a stale seq aborts.
CREATE TRIGGER decision_events_seq_gapless BEFORE INSERT ON decision_events
WHEN NEW.seq <> COALESCE((SELECT MAX(seq) FROM decision_events WHERE case_id = NEW.case_id), 0) + 1
BEGIN SELECT RAISE(ABORT,'E-DEC-SEQ-CONFLICT'); END;

CREATE TABLE evidence_record(
  ev_id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('document','intake_item','crosswalk_object','external_ref')),
  source TEXT NOT NULL, source_ref TEXT NOT NULL, source_hash TEXT, access_level TEXT NOT NULL DEFAULT 'restricted',
  attached_by TEXT NOT NULL, attached_at TEXT NOT NULL);
CREATE TRIGGER evidence_record_no_update BEFORE UPDATE ON evidence_record BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER evidence_record_no_delete BEFORE DELETE ON evidence_record BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE case_state(          -- projection, rebuildable from decision_events
  case_id TEXT PRIMARY KEY, state TEXT NOT NULL, cycle INTEGER NOT NULL, last_seq INTEGER NOT NULL, updated_from_event TEXT NOT NULL);

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
CREATE TRIGGER crosswalk_link_event_no_update BEFORE UPDATE ON crosswalk_link_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER crosswalk_link_event_no_delete BEFORE DELETE ON crosswalk_link_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE INDEX crosswalk_link_from ON crosswalk_link(from_type, from_id);
CREATE INDEX crosswalk_link_to ON crosswalk_link(to_type, to_id);
CREATE INDEX crosswalk_link_event_link ON crosswalk_link_event(link_id);

-- addendum: Idempotency-Key ledger (BEH-DEC-09); insert-only.
CREATE TABLE decision_idempotency(
  idem_key TEXT PRIMARY KEY, body_hash TEXT NOT NULL, event_id TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TRIGGER decision_idempotency_no_update BEFORE UPDATE ON decision_idempotency BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER decision_idempotency_no_delete BEFORE DELETE ON decision_idempotency BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
