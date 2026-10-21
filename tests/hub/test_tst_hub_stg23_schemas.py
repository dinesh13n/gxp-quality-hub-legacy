"""Stage 23 contract tests (DW-16, DW-13 schema part; FAC-09; DC-02, DC-03; IC-3, IC-7). Synthetic, unvalidated.

  S30  the stdlib validator supports every keyword the 16 schemas use and agrees with the Stage 12 examples (13 valid accepted, 17 invalid rejected)
  S31  the Stage 12 v0.2 schemas are ADDITIVE over the frozen v0.1 files and the change list names exactly the schemas that differ
  S32  16 of 16 schemas are exercised on objects the built hub produced (store rows, service outputs, shipped partner feed): 0 invalid under v0.2;
       under v0.1 exactly the 5 schemas of the change list fail (the addendum is needed and sufficient)
  S33  every store table is either mapped to a schema or on the reviewed list of tables that have no Stage 12 JSON schema (a new table forces a decision)
  S34  drift is detected: a planted extra field / missing field / wrong enum in a real object is rejected
"""
import copy
import glob
import json
import os
import unittest

import _support as S
import _inc08 as W
import _schema_lite as L
import _stg23 as T


def setUpModule():
    T.skip_in_inner_egress_run()


EXAMPLES = os.path.join(S.CODE_ROOT, "docs", "12-specs", "contracts", "examples")
CHANGED = {"intake-outcome", "metric-value", "partner-feed-envelope", "error-envelope", "hub-config"}
TABLE_SCHEMA = {"audit_log": "audit-record", "crosswalk_link": "crosswalk-link", "decision_events": "decision-event", "evidence_record": "evidence-record",
                "intake_outcome": "intake-outcome", "raw_intake": "raw-intake", "metric_definition": "metric-definition", "metric_value": "metric-value",
                "policy_object": "policy-object", "rule_set": "rule-set"}
# store tables with no Stage 12 JSON schema (reviewed in Stage 23; FAC-09 covers the 10 mapped tables; see docs/23-human-control/stage12-v0.2/README)
NO_SCHEMA = {"active_ruleset", "case_state", "coexistence_inventory", "crosswalk_link_event", "decision_idempotency", "deviation_register", "flag_action",
             "intake_item_attr", "intake_run_event", "login_attempt", "obs_metric", "policy_events", "principal", "principal_role", "release_gate_result",
             "release_record", "rule_row", "rule_trace", "run_event", "run_lock", "service_token", "service_token_revocation", "session"}


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def wstore(self, *a, **kw):
        st = W.WStore(*a, **kw)
        self.stores.append(st)
        return st


class TST_HUB_STG23_Contracts(_Base):
    _cache = {}

    def objs(self):
        if "o" not in TST_HUB_STG23_Contracts._cache:
            st, objs, info = T.scenario(self)
            TST_HUB_STG23_Contracts._cache["o"] = (objs, info, [r[0] for r in st.con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY 1")],
                dict((t, st.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0]) for t in TABLE_SCHEMA))
        return TST_HUB_STG23_Contracts._cache["o"]

    def test_TST_HUB_STG23_S30_validator_supports_the_schemas_and_agrees_with_the_examples(self):
        """S30 (DW-16): no unsupported keyword in the 16 v0.1 or v0.2 schemas; the 13 Stage 12 valid examples are accepted and the 17 invalid cases are
        rejected by the v0.2 schemas (and by v0.1 where the schema is unchanged)."""
        for v02 in (False, True):
            for n in T.SCHEMA_NAMES:
                self.assertEqual(L.unsupported(T.load_schema(n, v02)), [], (n, v02))
        valid = sorted(glob.glob(os.path.join(EXAMPLES, "*.valid-*.json")))
        self.assertEqual(len(valid), 13)
        for p in valid:
            name = os.path.basename(p).split(".valid-")[0]
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            for v02 in (True, False):
                if name == "hub-config" and v02:
                    doc = dict(doc)  # the v0.1 example is a raw file; the v0.2 schema describes the effective configuration (required keys still present)
                self.assertEqual(L.errors(T.load_schema(name, v02), doc), [], (name, v02))
        with open(os.path.join(EXAMPLES, "invalid-cases.json"), encoding="utf-8") as f:
            cases = json.load(f)
        self.assertEqual(len(cases), 17)
        for c in cases:
            self.assertEqual(c["expected"], "reject")
            self.assertNotEqual(L.errors(T.load_schema(c["schema"], True), c["instance"]), [], c["case"])
            if c["schema"] not in CHANGED:
                self.assertNotEqual(L.errors(T.load_schema(c["schema"], False), c["instance"]), [], c["case"])

    def test_TST_HUB_STG23_S31_v0_2_schemas_are_additive_over_v0_1(self):
        """S31 (DW-13 / IC-7): 16 v0.2 schemas exist; no v0.2 schema adds a required property or drops / redefines a v0.1 property except the listed
        change; the change file names exactly the schemas that differ from v0.1."""
        with open(os.path.join(S.CODE_ROOT, "docs", "23-human-control", "stage12-v0.2", "schema-addendum-changes.json"), encoding="utf-8") as f:
            ch = json.load(f)
        self.assertEqual(sorted(ch["schemas"]), sorted(T.SCHEMA_NAMES))
        self.assertEqual(sorted(set(c["schema"] for c in ch["changes"])), sorted(CHANGED))
        differing = set()
        for n in T.SCHEMA_NAMES:
            a, b = T.load_schema(n, False), T.load_schema(n, True)
            if n != "hub-config":
                self.assertEqual(set(b.get("required", [])), set(a.get("required", [])), n)
                self.assertEqual(b.get("additionalProperties"), a.get("additionalProperties"), n)
                for k, v in a.get("properties", {}).items():
                    if (n, k) != ("error-envelope", "error"):
                        self.assertEqual(b["properties"].get(k), v, (n, k))
                self.assertEqual(a.get("allOf"), b.get("allOf"), n)
            else:
                self.assertEqual(sorted(b["required"]), sorted(a["required"]))
                self.assertEqual(b["properties"]["contract_bindings"], a["properties"]["contract_bindings"])
            a2, b2 = copy.deepcopy(a), copy.deepcopy(b)
            for d in (a2, b2):
                d.pop("$id", None)
                d.pop("description", None)
            if a2 != b2:
                differing.add(n)
        self.assertEqual(differing, CHANGED)

    def test_TST_HUB_STG23_S32_sixteen_of_sixteen_schemas_exercised_on_built_objects(self):
        """S32 (DW-16, FAC-09, DC-03): objects the built hub produced - store rows of the ingest / policy / decision / metric / audit tables, a run record,
        rule results, real HTTP error envelopes, the effective configuration, and the 8,567 shipped partner_feed rows - are validated against EVERY schema:
        16 of 16 exercised, 0 invalid under v0.2; under v0.1 exactly the changed schemas fail."""
        objs, info, tables, counts = self.objs()
        self.assertEqual(sorted(objs), sorted(T.SCHEMA_NAMES))
        report = []
        for n in T.SCHEMA_NAMES:
            r2 = T.check_objects(n, objs[n], True)
            r1 = T.check_objects(n, objs[n], False)
            self.assertGreater(r2["objects"], 0, n)
            self.assertEqual((n, r2["invalid"], r2["top_errors"]), (n, 0, []))
            self.assertEqual(r1["invalid"] > 0, n in CHANGED, (n, r1))
            report.append({"schema": n, "objects": r2["objects"], "valid_v0_2": r2["valid"], "invalid_v0_2": r2["invalid"], "invalid_v0_1": r1["invalid"],
                           "v0_1_top_errors": r1["top_errors"][:3]})
        self.assertEqual(len([r for r in report if r["objects"] > 0]), 16)
        outcomes = sorted(set(o["outcome"] for o in objs["intake-outcome"]))
        self.assertGreaterEqual(len(outcomes), 4)
        T.write_evidence("schema-validation.json", {"label": T.LABEL, "validator": "tests/hub/_schema_lite.py (stdlib draft-07 subset; cross-checked with jsonschema 3.2.0 off-line)",
                                                    "schemas_exercised": 16, "per_schema": report, "ingest_outcomes_in_scenario": outcomes,
                                                    "note": "partner-feed-envelope / -payload are INPUT-side schemas: validated on the 8,567 shipped legacy partner_feed rows"})

    def test_TST_HUB_STG23_S33_every_store_table_is_mapped_or_reviewed(self):
        """S33 (DW-16): the 10 store tables behind a schema all hold rows in the scenario; every other table of an M001..M006 store is on the reviewed
        no-schema list (a new table fails here until someone decides whether it needs a schema)."""
        objs, info, tables, counts = self.objs()
        for t, n in TABLE_SCHEMA.items():
            self.assertGreater(counts[t], 0, t)
        unmapped = sorted(t for t in tables if t not in TABLE_SCHEMA and not t.endswith("schema_migrations") and t != "schema_migrations")
        self.assertEqual(unmapped, sorted(NO_SCHEMA))
        T.write_evidence("store-table-coverage.json", {"label": T.LABEL, "tables_with_schema": TABLE_SCHEMA, "tables_without_schema": sorted(NO_SCHEMA),
                                                       "row_counts_mapped": counts})

    def test_TST_HUB_STG23_S34_drift_is_detected(self):
        """S34 (DW-16): the contract test would notice schema drift - a planted extra field, a missing required field and an out-of-vocabulary value in
        real objects are all rejected."""
        objs, _info, _t, _c = self.objs()
        for name, mutate in (("intake-outcome", lambda o: o.update(surprise_field=1)), ("intake-outcome", lambda o: o.pop("run_id")),
                             ("intake-outcome", lambda o: o.update(outcome="NOT_AN_OUTCOME")), ("audit-record", lambda o: o.update(actor_kind="robot")),
                             ("decision-event", lambda o: o.update(hash="short")), ("run-record", lambda o: o.update(outcome="exploded")),
                             ("hub-config", lambda o: o["zone_h"].update(reauth_window_seconds=0)), ("hub-config", lambda o: o.update(unknown_key=True)),
                             ("rule-set", lambda o: o.update(read_only="yes"))):
            o = copy.deepcopy(objs[name][0])
            self.assertEqual(L.errors(T.load_schema(name), o), [], name)
            mutate(o)
            self.assertNotEqual(L.errors(T.load_schema(name), o), [], name)


if __name__ == "__main__":
    unittest.main()
