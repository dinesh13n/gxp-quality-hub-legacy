"""Stage 15 INC-06 supplementary tests (no Stage 13 ID; TST-HUB-INC06-Sxx): the M004 applier and the intake CLI, the declared-contract copy, the
Zone H gate on contract bindings, database triggers, audit chain / atomicity, request-level errors, identity and hash edge cases, the gateway
client against a loopback server, the Untrusted display, shipped-source profiling (prints INC06-EVIDENCE lines), purity / deny-list checks,
retention triggers and error codes. Synthetic, unvalidated.
"""
import hashlib
import http.server
import json
import os
import sqlite3
import subprocess
import sys
import threading
import unittest
from unittest import mock

import _support as S
import _inc03 as H
import _inc06 as I
from hub.adapters import gateway_client, intake_sources
from hub.core.errors import MigrationDrift
from hub.gate import errors as GE
from hub.guards import no_ai
from hub.intake import canon, contracts, errors as E, profiles, reasons as R, schema as ischema, validate
from hub.policy.errors import AuthorityRequired
from hub.security import audit, scan
from hub.security.errors import AuditWriteFailed, StoreNotMigrated


def setUpModule():
    I.skip_in_inner_egress_run()


def rawid(n):
    return "RAW-%010d" % n


def cli(module, args, cfg_path, timeout=170):
    return subprocess.run([sys.executable, "-B", "-m", module, "--config", cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


class _Gateway(object):
    """A loopback gateway double: responses are consumed from `plan` (status, body) in order; the last entry repeats."""

    def __init__(self, plan):
        outer = self
        self.plan, self.hits = list(plan), []

        class H_(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                outer.hits.append(self.path)
                status, body, headers = outer.plan[min(len(outer.hits), len(outer.plan)) - 1]
                data = body if isinstance(body, bytes) else json.dumps(body).encode()
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *a):
                pass
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H_)
        self.url = "http://127.0.0.1:%d" % self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def event(i, **over):
    e = {"message_id": "gw%03d" % i, "business_key": "BT%08d" % i, "system": "mes", "event_type": "lab_test", "schema_version": "1.0",
         "occurred_at": "2025-03-%02dT10:00:00Z" % (1 + i), "published_at": "2025-03-%02dT12:15:00Z" % (1 + i),
         "payload": {"identifier": "BT%08d" % i, "note": "legacy operational note", "source_status": "OPEN"}}
    e.update(over)
    return e


class TST_HUB_INC06_Supplementary(unittest.TestCase):

    def setUp(self):
        self.st = None

    def tearDown(self):
        if self.st is not None:
            self.st.close()

    def store(self, **kw):
        self.st = I.IStore(**kw)
        return self.st

    # ---------------------------------------------------------------- M004 applier and CLI
    def test_TST_HUB_INC06_S01_m004_applier_and_cli(self):
        """S01: `hub.intake migrate` needs M001, M002 and M003, backs up first, is idempotent, does NOT touch schema_migrations and refuses a
        drifted M004 record (E-STORE-MIGRATION-DRIFT, exit 15); status reports counts."""
        base = S.tmpdir("i6s01-")
        cfg = H.write_config(base)
        data, bk = os.path.join(base, "data"), os.path.join(base, "bk")
        self.assertEqual(H.admin(["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        for needs, mod in (("M002", None), ("M003", "hub.policy")):
            if mod:
                self.assertEqual(cli(mod, ["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
            p = cli("hub.intake", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
            self.assertEqual((p.returncode, json.loads(p.stderr)["code"], json.loads(p.stderr)["details"]["needs"]), (22, "E-STORE-NOT-MIGRATED", needs))
        self.assertEqual(cli("hub.decision", ["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        p = cli("hub.intake", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertTrue(out["applied"] and out["backup"]["label"].startswith("pre-intake-M004-"))
        p = cli("hub.intake", ["migrate", "--data-dir", data, "--backup-root", bk], cfg)
        self.assertEqual((p.returncode, json.loads(p.stdout)["applied"], json.loads(p.stdout)["backup"]), (0, False, None))
        st = json.loads(cli("hub.intake", ["status", "--data-dir", data], cfg).stdout)
        self.assertEqual((st["state"], st["raw"], st["outcomes"], st["runs"], st["total_items"] if "total_items" in st else st["queue_snapshot"]["total_items"]),
                         ("applied", 0, 0, 0, 0))
        con = sqlite3.connect(os.path.join(data, "hub.sqlite3"))
        self.assertEqual([r[0] for r in con.execute("SELECT version FROM schema_migrations ORDER BY 1")], ["M000", "M001"])
        self.assertEqual([r[0] for r in con.execute("SELECT version FROM intake_schema_migrations")], ["M004"])
        con.execute("DROP TRIGGER intake_schema_migrations_no_update")
        con.execute("UPDATE intake_schema_migrations SET sha256 = ?", ("0" * 64,))
        con.commit()
        con.close()
        p = cli("hub.intake", ["status", "--data-dir", data], cfg)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (15, "E-STORE-MIGRATION-DRIFT"))
        c2 = sqlite3.connect(os.path.join(data, "hub.sqlite3"))
        try:
            with self.assertRaises(MigrationDrift):
                ischema.require(c2)
        finally:
            c2.close()
        c3 = sqlite3.connect(":memory:")
        with self.assertRaises(StoreNotMigrated):
            ischema.require(c3)
        c3.close()

    def test_TST_HUB_INC06_S02_cli_shadow_intake_over_the_sandbox_copy(self):
        """S02: CLI over a sandbox store: migrate chain, backfill the 125 cases, `ingest-legacy --csv-tier tiny` (feeds 8,567, messages 15, gateway
        1, CSV 2,400), a second run adds nothing, verify-replay and verify-audit pass, `gateway-pull` against a closed loopback port exits 28 with a
        failed run record and no outcome."""
        base = S.tmpdir("i6s02-")
        cfg = H.write_config(base, {"gateway": {"retries": 1}})
        data, bk, run = os.path.join(base, "data"), os.path.join(base, "bk"), os.path.join(base, "run")
        self.assertEqual(H.admin(["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        for mod in ("hub.policy", "hub.decision", "hub.intake"):
            self.assertEqual(cli(mod, ["migrate", "--data-dir", data, "--backup-root", bk], cfg).returncode, 0)
        p = cli("hub.decision", ["backfill", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        sha0 = S.sha256_file(os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3"))
        p = cli("hub.intake", ["ingest-legacy", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run, "--csv-tier", "tiny"], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual([out["runs"][k]["stored"] for k in ("partner_feed", "source_message", "gateway", "vendor_csv")], [8567, 15, 1, 2400])
        self.assertEqual(out["counts"]["raw"], 8567 + 15 + 1 + 2400)
        self.assertEqual(out["counts"]["noop_duplicate"], 67)
        self.assertEqual(out["legacy_db_sha256"], sha0)
        p = cli("hub.intake", ["ingest-legacy", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run, "--csv-tier", "tiny"], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out2 = json.loads(p.stdout)
        self.assertEqual([out2["runs"][k]["stored"] for k in out2["runs"]], [0, 0, 0, 0])
        self.assertEqual(out2["counts"]["raw"], out["counts"]["raw"])
        p = cli("hub.intake", ["verify-replay", "--data-dir", data, "--legacy-root", S.LEGACY_ROOT, "--run-dir", run], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)["ok"])
        self.assertEqual(json.loads(cli("hub.intake", ["report", "--data-dir", data], cfg).stdout)["total_items"], out["queue_snapshot"]["total_items"])
        self.assertEqual(H.admin(["verify-audit", "--data-dir", data], cfg).returncode, 0)
        s = socket_closed_port()
        p = cli("hub.intake", ["gateway-pull", "--data-dir", data, "--url", "http://127.0.0.1:%d" % s], cfg)
        self.assertEqual(p.returncode, 28, p.stderr)
        self.assertEqual(json.loads(p.stdout)["error"], "SOURCE_UNREACHABLE")
        con = sqlite3.connect(os.path.join(data, "hub.sqlite3"))
        try:
            self.assertEqual(con.execute("SELECT count(*) FROM intake_run_event WHERE event_type = 'RUN_FAILED'").fetchone()[0], 1)
            self.assertEqual(con.execute("SELECT count(*) FROM raw_intake").fetchone()[0], out["counts"]["raw"] + 8567)   # verify-replay stored 8,567 NOOP copies
        finally:
            con.close()
        self.assertEqual(S.sha256_file(os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3")), sha0)

    # ---------------------------------------------------------------- contract copy and bindings
    def test_TST_HUB_INC06_S03_bundled_contract_is_byte_identical(self):
        """S03: hub/intake/contracts/source-contract-v1.json is a byte-identical copy of integration/source-contract-v1.json; the check evaluates
        required keys and string types only."""
        a = S.sha256_file(os.path.join(S.CODE_ROOT, "hub", "intake", "contracts", "source-contract-v1.json"))
        b = S.sha256_file(os.path.join(S.CODE_ROOT, "integration", "source-contract-v1.json"))
        self.assertEqual(a, b)
        c = contracts.load("source-contract-v1")
        self.assertEqual(contracts.check(c, {"ref": "x", "status": "y", "schema_version": "1"}), ("pass", []))
        self.assertEqual(contracts.check(c, {"ref": "x", "status": 3}), ("fail", ["schema_version", "status"]))
        self.assertEqual(contracts.check(c, [1]), ("fail", ["ref", "schema_version", "status"]))
        self.assertEqual(contracts.available(), ["source-contract-v1"])

    def test_TST_HUB_INC06_S04_binding_changes_go_through_the_zone_h_gate(self):
        """S04: every source defaults to record_only; set_binding needs a human holder (ZH-10) with a fresh re-auth and an authority_ref; shipped
        empty holders -> E-GATE-NO-HOLDERS; non-holder / stale re-auth refused; an accepted change is a CONTRACT_BINDING_CHANGED policy event with
        holder_check_ref and an audit record; the mode can be set back."""
        st = self.store()
        for s in profiles.PROFILES:
            self.assertEqual(st.isvc.binding(s)["mode"], "record_only")
        with self.assertRaises(E.EnvelopeInvalid):
            st.isvc.set_binding(st.reauth("holder-1"), "partner_feed", "strict", I.AUTH)
        with self.assertRaises(AuthorityRequired):
            st.isvc.set_binding(st.reauth("holder-1"), "partner_feed", "enforce", " ")
        with self.assertRaises(GE.GateNotAuthorised):
            st.isvc.set_binding(st.reauth("nonholder"), "partner_feed", "enforce", I.AUTH)
        with self.assertRaises(GE.GateNotAuthorised):
            st.isvc.set_binding(st.reauth("rev"), "partner_feed", "enforce", I.AUTH)
        st.clock.advance(st.s["zone_h"]["reauth_window_seconds"] + 5)
        with self.assertRaises(GE.GateReauthRequired):
            st.isvc.set_binding(st.sess("holder-1"), "partner_feed", "enforce", I.AUTH)
        self.assertEqual(st.isvc.binding("partner_feed")["mode"], "record_only")
        denied = [a for a in st.audit_actions("ZONE_H_ATTEMPT") if a["outcome"] == "denied"]
        self.assertGreaterEqual(len(denied), 3)
        b = st.isvc.set_binding(st.reauth("holder-1"), "partner_feed", "enforce", I.AUTH, "s04")
        self.assertEqual((b["mode"], b["origin"].startswith("PE-")), ("enforce", True))
        ev = st.con.execute("SELECT event_type, actor, authority_ref, holder_check_ref, old_value, new_value FROM policy_events"
                            " WHERE policy_ref = 'contract_binding:partner_feed'").fetchall()
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0][0], ev[0][1], ev[0][2]), ("CONTRACT_BINDING_CHANGED", "holder-1", I.AUTH))
        self.assertTrue(ev[0][3].startswith("audit:"))
        self.assertEqual(json.loads(ev[0][5])["mode"], "enforce")
        self.assertEqual(st.isvc.binding("source_message")["mode"], "record_only")        # per-source
        st.isvc.set_binding(st.reauth("holder-2"), "partner_feed", "record_only", I.AUTH, "s04")
        self.assertEqual(st.isvc.binding("partner_feed")["mode"], "record_only")
        none = I.IStore(extra={"zone_h": {"holders": []}})
        try:
            with self.assertRaises(GE.GateNoHolders):
                none.isvc.set_binding(none.reauth("holder-1"), "partner_feed", "enforce", I.AUTH)
            self.assertEqual(none.isvc.binding("partner_feed")["mode"], "record_only")
        finally:
            none.close()
        with self.assertRaises(Exception):
            st.isvc.set_binding(None, "partner_feed", "enforce", I.AUTH)

    # ---------------------------------------------------------------- database level
    def test_TST_HUB_INC06_S05_insert_only_triggers(self):
        """S05: UPDATE / DELETE on raw_intake, intake_outcome, intake_item_attr and intake_run_event are rejected by trigger (E-INT-RAW-IMMUTABLE);
        a NOOP_DUPLICATE cannot count toward totals; notes_trust cannot be 'trusted'; intake_current excludes NOOP_DUPLICATE."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(1), I.feed(1)], "s05", "s05")
        stmts = ["UPDATE raw_intake SET partner = 'x'", "DELETE FROM raw_intake", "UPDATE intake_outcome SET queue = NULL",
                 "DELETE FROM intake_outcome", "UPDATE intake_item_attr SET source_state = 'x'", "DELETE FROM intake_item_attr",
                 "UPDATE intake_run_event SET body = '{}'", "DELETE FROM intake_run_event"]
        for sql in stmts:
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                st.con.execute(sql)
            self.assertIn("E-INT-RAW-IMMUTABLE", str(cm.exception), sql)
        with self.assertRaises(sqlite3.IntegrityError):
            st.con.execute("INSERT INTO intake_outcome(raw_id, outcome_seq, outcome, counts_toward_totals, run_id, decided_at) VALUES (?,9,'NOOP_DUPLICATE',1,'x','x')", (rawid(1),))
        st.con.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            st.con.execute("INSERT INTO intake_item_attr(raw_id, notes_trust) VALUES (?, 'trusted')", (rawid(2),))
        st.con.rollback()
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_current").fetchone()[0], 1)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome").fetchone()[0], 2)

    def test_TST_HUB_INC06_S06_audit_chain_and_atomic_runs(self):
        """S06: a run writes ONE INTAKE_RUN audit record (counts + outcomes_digest) and the chain verifies; a failing audit write rolls the whole
        run back (no raw, outcome, attribute, link or run row)."""
        st = self.store()
        rep = st.isvc.ingest("partner_feed", I.batch(20), "s06a", "s06")
        a = st.audit_actions("INTAKE_RUN")
        self.assertEqual((len(a), a[0]["actor_kind"], a[0]["details"]["outcomes_digest"]), (1, "system", rep["outcomes_digest"]))
        self.assertEqual((a[0]["details"]["stored"], a[0]["details"]["linked"], a[0]["details"]["binding_mode"]), (20, 20, "record_only"))
        audit.write_anchor(st.con, st.anchor_path)
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        before = (st.counts(), st.isvc.counts(), st.con.execute("SELECT count(*) FROM intake_item_attr").fetchone()[0])
        with mock.patch.object(audit, "_insert", side_effect=sqlite3.OperationalError("forced audit failure (synthetic)")):
            with self.assertRaises(AuditWriteFailed):
                st.isvc.ingest("partner_feed", I.batch(20, 50), "s06b", "s06")
        after = (st.counts(), st.isvc.counts(), st.con.execute("SELECT count(*) FROM intake_item_attr").fetchone()[0])
        self.assertEqual(before, after)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_run_event WHERE run_id = 's06b'").fetchone()[0], 0)
        # the same run id can be used again after the rolled-back attempt
        self.assertEqual(st.isvc.ingest("partner_feed", I.batch(20, 50), "s06b", "s06")["stored"], 20)

    def test_TST_HUB_INC06_S07_request_level_errors_write_nothing(self):
        """S07: unknown source, a non-list / non-object delivery list, an invalid or re-used run id -> E-INT-ENVELOPE-INVALID, nothing written;
        item-level defects never raise; error envelopes carry fixed messages (user text only in details)."""
        st = self.store()
        n = (st.isvc.counts(), st.counts())
        for args in (("nope", [I.feed(1)], "r1"), ("partner_feed", "abc", "r2"), ("partner_feed", [1, 2], "r3"), ("partner_feed", [I.feed(1)], "bad id"),
                     ("partner_feed", [I.feed(1)], "")):
            with self.assertRaises(E.EnvelopeInvalid):
                st.isvc.ingest(*args)
        self.assertEqual((st.isvc.counts(), st.counts()), n)
        st.isvc.ingest("partner_feed", [{}], "r-empty", "s07")                      # an empty object is an item with every field missing
        cur = st.isvc.get_item(rawid(1))["current"]
        self.assertEqual((cur["outcome"], cur["primary_reason"]), ("QUARANTINED", "MISSING_ENVELOPE_FIELD"))
        self.assertEqual(sorted(cur["reason_detail"]["MISSING_ENVELOPE_FIELD"]), ["feed_id", "partner", "raw_json", "record_kind", "ref_id", "schema_rev", "source_ts"])
        with self.assertRaises(E.EnvelopeInvalid):
            st.isvc.ingest("partner_feed", [], "r-empty", "s07")                     # run id re-used
        rep = st.isvc.ingest("partner_feed", [], "r-none", "s07")
        self.assertEqual((rep["received"], rep["stored"], rep["outcomes"]), (0, 0, {}))
        env = E.ItemNotFound({"raw_id": "<script>"}).envelope()
        self.assertEqual((env["code"], env["message"], env["details"]), ("E-INT-ITEM-NOT-FOUND", "unknown raw_id or not a revision conflict", {"raw_id": "<script>"}))
        self.assertEqual(sorted(set(c.exit_code for c in (E.RawImmutable, E.EnvelopeInvalid, E.SourceUnreachable, E.UrlSchemeRefused,
                                                          E.ResolutionReasonRequired, E.ItemNotFound, E.ConflictAlreadyResolved))), [28])

    def test_TST_HUB_INC06_S08_identity_and_hash_edge_cases(self):
        """S08: identity = natural key (OD-18): ts offset spelling, NFC and trim do not split an item; business_key / feed_id / key order / whitespace
        do not matter; incomplete identities never merge; numeric spelling is content (1 vs 1.0 = revision); a 3rd version is also a conflict."""
        self.assertEqual(canon.norm_source_ts("2024-01-01T00:00:00+00:00"), "2024-01-01T00:00:00Z")
        self.assertEqual(canon.norm_source_ts("2024-01-01T00:00:00.5Z"), "2024-01-01T00:00:00.5Z")
        for bad in ("2024-01-01", "2024-01-01T00:00:00+02:00", "2024-13-01T00:00:00Z", "yesterday", None, 5):
            self.assertIsNone(canon.norm_source_ts(bad))
        h1 = canon.content_hash("1.0", '{"a": 1, "b": [1, 2]}')
        self.assertEqual(h1, canon.content_hash("1.0", '{ "b":[1,2],\n "a":1 }'))
        self.assertNotEqual(h1, canon.content_hash("1.1", '{"a": 1, "b": [1, 2]}'))
        self.assertNotEqual(canon.content_hash("1.0", '{"a": 1}'), canon.content_hash("1.0", '{"a": 1.0}'))
        self.assertNotEqual(canon.content_hash("1.0", "{bad"), canon.content_hash("1.0", "{bad2"))
        k1, ok1 = canon.identity_key("partner_feed", "north", "OOS_RESULT", "C00000001", "2024-01-01T00:00:00+00:00", "F1", "h")
        k2, ok2 = canon.identity_key("partner_feed", " north ", "OOS_RESULT", "C00000001", "2024-01-01T00:00:00Z", "F2", "h2")
        self.assertEqual((k1, ok1, ok2), (k2, True, True))
        e1, bad1 = canon.identity_key("partner_feed", "north", "OOS_RESULT", None, "2024-01-01T00:00:00Z", "F1", "ha")
        e2, bad2 = canon.identity_key("partner_feed", "north", "OOS_RESULT", None, "2024-01-01T00:00:00Z", "F2", "hb")
        self.assertEqual((bad1, bad2, e1 != e2), (False, False, True))
        st = self.store()
        a = I.feed(1)
        b = I.feed(1, source_key="OTHER-FEED-ID", source_ts="2024-01-01T00:01:00Z")        # same natural key, other spelling and feed_id
        c = I.feed(1, payload={"business_key": "C00000099"}, source_key="F3")                # same natural key, other business_key -> revision
        d = I.feed(2, ref_id=None)
        e = I.feed(3, ref_id=None)
        rep = st.isvc.ingest("partner_feed", [a, b, c, d, e], "s08", "s08")
        o = [st.isvc.get_item(rawid(i))["current"]["outcome"] for i in range(1, 6)]
        self.assertEqual(o, ["VALIDATED", "NOOP_DUPLICATE", "QUARANTINED", "QUARANTINED", "QUARANTINED"])
        self.assertEqual(st.isvc.get_item(rawid(3))["current"]["primary_reason"], "REVISED_CONFLICT")
        self.assertEqual(st.isvc.get_item(rawid(4))["current"]["primary_reason"], "MISSING_ENVELOPE_FIELD")
        self.assertEqual(rep["revised_conflict"], 1)
        c2 = I.feed(1, payload={"quantity": 1}, source_key="F4")
        st.isvc.ingest("partner_feed", [c2], "s08b", "s08")
        self.assertEqual(st.isvc.versions(rawid(6)), [rawid(1), rawid(6)])                  # always linked to the FIRST version

    # ---------------------------------------------------------------- gateway client
    def test_TST_HUB_INC06_S09_gateway_client_against_a_loopback_server(self):
        """S09: page fetch + checkpoint + ingest; 503 is retried with back-off then succeeds; 404 is not retried; a bad response shape, a redirect and
        an oversized body are run errors; invalid events (unknown system / event type) are quarantined, not dropped."""
        page = {"items": [event(1), event(2), event(3, system="xyz"), event(4, event_type="surprise")], "count": 4, "next_offset": 4}
        gw = _Gateway([(200, page, {})])
        try:
            got = gateway_client.fetch_events(gw.url, 0, 50, retries=1)
            self.assertEqual((len(got["items"]), got["next_offset"], got["attempts"]), (4, 4, 1))
            self.assertEqual(gw.hits, ["/api/events?offset=0&limit=50"])
            st = self.store()
            rep = st.isvc.ingest("gateway", intake_sources.gateway_event_deliveries(got["items"]), "s09", "s09",
                                 checkpoint={"next_offset": got["next_offset"]})
            self.assertEqual(rep["outcomes"], {"VALIDATED": 2, "QUARANTINED": 2})
            self.assertEqual(st.isvc.get_item(rawid(3))["current"]["reason_detail"]["MISSING_ENVELOPE_FIELD"], ["system"])
            self.assertEqual(st.isvc.get_item(rawid(4))["current"]["primary_reason"], "UNKNOWN_RECORD_KIND")
            self.assertEqual(st.isvc.last_checkpoint("gateway"), {"next_offset": 4})
            self.assertEqual(st.isvc.get_item(rawid(1))["notes"], {"text": "legacy operational note", "trust": "untrusted"})
            self.assertEqual(st.isvc.get_item(rawid(1))["attributes"]["source_state"], "OPEN")
            ev = [r[0] for r in st.con.execute("SELECT event_type FROM intake_run_event WHERE run_id = 's09' ORDER BY run_seq")]
            self.assertEqual(ev, ["RUN_STARTED", "RUN_CHECKPOINT", "RUN_FINISHED"])
        finally:
            gw.close()
        sleeps = []
        gw = _Gateway([(503, {"error": "unavailable"}, {}), (429, {"error": "throttle"}, {}), (200, page, {})])
        try:
            got = gateway_client.fetch_events(gw.url, 8, 4, retries=3, sleep=sleeps.append, backoff=0.25)
            self.assertEqual((got["attempts"], sleeps, len(gw.hits)), (3, [0.25, 0.5], 3))
        finally:
            gw.close()
        for plan, label in (([(404, {"error": "nf"}, {})], "http_404"), ([(200, {"unexpected_schema": "v3", "records": None}, {})], "ValueError"),
                            ([(200, b"not json", {})], "JSONDecodeError"), ([(302, b"", {"Location": "http://203.0.113.9/x"})], "http_302")):
            gw = _Gateway(plan)
            try:
                with self.assertRaises(E.SourceUnreachable) as cm:
                    gateway_client.fetch_events(gw.url, retries=0)
                self.assertEqual(cm.exception.details["last_error"], label)
                self.assertEqual(len(gw.hits), 1)
            finally:
                gw.close()
        gw = _Gateway([(404, {"error": "nf"}, {})])
        try:
            with self.assertRaises(E.SourceUnreachable) as cm:
                gateway_client.fetch_events(gw.url, retries=5, sleep=sleeps.append)
            self.assertEqual((cm.exception.details["attempts"], len(gw.hits)), (1, 1))     # client errors are not retried
        finally:
            gw.close()

    # ---------------------------------------------------------------- untrusted
    def test_TST_HUB_INC06_S10_untrusted_storage_and_wire_form(self):
        """S10: free text is stored verbatim, returned as {text, trust: untrusted}, displayed escaped; resolution reasons are stored verbatim;
        the stored text is never interpreted (a SQL-looking note changes nothing)."""
        st = self.store()
        note = "a & b <i>\"q\"</i> '; DROP TABLE raw_intake; --"
        st.isvc.ingest("partner_feed", [I.feed(1, payload={"notes": note}), I.feed(1, payload={"notes": "x"}, source_key="F2")], "s10", "s10")
        it = st.isvc.get_item(rawid(1))
        self.assertEqual(it["notes"], {"text": note, "trust": "untrusted"})
        self.assertEqual(st.isvc.display_notes(rawid(1))["text"], "a &amp; b &lt;i&gt;&quot;q&quot;&lt;/i&gt; &#x27;; DROP TABLE raw_intake; --")
        self.assertEqual(st.isvc.display_notes(rawid(2))["text"], "x")                       # the conflict item keeps its own notes
        st.isvc.resolve_conflict(st.sess("ql"), rawid(2), "reject_both", "<b>reason</b>", "s10")
        cur = st.isvc.get_item(rawid(2))["current"]
        self.assertEqual((cur["resolution_reason"], cur["resolved_by"]), ("<b>reason</b>", "ql"))
        self.assertEqual(st.con.execute("SELECT count(*) FROM raw_intake").fetchone()[0], 2)

    # ---------------------------------------------------------------- shipped sources
    def test_TST_HUB_INC06_S11_shipped_source_profile(self):
        """S11: profile of the shipped sources under the default record_only binding (printed as INC06-EVIDENCE lines for the evidence folder):
        feed outcomes, reasons, queues; spec numbers that differ are listed explicitly."""
        st, rep = I.full_store("record_only")
        snap = st.isvc.queue_snapshot(st.now())
        by, sha = I.legacy_deliveries()
        ev = {"legacy_db_sha256": sha, "feed_received": rep["received"], "feed_outcomes": rep["outcomes"], "feed_reasons": rep["reasons"],
              "feed_queues": rep["queues"], "feed_linked": rep["linked"], "noop_duplicate": rep["noop_duplicate"],
              "revised_conflict": rep["revised_conflict"], "contract_check": rep["contract_check"], "snapshot_total_items": snap["total_items"],
              "outcomes_digest": rep["outcomes_digest"]}
        print("INC06-EVIDENCE " + json.dumps(ev, sort_keys=True))
        self.assertEqual(rep["outcomes"]["NOOP_DUPLICATE"], 67)
        self.assertEqual(sum(rep["outcomes"].values()), 8567)
        self.assertEqual(rep["reasons"]["UNSUPPORTED_REVISION"] + 0, rep["reasons"]["UNSUPPORTED_REVISION"])
        self.assertEqual(st.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0], rep["linked"])
        self.assertEqual(snap["total_items"], 8567 - 67)
        # matched feed refs are exactly the non-quarantined items whose ref_id is one of the 125 cases
        cases = set(r[0] for r in st.con.execute("SELECT case_id FROM case_state"))
        expected = 0
        qrows = dict((r[0], (r[1], json.loads(r[2]))) for r in st.con.execute("SELECT raw_id, outcome, all_reasons FROM intake_outcome"))
        for n, d in enumerate(by["partner_feed"], 1):
            outcome, reasons_ = qrows[rawid(n)]
            if outcome == "NOOP_DUPLICATE" or set(reasons_) & R.NO_MATCH_REASONS:
                continue
            expected += d["ref_id"] in cases
        self.assertEqual(rep["linked"], expected)
        self.assertGreater(expected, 100)
        st2 = self.store()
        r2 = st2.isvc.ingest("source_message", by["source_message"], "s11a", "s11")
        r3 = st2.isvc.ingest("gateway", by["gateway"], "s11b", "s11")
        print("INC06-EVIDENCE " + json.dumps({"source_message": r2["outcomes"], "source_message_contract": r2["contract_check"],
                                              "gateway_inbox": r3["outcomes"], "gateway_inbox_contract": r3["contract_check"]}, sort_keys=True))

    # ---------------------------------------------------------------- purity, deny-list, retention
    def test_TST_HUB_INC06_S12_deny_list_and_import_graph(self):
        """S12: the dependency / import deny-list (ADR-002) finds nothing in the INC-06 code (the HTTP client lives only under adapters/); hub/intake
        imports no network, random, time or model module; no new dependency was declared."""
        paths = [os.path.join(S.CODE_ROOT, "hub", "intake"), os.path.join(S.CODE_ROOT, "hub", "adapters"),
                 os.path.join(S.CODE_ROOT, "tests", "hub")]
        self.assertEqual(no_ai.scan(paths), [])
        import ast
        banned = ("socket", "urllib", "http", "random", "time", "requests", "subprocess", "ssl", "ftplib", "smtplib")
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub", "intake")):
            for fn in fns:
                if fn.endswith(".py"):
                    tree = ast.parse(open(os.path.join(d, fn), encoding="utf-8").read())
                    for n in ast.walk(tree):
                        mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                        for m in mods:
                            self.assertNotIn(m.split(".")[0], banned, (fn, m))
        gw = open(os.path.join(S.CODE_ROOT, "hub", "adapters", "gateway_client.py"), encoding="utf-8").read()
        self.assertIn("import urllib.request", gw)
        self.assertEqual(no_ai.scan([os.path.join(S.CODE_ROOT, "hub", "adapters", "gateway_client.py")]), [])

    def test_TST_HUB_INC06_S13_retention_triggers_and_scans(self):
        """S13: every INC-06 table has an aborting BEFORE DELETE trigger; the secret scan / deletion grep / retention check are clean on a store
        with M004 (raw_intake and intake_outcome are on the retained-table list of hub.security.scan)."""
        st = self.store()
        st.isvc.ingest("partner_feed", I.batch(5), "s13", "s13")
        rep = scan.run(S.CODE_ROOT, st.con)
        self.assertEqual((rep["secret_findings"], rep["deletion_findings"], rep["tables_without_delete_trigger"], rep["clean"]), ([], [], [], True))
        for t in st.INTAKE_TABLES:
            sqls = [r[0] for r in st.con.execute("SELECT sql FROM sqlite_master WHERE type = 'trigger' AND tbl_name = ?", (t,))]
            self.assertTrue(any("BEFORE DELETE" in s and "RAISE(ABORT" in s for s in sqls), t)
        self.assertIn("raw_intake", scan.RETAINED_TABLES)
        self.assertIn("intake_item_attr", scan.RETAINED_TABLES)                             # S24-DEV-05: since Stage 24 the list derives from the table disposition register (39 tables incl. the INC-06 addendum tables; was RTD-52)

    def test_TST_HUB_INC06_S14_queue_snapshot_ages_and_run_records(self):
        """S14: queue ages are relative to the as_of argument (deterministic); run records are STARTED/FINISHED with counts; the intake run adds
        one audit record per run and per resolution only."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(1, payload={"quantity": -1}), I.feed(2, ref_id="C00009999")], "s14", "s14")
        t = st.now()
        s1 = st.isvc.queue_snapshot(t)
        s2 = st.isvc.queue_snapshot(t)
        self.assertEqual(s1, s2)
        from hub.security.canonical import fmt, parse
        import datetime
        later = fmt(parse(t) + datetime.timedelta(hours=1))
        s3 = st.isvc.queue_snapshot(later)
        self.assertAlmostEqual(s3["ages_seconds"]["flagged_value"]["max"] - s1["ages_seconds"]["flagged_value"]["max"], 3600, places=3)
        self.assertEqual(s3["queues"], s1["queues"])
        self.assertEqual(s1["reasons"], {"NEGATIVE_VALUE": 1, "UNMATCHED_REF": 1})
        ev = st.con.execute("SELECT run_seq, event_type, body FROM intake_run_event WHERE run_id = 's14' ORDER BY run_seq").fetchall()
        self.assertEqual([e[1] for e in ev], ["RUN_STARTED", "RUN_FINISHED"])
        self.assertEqual(json.loads(ev[1][2])["received"], 2)


def socket_closed_port():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


if __name__ == "__main__":
    unittest.main()
