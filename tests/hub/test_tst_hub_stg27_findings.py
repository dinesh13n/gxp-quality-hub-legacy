"""Stage 27 tests, part 1: the Stage 26 findings F-01 .. F-09 and the mutant gaps (DW-25; AC-HRD-01 .. AC-HRD-06). Synthetic, unvalidated.
The Stage 26 tests were updated to assert the fixed behaviour (S27-DEV-01); these tests pin each fix once more from the point of view of Stage 27 and add what a
mutation run showed missing (M5, M9, M10: each layer is now tested on its own).

  F01  OP-GATE-02: authentication before validation (anonymous 401 for every action text, authenticated unknown action still 422)
  F02  restricted-evidence note withheld from roles that may not read the record (list and single event), stored basis and the chain unchanged   [A-27-02]
  F03  lone surrogate: 400 on every JSON surface, never 500
  F04  config errors: E-CFG-INVALID with exit 2 and no traceback for a missing / truncated / non-JSON / non-object file
  F05  unknown configuration keys refused; the closed key sets equal the v0.2 hub-config schema (plus rate_limit)
  F07  store fault -> 503 E-STORE-UNAVAILABLE, an integrity error stays a 500
  M5   WebAuthorizer.authorize on an unregistered route raises AuthForbidden by itself (layer test)
  M9   zone_h_service_actor_accepted counts non-human success rows only
  M10  ScheduleService.set_enabled refuses a missing / blank / non-string authority_ref and writes nothing
"""
import json
import os
import sqlite3
import subprocess
import sys
import unittest

import _inc08 as W
import _stg26 as T26
import _stg27 as T
from hub import config as hubconfig
from hub.core.errors import ConfigInvalid
from hub.decision import service as decision_service
from hub.gate.service import GateService
from hub.obs import collect
from hub.runs.schedule import ScheduleService
from hub.security import audit
from hub.security.errors import AuthForbidden, AuthUnauthenticated
from hub.web import tokens as wtokens
from hub.web.app import Request

GATE = "/api/v2/zone-h/actions"
OFF = {"rate_limit": {"enabled": False}}


def setUpModule():
    T.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def store(self, **kw):
        kw["extra"] = dict(OFF, **(kw.get("extra") or {}))
        st = W.WStore(loaded=False, **kw)
        self.addCleanup(st.close)
        return st


class TST_HUB_STG27_Findings(_Base):

    def test_TST_HUB_STG27_F01_authentication_before_validation_on_the_gate_route(self):
        """F01 (S26-F-01): an anonymous or unknown-token caller gets 401 for EVERY action text (valid, unknown, missing, non-string) and learns nothing about the valid
        names; an authenticated caller with an unknown action still gets 422 E-GATE-UNKNOWN-ACTION. At service level a missing session is refused before the action is read."""
        st = self.store()
        for body in ({"action": "ZH-01"}, {"action": "ZH-99"}, {"action": "nonsense"}, {"authority_ref": "x"}, {"action": 7}, {}):
            for tok in (None, "f" * 64):
                r = st.call("POST", GATE, body, token=tok)
                self.assertEqual((r.status, r.code), (401, "E-AUTH-UNAUTHENTICATED"), (body, tok))
        r = st.post(GATE, {"action": "ZH-99", "authority_ref": W.AUTH}, "nonholder")
        self.assertEqual((r.status, r.code), (422, "E-GATE-UNKNOWN-ACTION"))
        # service level: sess None -> unauthenticated even for an unknown action; the audit row carries no attacker-chosen text
        gs = GateService(st.con, st.s, st.clock, st.anchor)
        n0 = st.count("audit_log")
        for zh in ("ZH-99", "ZH-01", "<script>alert(1)</script>"):
            with self.assertRaises(AuthUnauthenticated):
                gs.require_holder(None, zh, "t-f01", "OP-GATE-02")
        rows = st.con.execute("SELECT actor, outcome, reason, details FROM audit_log WHERE audit_seq > ? ORDER BY audit_seq", (n0,)).fetchall()
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r[0] == "anonymous" and r[1] == "denied" and r[2] == "unauthenticated" for r in rows))
        self.assertNotIn("script", " ".join(r[3] for r in rows))
        self.assertEqual(json.loads(rows[0][3])["zh"], "unrecognised")
        self.assertEqual(T26.verify_chain(st)["status"], "ok")

    def test_TST_HUB_STG27_F02_restricted_evidence_note_is_withheld_from_non_readers(self):
        """F02 (S26-F-02, High; rule = assumption A-27-02): the evidence `note` is copied into the basis of the EVIDENCE_ATTACHED event. Roles that may not read the record
        (reviewer, finance_read, integration) see WITHHELD_BASIS and basis_withheld=true in the event list and the single event; quality_lead and compliance still see the
        note; a quality-level or public note is unchanged for everyone; the STORED basis and the hash chain are unchanged (the redaction is view-layer only)."""
        st = self.store()
        st.authn.create_user("fin", st.pw, ["finance_read"], "op")
        st.tokens["fin"] = st.authn.login("fin", st.pw, "t-fin")
        st.authn.create_user("svc-int", st.pw, ["integration"], "op", kind="service")
        st.tokens["svc"] = wtokens.issue(st.con, st.clock, st.anchor, "svc-int", "s27 synthetic service token", "op")
        st.con.commit()
        case = st.new_case("C92000001")
        marker = "RESTRICTED-S27-MARKER-5b1c"
        plain = "QUALITY-S27-NOTE-9d2e"
        st.svc.attach_evidence(st.sess("ql"), case, "document", "s27", "ref-r", access_level="restricted", note=marker, correlation_id="t-r")
        st.svc.attach_evidence(st.sess("ql"), case, "document", "s27", "ref-q", access_level="quality", note=plain, correlation_id="t-q")
        stored = [r[0] for r in st.con.execute("SELECT basis FROM decision_events WHERE event_type = 'EVIDENCE_ATTACHED' ORDER BY rowid")]
        self.assertEqual(stored, [marker, plain])
        chain0 = st.con.execute("SELECT group_concat(event_id || hash) FROM (SELECT event_id, hash FROM decision_events ORDER BY rowid)").fetchone()
        ev_ids = [r[0] for r in st.con.execute("SELECT event_id FROM decision_events WHERE event_type = 'EVIDENCE_ATTACHED' ORDER BY rowid")]
        withheld = decision_service.WITHHELD_BASIS
        self.assertNotIn(marker, withheld)
        for who in ("rev", "fin", "svc"):
            lst = st.get("/api/v2/cases/%s/events" % case, who)
            self.assertNotIn(marker, lst.text, who)
            if who == "rev":  # the reviewer may list events: the exact view is pinned
                self.assertEqual(lst.status, 200, lst.text)
                items = [e for e in (lst.json().get("items") or lst.json().get("events") or []) if e["event_type"] == "EVIDENCE_ATTACHED"]
                self.assertEqual(len(items), 2, lst.text)
                self.assertEqual(items[0]["basis"], withheld)
                self.assertTrue(items[0]["basis_withheld"])
                self.assertEqual(items[1]["basis"], plain)
                self.assertNotIn("basis_withheld", items[1])
            one = st.get("/api/v2/events/" + ev_ids[0], who)
            self.assertNotIn(marker, one.text, who)
        for who in ("ql", "comp"):
            self.assertIn(marker, st.get("/api/v2/cases/%s/events" % case, who).text, who)
            self.assertIn(marker, st.get("/api/v2/events/" + ev_ids[0], who).text, who)
        r = st.get("/api/v2/events/" + ev_ids[1], "rev")
        self.assertIn(plain, r.text)
        self.assertEqual([r[0] for r in st.con.execute("SELECT basis FROM decision_events WHERE event_type = 'EVIDENCE_ATTACHED' ORDER BY rowid")], [marker, plain])
        self.assertEqual(st.con.execute("SELECT group_concat(event_id || hash) FROM (SELECT event_id, hash FROM decision_events ORDER BY rowid)").fetchone(), chain0)
        self.assertEqual(T26.verify_chain(st)["status"], "ok")

    def test_TST_HUB_STG27_F03_lone_surrogate_is_a_400_on_every_json_surface(self):
        """F03 (S26-F-03): a lone UTF-16 surrogate escape in any string of a JSON body is refused at the wire with 400 E-REQ-INVALID (also nested in arrays and objects, as a key,
        and in the high and low halves), a valid surrogate PAIR is accepted by the parser, and nothing is stored."""
        from hub.core import unitext
        from hub.web import wire
        st = self.store()
        before = T26.snapshot(st)
        for raw in ('{"username": "\\ud800", "password": "x"}', '{"username": "a", "password": "\\udfff"}', '{"username": ["\\ud83d"], "password": "x"}',
                    '{"\\ud800": 1}', '{"username": {"a": ["x", {"b": "\\udc00"}]}, "password": "x"}'):
            r = st.call("POST", "/api/v2/auth/login", raw=raw, csrf=False)
            self.assertEqual((r.status, r.code), (400, "E-REQ-INVALID"), raw)
        self.assertEqual(T26.diff(before, T26.snapshot(st)), [])
        self.assertTrue(unitext.has_lone_surrogate({"a": ["\ud800"]}))
        self.assertTrue(unitext.has_lone_surrogate(["x", {"\udfff": 1}]))
        self.assertFalse(unitext.has_lone_surrogate({"a": ["\U0001f600", "café"]}))
        self.assertEqual(wire.parse_json(b'{"a": "\\ud83d\\ude00"}'), {"a": "\U0001f600"})  # a valid pair is one scalar value

    def test_TST_HUB_STG27_F04_config_errors_are_codes_not_tracebacks(self):
        """F04 (S26-F-04): the CLI with a missing, truncated, non-JSON or non-object config file ends with exit 2 and E-CFG-INVALID, no traceback; hubconfig.load raises ConfigInvalid."""
        st = self.store()
        d = T.S.tmpdir("s27-f04-")
        cases = {"missing": None, "empty": "", "truncated": '{"hub": {"mode"', "array": "[1, 2]", "scalar": "7", "binary": b"\xff\xfe\x00"}
        for name, content in cases.items():
            p = os.path.join(d, name + ".json")
            if content is not None:
                with open(p, "wb") as f:
                    f.write(content if isinstance(content, bytes) else content.encode())
            with self.assertRaises(ConfigInvalid, msg=name):
                hubconfig.load(p)
            run = subprocess.run([sys.executable, "-B", "-m", "hub.web", "--config", p, "status", "--data-dir", st.data], cwd=T.S.CODE_ROOT, env=T.S.child_env(),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
            self.assertEqual(run.returncode, 2, (name, run.stderr[-300:]))
            self.assertEqual(json.loads(run.stderr)["code"], "E-CFG-INVALID", name)
            self.assertNotIn("Traceback", run.stderr, name)

    def test_TST_HUB_STG27_F05_unknown_config_keys_are_refused_and_match_the_schema(self):
        """F05 (S26-F-05): an unknown key at the top level or in any section is refused with ConfigInvalid naming the key path (not the value); the closed key sets equal the
        properties of the v0.2 hub-config schema plus the Stage 27 rate_limit section (A-27-04) and the two INC-09 sections crosswalk_view / intake_reports that the code reads but the v0.2 schema lacks, so the two cannot drift apart silently."""
        base = json.loads(json.dumps(hubconfig.DEFAULTS))
        for path in (("kil",), ("hub", "kil"), ("zone_h", "holderz"), ("audit", "anchor_pathh"), ("rate_limit", "burst")):
            doc = json.loads(json.dumps(base))
            tgt = doc
            for k in path[:-1]:
                tgt = tgt.setdefault(k, {})
            tgt[path[-1]] = "SECRET-VALUE-SHOULD-NOT-ECHO"
            with self.assertRaises(ConfigInvalid) as cm:
                hubconfig.validate(doc)
            self.assertIn(".".join(path), json.dumps(cm.exception.details), path)
            self.assertNotIn("SECRET-VALUE-SHOULD-NOT-ECHO", json.dumps(cm.exception.details), path)
        sch_path = os.path.join(T.S.CODE_ROOT, "docs", "23-human-control", "stage12-v0.2", "schemas", "hub-config.schema.json")
        with open(sch_path, encoding="utf-8") as f:
            sch = json.load(f)

        def compare(schema, known, where):
            props = schema.get("properties", {})
            expect = set(props)
            if where == "$":
                expect |= {"rate_limit", "crosswalk_view", "intake_reports"}  # S27-DEV-07 (rate_limit), S27-DEV-03 (INC-09 sections); the two INC-09 sections are read by hub.r2 but absent from the v0.2 schema (spec addendum open)
            self.assertEqual(set(known), expect, where)
            for k, sub in props.items():
                if sub.get("type") == "object" and sub.get("properties") and isinstance(known[k], dict):
                    compare(sub, known[k], where + "." + k)
        compare(sch, hubconfig.KNOWN_KEYS, "$")
        # every option the code actually reads is accepted (the I9 regression of the first closed-set draft: crosswalk_view.size_cap was refused)
        from hub.decision import settings as dset
        from hub.r2 import intake_reports, joined
        from hub.runs import settings as rset
        from hub.security import settings as sset
        self.assertEqual(hubconfig.unknown_keys(dset.DEFAULTS), [])
        self.assertEqual(hubconfig.unknown_keys(rset.DEFAULTS), [])
        self.assertEqual(hubconfig.unknown_keys(sset.DEFAULTS), [])
        self.assertEqual(hubconfig.unknown_keys({"crosswalk_view": joined.DEFAULTS, "intake_reports": intake_reports.DEFAULTS, "search": {"enabled": True, "fts": "off"}}), [])

    def test_TST_HUB_STG27_F07_store_fault_is_503_and_other_errors_stay_500(self):
        """F07 (S26-F-07): sqlite3.OperationalError / DatabaseError while serving -> 503 E-STORE-UNAVAILABLE (retryable, content-free), /healthz included; an IntegrityError
        (a hub bug, not a store fault) is still the generic 500 so that a defect is not mistaken for an outage."""
        from hub.web import app as webapp
        self.assertTrue(webapp._is_store_fault(sqlite3.OperationalError("disk I/O error")))
        self.assertTrue(webapp._is_store_fault(sqlite3.DatabaseError("file is not a database")))
        self.assertFalse(webapp._is_store_fault(sqlite3.IntegrityError("UNIQUE constraint failed: x")))
        self.assertFalse(webapp._is_store_fault(ValueError("x")))
        st = self.store()
        orig = st.app._dispatch

        def boom(kind):
            def f(*a, **k):
                raise kind("secret detail /sessions/x")
            return f
        for kind, status, code in ((sqlite3.OperationalError, 503, "E-STORE-UNAVAILABLE"), (sqlite3.DatabaseError, 503, "E-STORE-UNAVAILABLE"),
                                   (sqlite3.IntegrityError, 500, "E-HUB-INTERNAL")):
            st.app._dispatch = boom(kind)
            r = st.app.handle(Request("GET", "/api/v2/policies", {}, {"Authorization": "Bearer " + st.tokens["rev"]}, b""))
            st.app.last_exception = None
            body = r.body.decode("utf-8") if isinstance(r.body, bytes) else r.body
            self.assertEqual(r.status, status, kind)
            self.assertEqual(json.loads(body)["error"]["code"], code, kind)
            self.assertNotIn("secret detail", body)
            self.assertNotIn("sqlite", body.lower())
        st.app._dispatch = orig
        self.assertEqual(st.get("/api/v2/policies", "rev").status, 200)

    def test_TST_HUB_STG27_M5_deny_by_default_holds_in_the_authorizer_layer_alone(self):
        """M5 (S26-F-10): WebApp._dispatch refuses an unregistered route before the authorizer is reached, so removing the authorizer's own branch changed nothing at system level.
        This test calls WebAuthorizer.authorize directly: an unregistered method / path raises AuthForbidden('route not registered'), with and without a token."""
        st = self.store()
        from hub.web.tokens import CompositeAuthenticator
        from hub.web.authz import WebAuthorizer
        from hub.security.auth import LocalAuthenticator
        authn = CompositeAuthenticator(LocalAuthenticator(st.con, st.s, st.clock, st.anchor), st.con, st.clock)
        authz = WebAuthorizer(st.con, st.s, st.clock, authn, st.anchor, registry=st.app.table.api + st.app.table.ui)
        for method, path in (("GET", "/no/such/route"), ("DELETE", "/api/v2/policies"), ("POST", "/api/v2/../etc/passwd"), ("PATCH", "/healthz")):
            for tok in (None, st.tokens["ql"]):
                with self.assertRaises(AuthForbidden) as cm:
                    authz.authorize(method, path, tok, "t-m5")
                self.assertIn("not registered", json.dumps(cm.exception.details))

    def test_TST_HUB_STG27_M9_service_actor_tripwire_counts_non_human_successes_only(self):
        """M9 (S26-F-08): zone_h_service_actor_accepted = ZONE_H_ATTEMPT rows with outcome success by an actor_kind other than 'human'. Planted rows: human success (not
        counted), service success (counted), system success (counted), service denied (not counted), non-ZONE_H service success (not counted). The rejection metric counts
        non-human DENIED rows. A mutant that flips the comparison counts the human row instead and fails here."""
        st = self.store()
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 0)

        def put(kind, outcome, action="ZONE_H_ATTEMPT", actor="a"):
            audit.append(st.con, st.clock, anchor=st.anchor, actor=actor, actor_kind=kind, action=action, outcome=outcome, correlation_id="t-m9", object_ref="OP-GATE-02",
                         details={"zone_h_action": "ZH-01", "zh": "ZH-01"})
        put("human", "success")
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 0)
        put("service", "success")
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 1)
        put("system", "success")
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 2)
        put("service", "denied")
        put("service", "success", action="LOGIN")
        put("human", "success")
        self.assertEqual(collect.zone_h_service_actor_accepted(st.con), 2)
        self.assertEqual(collect.tripwires(st.con)["zone_h_service_actor_accepted"], 2)
        rej = [s for s in collect.samples(st.con) if s["name"] == "zone_h_service_actor_rejections_total"]
        self.assertEqual(sum(int(s["value"]) for s in rej), 1)

    def test_TST_HUB_STG27_M10_schedule_enable_needs_a_real_authority_ref(self):
        """M10 (S26-F-09): ScheduleService.set_enabled raises AuthorityRequired for a missing, empty, blank or non-string authority_ref BEFORE any holder check or write
        (no audit row, no policy event, state unchanged); a non-bool `enabled` is ConfigInvalid. A mutant that removes the check reaches the holder check instead and fails here."""
        from hub.policy.errors import AuthorityRequired
        st = self.store()
        svc = ScheduleService(st.con, st.s, st.clock, st.anchor)
        sess = st.sess("ql")
        before = (st.count("audit_log"), st.count("policy_events"), svc.state())
        for bad in (None, "", "   ", "\t\n", 0, 7, [], {}, b"x"):
            with self.assertRaises(AuthorityRequired, msg=repr(bad)):
                svc.set_enabled(sess, True, bad, "t-m10")
        for bad in ("yes", 1, None):
            with self.assertRaises(ConfigInvalid, msg=repr(bad)):
                svc.set_enabled(sess, bad, "AUTH-1", "t-m10")
        self.assertEqual((st.count("audit_log"), st.count("policy_events"), svc.state()), before)


if __name__ == "__main__":
    unittest.main()
