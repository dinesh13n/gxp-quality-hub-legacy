"""Shared helpers for the Stage 27 hardening tests (DW-25 .. DW-27). Synthetic, unvalidated.

Stage 27 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg27_egress_guard.py (E27EGRESS), the same split as Stages 20, 21, 23, 24 and 26. Nothing here changes hub behaviour or a legacy path.
No helper in this directory imports a deny-listed module (hub.guards.no_ai rule R2).

  table_schema(con, t)    JSON Schema (draft-07 subset of _schema_lite) derived from the live DDL of store table t: column types, nullability, simple
                          CHECK ... IN (...) vocabularies, additionalProperties false
  SCHEMA_DIR              docs/27-hardening/schemas/store-tables (the committed copies; a test compares them with table_schema())
  ENVELOPE_PATH           the intake-envelope schema (OP-INT-01 request item, the 17th contract schema)
  write_evidence(...)     JSON under HUB_SANDBOX_ROOT/s27-evidence
"""
import json
import os
import re
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
SCHEMA_DIR = os.path.join(S.CODE_ROOT, "docs", "27-hardening", "schemas", "store-tables")
ENVELOPE_PATH = os.path.join(S.CODE_ROOT, "docs", "27-hardening", "schemas", "intake-envelope.schema.json")
NO_SCHEMA_23 = ["active_ruleset", "case_state", "coexistence_inventory", "crosswalk_link_event", "decision_idempotency", "deviation_register", "flag_action",
                "intake_item_attr", "intake_run_event", "login_attempt", "obs_metric", "policy_events", "principal", "principal_role", "release_gate_result",
                "release_record", "rule_row", "rule_trace", "run_event", "run_lock", "service_token", "service_token_revocation", "session"]
_TYPES = {"INTEGER": "integer", "INT": "integer", "TEXT": "string", "REAL": "number", "NUMERIC": "number", "BLOB": "string"}
_CHECK_IN = re.compile(r"(\w+)\s+IN\s*\(([^)]*)\)", re.I)


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 27 module: covered by test_tst_hub_stg27_egress_guard.py (E27EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s27-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def table_schema(con, table):
    cols = con.execute("PRAGMA table_info(%s)" % table).fetchall()  # cid, name, type, notnull, dflt, pk
    ddl = con.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)).fetchone()[0] or ""
    vocab = {}
    for col, body in _CHECK_IN.findall(ddl):
        vals = [v.strip().strip("'") for v in body.split(",") if v.strip()]
        if vals and all(re.fullmatch(r"[A-Za-z0-9_.:-]+", v) for v in vals):
            vocab[col] = vals
    props, required = {}, []
    for _cid, name, ctype, notnull, _dflt, pk in cols:
        t = _TYPES.get((ctype or "").split("(")[0].strip().upper(), "string")
        nullable = not notnull and not pk
        prop = {"type": [t, "null"] if nullable else t}
        if name in vocab and all(not re.fullmatch(r"-?\d+", v) for v in vocab[name]):
            prop["enum"] = vocab[name] + ([None] if nullable else [])
        props[name] = prop
        if notnull or pk:
            required.append(name)
    return {"$schema": "http://json-schema.org/draft-07/schema#", "title": "hub store table " + table,
            "description": "Stage 27 (FAC-09): derived from the live DDL by tests/hub/_stg27.table_schema; synthetic, unvalidated",
            "type": "object", "properties": props, "required": sorted(required), "additionalProperties": False}
