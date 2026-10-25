"""Stage 26 red-team tests, part A: control bypass, excessive agency, tool abuse, session and CSRF abuse (DW-21; threats T-03, T-09, T-11, T-12, T-17, T-19).
The product is No-AI (OD-08): these attack the DETERMINISTIC controls. Thresholds RT-09 / RT-10 are declared in docs/26-tevv/release-thresholds.md before
this file ran. A test records what it observes in evidence JSON; a failing assertion is a finding (red-team-findings.md), never a reason to edit a threshold.
Synthetic, unvalidated. The Zone H holder list used in A03 / A06 (holder-1, holder-2) is SYNTHETIC TEST DATA inside sandbox stores only: the shipped config keeps
zone_h.holders EMPTY and A02 runs with exactly that.

  A01  route x principal matrix over the 48 API operations and the UI GET routes against the registries (RT-09)
  A02  Zone H attempts ZH-01..ZH-10 by every actor kind with the SHIPPED empty holder list: all refused, zero footprint (RT-10)
  A03  identity confusion (look-alike holder ids), re-authentication boundary window-1 / window / window+1, replayed and foreign proofs (RT-10, ED-01, ED-06)
  A04  mass-assignment keys and spoofed identity / method headers have no effect (RT-09, RT-10)
  A05  CSRF: every authenticated POST without proof is refused and writes nothing; no CORS header anywhere (RT-09)
  A06  sessions: token after logout, bearer / cookie precedence, fixation, idle and absolute expiry boundaries (RT-09, ED-05, FD-07)
  A07  unauthenticated flood: audit amplification measured and the raw hostile path never stored (RT-A13, informational)
"""
import unittest
import urllib.parse as up

import _inc08 as W
import _stg26 as T
from hub.gate import reauth as greauth
from hub.security import audit
from hub.web import tokens as wtokens
from hub.web.routes import Table

HUMAN_ROLES = {"rev": ["reviewer"], "ql": ["quality_lead"], "comp": ["compliance"], "nonholder": ["dispositioner"], "fin": ["finance_read"]}
ROLE_OF = dict(HUMAN_ROLES, svc=["integration"])
PRINCIPALS = ["none", "bogus", "rev", "ql", "comp", "nonholder", "fin", "svc"]
GATE_OPS = ("OP-GATE-01", "OP-GATE-02", "UI-PACK", "UI-DISPOSITION")
EXCLUDED = ("OP-SEC-01", "OP-SEC-02")  # login is public, logout revokes the very session under test (A06)
BOGUS = "f" * 64
# Findings REGISTERED by this stage (docs/26-tevv/red-team-findings.md). The test still fails on any OTHER mismatch; it never hides a new one.
# S26-F-01 was REGISTERED here in Stage 26 (OP-GATE-02 answered 422 E-GATE-UNKNOWN-ACTION before it looked at the session). Fixed in Stage 27 (hub/gate/service.py,
# S27-DEV-05): authentication first, 401 E-AUTH-UNAUTHENTICATED. The registry is now empty and A01 asserts that no registered deviation remains.
REGISTERED_A01 = {}


def setUpModule():
    T.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def store(self, loaded=False, **kw):
        kw["extra"] = dict({"rate_limit": {"enabled": False}}, **(kw.get("extra") or {}))  # Stage 27: the sweeps below send > 100 refused requests; A07 turns the limiter on
        st = W.WStore(loaded=loaded, **kw)
        self.addCleanup(st.close)
        st.authn.create_user("fin", st.pw, ["finance_read"], "op")
        st.tokens["fin"] = st.authn.login("fin", st.pw, "t-fin")
        st.authn.create_user("svc-int", st.pw, ["integration"], "op", kind="service")
        st.tokens["svc"] = wtokens.issue(st.con, st.clock, st.anchor, "svc-int", "s26 synthetic service token", "op")
        st.tokens["bogus"] = BOGUS
        st.tokens["none"] = None
        st.con.commit()
        return st

    def hit(self, st, who, method, path, body=None, **kw):
        return st.call(method, path, body, token=st.tokens[who], **kw)


def fill(path, case):
    vals = {"case_id": case, "event_id": "EV-00000001", "link_id": "LK-00000001", "raw_id": "RAW-00000001", "flag_id": "FL-00000001", "run_id": "RUN-00000001",
            "ruleset_id": "as-found-python", "version": "1", "policy_id": "POL-00000001", "value_id": "MV-00000001", "source": "partner_feed"}
    out = path
    for k, v in vals.items():
        out = out.replace("{%s}" % k, v)
    assert "{" not in out, out
    return out


class TST_HUB_STG26_Control(_Base):

    def test_TST_HUB_STG26_A01_route_by_principal_matrix_matches_the_registries(self):
        """A01 (RT-09, T-09 / T-17): every registered operation x {no token, unknown token, 6 roles}. Outcome class must equal the registry: a role not in x-roles
        -> 403 (401 without a valid session), audited, and the store unchanged; a role in x-roles -> never 401 / never the generic E-AUTH-FORBIDDEN (Zone H routes
        may answer E-GATE-*), never 500."""
        st = self.store()
        case = st.new_case()
        tab = Table()
        routes = [r for r in tab.api if r["op_id"] not in EXCLUDED and "public" not in r["roles"]]
        self.assertEqual(len(tab.api), 48)
        cells, mism, deny_cells = 0, [], []
        before, a0 = T.snapshot(st), T.audit_n(st)
        for r in routes:
            path = fill(r["path"], case)
            for who in PRINCIPALS:
                roles = ROLE_OF.get(who, [])
                allowed = bool(set(roles) & set(r["roles"]))
                if allowed:
                    continue
                resp = self.hit(st, who, r["method"], path, {} if r["method"] == "POST" else None)
                cells += 1
                deny_cells.append((r["op_id"], who))
                want = 401 if who in ("none", "bogus") else 403
                codes = ("E-AUTH-UNAUTHENTICATED",) if want == 401 else ("E-AUTH-FORBIDDEN", "E-GATE-NOT-AUTHORISED")
                if resp.status != want or resp.code not in codes:
                    mism.append((r["op_id"], who, resp.status, resp.code))
        denied_delta = T.audit_n(st) - a0
        self.assertEqual(T.diff(before, T.snapshot(st)), [], "refused cells changed state")
        registered = [m for m in mism if REGISTERED_A01.get((m[0], m[1])) == (m[2], m[3], REGISTERED_A01.get((m[0], m[1]), (0, 0, ""))[2])]
        unexpected = [m for m in mism if m not in registered]
        self.assertEqual(registered, [], "S26-F-01 is fixed in Stage 27: no registered deviation remains")
        self.assertEqual(unexpected, [], "authorisation mismatches (RT-09)")
        self.assertGreaterEqual(denied_delta, len(deny_cells), "every refused request leaves an audit trace")
        # allowed cells: never 401, never the generic role refusal, never 500
        allow_cells, dist, bad = 0, {}, []
        for r in routes:
            path = fill(r["path"], case)
            for who in PRINCIPALS:
                if not (set(ROLE_OF.get(who, [])) & set(r["roles"])):
                    continue
                resp = self.hit(st, who, r["method"], path, {} if r["method"] == "POST" else None)
                allow_cells += 1
                dist[resp.status] = dist.get(resp.status, 0) + 1
                gate_ok = r["op_id"] in GATE_OPS and (resp.code or "").startswith("E-GATE-")
                if resp.status in (401, 500) or (resp.code == "E-AUTH-FORBIDDEN") or (resp.status == 403 and not gate_ok):
                    bad.append((r["op_id"], who, resp.status, resp.code))
        self.assertEqual(bad, [], "role-allowed cells refused for a role reason (RT-09)")
        # UI GET routes
        ui_rows = [u for u in tab.ui if u["method"] == "GET" and "public" not in u["roles"]]
        ui_bad, ui_cells = [], 0
        for u in ui_rows:
            path = fill(u["path"], case)
            for who in PRINCIPALS:
                resp = self.hit(st, who, "GET", path)
                ui_cells += 1
                allowed = bool(set(ROLE_OF.get(who, [])) & set(u["roles"]))
                if who in ("none", "bogus"):
                    ok = resp.status == 303 and dict(resp.headers).get("location") == "/ui/login"
                elif not allowed:
                    ok = resp.status == 403
                else:
                    gate_ok = u["op_id"] in GATE_OPS and (resp.code or "").startswith("E-GATE-")
                    ok = resp.status not in (401, 500) and (resp.status != 403 or gate_ok) and resp.code != "E-AUTH-FORBIDDEN"
                if not ok:
                    ui_bad.append((u["op_id"], who, resp.status, resp.code))
        self.assertEqual(ui_bad, [], "UI route mismatches (RT-09)")
        rep = T.verify_chain(st)
        self.assertEqual(rep["status"], "ok", rep)
        T.write_evidence("authz-matrix.json", {"label": T.LABEL, "api_routes_in_registry": len(tab.api), "api_routes_swept": len(routes),
                                              "principals": PRINCIPALS, "refused_cells": cells, "refused_mismatches": len(mism), "registered_deviations": [list(m) + [REGISTERED_A01[(m[0], m[1])][2]] for m in registered], "unregistered_mismatches": len(unexpected), "allowed_cells": allow_cells,
                                              "allowed_status_distribution": dict((str(k), v) for k, v in sorted(dist.items())), "allowed_mismatches": len(bad),
                                              "ui_get_routes": len(ui_rows), "ui_cells": ui_cells, "ui_mismatches": len(ui_bad), "audit_rows_added_by_refused_cells": denied_delta,
                                              "state_changed_tables": [], "audit_chain": rep["status"]})

    def test_TST_HUB_STG26_A02_zone_h_with_the_shipped_empty_holder_list_refuses_every_actor(self):
        """A02 (RT-10, T-03): holders EMPTY as shipped. ZH-01..ZH-10 by every actor kind -> refused (423 E-GATE-NO-HOLDERS for a human dispositioner, 403 for any
        other role or the service token, 401 without a session); no footprint in any non-volatile table; no accepted ZONE_H_ATTEMPT; chain verifies."""
        st = self.store(extra={"zone_h": {"holders": []}})
        self.assertEqual(st.s["zone_h"]["holders"], [])
        case = st.new_case()
        st.con.commit()
        before, zh0 = T.snapshot(st), st.zh_counts()
        a0 = st.count("audit_log", "action = 'ZONE_H_ATTEMPT'")
        attempts, bypass, seen = 0, [], {}
        for who in PRINCIPALS:
            for zh in T.ZH_ALL:
                proof = greauth.token_for(st.sess(who)) if who in ("nonholder", "rev", "ql", "comp") and who in st.tokens else "0" * 64
                body = {"action": zh, "case_id": case, "payload": {}, "pack_hash": "0" * 64, "authority_ref": W.AUTH, "reauth_token": proof}
                r = self.hit(st, who, "POST", "/api/v2/zone-h/actions", body)
                attempts += 1
                seen[(who, r.status, r.code)] = seen.get((who, r.status, r.code), 0) + 1
                want = {"none": (401, "E-AUTH-UNAUTHENTICATED"), "bogus": (401, "E-AUTH-UNAUTHENTICATED"), "nonholder": (423, "E-GATE-NO-HOLDERS")}.get(who, (403, "E-GATE-NOT-AUTHORISED"))
                if (r.status, r.code) != want:
                    bypass.append((who, zh, r.status, r.code))
        self.assertEqual(bypass, [], "M-12: Zone H attempts not refused as designed")
        self.assertEqual(T.diff(before, T.snapshot(st)), [])
        self.assertEqual(st.zh_counts(), zh0)
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'success'"), 0)
        self.assertGreaterEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT'") - a0, attempts - 0, "each attempt is traced")
        # the evidence-pack read (Zone H eligibility on a GET) is refused the same way
        for who in ("nonholder", "rev", "none"):
            self.assertIn(self.hit(st, who, "GET", "/api/v2/cases/%s/evidence-pack" % case).status, (401, 403, 423), who)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("zone-h-bypass-shipped.json", {"label": T.LABEL, "holders": [], "attempts": attempts, "bypasses": 0,
                                                       "outcomes": dict(("%s %s %s" % k, v) for k, v in sorted(seen.items()))})

    def test_TST_HUB_STG26_A03_identity_confusion_and_reauthentication_boundary(self):
        """A03 (RT-10, ED-01 / ED-06, T-03 / T-11) with the SYNTHETIC test holders holder-1 / holder-2: dispositioners whose id only LOOKS like a holder are refused
        (not_a_holder); the step-up window accepts window-1 s and window s and refuses window+1 s; an old, a foreign or a post-logout proof is refused."""
        st = self.store()
        self.assertEqual(st.s["zone_h"]["holders"], ["holder-1", "holder-2"])
        win = st.s["zone_h"]["reauth_window_seconds"]
        # (1) look-alike identities
        looks = ["Holder-1", "holder-1 ", "holder-1​", "hоlder-1", "holder-10", "holder-1.", "HOLDER-2", " holder-2", "holder-1\u0000"]
        made = {}
        for i, name in enumerate(looks):
            try:
                st.authn.create_user(name, st.pw, ["dispositioner"], "op")
                made[name] = st.authn.login(name, st.pw, "t-look-%d" % i)
            except Exception as e:  # noqa: BLE001 - creation refused is also a safe outcome; record which
                made[name] = "REFUSED:" + type(e).__name__
        st.con.commit()
        zh0, refused = st.zh_counts(), {}
        before = T.snapshot(st)
        for name, tok in made.items():
            if tok.startswith("REFUSED"):
                refused[name] = tok
                continue
            st.tokens["look"] = tok
            proof = self.hit(st, "look", "POST", "/api/v2/auth/reauth", {"password": st.pw})
            self.assertEqual(proof.status, 201, (name, proof.text))
            r = st.zh("look", "ZH-08", {"mode": "event", "values": ["accept"]}, reauth_token=proof.json()["reauth_token"])
            self.assertEqual((r.status, r.code), (403, "E-GATE-NOT-AUTHORISED"), (name, r.text))
            refused[name] = "not_a_holder"
        self.assertEqual(st.zh_counts(), zh0, "look-alike identities wrote Zone H events")
        self.assertEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'success'"), 0)
        # login names are exact-match: the holder's own name in another case does not reach the holder's principal
        r = st.call("POST", "/api/v2/auth/login", {"username": "HOLDER-1", "password": st.pw}, csrf=False)
        self.assertEqual(r.status, 401, r.text)
        # (2) boundary. The test clock ticks 1 microsecond per call, so "exactly the window" is not reachable over HTTP: probe +-1 s and +-1 ms over HTTP and
        # the exact equality / one microsecond over on the pure rule (zone_h.refusal), which is the single place the comparison is written.
        ok_events, outcomes = 0, {}
        for label, delta in (("window-1s", win - 1), ("window-1ms", win - 0.001), ("window+1ms", win + 0.001), ("window+1s", win + 1)):
            proof = st.reauth_token("holder-1")
            st.clock.advance(delta)
            r = st.zh("holder-1", "ZH-08", {"mode": "event", "values": ["accept", "reject"]}, reauth_token=proof)
            outcomes[label] = (r.status, r.code)
            if delta < win:
                self.assertEqual(r.status, 201, (label, r.text))
                ok_events += 1
            else:
                self.assertEqual((r.status, r.code), (401, "E-GATE-REAUTH-REQUIRED"), (label, r.text))
        self.assertEqual(st.count("policy_events", "event_type = 'DISPOSITION_MODE_CHANGED'"), ok_events)
        from hub.gate.dispositions import DispositionService  # noqa: F401  (import keeps the gate package loaded as in production)
        from hub.security import zone_h
        from hub.security.canonical import fmt, parse
        import datetime
        t0 = parse("2026-10-25T10:00:00.000000Z")

        class P(object):
            kind, roles, principal_id = "human", ["dispositioner"], "holder-1"
        for label, extra, want in (("exact", 0, None), ("+1us", 1e-6, zone_h.REAUTH), ("-1us", -1e-6, None)):
            now = fmt(t0 + datetime.timedelta(seconds=win + extra))
            outcomes["pure " + label] = zone_h.refusal(P, fmt(t0), lambda n=now: n, {"holders": ["holder-1"], "reauth_window_seconds": win})
            self.assertEqual(outcomes["pure " + label], want, label)
        # (3) proofs: an old proof after a newer re-authentication, a foreign proof, and a proof after logout
        old = st.reauth_token("holder-1")
        st.clock.advance(2)
        new = st.reauth_token("holder-1")
        n0 = st.zh_counts()
        r = st.zh("holder-1", "ZH-08", {"mode": "none", "values": []}, reauth_token=old)
        self.assertEqual(r.status, 401, r.text)
        foreign = st.reauth_token("holder-2")
        r = st.zh("holder-1", "ZH-08", {"mode": "none", "values": []}, reauth_token=foreign)
        self.assertEqual(r.status, 401, r.text)
        self.assertEqual(st.zh_counts(), n0)
        r = st.zh("holder-1", "ZH-08", {"mode": "none", "values": []}, reauth_token=new)
        self.assertEqual(r.status, 201, r.text)
        lo = self.hit(st, "holder-1", "POST", "/api/v2/auth/logout", {})
        self.assertEqual(lo.status, 201, lo.text)
        n1 = st.zh_counts()
        r = st.zh("holder-1", "ZH-08", {"mode": "event", "values": ["accept"]}, reauth_token=st.reauth_token("holder-2"), token=st.tokens["holder-1"])
        self.assertEqual(r.status, 401, r.text)
        self.assertEqual(st.zh_counts(), n1)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("zone-h-identity-boundary.json", {"label": T.LABEL, "test_only_holders": ["holder-1", "holder-2"], "window_seconds": win,
                                                          "lookalikes": refused, "boundary_outcomes": dict((str(k), v) for k, v in outcomes.items()),
                                                          "state_change_by_lookalikes": 0})
        del before

    def test_TST_HUB_STG26_A04_mass_assignment_and_spoofed_identity_have_no_effect(self):
        """A04 (RT-09 / RT-10, T-09 / T-17): the 19 mass-assignment keys added to a Zone H body and to a legitimate transition never change who acted or who is a
        holder; the 14 spoof headers (X-Hub-Role, X-User, X-Forwarded-*, method / URL override, Host, Origin, X-Hub-Request: 0) never change the principal, the
        route or the CSRF verdict."""
        st = self.store(extra={"zone_h": {"holders": []}})
        c = T.corpus()
        case = st.new_case()
        st.con.commit()
        mass = dict((k, "holder-1" if k in ("principal_id", "actor", "role") else ["dispositioner"] if k in ("roles", "holders") else
                     {"holders": ["nonholder"], "reauth_window_seconds": 99999} if k == "zone_h" else True if k in ("is_admin", "authoritative") else "x")
                    for k in c["mass_assignment_keys"])
        before = T.snapshot(st)
        body = {"action": "ZH-08", "case_id": case, "payload": {"mode": "event", "values": ["accept"]}, "authority_ref": W.AUTH,
                "reauth_token": greauth.token_for(st.sess("nonholder"))}
        body.update(mass)
        r = self.hit(st, "nonholder", "POST", "/api/v2/zone-h/actions", body)
        self.assertIn((r.status, r.code), ((423, "E-GATE-NO-HOLDERS"), (400, "E-REQ-INVALID")), r.text)
        # query-string and header variants of the same idea
        r = self.hit(st, "nonholder", "POST", "/api/v2/zone-h/actions?holders=nonholder&zone_h.holders=nonholder&principal=holder-1",
                     {"action": "ZH-08", "payload": {}, "authority_ref": W.AUTH, "reauth_token": "0" * 64})
        self.assertIn(r.status, (423, 400), r.text)
        self.assertEqual(T.diff(before, T.snapshot(st)), [])
        self.assertEqual(st.count("decision_events", "event_type LIKE 'DISPOSITION%'"), 0)
        self.assertEqual(st.count("flag_action"), 0)
        # a legitimate write by `rev` with mass keys: refused as unknown fields, or applied with the server-derived actor, never the injected one
        ev = self.hit(st, "rev", "POST", "/api/v2/cases/%s/evidence" % case,
                      dict({"kind": "document", "source": "s26", "source_ref": "ref-1", "access_level": "quality", "note": "n"}, **mass))
        self.assertIn(ev.status, (201, 400), ev.text)
        if ev.status == 201:
            rec = st.con.execute("SELECT recorded_by FROM evidence_record ORDER BY rowid DESC LIMIT 1").fetchone()
            self.assertEqual(rec[0], "rev")
        tr = self.hit(st, "rev", "POST", "/api/v2/cases/%s/transitions" % case,
                      dict({"to_state": "UNDER_REVIEW", "event_type": "STATE_CHANGE", "basis": "s26", "expected_seq": 1}, **mass))
        self.assertIn(tr.status, (201, 400, 409, 422), tr.text)
        for row in st.con.execute("SELECT actor FROM decision_events WHERE case_id = ?", (case,)):
            self.assertIn(row[0], ("rev", "hub", "system", "op", "backfill"), row)
        # spoofed headers
        spoof = c["spoof_headers"]
        for who, path, want_ok in (("rev", "/api/v2/policies", True), ("rev", "/api/v2/cases/%s/evidence-pack" % case, False), ("rev", "/api/v2/audit/records", False),
                                   ("none", "/api/v2/policies", False)):
            r = self.hit(st, who, "GET", path, headers=spoof)
            if want_ok:
                self.assertEqual(r.status, 200, (path, r.text))
            else:
                self.assertIn(r.status, (401, 403, 423), (who, path, r.status, r.text))
        r = self.hit(st, "none", "GET", "/healthz", headers=spoof)
        self.assertEqual(r.status, 200)
        self.assertEqual(r.json(), {"status": "ok"})  # X-Original-URL / X-Rewrite-URL / X-HTTP-Method-Override did not re-route it
        r = self.hit(st, "rev", "GET", "/api/v2/policies", headers={"X-HTTP-Method-Override": "POST"})
        self.assertEqual(r.status, 200)
        r = self.hit(st, "rev", "POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s26", "source_ref": "ref-2", "access_level": "quality"},
                     headers={"X-Hub-Request": "0"})
        self.assertEqual((r.status, r.code), (403, "E-SEC-CSRF"))
        self.assertEqual(st.count("decision_events", "event_type LIKE 'DISPOSITION%'"), 0)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("mass-assignment-spoofing.json", {"label": T.LABEL, "mass_keys": len(mass), "spoof_headers": len(spoof), "zone_h_effect": 0,
                                                          "evidence_actor_is_server_derived": True})

    def test_TST_HUB_STG26_A05_csrf_and_cors(self):
        """A05 (RT-09, T-12): every authenticated, role-allowed POST API operation without a valid X-Hub-Request proof is refused 403 E-SEC-CSRF (audited,
        nothing written); wrong proof values too; a UI form post with a missing or wrong csrf_token is refused; OPTIONS (a preflight) and cross-origin Origin /
        Referer never produce an Access-Control-* header; Access-Control headers appear on no answer at all."""
        st = self.store()
        case = st.new_case()
        tab = Table()
        posts = [r for r in tab.api if r["method"] == "POST" and "public" not in r["roles"] and r["op_id"] not in EXCLUDED]
        who_for = {"integration": "svc", "reviewer": "rev", "quality_lead": "ql", "compliance": "comp", "dispositioner": "nonholder"}
        before, a0, n, seen_cors = T.snapshot(st), st.count("audit_log", "action = 'CSRF_REFUSED'"), 0, []
        for r in posts:
            role = [x for x in r["roles"] if x in who_for][0]
            for bad in (None, "0", "true", "1 ", "yes", ""):
                hdr = {} if bad is None else {"X-Hub-Request": bad}
                resp = st.call("POST", fill(r["path"], case), {}, token=st.tokens[who_for[role]], csrf=False, headers=hdr)
                n += 1
                self.assertEqual((resp.status, resp.code), (403, "E-SEC-CSRF"), (r["op_id"], bad, resp.text))
                seen_cors += [k for k in resp.headers if k.startswith("access-control-")]
        self.assertEqual(T.diff(before, T.snapshot(st)), [])
        self.assertEqual(st.count("audit_log", "action = 'CSRF_REFUSED'") - a0, n)
        # UI form posts
        cookie = st.login_cookie("rev")
        for path, form in (("/ui/flags/FL-00000001/override", "action=dismiss&reason=x"), ("/ui/logout", "")):
            for body in (form, form + "&csrf_token=" + "0" * 64, form + "&csrf_token="):
                resp = st.call("POST", path, raw=body.lstrip("&"), cookie=cookie, ctype="application/x-www-form-urlencoded", csrf=False)
                self.assertEqual((resp.status, resp.code), (403, "E-SEC-CSRF"), (path, resp.text))
        # preflight and cross-origin hints
        for path in ("/api/v2/policies", "/api/v2/zone-h/actions", "/healthz", "/ui/"):
            for hdrs in ({}, {"Origin": "http://evil.example", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "x-hub-request"}):
                resp = st.call("OPTIONS", path, None, token=st.tokens["rev"], headers=hdrs, csrf=False)
                self.assertEqual(resp.status, 403, (path, resp.text))
                seen_cors += [k for k in resp.headers if k.startswith("access-control-")]
        resp = st.call("GET", "/api/v2/policies", None, token=st.tokens["rev"], headers={"Origin": "http://evil.example", "Referer": "http://evil.example/x"})
        self.assertEqual(resp.status, 200)
        seen_cors += [k for k in resp.headers if k.startswith("access-control-")]
        self.assertEqual(seen_cors, [])
        T.write_evidence("csrf-cors.json", {"label": T.LABEL, "post_operations": len(posts), "refused_requests": n, "cors_headers_seen": 0, "ui_form_cases": 6})

    def test_TST_HUB_STG26_A06_session_abuse_and_expiry_boundaries(self):
        """A06 (RT-09, ED-05, FD-07, T-11): a token is dead after logout (bearer and cookie); with BOTH a bearer and a cookie the bearer identity alone applies
        (roles are never merged); a cookie value chosen before login never becomes valid (no fixation); idle expiry: valid at idle, expired at idle+1; absolute expiry
        beats activity; a clock that moves backwards never extends or revives a session."""
        st = self.store()
        idle, absolute = st.s["auth"]["session_idle_seconds"], st.s["auth"]["session_absolute_seconds"]
        # logout kills the token for both carriers
        tok = st.authn.login("rev", st.pw, "t-a06")
        self.assertEqual(st.call("GET", "/api/v2/policies", token=tok).status, 200)
        self.assertEqual(st.call("POST", "/api/v2/auth/logout", {}, token=tok).status, 201)
        for kw in ({"token": tok}, {"cookie": tok}):
            self.assertEqual(st.call("GET", "/api/v2/policies", **kw).status, 401, kw)
        # precedence: bearer rev + cookie ql -> exactly rev (no audit read, which only ql / comp hold)
        r = st.call("GET", "/api/v2/audit/records", token=st.tokens["rev"], headers={"Cookie": "hub_session=" + st.tokens["ql"]})
        self.assertEqual(r.status, 403, r.text)
        r = st.call("GET", "/api/v2/audit/records", token=st.tokens["ql"], headers={"Cookie": "hub_session=" + st.tokens["rev"]})
        self.assertEqual(r.status, 200, r.text)
        # fixation: a chosen cookie value is not accepted before or after a login
        chosen = "a" * 64
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=chosen).status, 401)
        login = st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, csrf=False, headers={"Cookie": "hub_session=" + chosen})
        self.assertEqual(login.status, 201)
        self.assertNotEqual(login.json()["token"], chosen)
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=chosen).status, 401)
        # idle boundary (the previous request touched the session, so measure from a fresh login)
        t1 = st.authn.login("comp", st.pw, "t-idle")
        st.clock.advance(idle - 1)
        self.assertEqual(st.call("GET", "/api/v2/policies", token=t1).status, 200)  # one second inside the idle limit; the request touches the session
        st.clock.advance(idle - 1)
        self.assertEqual(st.call("GET", "/api/v2/policies", token=t1).status, 200)
        st.clock.advance(idle + 1)
        r = st.call("GET", "/api/v2/policies", token=t1)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-SESSION-EXPIRED"), r.text)
        # absolute: constant activity does not keep a session alive past the absolute limit
        t2 = st.authn.login("ql", st.pw, "t-abs")
        waited, st_codes = 0, []
        while waited <= absolute:
            st.clock.advance(1500)
            waited += 1500
            st_codes.append(st.call("GET", "/api/v2/policies", token=t2).status)
        self.assertEqual(st_codes[0], 200)
        self.assertEqual(st_codes[-1], 401, st_codes[-3:])
        self.assertTrue(all(c == 200 for c in st_codes[:-1]))
        # revoked / expired sessions stay dead when the clock goes back
        st.clock.advance(-(absolute * 2))
        self.assertEqual(st.call("GET", "/api/v2/policies", token=t2).status, 401)
        self.assertEqual(st.call("GET", "/api/v2/policies", token=t1).status, 401)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("session-abuse.json", {"label": T.LABEL, "idle_seconds": idle, "absolute_seconds": absolute, "absolute_probe_steps": len(st_codes)})

    def test_TST_HUB_STG26_A07_unauthenticated_flood_audit_amplification(self):
        """A07 (RT-A13, T-19; Stage 27 RS-04 fix): N unauthenticated requests to unknown routes. Before Stage 27 every one added an audit row (an unauthenticated
        client could grow the audit table). Now the per-peer limiter (rate_limit.max_rejected, default 100 per 60 s) answers 429 E-REQ-RATE-LIMITED with NO audit row
        once the peer is over the limit, so the growth is bounded by the limit; the hostile path text itself is never stored (only a 16-hex path digest)."""
        st = self.store(extra={"rate_limit": {"enabled": True}})
        limit = st.app.limiter.limit
        n, a0 = 200, T.audit_n(st)
        evil = "/api/v2/<script>alert(1)</script>/../../etc/passwd?x=1"
        b0 = st.con.execute("SELECT coalesce(sum(length(details)),0) FROM audit_log").fetchone()[0]
        r = st.call("GET", up.quote(evil, safe="/<>()"), None)
        self.assertEqual(r.status, 403)
        statuses = []
        for i in range(n):
            r = st.call("GET", "/nope/%d" % i if i % 2 else "/api/v2/x%d" % i, None)
            statuses.append(r.status)
            self.assertIn((r.status, r.code), ((403, "E-AUTH-FORBIDDEN"), (429, "E-REQ-RATE-LIMITED")))
        added = T.audit_n(st) - a0
        b1 = st.con.execute("SELECT coalesce(sum(length(details)),0) FROM audit_log").fetchone()[0]
        self.assertEqual(statuses.count(403), limit - 1)       # the evil-path request used one place of the window
        self.assertEqual(statuses.count(429), n - (limit - 1))
        self.assertEqual(added, limit)                          # bounded by the limit, not by the number of requests
        self.assertEqual(r.headers.get("retry-after") is not None, True)
        blob = " ".join(row[0] for row in st.con.execute("SELECT details FROM audit_log ORDER BY audit_seq DESC LIMIT 20"))
        self.assertNotIn("script", blob)
        self.assertNotIn("passwd", blob)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("audit-amplification.json", {"label": T.LABEL, "unauthenticated_requests": n + 1, "audit_rows_added": added, "limit": limit,
                                                     "answered_429": statuses.count(429), "detail_bytes_added": b1 - b0,
                                                     "raw_path_stored": False, "severity_if_loopback": "Low (RS-04, bounded by the Stage 27 limiter)"})


if __name__ == "__main__":
    unittest.main()
