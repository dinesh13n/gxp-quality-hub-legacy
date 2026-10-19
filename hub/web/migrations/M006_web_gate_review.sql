-- M006 (Stage 15 INC-08) - docs/14-transformation/schema-migration-plan.md (HTTP surface, service tokens, rule traces, flag actions).
-- Applied ONLY by hub.web.schema (backup-before-migrate), recorded in web_schema_migrations (NOT in schema_migrations: same
-- constraint as M002..M005, see docs/15-modernization/inc08-design-notes.md D-02). Forward-only, sha256-checked.
--
-- DDL ADDENDA (the Stage 12 file is not edited in place, HAR-13):
--   service_token / service_token_revocation  non-human bearer tokens for `integration` principals (BEH-SEC-03, AC-SEC-08). Only
--                                             sha256(token) is stored; both tables are insert-only (revocation = a new row).
--   rule_trace                                a stored rule evaluation for a case (BEH-REV-02): inputs + the rule-result object, with the
--                                             flag_id under which a human can override / dismiss / refuse it (BEH-GATE-08). Insert-only.
--   flag_action                               the human override / dismiss / refuse of a rule-generated item (BEH-GATE-08). Insert-only;
--                                             the original rule output is never touched. Human actors only (CHECK + trigger-free).
-- Synthetic, unvalidated. Rollback: restore the pre-migration backup written by hub.web.schema.

CREATE TABLE service_token(
  token_sha256 TEXT PRIMARY KEY, principal_id TEXT NOT NULL REFERENCES principal(principal_id),
  label TEXT NOT NULL, created_at TEXT NOT NULL, created_by TEXT NOT NULL, expires_at TEXT);
CREATE TRIGGER service_token_no_update BEFORE UPDATE ON service_token BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER service_token_no_delete BEFORE DELETE ON service_token BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

CREATE TABLE service_token_revocation(
  token_sha256 TEXT PRIMARY KEY REFERENCES service_token(token_sha256), revoked_at TEXT NOT NULL, revoked_by TEXT NOT NULL);
CREATE TRIGGER service_token_revocation_no_update BEFORE UPDATE ON service_token_revocation BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER service_token_revocation_no_delete BEFORE DELETE ON service_token_revocation BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

CREATE TABLE rule_trace(
  trace_id TEXT PRIMARY KEY, flag_id TEXT NOT NULL UNIQUE, case_id TEXT NOT NULL, "function" TEXT NOT NULL,
  ruleset_ref TEXT NOT NULL, authoritative INTEGER NOT NULL CHECK(authoritative IN (0,1)),
  inputs TEXT NOT NULL, result TEXT NOT NULL, template_version TEXT NOT NULL,
  recorded_at TEXT NOT NULL, recorded_by TEXT NOT NULL, data_origin TEXT NOT NULL DEFAULT 'synthetic' CHECK(data_origin IN ('synthetic','production')));
CREATE INDEX rule_trace_case ON rule_trace(case_id, trace_id);
CREATE TRIGGER rule_trace_no_update BEFORE UPDATE ON rule_trace BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER rule_trace_no_delete BEFORE DELETE ON rule_trace BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

CREATE TABLE flag_action(
  action_id TEXT PRIMARY KEY, flag_id TEXT NOT NULL, flag_kind TEXT NOT NULL CHECK(flag_kind IN ('rule_trace','intake_queue')),
  action TEXT NOT NULL CHECK(action IN ('override','dismiss','refuse')),
  reason TEXT NOT NULL CHECK(length(trim(reason)) > 0), replacement TEXT,
  actor TEXT NOT NULL, actor_kind TEXT NOT NULL CHECK(actor_kind = 'human'), acted_at TEXT NOT NULL,
  case_id TEXT, event_id TEXT);
CREATE INDEX flag_action_flag ON flag_action(flag_id, action_id);
CREATE TRIGGER flag_action_no_update BEFORE UPDATE ON flag_action BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER flag_action_no_delete BEFORE DELETE ON flag_action BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
