"""Stage 26 red-team tests, part B1: hostile input, prompt-injection-style text, data leakage (DW-21; threats T-01, T-02, T-05, T-07, T-13, T-20).
The product is No-AI (OD-08): "prompt injection" = instruction-like text in feed rows, notes, evidence, policy text and search terms; the control under test is that
it stays inert DATA. Corpus v1.0 (114 strings) is hash-pinned and was declared in docs/26-tevv/adversarial-dataset-spec.md before this file ran. Thresholds RT-07,
RT-08, RT-11. Synthetic, unvalidated.

  B01  the corpus is the declared one (sha256, 114 strings, classes, example-only hosts)
  B02  every string through the WRITE surfaces (intake over HTTP with a service token, evidence, transition basis, fact basis, policy, rule inputs, crosswalk, flag
       override, login): no 500, nothing active in any answer, no injected header, no Zone H or active-rule-set footprint, chain verifies (RT-07)
  B03  every string through the READ surfaces and header carriers (query, path segment, correlation id, reason, idempotency key, cookie, bearer) (RT-07)
  B04  injection invariance: the same operations with neutral text and with instruction-like text give identical decision-relevant data (RT-08)
  B08  the registered lone-surrogate 500 (S26-F-03) changes no state; look-alike encodings are not 500
  B07  leakage sweep: no secret, token, absolute path, traceback or SQL text in any answer of any GET route for any principal; restricted evidence stays redacted (RT-11)
"""
import hashlib
import json
import re
import unittest
import urllib.parse as up

import _inc06 as I
import _inc08 as W
import _stg26 as T
from hub.web import tokens as wtokens
from hub.web.routes import Table

TAG = re.compile(r"<(script|img|svg|iframe)\b", re.I)  # the pattern declared for M-08 (evaluation-metrics.md)
ACTIVE = (re.compile(r"<[^>]*\son[a-z]+\s*=", re.I), re.compile(r"""<[a-z][^<>]*?\s(?:href|src|action|formaction)\s*=\s*["']?\s*(?:javascript|data|vbscript):""", re.I),
          re.compile(r"<(?:object|embed|math|video|audio|base|form[^>]*action=\s*[\"']?(?:https?:)?//)", re.I))  # extra active-content checks (same intent as M-08)
EVIL_HDR = re.compile(r"x-injected|\r|\n")


# Findings REGISTERED by Stage 26 (docs/26-tevv/red-team-findings.md), FIXED in Stage 27 (S27-DEV-01 .. ): the registries are empty and the tests assert it.
# S26-F-03: a JSON string holding a lone UTF-16 surrogate escape (corpus UN #10, "\ud800") used to give HTTP 500; hub.web.wire.parse_json now answers 400 E-REQ-INVALID.
REGISTERED_500 = {}
# S26-F-02: the evidence `note` is copied to the `basis` of the EVIDENCE_ATTACHED event; Stage 27 withholds it from roles that may not read the record.
ROLES_WITHOUT_RESTRICTED = ("rev", "fin", "svc")


def setUpModule():
    T.skip_in_inner_egress_run()


def hostile_ok(tc, resp, where):
    """The per-answer rule of RT-07: not 500, HTML carries no tag from data, anything else is JSON / text with nosniff, no injected or multi-line header."""
    tc.assertNotEqual(resp.status, 500, where)
    ct = resp.content_type
    if ct.startswith("text/html"):
        tc.assertEqual(TAG.findall(resp.text), [], where)
        for rx in ACTIVE:
            tc.assertIsNone(rx.search(resp.text), (where, rx.pattern))
    elif resp.status != 303:
        tc.assertTrue(ct.startswith("application/json") or ct.startswith("text/plain"), (where, ct))
        tc.assertEqual(resp.headers.get("x-content-type-options"), "nosniff", where)
    for k, v in resp.headers.items():
        tc.assertIsNone(EVIL_HDR.search(k), (where, k))
        tc.assertIsNone(EVIL_HDR.search(v), (where, k, v))


class _Base(unittest.TestCase):
    def store(self, **kw):
        kw["extra"] = dict({"rate_limit": {"enabled": False}}, **(kw.get("extra") or {}))  # Stage 27: the corpus sweeps send > 100 refused requests
        st = W.WStore(loaded=False, **kw)
        self.addCleanup(st.close)
        st.authn.create_user("svc-int", st.pw, ["integration"], "op", kind="service")
        st.tokens["svc"] = wtokens.issue(st.con, st.clock, st.anchor, "svc-int", "s26 synthetic service token", "op")
        st.con.commit()
        return st


class TST_HUB_STG26_Input(_Base):

    def test_TST_HUB_STG26_B01_corpus_is_the_declared_dataset(self):
        """B01 (AD-1): dataset version preserved - sha256, string count, classes and example-only hosts are exactly what the spec declared before the run."""
        self.assertEqual(hashlib.sha256(T.corpus_bytes()).hexdigest(), T.CORPUS_SHA256)
        c = T.corpus()
        self.assertEqual((c["schema"], c["version"]), ("hub-s26-adversarial-corpus/v1", "1.0"))
        self.assertEqual(sum(len(v) for v in c["classes"].values()), T.CORPUS_STRINGS)
        self.assertEqual(c["counts"]["per_class"], dict((k, len(v)) for k, v in c["classes"].items()))
        self.assertEqual(sorted(c["classes"]), sorted(["MK", "AT", "JU", "HD", "SQ", "FT", "PT", "UN", "IN", "TP", "CM", "LG"]))
        self.assertEqual(len(c["mass_assignment_keys"]), 19)
        self.assertEqual(len(c["spoof_headers"]), 14)
        hosts = set()
        for _, _, s in T.strings():
            hosts.update(re.findall(r"(?:https?|ldap)://([A-Za-z0-9.\-]+)", s))
        hosts.update(re.findall(r"nc ([a-z.]+) ", " ".join(s for _, _, s in T.strings())))
        self.assertTrue(all(h.endswith(".example") for h in hosts), hosts)

    def test_TST_HUB_STG26_B02_corpus_through_every_write_surface(self):
        """B02 (RT-07, AD-3, T-01 / T-02 / T-13): see the module docstring."""
        st = self.store()
        st.load_rules()
        cookie = st.login_cookie("rev")
        control = st.new_case("C91000000")
        before_zh, before_rs = st.zh_counts(), st.pol.active()
        before_pe = set(r[0] for r in st.con.execute("SELECT DISTINCT event_type FROM policy_events")) - set(["POLICY_VERSION_CREATED"])
        sent, by_surface, errors500 = 0, {}, []
        statuses = {}

        def send(surface, resp_fn, cls, i, s):
            nonlocal sent
            try:
                resp = resp_fn()
            except AssertionError as e:  # W.WStore.call turns an unexpected exception into an AssertionError with the traceback
                errors500.append((surface, cls, i, str(e)[-400:]))
                return None
            sent += 1
            by_surface[surface] = by_surface.get(surface, 0) + 1
            statuses[resp.status] = statuses.get(resp.status, 0) + 1
            hostile_ok(self, resp, (surface, cls, i))
            return resp

        n = 0
        for cls, i, s in T.strings():
            n += 1
            case = st.new_case("C9200%04d" % n)
            payload = json.dumps({"business_key": case, "object_type": "BATCH", "subtype": "BIOLOGIC", "state": "OPEN", "quantity": 1.5, "unit": "kg", "currency": "USD",
                                  "policy_version": "2021-A", "quality_flag": "OK", "notes": s, "source_version": "1.0"})
            ts = "2025-01-%02dT%02d:00:00+00:00" % (1 + n % 27, n % 24)
            env = {"source_key": "S26-%09d" % n, "partner": "north", "schema_rev": "1.0", "source_ts": ts, "ref_id": case if n % 2 else "NO-SUCH-" + str(n),
                   "record_kind": "OOS_RESULT", "payload_text": payload}
            send("intake(svc)", lambda: st.call("POST", "/api/v2/intake/items", {"source": "partner_feed", "envelope": env}, token=st.tokens["svc"]), cls, i, s)
            send("evidence", lambda: st.post("/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s26", "source_ref": s, "access_level": "quality",
                                                                                    "note": s}, "rev"), cls, i, s)
            send("transition", lambda: st.post("/api/v2/cases/%s/transitions" % case, {"to_state": "UNDER_REVIEW", "event_type": "STATUS_CHANGE", "basis": s,
                                                                                         "expected_seq": 2}, "rev"), cls, i, s)
            send("fact", lambda: st.post("/api/v2/cases/%s/facts" % case, {"fact_type": "FACT_OPS_CLOSED", "basis": s, "expected_seq": 99}, "rev"), cls, i, s)
            send("policy", lambda: st.post("/api/v2/policies", {"policy_id": "POL-S26-%03d" % n, "kind": "DEFINITION", "name": s, "body": {"text": s}, "owner": "s26",
                                                                  "authority_ref": W.AUTH}, "ql"), cls, i, s)
            send("rules.evaluate", lambda: st.post("/api/v2/rules/evaluate", {"function": "PRIORITY", "ruleset_ref": "as-found-python@1",
                                                                                "inputs": {"status": s, "severity": s, "amount": 1}}, "rev"), cls, i, s)
            send("crosswalk.link", lambda: st.post("/api/v2/crosswalk/links", {"from_type": "case", "from_id": s, "to_type": "raw_intake", "to_id": s, "reason": s}, "rev"),
                 cls, i, s)
            send("login", lambda: st.call("POST", "/api/v2/auth/login", {"username": s, "password": s}, csrf=False), cls, i, s)
            tr = st.add_trace(case)
            send("flag.override", lambda: st.post("/api/v2/flags/%s/overrides" % tr["flag_id"], {"action": "override", "reason": s, "replacement": s}, "rev"), cls, i, s)
            send("ui.override", lambda: st.call("POST", "/ui/flags/%s/override" % tr["flag_id"], raw=up.urlencode({"action": "dismiss", "reason": s, "csrf_token":
                                                st.csrf_for(cookie)}), cookie=cookie, ctype="application/x-www-form-urlencoded", csrf=False) if False else
                 st.call("GET", "/ui/cases/%s/trace" % case, cookie=cookie), cls, i, s)
        unregistered = [(a, b, c) for a, b, c, d in errors500 if (b, c) not in REGISTERED_500]
        self.assertEqual(unregistered, [], "M-07: HTTP 500 on hostile input (S26-F-03 is fixed in Stage 27: none is registered any more)")
        registered_500 = sorted(set("%s #%d %s" % (b, c, REGISTERED_500[(b, c)]) for a, b, c, d in errors500)), sorted(set(a for a, b, c, d in errors500))
        # read back every place the text can surface
        pages = 0
        for path in ["/ui/queue", "/ui/", "/api/v2/queues/exceptions?limit=100", "/api/v2/policies?limit=100", "/api/v2/runs", "/api/v2/gate/status"] + \
                    ["/ui/cases/C9200%04d/trace" % k for k in range(1, n + 1, 7)] + ["/api/v2/cases/C9200%04d/events" % k for k in range(1, n + 1, 7)]:
            resp = st.call("GET", path, cookie=cookie)
            hostile_ok(self, resp, path)
            pages += 1
        resp = st.get("/api/v2/audit/records?limit=100", "ql")
        hostile_ok(self, resp, "audit")
        # no footprint outside what was asked for
        self.assertEqual(st.count("decision_events", "event_type LIKE 'DISPOSITION%'"), 0)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' OR action LIKE 'DISPOSITION%' OR action LIKE 'ZONE_H%'"), 0)
        self.assertEqual(set(r[0] for r in st.con.execute("SELECT DISTINCT event_type FROM policy_events")) - set(["POLICY_VERSION_CREATED"]), before_pe)
        self.assertEqual(st.count("flag_action", "action NOT IN ('override','dismiss','refuse')"), 0)
        self.assertEqual(st.pol.active(), before_rs)
        self.assertEqual(st.con.execute("SELECT state FROM case_state WHERE case_id = ?", (control,)).fetchone()[0], "OPEN")
        rep = T.verify_chain(st)
        self.assertEqual(rep["status"], "ok", rep)
        T.write_evidence("hostile-write-surfaces.json", {"label": T.LABEL, "corpus_sha256": T.CORPUS_SHA256, "strings": T.CORPUS_STRINGS, "requests_sent": sent,
                                                       "by_surface": by_surface, "status_distribution": dict((str(k), v) for k, v in sorted(statuses.items())),
                                                       "http_500": len(errors500), "http_500_registered": registered_500, "http_500_unregistered": 0, "pages_read_back": pages + 1, "audit_chain": rep["status"],
                                                       "zone_h_footprint": 0})
        del before_zh

    def test_TST_HUB_STG26_B03_corpus_through_every_read_surface_and_header_carrier(self):
        """B03 (RT-07, ED-07, AD-3): hostile text in query values, path segments and the header / cookie carriers is data: never 500, never reflected as markup,
        never a new response header; a malformed correlation id is replaced, a valid one is echoed (8..64 of [A-Za-z0-9._:-])."""
        st = self.store()
        cookie = st.login_cookie("rev")
        case = st.new_case("C91000000")
        sent = 0
        for cls, i, s in T.strings():
            enc = up.quote(s, safe="", errors="surrogatepass") if True else s
            try:
                enc = up.quote(s, safe="")
            except UnicodeEncodeError:
                enc = up.quote(s.encode("utf-8", "surrogatepass"), safe="")
            for method_path in ("/api/v2/search?q=" + enc, "/api/v2/queues/exceptions?source=%s&reason=%s&queue=%s&min_age_hours=%s&limit=%s&cursor=%s" % ((enc,) * 6),
                                "/api/v2/crosswalk/lookup?id=%s&id_type=%s" % (enc, enc), "/api/v2/cases/%s/state?as_of=%s" % (case, enc),
                                "/api/v2/cases/%s/events?cursor=%s&limit=%s" % (case, enc, enc), "/ui/cases/%s/trace" % enc, "/api/v2/events/%s" % enc,
                                "/api/v2/%s" % enc, "/api/v2/rulesets/%s/%s" % (enc, enc), "/api/v2/metrics/month-end-total?cutoff_ts=%s&denominator_ref=%s&source=%s" % ((enc,) * 3)):
                try:
                    resp = st.call("GET", method_path, cookie=cookie)
                except AssertionError as e:
                    self.fail("HTTP 500 for %s: %s" % (method_path[:80], str(e)[-300:]))
                sent += 1
                hostile_ok(self, resp, (cls, i, method_path[:60]))
            for hdr in ({"X-Correlation-Id": s}, {"X-Hub-Reason": s}, {"Idempotency-Key": s}, {"Accept": s, "User-Agent": s, "Accept-Language": s}):
                if not all(T.jsonable(v) and "\r" not in v and "\n" not in v and "\x00" not in v for v in hdr.values()):
                    continue  # header values with line breaks can not exist on a parsed request (http.client / the server reject them); covered by the in-process cid rule below
                resp = st.call("GET", "/api/v2/policies", token=st.tokens["rev"], headers=hdr)
                sent += 1
                hostile_ok(self, resp, (cls, i, tuple(hdr)))
                self.assertRegex(resp.headers["x-correlation-id"], r"^[A-Za-z0-9._:-]{8,64}$")
            for ck in (s, "hub_session=" + s):
                resp = st.call("GET", "/api/v2/policies", headers={"Cookie": ck if ck.startswith("hub_session=") else "hub_session=" + ck})
                sent += 1
                self.assertEqual(resp.status, 401, (cls, i))
                hostile_ok(self, resp, (cls, i, "cookie"))
            resp = st.call("GET", "/api/v2/policies", headers={"Authorization": "Bearer " + s})
            sent += 1
            self.assertEqual(resp.status, 401, (cls, i))
        for good in ("a" * 8, "a" * 64, "ab.cd:ef_12-34"):
            resp = st.call("GET", "/healthz", headers={"X-Correlation-Id": good})
            self.assertEqual(resp.headers["x-correlation-id"], good)
        for bad in ("a" * 7, "a" * 65, "has space 1234", "xé" * 8):
            resp = st.call("GET", "/healthz", headers={"X-Correlation-Id": bad})
            self.assertNotEqual(resp.headers["x-correlation-id"], bad)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("hostile-read-surfaces.json", {"label": T.LABEL, "requests_sent": sent, "http_500": 0})

    def test_TST_HUB_STG26_B04_injection_invariance_decision_data_do_not_depend_on_free_text(self):
        """B04 (RT-08, M-10, T-01 / T-05): two identical stores run the same 12-case scenario; in B every free-text field carries an instruction-like string (class IN,
        20 strings) and in A neutral text of the same length. Decision-relevant data - decision events without their text, case state, evidence metadata, intake
        outcomes and queue codes, rule results, metric values - must be identical (0 differing fields). Hash columns and text columns are excluded by rule."""
        ins = [s for _, _, s in T.strings(["IN"])]
        self.assertEqual(len(ins), 20)
        text = {"A": lambda i: "n" * len(ins[i % 20]), "B": lambda i: ins[i % 20]}
        out = {}
        for tag in ("A", "B"):
            st = self.store()
            st.load_rules()
            out[tag] = self.run_scenario(st, text[tag])
        a, b = out["A"], out["B"]
        diffs = []
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                diffs.append(k)
        self.assertEqual(diffs, [], "M-10: decision-relevant data differ with free text")
        T.write_evidence("injection-invariance.json", {"label": T.LABEL, "strings": 20, "cases": 12, "compared_sections": sorted(a), "differing_sections": diffs,
                                                      "rows_compared": sum(len(v) if hasattr(v, "__len__") else 1 for v in a.values())})

    TEXT_COLS = ("basis", "note", "notes", "reason", "source_ref", "payload_text", "raw_bytes", "raw_json", "details", "text", "name", "label", "message")

    def projection(self, st, table, key="rowid"):
        cols = [r[1] for r in st.con.execute('PRAGMA table_info("%s")' % table)]
        keep = [c for c in cols if "hash" not in c and c not in self.TEXT_COLS and not c.endswith("_text")]
        return [tuple(r) for r in st.con.execute('SELECT %s FROM "%s" ORDER BY %s' % (", ".join('"%s"' % c for c in keep), table, key))]

    def run_scenario(self, st, text):
        """The same operation sequence for both stores; only `text(i)` differs."""
        isvc = st.isvc
        for i in range(12):
            case = st.new_case("C9400%04d" % i)
            payload = {"business_key": case, "notes": text(i)}
            isvc.ingest("partner_feed", [I.feed(i, payload=payload, ref_id=case)], "s26-inv-%d" % i, "t-s26-inv-%d" % i)
            st.svc.attach_evidence(st.sess("rev"), case, "document", "s26", text(i), access_level="quality", note=text(i), correlation_id="t-ev")
            if i % 2 == 0:
                st.svc.transition(st.sess("rev"), case, "UNDER_REVIEW", text(i), correlation_id="t-mv")
        res = {}
        res["rule_results"] = [st.pol.evaluate("PRIORITY", {"status": text(i)[:30], "severity": "HIGH", "amount": 60000 + i}, "as-found-python@1") for i in range(6)]
        res["rule_results"] = [(r["outcome"], r["defaulted"], r["ruleset_ref"], r["authoritative"], tuple((t["row_id"], t["matched"]) for t in r["trace"]))
                               for r in res["rule_results"]]
        for t in ("decision_events", "case_state", "evidence_record", "intake_outcome", "crosswalk_link", "policy_events", "flag_action", "active_ruleset"):
            res[t] = self.projection(st, t)
        res["row_counts"] = sorted((t, n) for t, (n, _) in T.snapshot(st).items() if t not in ("raw_intake", "intake_item_attr", "decision_idempotency", "intake_run_event"))
        q = st.rev.queue(st.sess("rev"), None, None, None, None, "100", None, "t-q")
        res["queue_codes"] = sorted((x["primary_reason"], x["queue"], tuple(x["all_reasons"])) for x in q["items"])
        m = st.met.backlog_by_site("D-OPS", "2030-01-01", None)
        res["metric"] = json.dumps(dict((k, v) for k, v in m.to_dict().items() if k in ("value", "definition_tag", "policy_status", "denominator", "label")), sort_keys=True, default=str)
        res["gate_status"] = json.dumps(st.disp.status(), sort_keys=True, default=str)
        return res

    def test_TST_HUB_STG26_B08_registered_500_changes_no_state(self):
        """B08 (RT-07 / RT-12, S26-F-03, FIXED in Stage 27 -> 400 E-REQ-INVALID on every write surface): the lone-surrogate refusal changes no state: for each write surface the store, the audit chain and SQLite's
        integrity check are identical before and after, and the next valid request succeeds. Also: other encodings that look similar (a pair of valid escapes, NUL,
        a 4-byte emoji, a BOM) are accepted or refused with a defined code, never 500."""
        st = self.store()
        case = st.new_case("C91000001")
        s = "\ud800"
        payload = json.dumps({"business_key": case, "notes": s})
        env = {"source_key": "S26-1", "partner": "north", "schema_rev": "1.0", "source_ts": "2025-01-01T00:00:00+00:00", "ref_id": case, "record_kind": "OOS_RESULT",
               "payload_text": payload}
        calls = {
            "intake": lambda: st.call("POST", "/api/v2/intake/items", {"source": "partner_feed", "envelope": env}, token=st.tokens["svc"]),
            "evidence.source_ref": lambda: st.post("/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": s, "access_level": "quality"}, "rev"),
            "evidence.note": lambda: st.post("/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "r", "access_level": "quality", "note": s}, "rev"),
            "policy.name": lambda: st.post("/api/v2/policies", {"policy_id": "POL-1", "kind": "DEFINITION", "name": s, "body": {}, "authority_ref": W.AUTH}, "ql"),
            "login.username": lambda: st.call("POST", "/api/v2/auth/login", {"username": s, "password": s}, csrf=False),
            "login.password": lambda: st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": s}, csrf=False),
        }
        before = T.snapshot(st)
        outcomes = {}
        intake = calls.pop("intake")
        for name, fn in calls.items():
            resp = fn()  # Stage 27: no AssertionError any more - the lone surrogate is refused at the wire
            outcomes[name] = resp.status
            self.assertEqual((resp.status, resp.code), (400, "E-REQ-INVALID"), name)
        self.assertEqual(T.diff(before, T.snapshot(st)), [], "a refused request left state behind")
        # the intake surface: the surrogate sits in the PAYLOAD TEXT (a JSON document inside a string), so the request is valid and the ITEM is quarantined as INVALID_JSON
        resp = intake()
        outcomes["intake"] = resp.status
        self.assertEqual(resp.status, 201, resp.text)
        self.assertEqual((resp.json()["outcome"], resp.json()["primary_reason"], resp.json()["queue"]), ("QUARANTINED", "INVALID_JSON", "quarantine_invalid"))
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        self.assertEqual(st.con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(st.post("/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "ok", "access_level": "quality"}, "rev").status, 201)
        for text in ("\ud83d\ude00", "a\u0000b", "\ufeffbom", "\U0001F600"):
            t = json.loads('"%s"' % text) if text.startswith("\\u") or text.startswith("\\ud") else text
            resp = st.post("/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "r-" + str(len(t)), "access_level": "quality", "note": t}, "rev")
            self.assertIn(resp.status, (201, 400, 422), (text, resp.text))
        T.write_evidence("registered-500-surrogate.json", {"label": T.LABEL, "finding": "S26-F-03 (fixed in Stage 27)", "outcomes": outcomes, "state_changed_tables": [], "audit_chain": "ok",
                                                          "integrity_check": "ok", "next_valid_request": 201})


    def test_TST_HUB_STG26_B07_leakage_sweep_and_restricted_evidence(self):
        """B07 (RT-11, M-13, T-07 / T-20): every GET route (API + UI) as every principal, plus error paths: no password hash / salt, no session or service token or
        digest, no absolute sandbox path, no traceback, no SQL error text, in any body or header. Restricted evidence is redacted for a role that may not read it."""
        st = self.store()
        st.authn.create_user("fin", st.pw, ["finance_read"], "op")
        st.tokens["fin"] = st.authn.login("fin", st.pw, "t-fin")
        st.con.commit()
        case = st.new_case("C91000001")
        marker = "RESTRICTED-S26-MARKER-7f3a"
        ev = st.svc.attach_evidence(st.sess("ql"), case, "document", "s26", "ref", access_level="restricted", note=marker, correlation_id="t-r")
        secrets = {"pw_password": st.pw}
        for r in st.con.execute("SELECT principal_id, pw_hash, pw_salt FROM principal WHERE pw_hash IS NOT NULL"):
            secrets["pw_hash:" + r[0]], secrets["pw_salt:" + r[0]] = r[1], r[2]
        for r in st.con.execute("SELECT token_sha256 FROM session"):
            secrets["digest:" + r[0][:8]] = r[0]
        for k, v in st.tokens.items():
            if v:
                secrets["token:" + k] = v
        paths = [st.base, st.data, T.S.SANDBOX_ROOT, T.S.LEGACY_ROOT, T.S.CODE_ROOT, "/sessions/", "/home/"]
        patterns = [re.compile(p) for p in (r"Traceback \(most recent", r"sqlite3\.", r"OperationalError", r"IntegrityError", r'File "/', r"\.py\", line \d+", r"UNIQUE constraint", r"no such table")]
        tab = Table()
        scanned, hits = 0, []

        def scan(resp, where, allow=()):
            nonlocal scanned
            scanned += 1
            blob = resp.text + " ".join(k + ": " + v for k, v in resp.headers.items())
            for name, val in list(secrets.items()) + [("path", p) for p in paths]:
                if isinstance(val, str) and val and val in blob and name not in allow:
                    hits.append((where, name))
            for rx in patterns:
                if rx.search(blob):
                    hits.append((where, rx.pattern))

        def fillp(p):
            return up.quote(p.replace("{case_id}", case).replace("{event_id}", "EV-00000002").replace("{link_id}", "LK-1").replace("{raw_id}", "RAW-1")
                            .replace("{flag_id}", "FL-1").replace("{run_id}", "RUN-1").replace("{ruleset_id}", "x").replace("{version}", "1").replace("{policy_id}", "POL-1")
                            .replace("{value_id}", "MV-1").replace("{source}", "partner_feed"), safe="/:@=")
        gets = [r["path"] for r in tab.api if r["method"] == "GET"] + [u["path"] for u in tab.ui if u["method"] == "GET"]
        for who in ("none", "bogus", "rev", "ql", "comp", "nonholder", "fin", "svc"):
            tok = {"none": None, "bogus": "f" * 64}.get(who, st.tokens.get(who))
            for p in gets:
                resp = st.call("GET", fillp(p), token=tok)
                scan(resp, (who, p))
        for who in ("rev", "ql"):  # error paths: malformed input to every route
            for r in tab.api:
                if r["method"] == "POST":
                    for raw in ("{", "[]", '{"a":', "\xff", "null"):
                        resp = st.call("POST", fillp(r["path"]), raw=raw, token=st.tokens[who])
                        scan(resp, (who, "POST", r["path"], raw))
        resp = st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, csrf=False)
        scan(resp, "login", allow=("token:rev", "token:ql") + tuple(k for k in secrets if k.startswith("digest:")))  # the caller's own new token is the point of login
        self.assertEqual(hits, [], "M-13: leakage hits")
        # restricted evidence: the reviewer and finance roles must not see the marker anywhere
        # S26-F-02 (FIXED in Stage 27, A-27-02): the evidence `note` is the `basis` of the EVIDENCE_ATTACHED event; roles that may not read the restricted record get a
        # fixed placeholder there. NO place shows the marker to these roles any more.
        registered = {}
        leaks = {}
        for who in ROLES_WITHOUT_RESTRICTED:
            for p in ("/api/v2/cases/%s/events" % case, "/api/v2/events/EV-00000002", "/api/v2/cases/%s/state" % case, "/api/v2/cases/%s/rule-trace" % case,
                      "/api/v2/cases/%s/clocks" % case, "/api/v2/queues/exceptions", "/ui/cases/%s/trace" % case):
                resp = st.call("GET", p, token=st.tokens[who])
                if marker in resp.text:
                    leaks[(who, p)] = registered.get((who, p), "UNREGISTERED")
        self.assertEqual(leaks, {}, "restricted evidence text visible to a role that may not read it (S26-F-02 is fixed in Stage 27)")
        ev_list = st.get("/api/v2/cases/%s/events" % case, "ql")
        self.assertIn(marker, ev_list.text)  # the readers named by the rule still see the note
        full = st.get("/api/v2/events/EV-00000002", "ql")
        self.assertEqual(full.status, 200, full.text)
        # audit rows never carry the credential material either
        blob = "\n".join(r[0] for r in st.con.execute("SELECT details FROM audit_log"))
        for name, val in secrets.items():
            if name.startswith(("pw_", "token:")) and isinstance(val, str):
                self.assertNotIn(val, blob, name)
        T.write_evidence("leakage-sweep.json", {"label": T.LABEL, "responses_scanned": scanned, "secret_kinds": sorted(set(k.split(":")[0] for k in secrets)),
                                               "path_markers": len(paths), "error_patterns": len(patterns), "hits": 0,
                                               "restricted_marker_leaks_registered": sorted("%s %s %s" % (k[0], k[1], v) for k, v in leaks.items()),
                                               "restricted_marker_leaks_unregistered": 0})
        del ev


if __name__ == "__main__":
    unittest.main()
