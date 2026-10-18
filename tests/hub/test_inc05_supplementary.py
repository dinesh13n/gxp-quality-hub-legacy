"""Stage 15 INC-05 supplementary tests (no Stage 13 ID; TST-HUB-INC05-Sxx): M003 applier and the decision CLI, the shared Zone H gate
matrix and its binding to the INC-04 policy service (DEV-34), the 125-case backfill (counts, provenance, idempotency, atomicity,
CT-02 priority distribution), hash-chain tamper detection, database-level triggers, projection rebuild, crosswalk rule runs on the
shipped data via the CLI, and static import-graph checks. Synthetic, unvalidated.
"""
import ast
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import unittest
from unittest import mock

import _support as S
import _inc03 as H
import _inc05 as D
from hub.core.errors import ConfigInvalid, MigrationDrift
from hub.crosswalk import sources
from hub.decision import backfill, errors as E, schema as dschema
from hub.decision.service import norm_ts
from hub.gate import errors as GE
from hub.gate.service import GateService, ZONE_H_ACTIONS
from hub.policy.service import PolicyService
from hub.security import audit, scan
from hub.security.errors import AuditWriteFailed, AuthForbidden, AuthUnauthenticated, StoreNotMigrated

PINNED_SHA_PREFIX = "c254649f"  # OD-09 baseline legacy.sqlite3 (sha256 c254649f...d70aa)
AUTH = "TEST-AUTH-S (synthetic)"


def setUpModule():
    D.skip_in_inner_egress_run()


def cli(module, args, cfg_path, timeout=170):
    return subprocess.run([sys.executable, "-B", "-m", module, "--config", cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


class TST_HUB_INC05_Supplementary(unittest.TestCase):

    def setUp(self):
        self.ds = None

    def tearDown(self):
        if self.ds is not None:
            self.ds.close()

    def store(self, **kw):
        self.ds = D.DStore(**kw)
        return self.ds

    # ---------------------------------------------------------------- M003 applier and CLI
    def test_TST_HUB_INC05_S01_m003_applier_and_cli(self):
        """S01: `hub.decision migrate` needs M001 and M002, backs up first, is idempotent, does NOT touch schema_migrations and refuses a drifted
        M003 record (E-STORE-MIGRATION-DRIFT, exit 15)."""
        base = S.tmpdir("s01-")
        cfg = H.write_config(base)
        data, bk = os.path.join(base, "data"), os.path.join(base, "bk")
        self.assertEqual(H.admin(["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        p = cli("hub.decision", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (22, "E-STORE-NOT-MIGRATED"))
        self.assertEqual(json.loads(p.stderr)["details"]["needs"], "M002")
        self.assertEqual(cli("hub.policy", ["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        p = cli("hub.decision", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertTrue(out["applied"])
        self.assertTrue(out["backup"]["label"].startswith("pre-decision-M003-"))
        p = cli("hub.decision", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
        self.assertEqual((p.returncode, json.loads(p.stdout)["applied"], json.loads(p.stdout)["backup"]), (0, False, None))
        st = json.loads(cli("hub.decision", ["status", "--data-dir", data], cfg).stdout)
        self.assertEqual((st["state"], st["events"], st["cases"], st["links"]), ("applied", 0, 0, 0))
        con = sqlite3.connect(os.path.join(data, "hub.sqlite3"))
        self.assertEqual([r[0] for r in con.execute("SELECT version FROM schema_migrations ORDER BY 1")], ["M000", "M001"])
        self.assertEqual([r[0] for r in con.execute("SELECT version FROM decision_schema_migrations")], ["M003"])
        con.execute("DROP TRIGGER decision_schema_migrations_no_update")
        con.execute("UPDATE decision_schema_migrations SET sha256 = ?", ("0" * 64,))
        con.commit()
        con.close()
        p = cli("hub.decision", ["status", "--data-dir", data], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (15, "E-STORE-MIGRATION-DRIFT"))
        from hub.store import db
        c2 = sqlite3.connect(os.path.join(data, "hub.sqlite3"))
        try:
            with self.assertRaises(MigrationDrift):
                dschema.require(c2)
        finally:
            c2.close()
        c3 = sqlite3.connect(":memory:")
        with self.assertRaises(StoreNotMigrated):
            dschema.require(c3)
        c3.close()
        self.assertTrue(db.HUB_DB_NAME)

    # ---------------------------------------------------------------- shared gate
    def test_TST_HUB_INC05_S02_gate_matrix_all_ten_actions(self):
        """S02: the shared gate for ZH-01..ZH-10: human holder with a fresh step-up -> audit_seq of an accepted ZONE_H_ATTEMPT; empty holders ->
        E-GATE-NO-HOLDERS; non-holder / reviewer / service -> E-GATE-NOT-AUTHORISED; stale re-auth -> E-GATE-REAUTH-REQUIRED; no session ->
        E-AUTH-UNAUTHENTICATED; unknown action -> E-GATE-UNKNOWN-ACTION; every attempt is in the audit chain and nothing else is written."""
        ds = self.store()
        gate = GateService(ds.con, ds.s, ds.clock, ds.anchor)
        self.assertEqual(gate.available(), {"holders_configured": 2, "available": True})
        self.assertEqual(sorted(ZONE_H_ACTIONS), ["ZH-%02d" % i for i in range(1, 11)])
        n = ds.counts()
        for zh in sorted(ZONE_H_ACTIONS):
            seq = gate.require_holder(ds.sess("holder-1"), zh, "t-gate", "obj")
            row = [a for a in ds.audit_actions("ZONE_H_ATTEMPT") if a["audit_seq"] == seq][0]
            self.assertEqual((row["outcome"], row["details"]["zh"], row["details"]["zone_h_action"]), ("success", zh, ZONE_H_ACTIONS[zh]))
            for who, exc in (("nonholder", GE.GateNotAuthorised), ("rev", GE.GateNotAuthorised), ("ql", GE.GateNotAuthorised)):
                with self.assertRaises(exc):
                    gate.require_holder(ds.sess(who), zh, "t-gate", "obj")
            with self.assertRaises(GE.GateNotAuthorised):
                gate.require_holder(ds.service_session(), zh, "t-gate", "obj")
            with self.assertRaises(AuthUnauthenticated):
                gate.require_holder(None, zh, "t-gate", "obj")
        with self.assertRaises(GE.GateUnknownAction):
            gate.require_holder(ds.sess("holder-1"), "ZH-11", "t-gate", "obj")
        ds.clock.advance(ds.s["zone_h"]["reauth_window_seconds"] + 5)
        stale = ds.sess("holder-1")
        with self.assertRaises(GE.GateReauthRequired):
            gate.require_holder(stale, "ZH-04", "t-gate", "obj")
        ds.authn.reauthenticate(ds.tokens["holder-1"], ds.pw, "t-re")
        self.assertIsInstance(gate.require_holder(ds.sess("holder-1"), "ZH-04", "t-gate", "obj"), int)
        att = ds.audit_actions("ZONE_H_ATTEMPT")
        self.assertEqual(sum(1 for a in att if a["outcome"] == "success"), 11)
        self.assertEqual(sum(1 for a in att if a["outcome"] == "denied"), 10 * 5 + 2)
        for k in ("decision_events", "evidence_record", "crosswalk_link"):
            self.assertEqual(ds.counts()[k], n[k])
        self.ds.close()
        ds = self.ds = D.DStore(extra={"zone_h": {"holders": []}})
        gate = GateService(ds.con, ds.s, ds.clock, ds.anchor)
        self.assertEqual(gate.available(), {"holders_configured": 0, "available": False})
        with self.assertRaises(GE.GateNoHolders):
            gate.require_holder(ds.sess("holder-1"), "ZH-01", "t-gate", "obj")

    def test_TST_HUB_INC05_S03_policy_service_uses_the_shared_gate(self):
        """S03 (DEV-34 / OD-17): GatedPolicyService works with the INC-04 local gate made unusable, so Zone H eligibility comes from the shared gate;
        the stale re-auth now raises the specified E-GATE-REAUTH-REQUIRED (the local copy raised E-GATE-NOT-AUTHORISED)."""
        ds = self.store()
        with mock.patch("hub.policy.gate.require_holder", side_effect=AssertionError("local INC-04 gate must not be used")):
            ds.closure_policy(("CLOSED",))
            self.assertEqual(ds.svc.closing_set()[1], "policy")
            att = [a for a in ds.audit_actions("ZONE_H_ATTEMPT") if a["details"]["zh"] == "ZH-05"]
            self.assertEqual([(a["actor"], a["outcome"]) for a in att], [("holder-1", "success")])
            with self.assertRaises(GE.GateNotAuthorised):
                ds.pol.adopt(ds.sess("nonholder"), "CL-1", 1, ds.clock()[:10], "owner-synthetic", AUTH)
            ds.clock.advance(ds.s["zone_h"]["reauth_window_seconds"] + 5)
            with self.assertRaises(GE.GateReauthRequired):
                ds.pol.adopt(ds.sess("holder-1"), "CL-1", 1, ds.clock()[:10], "owner-synthetic", AUTH)
        old = PolicyService(ds.con, ds.s, ds.clock, ds.anchor)
        with self.assertRaises(GE.GateNotAuthorised) as cm:
            old.adopt(ds.sess("holder-1"), "CL-1", 1, ds.clock()[:10], "owner-synthetic", AUTH)
        self.assertEqual(cm.exception.details["reason"], "reauth_required")

    # ---------------------------------------------------------------- backfill
    def test_TST_HUB_INC05_S04_backfill_125_cases(self):
        """S04 (DM-1, OD-09, gate G4): 125 CASE_IMPORTED + 125 FACT_RECEIVED events with provenance; states 42/30/36/9/8; 8 marked REOPENED; projection 0
        mismatches; per-case chains verify; CT-02 priority distribution archive 36 / queue 70 / review 17 / urgent 2 through the (inactive) as-found rule
        set; a second run writes nothing; the legacy sandbox copy is byte-identical."""
        ds = self.store()
        legacy_db = os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3")
        before = S.sha256_file(legacy_db)
        run_dir = S.tmpdir("s04-")
        ds.pol.load_as_found(S.LEGACY_ROOT, run_dir, "t-s04")
        self.assertEqual(ds.pol.active(), {})
        rep = backfill.run(ds.svc, S.LEGACY_ROOT, run_dir, "t-s04", policy_service=ds.pol)
        self.assertTrue(rep["source_db_sha256"].startswith(PINNED_SHA_PREFIX))
        self.assertEqual((rep["cases_in_source"], rep["imported_now"], rep["already_imported"], rep["events_written"]), (125, 125, 0, 250))
        self.assertEqual(rep["state_counts"], {"CLOSED": 36, "ESCALATED": 9, "OPEN": 42, "REOPENED": 8, "UNDER_REVIEW": 30})
        self.assertEqual((rep["marked_legacy_reopen"], rep["projection"]["mismatches"], rep["chain"]["status"]), (8, 0, "ok"))
        self.assertEqual(rep["priority_distribution"], {"archive": 36, "queue": 70, "review": 17, "urgent": 2})
        self.assertEqual(ds.pol.active(), {})
        c1 = ds.svc.events(ds.sess("rev"), "C00000001")
        self.assertEqual([(e["seq"], e["event_type"], e["from_state"], e["to_state"], e["actor_kind"], e["basis"]) for e in c1],
                         [(1, "CASE_IMPORTED", None, "CLOSED", "system", "legacy snapshot"), (2, "FACT_RECEIVED", None, None, "system", "")])
        self.assertEqual((c1[0]["occurred_at"], c1[1]["occurred_at"]), ("2025-04-18T22:00:00.000000Z",) * 2)
        self.assertEqual((c1[0]["payload"]["source_db_sha256"], c1[0]["payload"]["legacy_version"]), (rep["source_db_sha256"], 1))
        self.assertEqual(sum(1 for r in ds.con.execute("SELECT payload FROM decision_events WHERE event_type = 'CASE_IMPORTED'")
                             if json.loads(r[0]).get("marker") == "LEGACY_UNEVIDENCED_REOPEN"), 8)
        before_counts = ds.counts()
        again = backfill.run(ds.svc, S.LEGACY_ROOT, S.tmpdir("s04b-"), "t-s04b")
        self.assertEqual((again["imported_now"], again["already_imported"], again["events_written"]), (0, 125, 0))
        after = ds.counts()
        self.assertEqual(after["decision_events"], before_counts["decision_events"])
        self.assertEqual(after["audit_log"], before_counts["audit_log"] + 1)
        self.assertEqual([(a["outcome"], a["details"]["imported_now"]) for a in ds.audit_actions("BACKFILL_RUN")], [("success", 125), ("success", 0)])
        self.assertEqual(S.sha256_file(legacy_db), before)

    def test_TST_HUB_INC05_S05_backfill_is_all_or_nothing(self):
        """S05 (rollback L1): a count mismatch (expected 124) or a forced audit failure leaves the store without a single imported case."""
        ds = self.store()
        with self.assertRaises(E.BackfillMismatch) as cm:
            backfill.run(ds.svc, S.LEGACY_ROOT, S.tmpdir("s05-"), "t-s05", expected=124)
        self.assertEqual(cm.exception.details["imported_total"], 125)
        self.assertEqual((ds.counts()["decision_events"], ds.counts()["case_state"]), (0, 0))
        with mock.patch.object(audit, "_insert", side_effect=sqlite3.OperationalError("forced audit failure (synthetic)")):
            with self.assertRaises(AuditWriteFailed):
                backfill.run(ds.svc, S.LEGACY_ROOT, S.tmpdir("s05b-"), "t-s05b")
        self.assertEqual((ds.counts()["decision_events"], ds.counts()["case_state"]), (0, 0))
        self.assertEqual(ds.audit_actions("BACKFILL_RUN"), [])

    # ---------------------------------------------------------------- integrity
    def test_TST_HUB_INC05_S06_chain_tamper_detected(self):
        """S06 (ADR-005): an offline attacker who drops the triggers and edits or removes an event is detected by the per-case hash chain."""
        ds = self.store()
        ds.mk("C00000001")
        for to in ("UNDER_REVIEW", "ESCALATED", "OPEN"):
            ds.move("C00000001", to)
        self.assertEqual(ds.svc.require_chain()["status"], "ok")
        ds.con.execute("DROP TRIGGER decision_events_no_update")
        ds.con.execute("UPDATE decision_events SET basis = 'tampered' WHERE case_id = 'C00000001' AND seq = 3")
        ds.con.commit()
        rep = ds.svc.verify_chain()
        self.assertEqual((rep["status"], rep["kind"], rep["seq"]), ("broken", "hash_mismatch", 3))
        with self.assertRaises(E.ChainBroken):
            ds.svc.require_chain()
        ds.con.execute("UPDATE decision_events SET basis = 'synthetic' WHERE case_id = 'C00000001' AND seq = 3")
        ds.con.execute("DROP TRIGGER decision_events_no_delete")
        ds.con.execute("DELETE FROM decision_events WHERE case_id = 'C00000001' AND seq = 2")
        ds.con.commit()
        rep = ds.svc.verify_chain()
        self.assertEqual((rep["status"], rep["kind"], rep["seq"]), ("broken", "seq_gap", 3))

    def test_TST_HUB_INC05_S07_database_level_triggers(self):
        """S07: raw INSERT of a Zone H event type as system / without holder_check_ref -> E-GATE-NOT-AUTHORISED; a seq gap -> E-DEC-SEQ-CONFLICT;
        evidence_record, crosswalk_link, crosswalk_link_event and the idempotency ledger reject UPDATE and DELETE; retention trigger scan clean."""
        ds = self.store()
        ds.mk("C00000001")
        ev = ds.evidence("C00000001")
        ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "r", correlation_id="t")
        ds.move("C00000001", "UNDER_REVIEW", idempotency_key="idem-s07")

        def raw(etype, actor_kind, ref, seq):
            return ("INSERT INTO decision_events(event_id, case_id, seq, event_type, from_state, to_state, affects_state, actor, actor_kind,"
                    " occurred_at, recorded_at, basis, evidence_refs, cycle, exception, holder_check_ref, payload, prev_hash, hash)"
                    " VALUES ('EV-RAW', 'C00000001', %d, '%s', 'OPEN', 'CLOSED', 1, 'x', '%s', '2026-10-18T00:00:00.000000Z',"
                    " '2026-10-18T00:00:00.000000Z', '', '[]', 1, 1, %s, '{}', '%s', '%s')" % (seq, etype, actor_kind, ref, "0" * 64, "1" * 64))
        nxt = ds.con.execute("SELECT max(seq) + 1 FROM decision_events WHERE case_id = 'C00000001'").fetchone()[0]
        for sql, code in ((raw("CLOSE_EXCEPTION", "system", "'audit:1'", nxt), "E-GATE-NOT-AUTHORISED"),
                          (raw("DISPOSITION_RECORDED", "human", "NULL", nxt), "E-GATE-NOT-AUTHORISED"),
                          (raw("QA_RELEASE_RECORDED", "rule", "'audit:1'", nxt), "E-GATE-NOT-AUTHORISED"),
                          (raw("CLOSE_EXCEPTION", "human", "'audit:1'", nxt + 3), "E-DEC-SEQ-CONFLICT")):
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                ds.con.execute(sql)
            ds.con.rollback()
            self.assertIn(code, str(cm.exception))
        for sql in ("UPDATE evidence_record SET source = 'x'", "DELETE FROM evidence_record", "UPDATE crosswalk_link SET reason = 'x'",
                    "DELETE FROM crosswalk_link", "UPDATE crosswalk_link_event SET reason = 'x'", "DELETE FROM crosswalk_link_event",
                    "UPDATE decision_idempotency SET body_hash = 'x'", "DELETE FROM decision_idempotency"):
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                ds.con.execute(sql)
            ds.con.rollback()
            self.assertIn("E-DEC-IMMUTABLE", str(cm.exception))
        self.assertEqual(ds.con.execute("SELECT count(*) FROM evidence_record WHERE ev_id = ?", (ev,)).fetchone()[0], 1)
        rep = scan.run(S.CODE_ROOT, ds.con)
        self.assertEqual((rep["deletion_findings"], rep["tables_without_delete_trigger"], rep["clean"]), ([], [], True))

    def test_TST_HUB_INC05_S08_expected_seq_and_errors(self):
        """S08: a stale expected_seq -> E-DEC-SEQ-CONFLICT (nothing stored), the current one succeeds; unknown case, bad id, duplicate create, disabled
        creation, unauthenticated and service callers."""
        ds = self.store()
        ds.mk("C00000001")
        ds.move("C00000001", "UNDER_REVIEW", expected_seq=1)
        n = ds.counts()["decision_events"]
        with self.assertRaises(E.SeqConflict):
            ds.move("C00000001", "ESCALATED", expected_seq=1)
        with self.assertRaises(E.SeqConflict):
            ds.move("C00000001", "ESCALATED", expected_seq=True)
        self.assertEqual(ds.counts()["decision_events"], n)
        self.assertEqual(ds.move("C00000001", "ESCALATED", expected_seq=2)["seq"], 3)
        with self.assertRaises(E.CaseNotFound):
            ds.move("C00000099", "UNDER_REVIEW")
        with self.assertRaises(E.CaseIdInvalid):
            ds.mk("C1")
        with self.assertRaises(E.CaseExists):
            ds.mk("C00000001")
        with self.assertRaises(AuthUnauthenticated):
            ds.svc.transition(None, "C00000001", "OPEN", "x")
        with self.assertRaises(AuthForbidden):
            ds.svc.transition(ds.service_session(), "C00000001", "OPEN", "x")
        with self.assertRaises(AuthForbidden):
            ds.svc.events(ds.service_session(), "C00000001")
        self.assertEqual(ds.audit_actions("AUTHZ_DENIED")[-1]["actor"], "svc-integration")
        self.ds.close()
        ds = self.ds = D.DStore(extra={"case_creation": {"enabled": False}})
        with self.assertRaises(E.CreationDisabled):
            ds.mk("C00000001")
        self.assertEqual(ds.counts()["decision_events"], 0)

    def test_TST_HUB_INC05_S09_projection_rebuild(self):
        """S09 (rollback L1): a damaged case_state projection is detected by verify-projection and rebuilt from the events (audited)."""
        ds = self.store(loaded=True)
        ds.con.execute("UPDATE case_state SET state = 'CLOSED', last_seq = 9 WHERE case_id IN ('C00000003', 'C00000004')")
        ds.con.execute("DELETE FROM case_state WHERE case_id = 'C00000005'")
        ds.con.commit()
        rep = ds.svc.verify_projection()
        self.assertEqual((rep["status"], rep["mismatches"]), ("mismatch", 3))
        self.assertEqual(ds.svc.rebuild_projection(), {"cases": 125})
        rep = ds.svc.verify_projection()
        self.assertEqual((rep["status"], rep["mismatches"], rep["projection_rows"]), ("ok", 0, 125))
        self.assertEqual([a["outcome"] for a in ds.audit_actions("PROJECTION_REBUILT")], ["success"])

    # ---------------------------------------------------------------- CLI over the shipped data
    def test_TST_HUB_INC05_S10_decision_cli_backfill_and_crosswalk(self):
        """S10: `python -m hub.decision` on a sandbox store and the sandbox legacy copy: backfill --priority-check (125 / 250 events, CT-02 36/70/17/2),
        verify-projection 0, verify-chain ok, reopen-invariant (0 violations, 8 marked), crosswalk-run LT-01..LT-05 (42 / 21 / 125 / 173 / 30 links;
        8,394 feed orphans and 1,170 document orphans reported), idempotent re-run."""
        ds = self.store()
        cfg, data = ds.cfg_path, ds.data
        ds.close()
        self.ds = None
        run_dir = S.tmpdir("s10-")
        p = cli("hub.decision", ["backfill", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir, "--priority-check"], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        rep = json.loads(p.stdout)
        self.assertEqual((rep["imported_now"], rep["events_written"], rep["marked_legacy_reopen"]), (125, 250, 8))
        self.assertEqual(rep["priority_distribution"], {"archive": 36, "queue": 70, "review": 17, "urgent": 2})
        self.assertEqual(json.loads(cli("hub.decision", ["verify-projection", "--data-dir", data], cfg).stdout)["mismatches"], 0)
        self.assertEqual(json.loads(cli("hub.decision", ["verify-chain", "--data-dir", data], cfg).stdout), {"cases": 125, "events": 250, "status": "ok"})
        inv = json.loads(cli("hub.decision", ["reopen-invariant", "--data-dir", data], cfg).stdout)
        self.assertEqual((inv["violation_count"], inv["marked_count"]), (0, 8))
        p = cli("hub.decision", ["crosswalk-run", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual(dict((k, v["counts"]["LINKED"]) for k, v in sorted(out["runs"].items())),
                         {"LT-01": 42, "LT-02": 21, "LT-03": 125, "LT-04": 173, "LT-05": 30})
        self.assertEqual(out["active_links"], 391)
        self.assertEqual((out["orphans"]["LT-04"]["orphans"], out["orphans"]["LT-05"]["orphans"], out["orphans"]["LT-01"]["orphans"]), (8394, 1170, 0))
        self.assertEqual(len(out["documents_sha256"]), 64)
        p = cli("hub.decision", ["crosswalk-run", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg)
        again = json.loads(p.stdout)
        self.assertEqual(sum(v["counts"]["LINKED"] for v in again["runs"].values()), 0)
        self.assertEqual(again["active_links"], 391)
        p = cli("hub.decision", ["backfill", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run_dir], cfg)
        self.assertEqual((json.loads(p.stdout)["imported_now"], json.loads(p.stdout)["already_imported"]), (0, 125))
        v = H.admin(["verify-audit", "--data-dir", data], cfg)
        self.assertEqual(v.returncode, 0, v.stderr)

    def test_TST_HUB_INC05_S11_crosswalk_rule_rerun_respects_retraction(self):
        """S11: a rule link retracted by a human is not silently re-created by a rule re-run (SKIPPED_RETRACTED); an ambiguous target and a missing key
        create nothing; LT-05 reads 1,200 documents from the sandbox copy."""
        ds = self.store()
        items, targets = [("DEV00000001", "BT00000001")], {"BT00000001": ["BT00000001"]}
        self.assertEqual(ds.cw.run_rule("LT-01", items, targets, "r1", "t")["counts"]["LINKED"], 1)
        link = ds.cw.active_links()[0]
        ds.cw.retract(ds.sess("rev"), link["link_id"], "rule link judged wrong (synthetic)", correlation_id="t")
        r = ds.cw.run_rule("LT-01", items, targets, "r2", "t")
        self.assertEqual((r["counts"]["SKIPPED_RETRACTED"], r["counts"]["LINKED"], ds.cw.count_active()), (1, 0, 0))
        r = ds.cw.run_rule("LT-01", [("DEV00000002", "BT00000002"), ("DEV00000003", None), ("DEV00000004", "  ")],
                           {"BT00000002": ["BT00000002", "BT00000002-dup"]}, "r3", "t", return_outcomes=True)
        self.assertEqual(dict(r["outcomes"]), {"DEV00000002": "AMBIGUOUS_MATCH", "DEV00000003": "NO_KEY", "DEV00000004": "NO_KEY"})
        self.assertEqual((r["orphans"], ds.cw.count_active()), (3, 0))
        docs, sha = sources.document_items(S.LEGACY_ROOT)
        self.assertEqual(len(docs), 1200)
        self.assertEqual(len(sha), 64)

    # ---------------------------------------------------------------- static / settings
    def test_TST_HUB_INC05_S12_import_graph_and_no_ai(self):
        """S12 (BEH-GATE-02 slice, DEV-34): the INC-04 local gate is imported only by the frozen hub/policy/service.py; hub/policy and hub/crosswalk do
        not import hub.gate; hub/decision uses hub.gate.service only; no INC-05 package imports a network, model or fuzzy-matching library."""
        importers = {}
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(d, fn)
                rel = os.path.relpath(p, S.CODE_ROOT)
                for n in ast.walk(ast.parse(open(p, encoding="utf-8").read())):
                    names = []
                    if isinstance(n, ast.Import):
                        names = [a.name for a in n.names]
                    elif isinstance(n, ast.ImportFrom) and n.module:
                        names = [n.module] + ["%s.%s" % (n.module, a.name) for a in n.names]
                    for m in names:
                        importers.setdefault(m, set()).add(rel)
        self.assertEqual(sorted(importers.get("hub.policy.gate", [])), [os.path.join("hub", "policy", "service.py")])
        for m, files in importers.items():
            if m == "hub.gate" or m.startswith("hub.gate."):
                self.assertEqual([f for f in files if f.startswith(os.path.join("hub", "policy")) or f.startswith(os.path.join("hub", "crosswalk"))], [], m)
        for m, files in importers.items():
            if m.split(".")[0] in ("requests", "urllib", "http", "socket", "openai", "anthropic", "langchain", "difflib"):
                self.assertEqual([f for f in files if f.startswith(("hub/decision", "hub/crosswalk", "hub/gate").__getitem__(0)[:0] or "hub")
                                  and any(f.startswith(os.path.join("hub", x)) for x in ("decision", "crosswalk", "gate"))], [], m)

    def test_TST_HUB_INC05_S13_settings_and_time(self):
        """S13: decision settings reject unknown keys and bad values; timestamps normalise to the canonical form and reject anything else."""
        from hub.decision import settings as dsettings
        self.assertEqual(dsettings.resolve(None)["closure"]["unconfigured_behaviour"], "treat_label_CLOSED_as_closing")
        for bad in ({"closure": {"nope": 1}}, {"case_creation": {"enabled": "yes"}}, {"workflow": {"transition_table": "x"}}, {"facts": "human_only"}):
            with self.assertRaises(ConfigInvalid):
                dsettings.resolve(bad)
        self.assertEqual(norm_ts("2026-10-18T10:00:00Z"), "2026-10-18T10:00:00.000000Z")
        self.assertEqual(norm_ts("2026-10-18T10:00:00+00:00"), "2026-10-18T10:00:00.000000Z")
        self.assertEqual(norm_ts("2026-10-18T12:00:00+02:00"), "2026-10-18T10:00:00.000000Z")
        self.assertEqual(norm_ts("2026-10-18T10:00:00.5Z"), "2026-10-18T10:00:00.500000Z")
        for bad in ("2026-10-18", "10:00", "", None, 5):
            with self.assertRaises(E.TimeOrder):
                norm_ts(bad)

    def test_TST_HUB_INC05_S14_attached_evidence_event_and_role_checks(self):
        """S14: the EVIDENCE_ATTACHED event resolves its own evidence on retrieval; evidence records are validated; reads need a reader role."""
        ds = self.store()
        ds.mk("C00000001")
        a = ds.svc.attach_evidence(ds.sess("rev"), "C00000001", "external_ref", "ext-system", "REF-1", source_hash="a" * 64, access_level="operations",
                                   note="note", correlation_id="t")
        got = ds.svc.event_with_evidence(ds.sess("holder-1"), a["event_id"])
        self.assertEqual(got["evidence"][0]["ev_id"], a["evidence"]["ev_id"])
        self.assertEqual((got["event"]["affects_state"], got["event"]["to_state"]), (False, None))
        for kw in ({"kind": "email"}, {"access_level": "public"}, {"source": ""}, {"source_hash": "xyz"}):
            args = dict(kind="document", source="s", source_ref="r", access_level="quality", source_hash=None)
            args.update(kw)
            with self.assertRaises(E.FieldTooLong):
                ds.svc.attach_evidence(ds.sess("rev"), "C00000001", correlation_id="t", **args)
        with self.assertRaises(AuthForbidden):
            ds.svc.event_with_evidence(ds.service_session(), a["event_id"])
        with self.assertRaises(E.CaseNotFound):
            ds.svc.event_with_evidence(ds.sess("rev"), "EV-99999999")
        self.assertEqual(ds.counts()["evidence_record"], 1)


if __name__ == "__main__":
    unittest.main()
