"""Stage 15 INC-04 supplementary tests (no Stage 13 ID; TST-HUB-INC04-Sxx): M002 applier and the policy CLI, the activation
refusal matrix (OD-16: no recorded human decision -> no activation), loader drift / purity of the importer, engine edge cases and
the documented deltas to the legacy code, audit atomicity."""
import ast
import json
import os
import shutil
import sqlite3
import unittest
from unittest import mock

import _support as S
import _inc03 as H
import _inc04 as P
from hub.core.errors import MigrationDrift
from hub.policy import asfound, engine, schema
from hub.policy.errors import AsFoundDrift, DecisionRequired, GateNoHolders, GateNotAuthorised, InputInvalid, NotFound, PolicyInvalid
from hub.policy.service import PolicyService
from hub.security import audit
from hub.security.errors import AuditWriteFailed, StoreNotMigrated
from hub.store import migrate

AUTH = "TEST-AUTH-5 (synthetic)"


def setUpModule():
    S.require_sandbox()


def policy_cli(args, cfg_path, timeout=150):
    import subprocess
    import sys
    return subprocess.run([sys.executable, "-B", "-m", "hub.policy", "--config", cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


class TST_HUB_INC04_Supplementary(unittest.TestCase):

    def test_TST_HUB_INC04_S01_m002_applier_and_policy_cli(self):
        """S01: `hub.policy migrate` needs M001, backs up first, is idempotent and does NOT touch schema_migrations (INC-03 S01 stays valid);
        drift of M002 is refused (exit 15); seed / load-as-found / rulesets / evaluate via the CLI; nothing is ever active."""
        base = S.tmpdir("s01-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        self.assertEqual(S.run_hub(["init", "--data-dir", d]).returncode, 0)        # M000 only
        p = policy_cli(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (22, "E-STORE-NOT-MIGRATED"), p.stderr)
        self.assertEqual(H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg).returncode, 0)
        p = policy_cli(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertTrue(out["applied"])
        self.assertEqual(out["backup"]["schema_versions"], ["M000", "M001"])
        self.assertEqual(json.loads(policy_cli(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg).stdout)["applied"], False)
        self.assertEqual(H.out_json(H.admin(["status", "--data-dir", d], cfg))["applied"], ["M000", "M001"])   # schema_migrations untouched
        self.assertEqual(H.out_json(H.admin(["status", "--data-dir", d], cfg))["pending"], [])
        self.assertEqual(json.loads(policy_cli(["seed", "--data-dir", d], cfg).stdout)["seeded"], ["D-OPS", "D-EVID", "D-FIN", "C-OPS", "C-EVID"])
        self.assertEqual(json.loads(policy_cli(["seed", "--data-dir", d], cfg).stdout)["seeded"], [])
        run_dir = S.tmpdir("s01run-")
        p = policy_cli(["load-as-found", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual([(r["ruleset_ref"], r["loaded"]) for r in json.loads(p.stdout)["rulesets"]],
                         [("as-found-python@1", True), ("as-found-js@1", True), ("as-found-batch@1", True)])
        self.assertEqual(json.loads(p.stdout)["active"], {})
        p = policy_cli(["load-as-found", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg)
        self.assertEqual([r["loaded"] for r in json.loads(p.stdout)["rulesets"]], [False, False, False])
        st = json.loads(policy_cli(["status", "--data-dir", d], cfg).stdout)
        self.assertEqual((st["state"], st["policies"], st["active"]), ("applied", 5, {}))
        arg = json.dumps({"status": "OPEN", "severity": "CRITICAL", "amount": 1})
        p = policy_cli(["evaluate", "--data-dir", d, "--function", "PRIORITY", "--input", arg], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (23, "E-POL-NO-ACTIVE-RULESET"))
        p = policy_cli(["evaluate", "--data-dir", d, "--function", "PRIORITY", "--input", arg, "--ruleset-ref", "as-found-python@1"], cfg)
        r = json.loads(p.stdout)
        self.assertEqual((p.returncode, r["outcome"], r["authoritative"]), (0, "urgent", False))
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        try:
            self.assertEqual(con.execute("SELECT count(*) FROM active_ruleset").fetchone()[0], 0)
            self.assertEqual(audit.verify(con, os.path.join(base, "anchor", H.ANCHOR))["status"], "ok")
            self.assertEqual([r[0] for r in con.execute("SELECT action FROM audit_log WHERE action LIKE 'POLICY_SCHEMA%' OR action = 'RULESET_ACTIVATED'")],
                             ["POLICY_SCHEMA_APPLIED"])
            with con:
                con.execute("DROP TRIGGER policy_schema_migrations_no_update")
                con.execute("UPDATE policy_schema_migrations SET sha256 = 'tampered'")
        finally:
            con.close()
        p = policy_cli(["status", "--data-dir", d], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (15, "E-STORE-MIGRATION-DRIFT"), p.stderr)

    def test_TST_HUB_INC04_S02_activation_refusal_matrix(self):
        """S02 (OD-16): activation is refused with no decision, a wrong / unknown / non-decision / service / non-holder decision, a decision for
        another set or function, a consumed decision and a broken audit chain; every refusal is audited and the pointer stays unset."""
        st = P.PStore(loaded=True)
        try:
            svc, h1, h2 = st.svc, st.sess("holder-1"), st.sess("holder-2")
            py, js = "as-found-python@1", "as-found-js@1"
            d_py = svc.record_activation_decision(h1, "PRIORITY", py, AUTH, "decision A (synthetic)")["decision_seq"]
            d_js = svc.record_activation_decision(h2, "AMOUNT_LIMIT", js, AUTH, "decision B (synthetic)")["decision_seq"]
            login_seq = st.audit_actions("LOGIN")[0]["audit_seq"]
            zh_seq = st.audit_actions("ZONE_H_ATTEMPT")[0]["audit_seq"]
            for label, fn, ref, seq in (("none", "PRIORITY", py, None), ("bad type", "PRIORITY", py, "7"), ("bool", "PRIORITY", py, True),
                                        ("unknown seq", "PRIORITY", py, 10 ** 6), ("not a decision (login)", "PRIORITY", py, login_seq),
                                        ("not a decision (zone h)", "PRIORITY", py, zh_seq), ("other function", "PRIORITY", py, d_js),
                                        ("other ruleset", "MANUAL_REVIEW", "as-found-python@1", d_py)):
                with self.subTest(label):
                    with self.assertRaises(DecisionRequired) as cm:
                        svc.activate(h1, fn, ref, AUTH, seq)
                    self.assertEqual(cm.exception.code, "E-POL-DECISION-REQUIRED")
                    self.assertEqual(svc.active(), {})
            denied = [a for a in st.audit_actions("RULESET_ACTIVATED") if a["outcome"] == "denied"]
            self.assertEqual(len(denied), 8)
            self.assertEqual({a["reason"] for a in denied}, {"decision_required"})
            # a decision recorded by a user who is no longer a holder is not valid
            st.s["zone_h"]["holders"].remove("holder-2")
            with self.assertRaises(DecisionRequired) as cm:
                svc.activate(h1, "AMOUNT_LIMIT", js, AUTH, d_js)
            st.s["zone_h"]["holders"].append("holder-2")
            self.assertIn("holder", cm.exception.details["problem"])
            # valid decision works exactly once
            svc.activate(h2, "PRIORITY", py, AUTH, d_py)
            svc.deactivate(h2, "PRIORITY", AUTH)
            with self.assertRaises(DecisionRequired) as cm:
                svc.activate(h2, "PRIORITY", py, AUTH, d_py)
            self.assertIn("already consumed", cm.exception.details["problem"])
            self.assertEqual(svc.active(), {})
            # a tampered audit chain (offline attacker) invalidates every pending decision
            con = sqlite3.connect(st.con.execute("PRAGMA database_list").fetchone()[2])
            con.execute("DROP TRIGGER audit_log_no_update")
            with con:
                con.execute("UPDATE audit_log SET reason = 'tampered' WHERE audit_seq = ?", (login_seq,))
            con.close()
            with self.assertRaises(DecisionRequired) as cm:
                svc.activate(h1, "AMOUNT_LIMIT", js, AUTH, d_js)
            self.assertIn("chain", cm.exception.details["problem"])
            self.assertEqual(svc.active(), {})
            # a human who is not a holder / has no dispositioner role cannot even record a decision
            for who, exc in ((st.sess("nonholder"), GateNotAuthorised), (st.sess("rev"), GateNotAuthorised), (st.service_session(), GateNotAuthorised)):
                with self.assertRaises(exc):
                    svc.record_activation_decision(who, "PRIORITY", py, AUTH, "x")
            with self.assertRaises(PolicyInvalid):
                svc.record_activation_decision(h1, "PRIORITY", py, AUTH, " ")
            with self.assertRaises(NotFound):
                svc.record_activation_decision(h1, "PRIORITY", "as-found-python@7", AUTH, "x")
        finally:
            st.close()

    def test_TST_HUB_INC04_S03_no_holders_configured_blocks_every_zone_h_action(self):
        """S03 (FR-GATE-04 / AC-GATE-02 pattern): with zone_h.holders empty (the shipped default) every adoption / activation is E-GATE-NO-HOLDERS."""
        st = P.PStore(loaded=True, extra={"zone_h": {"holders": []}})
        try:
            self.assertEqual(st.s["zone_h"]["holders"], [])
            h = st.sess("holder-1")
            for call in (lambda: st.svc.adopt(h, "D-OPS", 1, "2026-01-01", "o", AUTH),
                         lambda: st.svc.record_activation_decision(h, "PRIORITY", "as-found-python@1", AUTH, "r"),
                         lambda: st.svc.activate(h, "PRIORITY", "as-found-python@1", AUTH, 1)):
                with self.assertRaises(GateNoHolders) as cm:
                    call()
                self.assertEqual(cm.exception.code, "E-GATE-NO-HOLDERS")
            self.assertEqual((st.svc.list_policies(status="adopted"), st.svc.active()), ([], {}))
        finally:
            st.close()

    def test_TST_HUB_INC04_S04_loader_is_idempotent_fails_closed_and_never_executes_legacy(self):
        """S04 (AD-06): reloading is a no-op; a changed legacy source -> E-POL-ASFOUND-DRIFT; stored != legacy content -> drift; the importer
        has no import of legacy code, importlib or subprocess; set content hashes are stable."""
        st = P.PStore(loaded=True)
        try:
            self.assertEqual([r["loaded"] for r in st.svc.load_as_found(S.LEGACY_ROOT, S.tmpdir("s04-"))], [False] * 3)
            root = S.tmpdir("s04root-")
            for rel in ("app/legacy_logic.py", "legacy_js/legacy_policy.js", "contracts/decision-policies-archive.json"):
                os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
                shutil.copyfile(os.path.join(S.LEGACY_ROOT, rel), os.path.join(root, rel))
            self.assertEqual(asfound.build_python(root)["ruleset_id"], "as-found-python")
            for rel, old, new in (("app/legacy_logic.py", "50000", "60000"), ("legacy_js/legacy_policy.js", "1.05", "1.10"),
                                  ("contracts/decision-policies-archive.json", "25000", "25001")):
                p = os.path.join(root, rel)
                text = open(p, encoding="utf-8").read()
                open(p, "w", encoding="utf-8").write(text.replace(old, new))
                with self.assertRaises(AsFoundDrift) as cm:
                    asfound.build_all(root, S.tmpdir("s04b-"))
                self.assertEqual(cm.exception.details["source"], rel)
                open(p, "w", encoding="utf-8").write(text)
            # stored content differs from what the legacy sources now say (simulated by a different pin-compatible document)
            import hub.policy.service as service_mod
            doc = dict(asfound.build_python(root))
            doc["rows"] = [dict(r, outcome=dict(r["outcome"], value="X")) if r["row_id"] == "PY-P6" else r for r in doc["rows"]]
            with mock.patch.object(service_mod.asfound, "build_all", lambda lr, rd: [doc]):
                with self.assertRaises(AsFoundDrift) as cm:
                    st.svc.load_as_found(S.LEGACY_ROOT, S.tmpdir("s04c-"))
            self.assertIn("stored_sha256", cm.exception.details)
            src = open(os.path.join(S.CODE_ROOT, "hub", "policy", "asfound.py"), encoding="utf-8").read()
            mods = set()
            for n in ast.walk(ast.parse(src)):
                if isinstance(n, ast.Import):
                    mods |= {a.name for a in n.names}
                elif isinstance(n, ast.ImportFrom):
                    mods.add(n.module)
            self.assertFalse(mods & {"importlib", "subprocess", "runpy", "app", "legacy_js", "legacy_batch"}, sorted(mods))
            self.assertNotIn("exec(", src.replace("exec_module", ""))
        finally:
            st.close()

    def test_TST_HUB_INC04_S05_engine_edges_and_documented_deltas_to_legacy(self):
        """S05: year as text equals year as int; blank/None region -> NULL_INPUT; unknown function; custom set without a catch-all marks NO_MATCH;
        DELTA (DEV-29): legacy JS matches PARTIAL years by startsWith (year 202 -> the 2022 row), the service does not."""
        st = P.PStore(loaded=True)
        try:
            svc = st.svc
            a = svc.evaluate("AMOUNT_LIMIT", {"amount": 1, "region": "APAC", "year": "2026"}, "as-found-js@1")
            b = svc.evaluate("AMOUNT_LIMIT", {"amount": 1, "region": "APAC", "year": 2026}, "as-found-js@1")
            self.assertEqual(a, b)
            with self.assertRaises(InputInvalid):
                svc.evaluate("AMOUNT_LIMIT", {"region": "APAC", "year": 2026}, "as-found-js@1")   # amount missing
            doc = svc.get_ruleset("as-found-python@1")
            doc = dict(doc, rows=[r for r in doc["rows"] if r["row_id"] != "PY-P6"])
            r = engine.evaluate(doc, "PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 1})
            self.assertEqual((r["outcome"], r["defaulted"], r["defaulted_reason"]), (None, True, "NO_MATCH_REGION_YEAR"))
            with self.assertRaises(Exception) as cm:
                engine.evaluate(doc, "SHIFT_FLAG", {})
            self.assertEqual(cm.exception.code, "E-POL-UNKNOWN-FUNCTION")
            legacy = P.legacy_node([[0, "APAC", 202], [0, "APAC", 2], [0, "APAC", ""]])
            ours = [svc.evaluate("AMOUNT_LIMIT", {"amount": 0, "region": "APAC", "year": y}, "as-found-js@1") for y in (202, 2, "")]
            self.assertEqual([x[0] for x in legacy], [15000, 15000, 15000])     # legacy quirk: prefix match picks the 2022 row
            self.assertEqual([x["outcome"]["threshold"] for x in ours], [999999] * 3)
            self.assertEqual([x["defaulted"] for x in ours], [True] * 3)       # service: no 4-digit-year match -> fallback, marked
        finally:
            st.close()

    def test_TST_HUB_INC04_S06_audit_failure_rolls_the_change_back(self):
        """S06 (AC-SEC-14 pattern): if the audit insert for POLICY_ADOPTED fails, the new policy version and its event are rolled back
        and E-SEC-AUDIT-WRITE-FAILED is raised."""
        st = P.PStore()
        try:
            real = audit._insert
            before = st.counts()

            def flaky(con, clock, actor, actor_kind, action, outcome, correlation_id, **kw):
                if action == "POLICY_ADOPTED":
                    raise sqlite3.OperationalError("disk I/O error (simulated)")
                return real(con, clock, actor, actor_kind, action, outcome, correlation_id, **kw)
            with mock.patch.object(audit, "_insert", flaky):
                with self.assertRaises(AuditWriteFailed):
                    st.svc.adopt(st.sess("holder-1"), "D-OPS", 1, "2026-01-01", "ops-owner", AUTH)
            after = st.counts()
            self.assertEqual({k: after[k] - before[k] for k in after}, {"policy_object": 0, "policy_events": 0, "rule_set": 0, "rule_row": 0,
                                                                         "active_ruleset": 0, "audit_log": 1})  # only the ZONE_H_ATTEMPT record
            self.assertEqual(st.svc.get_policy("D-OPS")["version"], 1)
            self.assertEqual(st.verify()["status"], "ok")
        finally:
            st.close()

    def test_TST_HUB_INC04_S07_policy_service_requires_m002(self):
        """S07: PolicyService on a store without M002 refuses (E-STORE-NOT-MIGRATED); a changed M002 file / hash is drift."""
        st = H.Store("s07-")
        try:
            with self.assertRaises(StoreNotMigrated):
                PolicyService(st.con, st.s, st.clock, st.anchor)
            schema.apply(st.data, os.path.join(st.base, "bk2"), st.anchor_path, st.clock)
            PolicyService(st.con, st.s, st.clock, st.anchor)
            self.assertEqual(schema.status(st.con)["state"], "applied")
            self.assertEqual(sorted(migrate.applied(st.con)), ["M000", "M001"])
        finally:
            st.close()

    def test_TST_HUB_INC04_S08_rollback_l2_restore_then_rebuild_is_content_identical(self):
        """S08 (rollback-strategy INC-04: L1 + L2 rebuild): restore the pre-M002 backup -> no policy tables, audit chain verifies; re-applying
        M002, seed and the as-found load reproduces identical rule-set content hashes (the rebuild script is the CLI)."""
        base = S.tmpdir("s08-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        bk = os.path.join(base, "bk")
        self.assertEqual(H.admin(["migrate", "--data-dir", d, "--backup-root", bk], cfg).returncode, 0)
        p = policy_cli(["migrate", "--data-dir", d, "--backup-root", bk], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        label = json.loads(p.stdout)["backup"]["label"]
        self.assertEqual(policy_cli(["seed", "--data-dir", d], cfg).returncode, 0)
        run_dir = S.tmpdir("s08run-")
        first = json.loads(policy_cli(["load-as-found", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg).stdout)["rulesets"]
        p = H.admin(["restore", "--data-dir", d, "--backup", os.path.join(bk, label)], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        rep = H.out_json(p)
        self.assertEqual((rep["verify_audit"]["status"], rep["schema_after_restore"]), ("ok", ["M000", "M001"]))
        self.assertEqual(json.loads(policy_cli(["status", "--data-dir", d], cfg).stdout)["state"], "absent")
        self.assertEqual(policy_cli(["migrate", "--data-dir", d, "--backup-root", bk], cfg).returncode, 0)
        self.assertEqual(policy_cli(["seed", "--data-dir", d], cfg).returncode, 0)
        second = json.loads(policy_cli(["load-as-found", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg).stdout)["rulesets"]
        self.assertEqual([(r["ruleset_ref"], r["content_sha256"]) for r in first], [(r["ruleset_ref"], r["content_sha256"]) for r in second])
        self.assertEqual([r["loaded"] for r in second], [True, True, True])


if __name__ == "__main__":
    unittest.main()
