-- M001 (Stage 15 INC-03) - docs/14-transformation/schema-migration-plan.md row M001; backlog TB-09/TB-10/TB-11.
-- Applied ONLY by `python -m hub.admin migrate` (hub/store/migrate.py), which takes a backup first
-- (backup-before-migrate, schema-migration-plan / rollback-strategy L2). Forward-only, sha256-checksummed.
--
-- audit_log            verbatim from docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (SCH-AUDIT, ADR-005)
-- DDL ADDENDUM (DDL v0.1 has no users/roles tables; Stage 12 file not edited in place, HAR-13 / A-14-08):
--   principal, principal_role, session, login_attempt   (C2 local authenticator, ADR-013 option B, BEH-SEC-02/04)
--   release_record, release_gate_result                 (release checklist G1-G10, BEH-CO-06, AC-CO-10/15)
-- Retention: OD-S12-09 hold-all (OD-15) - no table here can have rows deleted (triggers); audit and attempt
-- and gate rows are insert-only. Synthetic, unvalidated.
-- Rollback: restore the pre-migration backup written by `migrate` (hub.sqlite3 + anchor file together).

CREATE TABLE audit_log(
  audit_seq INTEGER PRIMARY KEY, occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
  actor_kind TEXT NOT NULL CHECK(actor_kind IN ('human','service','rule','system')),
  action TEXT NOT NULL, object_ref TEXT, outcome TEXT NOT NULL CHECK(outcome IN ('success','denied','error')),
  reason TEXT, correlation_id TEXT NOT NULL, details TEXT NOT NULL DEFAULT '{}',
  prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TRIGGER audit_log_no_update BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;
CREATE TRIGGER audit_log_no_delete BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT,'E-DEC-IMMUTABLE'); END;

-- Principals: created offline by the host operator (`hub.admin user create`); no default/bootstrap account.
CREATE TABLE principal(
  principal_id   TEXT PRIMARY KEY CHECK(length(principal_id) BETWEEN 1 AND 64),
  principal_kind TEXT NOT NULL CHECK(principal_kind IN ('human','service')),
  pw_algo        TEXT,
  pw_iterations  INTEGER,
  pw_salt        TEXT,
  pw_hash        TEXT,
  status         TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','disabled')),
  created_at     TEXT NOT NULL,
  created_by     TEXT NOT NULL,
  CHECK(principal_kind = 'service' OR
        (pw_algo = 'pbkdf2_sha256' AND pw_iterations >= 1 AND length(pw_salt) = 32 AND length(pw_hash) = 64)));
CREATE TRIGGER principal_no_delete BEFORE DELETE ON principal BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER principal_identity_fixed BEFORE UPDATE OF principal_id, principal_kind, created_at, created_by ON principal
BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

CREATE TABLE principal_role(
  principal_id TEXT NOT NULL REFERENCES principal(principal_id),
  role         TEXT NOT NULL CHECK(role IN ('reviewer','quality_lead','compliance','finance_read','integration','dispositioner')),
  granted_at   TEXT NOT NULL,
  granted_by   TEXT NOT NULL,
  PRIMARY KEY(principal_id, role));
CREATE TRIGGER principal_role_no_update BEFORE UPDATE ON principal_role BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER principal_role_no_delete BEFORE DELETE ON principal_role BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

-- Sessions: only SHA-256 of the 256-bit token is stored (BEH-SEC-02). Revocation/expiry = update, never delete.
CREATE TABLE session(
  token_sha256 TEXT PRIMARY KEY CHECK(length(token_sha256) = 64),
  principal_id TEXT NOT NULL REFERENCES principal(principal_id),
  created_at   TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  reauth_at    TEXT NOT NULL,
  revoked_at   TEXT);
CREATE TRIGGER session_no_delete BEFORE DELETE ON session BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER session_identity_fixed BEFORE UPDATE OF token_sha256, principal_id, created_at ON session
BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

-- Login attempts (lockout state, BEH-SEC-02): insert-only. principal_id NULL = unknown principal.
CREATE TABLE login_attempt(
  attempt_seq  INTEGER PRIMARY KEY,
  principal_id TEXT,
  occurred_at  TEXT NOT NULL,
  outcome      TEXT NOT NULL CHECK(outcome IN ('success','bad_credentials','locked','lockout_started')));
CREATE TRIGGER login_attempt_no_update BEFORE UPDATE ON login_attempt BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER login_attempt_no_delete BEFORE DELETE ON login_attempt BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;

-- Release checklist (F10-3 G1-G10). A release can only become 'ready' when all 10 gates have a recorded 'pass'.
CREATE TABLE release_record(
  release_id TEXT PRIMARY KEY CHECK(length(trim(release_id)) > 0),
  created_at TEXT NOT NULL,
  status     TEXT NOT NULL DEFAULT 'candidate' CHECK(status IN ('candidate','ready')));
CREATE TABLE release_gate_result(
  release_id    TEXT NOT NULL REFERENCES release_record(release_id),
  gate          TEXT NOT NULL CHECK(gate IN ('G1','G2','G3','G4','G5','G6','G7','G8','G9','G10')),
  result        TEXT NOT NULL CHECK(result IN ('pass','fail','not_run')),
  evidence_path TEXT NOT NULL CHECK(length(trim(evidence_path)) > 0),
  note          TEXT,
  recorded_at   TEXT NOT NULL,
  PRIMARY KEY(release_id, gate));
CREATE TRIGGER release_gate_result_no_update BEFORE UPDATE ON release_gate_result BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER release_gate_result_no_delete BEFORE DELETE ON release_gate_result BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER release_record_no_delete BEFORE DELETE ON release_record BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER release_record_no_downgrade BEFORE UPDATE OF status ON release_record
WHEN OLD.status = 'ready' BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
CREATE TRIGGER release_record_ready_requires_all_gates BEFORE UPDATE OF status ON release_record
WHEN NEW.status = 'ready' AND
     (SELECT count(*) FROM release_gate_result WHERE release_id = NEW.release_id AND result = 'pass') < 10
BEGIN SELECT RAISE(ABORT,'E-CO-RELEASE-BLOCKED'); END;

-- Hold-all retrofit for the INC-02 register (OD-S12-09 / OD-15): M000 left deviation_register without a delete
-- guard; status changes (proposed -> approved/rejected) remain possible, deletion does not.
CREATE TRIGGER deviation_register_no_delete BEFORE DELETE ON deviation_register BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;
