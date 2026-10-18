-- M002 (Stage 15 INC-04) - docs/14-transformation/schema-migration-plan.md row M002; backlog TB-12.
-- Applied ONLY by hub.policy.schema (backup-before-migrate), recorded in policy_schema_migrations (NOT in
-- schema_migrations: see docs/15-modernization/inc04-design-notes.md D-02 / DEV-28). Forward-only, sha256-checked.
--
-- policy_object, policy_events, rule_set, rule_row, active_ruleset: verbatim from
-- docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (SCH-POLICY, SCH-RULE-SET).
-- DDL ADDENDUM (Stage 12 file not edited in place, HAR-13): immutability triggers on rule_set / rule_row
-- (edit = new version, BEH-POL-07), hold-all delete guard on active_ruleset history is policy_events (OD-S12-09).
-- active_ruleset is a pointer, not a record: its rows may be replaced/removed; every change is a policy_events row
-- AND an audit_log record written in one transaction (hub.policy.service).
-- Synthetic, unvalidated. Rollback: restore the pre-migration backup written by hub.policy.schema.

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

-- Addendum: immutability of rule data; as-found sets are additionally read-only by origin (never custom-edited).
CREATE TRIGGER rule_set_no_update BEFORE UPDATE ON rule_set BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER rule_set_no_delete BEFORE DELETE ON rule_set BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER rule_row_no_update BEFORE UPDATE ON rule_row BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER rule_row_no_delete BEFORE DELETE ON rule_row BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
-- A set can only be activated if it exists (pointer integrity).
CREATE TRIGGER active_ruleset_target_exists BEFORE INSERT ON active_ruleset
WHEN (SELECT count(*) FROM rule_set WHERE ruleset_id = NEW.ruleset_id AND version = NEW.version) = 0
BEGIN SELECT RAISE(ABORT,'E-POL-NOT-FOUND'); END;
