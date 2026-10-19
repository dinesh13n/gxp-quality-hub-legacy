-- M005 (Stage 15 INC-07) - docs/14-transformation/schema-migration-plan.md row M005; backlog TB-16 (runs) and TB-17 (metrics).
-- Applied ONLY by hub.runs.schema (backup-before-migrate), recorded in runs_schema_migrations (NOT in schema_migrations: same
-- constraint as M002..M004, see docs/15-modernization/inc07-design-notes.md D-02). Forward-only, sha256-checked.
--
-- run_event, metric_definition, metric_value: from docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (SCH-RUN-RECORD, SCH-METRIC-DEF,
-- SCH-METRIC-VALUE). DDL ADDENDA (the Stage 12 file is not edited in place, HAR-13):
--   run_event_seq_gapless          run_seq is gapless per run (same rule as decision_events)
--   run_event_job index            job + time lookups (detector, resume)
--   run_lock                       single-flight lock row per job with a heartbeat (BEH-RUN-06); a mutable pointer, not a record
--   metric_definition              insert-only (a changed definition is a new version)
--   metric_value                   + null_reason, policy_status, errors, params, inputs, detail (schema metric-value.schema.json
--                                  has them, the DDL did not); insert-only; value NULL needs a null_reason (never 0)
--   obs_metric                     stored samples of the observability metrics (observability-spec OBS-4); insert-only
-- Synthetic, unvalidated. Rollback: restore the pre-migration backup written by hub.runs.schema.

CREATE TABLE run_event(
  run_id TEXT NOT NULL, run_seq INTEGER NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN ('RUN_STARTED','RUN_CHECKPOINT','RUN_FINISHED','RUN_FAILED','RUN_ABANDONED','RUN_REFUSED')),
  job TEXT NOT NULL, trigger TEXT NOT NULL CHECK(trigger IN ('manual','scheduled')), triggered_by TEXT NOT NULL,
  occurred_at TEXT NOT NULL, body TEXT NOT NULL DEFAULT '{}', PRIMARY KEY(run_id, run_seq));
CREATE TRIGGER run_event_no_update BEFORE UPDATE ON run_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER run_event_no_delete BEFORE DELETE ON run_event BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER run_event_seq_gapless BEFORE INSERT ON run_event
WHEN NEW.run_seq <> COALESCE((SELECT MAX(run_seq) FROM run_event WHERE run_id = NEW.run_id), 0) + 1
BEGIN SELECT RAISE(ABORT,'E-DEC-SEQ-CONFLICT'); END;
CREATE INDEX run_event_job ON run_event(job, occurred_at);

CREATE TABLE run_lock(
  job TEXT PRIMARY KEY, run_id TEXT NOT NULL, started_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL);

CREATE TABLE metric_definition(
  metric_id TEXT NOT NULL, version INTEGER NOT NULL, name TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('time','count','money','rate','age')),
  definition_tag TEXT, involves_definition INTEGER NOT NULL CHECK(involves_definition IN (0,1)),
  "window" TEXT NOT NULL, denominator TEXT NOT NULL, exclusions TEXT NOT NULL, cutoff_ref TEXT,
  basis TEXT NOT NULL CHECK(basis IN ('event_derived','modelled')), documentation TEXT NOT NULL,
  PRIMARY KEY(metric_id, version),
  CHECK(involves_definition = 0 OR definition_tag IS NOT NULL));
CREATE TRIGGER metric_definition_no_update BEFORE UPDATE ON metric_definition BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER metric_definition_no_delete BEFORE DELETE ON metric_definition BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE metric_value(
  value_id TEXT PRIMARY KEY, metric_id TEXT NOT NULL, metric_version INTEGER NOT NULL, definition_tag TEXT, policy_version TEXT,
  value TEXT, n INTEGER NOT NULL, partial INTEGER NOT NULL DEFAULT 0, window_start TEXT, window_end TEXT,
  denominator TEXT NOT NULL, exclusions TEXT NOT NULL, basis TEXT NOT NULL, data_origin TEXT NOT NULL CHECK(data_origin IN ('synthetic','production')),
  label TEXT NOT NULL, inputs_hash TEXT NOT NULL, code_version TEXT NOT NULL, computed_at TEXT NOT NULL,
  null_reason TEXT, policy_status TEXT CHECK(policy_status IN ('candidate','adopted','accepted-open')),
  errors TEXT NOT NULL DEFAULT '[]', params TEXT NOT NULL DEFAULT '{}', inputs TEXT NOT NULL DEFAULT '[]', detail TEXT NOT NULL DEFAULT '{}',
  CHECK(data_origin <> 'synthetic' OR label = 'synthetic, unvalidated'),
  CHECK(value IS NOT NULL OR (null_reason IS NOT NULL AND length(null_reason) > 0)));
CREATE INDEX metric_value_metric ON metric_value(metric_id, computed_at);
CREATE TRIGGER metric_value_no_update BEFORE UPDATE ON metric_value BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER metric_value_no_delete BEFORE DELETE ON metric_value BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE obs_metric(
  sample_id INTEGER PRIMARY KEY AUTOINCREMENT, collected_at TEXT NOT NULL, name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('counter','gauge','histogram')), labels TEXT NOT NULL DEFAULT '{}', value TEXT NOT NULL, run_id TEXT);
CREATE INDEX obs_metric_name ON obs_metric(name, collected_at);
CREATE TRIGGER obs_metric_no_update BEFORE UPDATE ON obs_metric BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER obs_metric_no_delete BEFORE DELETE ON obs_metric BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
