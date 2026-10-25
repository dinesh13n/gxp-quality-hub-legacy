"""TST-GATE-01..22 (F02 human disposition gate, Zone H choke point OP-GATE-01..04; INC-08). Synthetic, unvalidated data; zone_h.holders in these tests are
SYNTHETIC TEST DATA (holder-1, holder-2): the shipped configuration keeps the list EMPTY and `disposition.mode` at `none`.

TST-GATE-01/02/22 and 03..08 are class B (OD-S12-05 / OD-S12-06: the disposition values and the holder list are open human decisions): they run here against
SYNTHETIC values and a synthetic holder list, which proves the mechanism, not the real decision. The real values and holders stay unset.
"""
import ast
import copy
import json
import os
import sqlite3
import unittest

import _support as S
import _inc08 as W
from hub import config
from hub.gate import reauth
from hub.gate.actions import ZoneHActions
from hub.gate.errors import GateNotAuthorised
from hub.security import audit
from hub.web import tokens
from hub.web.app import WebApp

ZH_ALL = ["ZH-%02d" % i for i in range(1, 11)]
EVENT_CFG = {"disposition": {"mode": "event", "values": ["accept", "reject", "hold"]}}
HOLD1 = {"zone_h": {"holders": ["holder-1"]}}


def setUpModule():
    W.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, *a, **kw):
        st = W.WStore(*a, **kw)
        self.stores.append(st)
        return st

    def event_store(self, **extra):
        cfg = dict(EVENT_CFG)
        cfg.update(extra)
        st = self.store(extra=cfg)
        st.case = st.new_case()
        return st

    def disposition(self, st, name="holder-1", pack_hash=None, payload=None, case=None):
        case = case or st.case
        if pack_hash is None:
            pack_hash = st.pack(name, case).json()["pack_hash"]
        return st.zh(name, "ZH-01", payload or {"decision": "accept", "basis": "synthetic basis"}, case, pack_hash)


class TST_GATE_Gate(_Base):

    def test_TST_GATE_01_fresh_install_gate_status(self):
        """AC-GATE-01 (class B, OD-S12-06): no configuration -> mode none, holders_configured 0, available false."""
        st = self.store(extra={"zone_h": {"holders": []}})
        r = st.get("/api/v2/gate/status", "rev")
        self.assertEqual(r.status, 200, r.text)
        self.assertEqual(r.json(), {"mode": "none", "values_set": False, "holders_configured": 0, "available": False})

    def test_TST_GATE_02_no_holders_every_action_refused(self):
        """AC-GATE-02 (class B, OD-S12-06): fresh install, a human dispositioner who is not a holder -> each of ZH-01..ZH-10 is E-GATE-NO-HOLDERS; zero
        Zone H events exist afterwards."""
        st = self.store(extra={"zone_h": {"holders": []}})
        case = st.new_case()
        before = st.zh_counts()
        for zh in ZH_ALL:
            r = st.zh("nonholder", zh, {}, case, "0" * 64)
            self.assertEqual((r.status, r.code), (423, "E-GATE-NO-HOLDERS"), (zh, r.text))
        self.assertEqual(st.zh_counts(), before)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'denied' AND reason = 'no_holders_configured'"), 10)

    def test_TST_GATE_03_mode_none_refuses_disposition(self):
        """AC-GATE-03 (class B, OD-S12-05): one holder, mode none -> ZH-01 is E-GATE-MODE-NONE; no event."""
        st = self.store(extra=HOLD1)
        case = st.new_case()
        before = st.zh_counts()
        r = st.zh("holder-1", "ZH-01", {"decision": "accept", "basis": "b"}, case, "0" * 64)
        self.assertEqual((r.status, r.code), (423, "E-GATE-MODE-NONE"), r.text)
        self.assertEqual(st.zh_counts(), before)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_REFUSED' AND reason = 'E-GATE-MODE-NONE'"), 1)

    def test_TST_GATE_04_event_mode_without_values(self):
        """AC-GATE-04 (class B, OD-S12-05): mode event, disposition.values empty -> E-GATE-VALUES-UNSET."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}, "disposition": {"mode": "event", "values": []}})
        case = st.new_case()
        r = st.zh("holder-1", "ZH-01", {"decision": "accept", "basis": "b"}, case, "0" * 64)
        self.assertEqual((r.status, r.code), (423, "E-GATE-VALUES-UNSET"), r.text)
        self.assertEqual(st.count("decision_events", "event_type LIKE 'DISPOSITION%'"), 0)

    def test_TST_GATE_05_event_mode_records_disposition(self):
        """AC-GATE-05 (class B, OD-S12-05): mode event, values set, holder re-authenticated, current pack_hash -> DISPOSITION_RECORDED with actor,
        decision, basis, evidence refs, pack_hash, mode_at_write event; the audit chain entry exists and the chain verifies."""
        st = self.event_store()
        ev = st.evidence(st.case)
        ph = st.pack("holder-1", st.case).json()["pack_hash"]
        r = st.zh("holder-1", "ZH-01", {"decision": "accept", "basis": "synthetic basis", "evidence_refs": [ev]}, st.case, ph)
        self.assertEqual(r.status, 201, r.text)
        out = r.json()
        self.assertEqual((out["action"], out["mode_at_write"]), ("ZH-01", "event"))
        row = st.con.execute("SELECT event_type, actor, actor_kind, basis, evidence_refs, mode_at_write, holder_check_ref, payload FROM decision_events"
                             " WHERE event_id = ?", (out["event_ref"],)).fetchone()
        self.assertEqual(row[:3], ("DISPOSITION_RECORDED", "holder-1", "human"))
        self.assertEqual((row[3], json.loads(row[4]), row[5]), ("synthetic basis", [ev], "event"))
        body = json.loads(row[7])
        self.assertEqual((body["decision"], body["pack_hash"]), ("accept", ph))
        self.assertTrue(row[6].startswith("audit:"))
        a = st.con.execute("SELECT action, actor FROM audit_log WHERE audit_seq = ?", (out["audit_seq"],)).fetchone()
        self.assertEqual(a, ("DISPOSITION_RECORDED", "holder-1"))
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")

    def test_TST_GATE_06_external_ref_records_reference_only(self):
        """AC-GATE-06 (class B, OD-S12-05): mode external_ref -> DISPOSITION_REFERENCED, verified false, no decision content."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}, "disposition": {"mode": "external_ref"}})
        case = st.new_case()
        r = st.zh("holder-1", "ZH-01", {"system": "QMS-synthetic", "reference": "REF-0001"}, case)
        self.assertEqual(r.status, 201, r.text)
        row = st.con.execute("SELECT event_type, mode_at_write, basis, payload FROM decision_events WHERE event_id = ?", (r.json()["event_ref"],)).fetchone()
        self.assertEqual((row[0], row[1], row[2]), ("DISPOSITION_REFERENCED", "external_ref", ""))
        body = json.loads(row[3])
        self.assertIs(body["verified"], False)
        self.assertEqual((body["system"], body["reference"]), ("QMS-synthetic", "REF-0001"))
        self.assertFalse([k for k in body if k in ("decision", "statement")])

    def test_TST_GATE_07_external_ref_requires_reference(self):
        """AC-GATE-07 (class B, OD-S12-05): mode external_ref, `reference` omitted -> E-GATE-EXTREF-INVALID."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}, "disposition": {"mode": "external_ref"}})
        case = st.new_case()
        before = st.zh_counts()
        r = st.zh("holder-1", "ZH-01", {"system": "QMS-synthetic"}, case)
        self.assertEqual((r.status, r.code), (422, "E-GATE-EXTREF-INVALID"), r.text)
        self.assertEqual(st.zh_counts(), before)

    def test_TST_GATE_08_mode_change_does_not_rewrite_history(self):
        """AC-GATE-08 (class B, OD-S12-05): events recorded in event mode, then ZH-08 -> external_ref; the earlier events still show mode_at_write event,
        byte-identical; the ZH-08 change is itself an audited event."""
        st = self.event_store()
        self.assertEqual(self.disposition(st).status, 201)
        before = st.get("/api/v2/cases/%s/events" % st.case, "holder-1").json()
        r = st.zh("holder-1", "ZH-08", {"mode": "external_ref"})
        self.assertEqual(r.status, 201, r.text)
        after = st.get("/api/v2/cases/%s/events" % st.case, "holder-1").json()
        self.assertEqual(before, after)
        self.assertEqual([e["mode_at_write"] for e in after["items"] if e["event_type"] == "DISPOSITION_RECORDED"], ["event"])
        self.assertEqual(st.get("/api/v2/gate/status", "rev").json()["mode"], "external_ref")
        ev = st.con.execute("SELECT event_type, actor, old_value, new_value FROM policy_events WHERE event_type = 'DISPOSITION_MODE_CHANGED'").fetchall()
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0][:2], ("DISPOSITION_MODE_CHANGED", "holder-1"))
        self.assertEqual(st.count("audit_log", "action = 'DISPOSITION_MODE_CHANGED' AND outcome = 'success'"), 1)

    def test_TST_GATE_09_only_humans_who_hold_can_act(self):
        """AC-GATE-09: for each of ZH-01..ZH-10 (holder configured, mode permitting) a service-account token, the scheduler identity, an integration-role
        human and an unauthenticated call are all rejected (E-GATE-NOT-AUTHORISED / E-AUTH-UNAUTHENTICATED); each rejection is audited; zero Zone H events."""
        st = self.event_store(zone_h={"holders": ["holder-1", "int-human"]})
        st.authn.create_user("svc-int", st.pw, ["integration"], "op", kind="service")
        stok = tokens.issue(st.con, st.clock, st.anchor, "svc-int", "synthetic service", "op")
        with self.assertRaises(Exception) as cm:  # a human can not be created with the non-human role (SEC-2) ...
            st.authn.create_user("int-human", st.pw, ["integration"], "op")
        self.assertIn("non-human role", str(cm.exception))
        st.authn.create_user("int-human", st.pw, ["dispositioner"], "op")  # ... so one is built by adding the role afterwards, and made a holder
        st.con.execute("INSERT INTO principal_role(principal_id, role, granted_at, granted_by) VALUES ('int-human', 'integration', ?, 'op')", (st.clock(),))
        st.con.commit()
        htok = st.login_cookie("int-human")
        before, audits = st.zh_counts(), st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'denied'")
        n = 0
        for zh in ZH_ALL:
            body = {"action": zh, "case_id": st.case, "payload": {}, "authority_ref": W.AUTH, "reauth_token": "0" * 64}
            for label, token, status, code in (("service token", stok, 403, "E-GATE-NOT-AUTHORISED"), ("integration human", htok, 403, "E-GATE-NOT-AUTHORISED"),
                                               ("unauthenticated", None, 401, "E-AUTH-UNAUTHENTICATED")):
                r = st.call("POST", "/api/v2/zone-h/actions", body, token=token)
                self.assertEqual((r.status, r.code), (status, code), (zh, label, r.text))
                n += 1
            # the scheduler identity has no HTTP path at all: a service-kind session handed straight to the choke point is refused the same way
            with self.assertRaises(GateNotAuthorised):
                ZoneHActions(st.con, st.s, st.clock, st.anchor, st.d, None, st.cfg).execute(st.service_session(), body, "t-sched-%s" % zh)
            n += 1
        self.assertEqual(st.zh_counts(), before)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'denied'") - audits, n)

    def test_TST_GATE_10_stale_login_needs_reauthentication(self):
        """AC-GATE-10 (also TST-GATE-10 in the plan: static/introspection part is TST-GATE-21): a holder session whose last re-authentication is older than
        the window -> E-GATE-REAUTH-REQUIRED; no event."""
        st = self.event_store()
        ph = st.pack("holder-1", st.case).json()["pack_hash"]
        proof = reauth.token_for(st.sess("holder-1"))
        st.clock.advance(st.s["zone_h"]["reauth_window_seconds"] + 60)
        before = st.zh_counts()
        r = st.zh("holder-1", "ZH-01", {"decision": "accept", "basis": "b"}, st.case, ph, reauth_token=proof)
        self.assertEqual((r.status, r.code), (401, "E-GATE-REAUTH-REQUIRED"), r.text)
        self.assertTrue(r.json()["error"]["retryable"])
        self.assertEqual(st.zh_counts(), before)
        # the evidence pack read needs the same step-up
        self.assertEqual((st.pack("holder-1", st.case).status), 401)

    def test_TST_GATE_11_no_import_path_from_automation_to_zone_h_writes(self):
        """AC-GATE-11: static import graph + call-name scan: no path from intake, runs, metrics, reviewer-support, observability or rule modules to the
        Zone H write modules (hub.gate.dispositions / actions / policy_binding / hub.web); the only importers of hub.gate.service are the documented ones.
        The test fails if a path or an importer is added."""
        root = os.path.join(S.CODE_ROOT, "hub")
        graph, trees = {}, {}
        for dp, _, fs in os.walk(root):
            for f in fs:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(dp, f)
                mod = os.path.relpath(path, S.CODE_ROOT)[:-3].replace(os.sep, ".")
                if mod.endswith(".__init__"):
                    mod = mod[:-9]
                trees[mod] = ast.parse(open(path, encoding="utf-8").read())
        for mod, tree in trees.items():
            deps = set()
            for n in ast.walk(tree):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                    names = [n.module] + ["%s.%s" % (n.module, a.name) for a in n.names]
                deps.update(x for x in names if x in trees)
            graph[mod] = deps
        automated = [m for m in trees if m.startswith(("hub.intake", "hub.runs", "hub.metrics", "hub.review", "hub.obs", "hub.crosswalk"))
                     or m in ("hub.policy.engine", "hub.policy.rulesets", "hub.policy.asfound", "hub.policy.inputs", "hub.policy.clocks")]
        automated = [m for m in automated if m != "hub.runs.schedule"]
        forbidden = {"hub.gate.dispositions", "hub.gate.actions", "hub.gate.policy_binding", "hub.gate.pack", "hub.gate.flags"} | \
            set(m for m in trees if m.startswith("hub.web") and m not in ("hub.web", "hub.web.schema", "hub.web.errors"))

        def reach(start):
            seen, todo = set(), [start]
            while todo:
                m = todo.pop()
                for d in graph.get(m, ()):
                    if d not in seen:
                        seen.add(d)
                        todo.append(d)
            return seen
        bad = [(m, sorted(reach(m) & forbidden)) for m in automated if reach(m) & forbidden]
        self.assertEqual(bad, [])
        importers = sorted(m for m, d in graph.items() if "hub.gate.service" in d and not m.startswith("hub.gate"))
        self.assertEqual(importers, ["hub.decision.service", "hub.intake.service", "hub.runs.schedule"])  # ZH-04, ZH-10 (set_binding), ZH-09
        # call-name scan: automated modules never call a Zone H write by name (intake.service.set_binding is the pre-existing ZH-10 holder check)
        names = {"require_holder", "record_disposition", "act_on_flag", "change_disposition_mode", "record_exception_rule", "adopt", "accept_open",
                 "activate", "deactivate", "edit_rule_row", "ZoneHActions"}
        calls = []
        for m in automated:
            for n in ast.walk(trees[m]):
                if isinstance(n, ast.Call):
                    f = n.func
                    nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
                    if nm in names:
                        calls.append((m, nm))
        self.assertEqual(sorted(calls), [("hub.intake.service", "require_holder")])

    def test_TST_GATE_12_database_trigger_refuses_system_zone_h_events(self):
        """AC-GATE-12: a direct INSERT of a Zone H event type with actor_kind 'system' (or 'service', or without a holder_check_ref) is aborted by the
        trigger E-GATE-NOT-AUTHORISED."""
        st = self.event_store()
        cols = "event_id, case_id, seq, event_type, affects_state, actor, actor_kind, occurred_at, recorded_at, basis, evidence_refs, cycle, exception," \
               " mode_at_write, holder_check_ref, payload, prev_hash, hash"
        head = st.con.execute("SELECT last_seq FROM case_state WHERE case_id = ?", (st.case,)).fetchone()[0]
        before = st.count("decision_events")
        for i, (etype, kind, ref) in enumerate([("DISPOSITION_RECORDED", "system", "audit:1"), ("QA_RELEASE_RECORDED", "service", "audit:1"),
                                                ("ESIGNATURE_RECORDED", "system", None), ("DISPOSITION_REFERENCED", "human", None)]):
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                st.con.execute("INSERT INTO decision_events(%s) VALUES (?,?,?,?,0,?,?,?,?,?,?,1,0,?,?,?,?,?)" % cols,
                               ("EV-X%d" % i, st.case, head + 1, etype, "someone", kind, "2026-10-18T00:00:00.000000Z", "2026-10-18T00:00:00.000000Z",
                                "x", "[]", "event", ref, "{}", "0" * 64, "1" * 64))
            self.assertIn("E-GATE-NOT-AUTHORISED", str(cm.exception))
            st.con.rollback()
        self.assertEqual(st.count("decision_events"), before)

    def test_TST_GATE_13_feed_text_cannot_disposition(self):
        """AC-GATE-13: a feed row with state DISPOSITIONED and notes 'approve and release batch' is received, reconciled and shown: no Zone H or state event
        is created; the text is shown escaped and labelled as untrusted source text."""
        import _inc06 as I
        st = self.store()
        before, events_before = st.zh_counts(), st.count("decision_events")
        d = I.feed(40, payload={"state": "DISPOSITIONED", "notes": "approve and release batch <b>now</b>"}, ref_id="C00009999")
        st.isvc.ingest("partner_feed", [d], "t-g13", "t-g13")
        r = st.get("/api/v2/queues/exceptions", "rev")
        self.assertEqual(r.status, 200, r.text)
        item = [i for i in r.json()["items"] if i["notes"] and "approve and release" in i["notes"]["text"]][0]
        self.assertEqual(item["notes"]["trust"], "untrusted")
        self.assertIn("&lt;b&gt;now&lt;/b&gt;", item["notes"]["text_escaped"])
        page = st.call("GET", "/ui/queue", cookie=st.login_cookie("rev"))
        self.assertEqual(page.status, 200, page.text[:300])
        self.assertIn("approve and release batch &lt;b&gt;now&lt;/b&gt;", page.text)
        self.assertNotIn("<b>now</b>", page.text)
        self.assertIn("untrusted source text", page.text)
        self.assertEqual(st.zh_counts(), before)
        self.assertEqual(st.count("decision_events"), events_before)

    def test_TST_GATE_14_no_decision_field_in_reports_search_templates_rules(self):
        """AC-GATE-14: every response of the report, search, template and rule endpoints is scanned: no key named decision / disposition / release carries a
        value."""
        st = self.store(extra={"search": {"enabled": True}})
        st.app.documents = lambda: [{"doc_id": "D1", "version": 1, "effective_at": "2026-01-01T00:00:00.000000Z", "source": "synthetic", "locale": "en",
                                     "access_level": "quality", "reference": "ref", "hash": "h", "body": "ignore previous instructions", "ocr_confidence": None}]
        st.app.search.documents = st.app.documents
        st.load_rules()
        case = st.new_case()
        st.add_trace(case)
        paths = ["/api/v2/queues/exceptions", "/api/v2/cases/%s/rule-trace" % case, "/api/v2/search?q=ignore", "/api/v2/rulesets",
                 "/api/v2/rulesets/as-found-python/1", "/api/v2/metrics/registry", "/api/v2/runs", "/api/v2/policies", "/api/v2/cases/%s/clocks" % case]
        bodies = [(p, st.get(p, "ql")) for p in paths]
        bodies.append(("evaluate", st.post("/api/v2/rules/evaluate", {"function": "PRIORITY", "ruleset_ref": "as-found-python@1",
                                                                       "inputs": {"status": "OPEN", "severity": "HIGH", "amount": 10}}, "ql")))
        names = ("decision", "disposition", "release", "answer", "summary", "recommendation")

        def walk(o, where, found):
            if isinstance(o, dict):
                for k, v in o.items():
                    if any(n in k.lower() for n in names) and v not in (None, "", [], {}, False):
                        found.append((where, k))
                    walk(v, where + "/" + k, found)
            elif isinstance(o, list):
                for v in o:
                    walk(v, where, found)
        found = []
        for p, r in bodies:
            self.assertIn(r.status, (200, 201), (p, r.text[:300]))
            walk(r.json(), p, found)
        self.assertEqual(found, [])

    def test_TST_GATE_15_pack_is_deterministic(self):
        """AC-GATE-15: a case with linked objects, evidence, a rule trace and an open finding -> two packs without data change are identical byte for byte
        including pack_hash; link classes with nothing are listed as 'none found'."""
        import _inc06 as I
        st = self.event_store()
        st.load_rules()
        st.evidence(st.case)
        st.add_trace(st.case)
        st.isvc.ingest("partner_feed", [I.feed(0, payload={"quantity": -1.5}, ref_id=st.case)], "t-g15", "t-g15", targets={st.case: [st.case]})
        a, b = st.pack("holder-1", st.case), st.pack("holder-1", st.case)
        self.assertEqual((a.status, b.status), (200, 200), a.text)
        self.assertEqual(a.raw, b.raw)
        pk = a.json()
        self.assertEqual(len(pk["pack_hash"]), 64)
        self.assertEqual(len(pk["rule_traces"]), 1)
        self.assertTrue(pk["evidence"])
        self.assertEqual(pk["linked_objects"]["batch"], "none found")
        self.assertTrue(isinstance(pk["linked_objects"].get("feed_item"), list) or pk["linked_objects"].get("feed_item") == "none found")
        self.assertTrue(pk["open_findings"] and pk["open_findings"] != "none found", pk["open_findings"])

    def test_TST_GATE_16_pack_has_no_preselected_decision(self):
        """AC-GATE-16: the pack response contains no recommended or pre-selected decision, and the HTML form has no checked radio / selected default."""
        st = self.event_store()
        r = st.pack("holder-1", st.case)
        flat = json.dumps(r.json()).lower()
        for word in ("recommend", "suggest", "preselect", "default_decision", "proposed_decision"):
            self.assertNotIn(word, flat)
        page = st.call("GET", "/ui/cases/%s/pack" % st.case, cookie=st.login_cookie("holder-1"))
        self.assertEqual(page.status, 200, page.text[:300])
        self.assertIn("<form", page.text)
        self.assertNotIn("checked", page.text)
        self.assertNotIn("selected", page.text)
        self.assertIn('<option value="">(choose)</option>', page.text)

    def test_TST_GATE_17_stale_pack_hash_is_refused(self):
        """AC-GATE-17: a pack_hash obtained, then new evidence attached -> ZH-01 with the old pack_hash is E-GATE-PACK-STALE (retryable)."""
        st = self.event_store()
        old = st.pack("holder-1", st.case).json()["pack_hash"]
        st.evidence(st.case)
        before = st.zh_counts()
        r = self.disposition(st, pack_hash=old)
        self.assertEqual((r.status, r.code), (409, "E-GATE-PACK-STALE"), r.text)
        self.assertTrue(r.json()["error"]["retryable"])
        self.assertEqual(st.zh_counts(), before)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_REFUSED' AND reason = 'E-GATE-PACK-STALE'"), 1)
        self.assertEqual(self.disposition(st).status, 201)

    def test_TST_GATE_18_override_keeps_original_output(self):
        """AC-GATE-18: a rule-generated priority flag; a reviewer posts override with reason 'not applicable' -> OVERRIDE_RECORDED stored, the original rule
        output unchanged, the flag shown as overridden."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        t = st.add_trace(case)
        orig = st.con.execute("SELECT result FROM rule_trace WHERE flag_id = ?", (t["flag_id"],)).fetchone()[0]
        r = st.post("/api/v2/flags/%s/overrides" % t["flag_id"], {"action": "override", "reason": "not applicable"}, "rev")
        self.assertEqual(r.status, 201, r.text)
        out = r.json()
        self.assertIs(out["original_output_retained"], True)
        ev = st.con.execute("SELECT event_type, actor, basis FROM decision_events WHERE event_id = ?", (out["event_id"],)).fetchone()
        self.assertEqual(ev, ("OVERRIDE_RECORDED", "rev", "not applicable"))
        self.assertEqual(st.con.execute("SELECT result FROM rule_trace WHERE flag_id = ?", (t["flag_id"],)).fetchone()[0], orig)
        trace = st.get("/api/v2/cases/%s/rule-trace" % case, "rev").json()["explanations"][0]
        self.assertEqual((trace["flag_id"], trace["flag_status"]), (t["flag_id"], "overridden"))

    def test_TST_GATE_19_override_needs_a_reason(self):
        """AC-GATE-19: an override with an empty (or blank) reason is E-GATE-REASON-REQUIRED; nothing is stored."""
        st = self.store()
        st.load_rules()
        t = st.add_trace(st.new_case())
        for reason in ("", "   "):
            r = st.post("/api/v2/flags/%s/overrides" % t["flag_id"], {"action": "override", "reason": reason}, "rev")
            self.assertEqual((r.status, r.code), (422, "E-GATE-REASON-REQUIRED"), r.text)
        self.assertEqual(st.count("flag_action"), 0)

    def test_TST_GATE_20_every_rule_output_has_a_flag_and_all_actions(self):
        """AC-GATE-20: every output type of the registry (4 rule functions + 5 intake exception queues) has a flag_id and accepts override, dismiss and refuse."""
        import _inc06 as I
        from hub.gate import flags
        st = self.store()
        st.load_rules()
        case = st.new_case()
        fixtures = {"PRIORITY": ("as-found-python@1", {"status": "OPEN", "severity": "HIGH", "amount": 10}),
                    "MANUAL_REVIEW": ("as-found-python@1", {"status": "CLOSED", "severity": "HIGH"}),
                    "AMOUNT_LIMIT": ("as-found-js@1", {"amount": 1000, "region": "MARS", "year": 2026}),
                    "SHIFT_FLAG": ("as-found-batch@1", {"value": 5, "threshold": 3})}
        by_output = {}
        for fn, (ref, inp) in fixtures.items():
            by_output["rule_" + fn.lower()] = [st.add_trace(case, fn, inp, ref)["flag_id"] for _ in range(3)]
        st.isvc.ingest("partner_feed", [I.feed(20, payload_text="{broken"), I.feed(21, ref_id="C00009999"), I.feed(22, ref_id="C00000023"),
                                        I.feed(23, payload={"quantity": -2})], "t-g20a", "t-g20a", targets={"C00000023": ["C00000023", "DEV00000001"],
                                                                                           "C00000024": ["C00000024"]})
        st.isvc.ingest("partner_feed", [I.feed(24)], "t-g20b", "t-g20b")
        st.isvc.ingest("partner_feed", [I.feed(24, payload={"quantity": 77})], "t-g20c", "t-g20c")
        q = st.get("/api/v2/queues/exceptions?limit=100", "rev").json()["items"]
        for it in q:
            by_output.setdefault("queue_" + it["queue"], []).append(it["flag_id"])
        self.assertEqual(sorted(by_output), sorted(o["output_type"] for o in flags.OUTPUT_REGISTRY))
        for out, ids in sorted(by_output.items()):
            self.assertGreaterEqual(len(ids), 1, out)
            ids = (ids * 3)[:3] if len(ids) < 3 else ids
            for fid, action in zip(sorted(set(ids)), flags.ACTIONS):
                r = st.post("/api/v2/flags/%s/overrides" % fid, {"action": action, "reason": "synthetic %s" % action}, "ql")
                self.assertEqual(r.status, 201, (out, fid, action, r.text))
            # a single flag also accepts all three actions in turn (the original output is never blocked or changed)
            one = sorted(set(ids))[0]
            for action in flags.ACTIONS:
                self.assertEqual(st.post("/api/v2/flags/%s/overrides" % one, {"action": action, "reason": "again"}, "ql").status, 201)
        bad = st.post("/api/v2/flags/FLG-RT-99999999/overrides", {"action": "override", "reason": "x"}, "rev")
        self.assertEqual((bad.status, bad.code), (404, "E-REV-NOT-FOUND"))

    def test_TST_GATE_21_no_switch_disables_the_gate(self):
        """AC-GATE-21: the configuration surface is searched: no setting, environment variable, header or CLI flag exists whose effect is to disable the
        Zone H checks; trying the obvious ones changes nothing."""
        import re
        pat = re.compile(r"(zone|gate|holder|reauth|step.?up)", re.I)
        pat2 = re.compile(r"(bypass|skip|disable|override|insecure|debug|no.?auth|no.?check|unsafe|trust)", re.I)
        found = []
        for dp, _, fs in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for f in fs:
                if not f.endswith(".py"):
                    continue
                tree = ast.parse(open(os.path.join(dp, f), encoding="utf-8").read())
                for n in ast.walk(tree):
                    key = None
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("get", "getenv", "add_argument") and n.args and \
                            isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                        owner = ast.unparse(n.func.value)
                        if n.func.attr == "getenv" or "environ" in owner or n.func.attr == "add_argument":
                            key = n.args[0].value
                    elif isinstance(n, ast.Subscript) and "environ" in ast.unparse(n.value) and isinstance(n.slice, ast.Constant):
                        key = n.slice.value
                    if isinstance(key, str) and pat.search(key) and pat2.search(key):
                        found.append((f, key))
        self.assertEqual(found, [])
        from hub.security import settings
        self.assertEqual(sorted(settings.DEFAULTS["zone_h"]), ["holders", "reauth_window_seconds"])
        from hub.core.errors import ConfigInvalid
        with self.assertRaises(ConfigInvalid):
            settings.resolve({"zone_h": {"holders": [], "reauth_window_seconds": 10 ** 9}})
        # behaviour: the obvious switches do not open the door
        os.environ["HUB_ZONE_H_DISABLE"] = "1"
        try:
            with self.assertRaises(ConfigInvalid):  # Stage 27 (S26-F-05): the obvious switch keys are not just inert any more, the configuration refuses them
                self.store(extra={"zone_h": {"holders": ["holder-1"], "enforce": False, "disabled": True}, **EVENT_CFG})
            st = self.store(extra={"zone_h": {"holders": ["holder-1"]}, **EVENT_CFG})
            case = st.new_case()
            r = st.zh("nonholder", "ZH-01", {"decision": "accept", "basis": "b"}, case, "0" * 64)
            self.assertEqual((r.status, r.code), (403, "E-GATE-NOT-AUTHORISED"), r.text)
            r = st.call("POST", "/api/v2/zone-h/actions", {"action": "ZH-01", "authority_ref": "x", "reauth_token": "0" * 64}, token=st.tokens["nonholder"],
                        headers={"X-Hub-Skip-Gate": "1", "X-Hub-Debug": "1"})
            self.assertEqual((r.status, r.code), (403, "E-GATE-NOT-AUTHORISED"))
        finally:
            del os.environ["HUB_ZONE_H_DISABLE"]
        self.assertEqual(st.count("decision_events", "event_type LIKE 'DISPOSITION%'"), 0)

    def test_TST_GATE_22_holder_change_is_audited_at_start(self):
        """AC-GATE-22 (class B, OD-S12-06): a holder-list change in configuration followed by a restart -> a CONFIG_LOADED entry with the new config hash,
        and the holder list, exists in the audit chain."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}})
        a1 = WebApp(st.data, st.cfg, st.clock)
        a1.start("t-start-1")
        cfg2 = copy.deepcopy(st.cfg)
        cfg2["zone_h"]["holders"] = ["holder-1", "holder-2"]
        a2 = WebApp(st.data, cfg2, st.clock)
        a2.start("t-start-2")
        rows = [r for r in st.audit_actions("CONFIG_LOADED") if r["details"].get("command") == "web-serve"]
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["details"]["config_hash"], rows[1]["details"]["config_hash"])
        self.assertEqual(rows[1]["details"]["config_hash"], a2.config_hash)
        self.assertEqual((rows[0]["details"]["zone_h_holders"], rows[1]["details"]["zone_h_holders"]), (["holder-1"], ["holder-1", "holder-2"]))
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")


if __name__ == "__main__":
    unittest.main()
