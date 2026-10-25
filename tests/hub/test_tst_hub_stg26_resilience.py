"""Stage 26 resilience tests (DW-21; dimension 6; threats T-15, T-16, T-19, T-23; thresholds RT-12). Fault injection in PRIVATE sandbox stores only - never DR or
availability testing (Stages 28 / 29, class C): no recovery time or point is claimed. Synthetic, unvalidated.

  C01  store faults: read-only file, corrupt header, missing store -> fail closed (generic envelope, nothing on the wire), no partial state, recovery on restore
  C02  configuration faults through the hub.web CLI: invalid values refuse with E-CFG-INVALID, hub.kill refuses with E-HUB-KILLED, unreadable files refuse (registered
       findings S26-F-04 traceback instead of a code, S26-F-05 unknown keys ignored)
  C03  audit tamper: trigger refusal, altered / missing / truncated / anchor-edited chains are detected by verify and OP-SEC-04; the documented host-level full rewrite
       (R-SEC-1 / RS-03) is demonstrated, not claimed fixed
  C04  concurrency: 8 clients x 8 requests on the real loopback listener -> no 5xx, no lost audit row, chain verifies, idempotent writes apply once
  C05  clock rollback after expiry does not revive a session or a re-authentication proof
  C06  transport anomalies on the listener (chunked, bad / duplicate / negative Content-Length, oversize header, garbage start line, absolute-URI target, pipelining,
       idle connections): defined 4xx or a closed socket, the server keeps answering; the missing read timeout is measured (registered finding S26-F-06)
"""
import hashlib
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import unittest

import _http8 as H
import _inc08 as W
import _stg26 as T
from hub.security import audit
from hub.store import db
from hub.web import server
from hub.web.app import Request, WebApp

# Stage 26 REGISTERED S26-F-04 (traceback instead of a code), S26-F-05 (unknown keys ignored), S26-F-06 (no read timeout) and S26-F-07 (generic 500 for a store fault).
# All four are FIXED in Stage 27 (S27-DEV-01 .. ); the tests below assert the fixed behaviour and the evidence files record the old observation for comparison.
REGISTERED = {"S26-F-04": "FIXED in Stage 27: an unreadable / non-JSON / non-object config file ends with E-CFG-INVALID (exit 2), no traceback",
              "S26-F-05": "FIXED in Stage 27: an unknown configuration key (top level or nested) is refused with E-CFG-INVALID",
              "S26-F-06": "FIXED in Stage 27: the listener sets a per-connection read timeout (hub.web.server.READ_TIMEOUT_SECONDS) and answers 408 E-REQ-TIMEOUT",
              "S26-F-07": "FIXED in Stage 27: a store fault answers 503 E-STORE-UNAVAILABLE (also /healthz), content-free"}


def setUpModule():
    T.skip_in_inner_egress_run()


def generic_500(tc, resp, where):
    """Stage 27 (S26-F-07): a store fault is 503 E-STORE-UNAVAILABLE - still content-free (name kept; it is the 'fail closed, nothing on the wire' check)."""
    tc.assertEqual(resp.status, 503, where)
    body = resp.body.decode("utf-8", "replace")
    doc = json.loads(body)
    tc.assertEqual(doc["error"]["code"], "E-STORE-UNAVAILABLE", where)
    for bad in (T.S.SANDBOX_ROOT, T.S.CODE_ROOT, "Traceback", "sqlite3", "OperationalError", "DatabaseError", "hub.sqlite3"):
        tc.assertNotIn(bad, body, (where, bad))


class TST_HUB_STG26_Resilience(unittest.TestCase):
    def store(self, **kw):
        kw["extra"] = dict({"rate_limit": {"enabled": False}}, **(kw.get("extra") or {}))  # Stage 27: some probes send > 100 refused requests
        st = W.WStore(**kw)
        self.addCleanup(st.close)
        return st

    def raw(self, st, method, path, body=None, token=None):
        h = {"Authorization": "Bearer " + token} if token else {}
        if method != "GET":
            h["X-Hub-Request"] = "1"
        data = json.dumps(body).encode("utf-8") if body is not None else b""
        if data:
            h["Content-Type"] = "application/json"
        r = st.app.handle(Request(method, path, {}, h, data))
        st.app.last_exception = None
        return r

    def test_TST_HUB_STG26_C01_store_faults_fail_closed(self):
        """C01 (RT-12, FD-01 / FD-02): a read-only store file and a corrupt header answer every request with 503 E-STORE-UNAVAILABLE (Stage 27, S26-F-07; before: the generic 500;
        nothing about paths, SQL or stack on the wire), change no data, and the very next request after the fault is removed succeeds with an intact chain and integrity_check ok. A missing store is refused at
        start-up with E-STORE-NOT-MIGRATED."""
        st = self.store(loaded=False)
        case = st.new_case("C91000001")
        dbp = os.path.join(st.data, db.HUB_DB_NAME)
        before = T.snapshot(st)
        outcomes = {}
        if os.geteuid() == 0:
            outcomes["readonly"] = "not applicable: running as root, chmod does not block writes"
        else:
            os.chmod(dbp, 0o444)
            try:
                for label, args in (("get", ("GET", "/api/v2/policies", None, st.tokens["rev"])),
                                    ("post", ("POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "r", "access_level": "quality"},
                                              st.tokens["rev"])),
                                    ("healthz", ("GET", "/healthz", None, None))):
                    r = self.raw(st, *args)
                    generic_500(self, r, "readonly " + label)
                    outcomes["readonly " + label] = r.status
            finally:
                os.chmod(dbp, 0o644)
        with open(dbp, "rb") as f:
            good = f.read(100)
        fd = os.open(dbp, os.O_WRONLY)
        try:
            os.pwrite(fd, b"X" * 100, 0)
        finally:
            os.close(fd)
        try:
            for p, tok in (("/api/v2/policies", st.tokens["rev"]), ("/healthz", None)):
                r = self.raw(st, "GET", p, None, tok)
                generic_500(self, r, "corrupt " + p)
                outcomes["corrupt " + p] = r.status
        finally:
            fd = os.open(dbp, os.O_WRONLY)
            os.pwrite(fd, good, 0)
            os.close(fd)
        r = self.raw(st, "GET", "/api/v2/policies", None, st.tokens["rev"])
        self.assertEqual(r.status, 200)
        ok = self.raw(st, "POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "after", "access_level": "quality"}, st.tokens["rev"])
        self.assertEqual(ok.status, 201, ok.body)
        diff = T.diff(before, T.snapshot(st))
        self.assertTrue(set(diff) <= set(["evidence_record", "decision_events", "case_state", "decision_idempotency"]), diff)
        self.assertEqual(st.con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        empty = T.S.tmpdir("c01-empty-")
        app = WebApp(empty, st.cfg, st.clock)
        try:
            app.start()
            started = True
            code = None
        except Exception as e:  # noqa: BLE001
            started, code = False, getattr(e, "code", type(e).__name__)
        self.assertFalse(started)
        self.assertEqual(code, "E-STORE-NOT-MIGRATED")
        T.write_evidence("store-faults.json", {"label": T.LABEL, "outcomes": outcomes, "missing_store_start": code, "recovery_request": 201, "integrity_check": "ok",
                                              "audit_chain": "ok", "observation": "S26-F-07 fixed in Stage 27: a fault surfaces as 503 E-STORE-UNAVAILABLE (fail closed, content-free), "
                                              "also on /healthz; before it was the generic E-HUB-INTERNAL 500"})

    def cli(self, cfg, st, command="status", extra=()):
        d = T.S.tmpdir("c02-")
        p = os.path.join(d, "c.json")
        if cfg == "MISSING":
            pass
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write(cfg if isinstance(cfg, str) else json.dumps(cfg))
        r = subprocess.run([sys.executable, "-B", "-m", "hub.web", "--config", p, command, "--data-dir", st.data] + list(extra), cwd=T.S.CODE_ROOT, env=T.S.child_env(),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
        try:
            code = json.loads(r.stderr)["code"]
        except ValueError:
            code = None
        return r.returncode, code, ("Traceback" in r.stderr)

    def test_TST_HUB_STG26_C02_configuration_faults(self):
        """C02 (RT-12, FD-03 / FD-04, T-23): invalid VALUES in safety settings are refused with E-CFG-INVALID (exit 2) and change nothing; hub.kill refuses with
        E-HUB-KILLED (exit 3); a non-default authority without approval_ref is refused; an unreadable / non-JSON / non-object file and an unknown key (top level or nested)
        are refused with E-CFG-INVALID, exit 2, no traceback (S26-F-04 / S26-F-05, fixed in Stage 27)."""
        import copy
        st = self.store(loaded=False)
        base = T.S.json.load(open(st.cfg_path)) if hasattr(T.S, "json") else json.load(open(st.cfg_path))
        before = T.snapshot(st)

        def mod(fn):
            c = copy.deepcopy(base)
            fn(c)
            return c
        cases = [
            ("valid", base, (0, None)),
            ("kill true", mod(lambda c: c.setdefault("hub", {}).update(kill=True)), (3, "E-HUB-KILLED")),
            ("kill string", mod(lambda c: c.setdefault("hub", {}).update(kill="false")), (2, "E-CFG-INVALID")),
            ("data_origin production", mod(lambda c: c.update(data_origin="production")), (2, "E-CFG-INVALID")),
            ("holders string", mod(lambda c: c.setdefault("zone_h", {}).update(holders="holder-1")), (2, "E-CFG-INVALID")),
            ("holders integers", mod(lambda c: c.setdefault("zone_h", {}).update(holders=[1, 2])), (2, "E-CFG-INVALID")),
            ("holders duplicate", mod(lambda c: c.setdefault("zone_h", {}).update(holders=["a", "a"])), (2, "E-CFG-INVALID")),
            ("reauth window -1", mod(lambda c: c.setdefault("zone_h", {}).update(reauth_window_seconds=-1)), (2, "E-CFG-INVALID")),
            ("reauth window 1e9", mod(lambda c: c.setdefault("zone_h", {}).update(reauth_window_seconds=10 ** 9)), (2, "E-CFG-INVALID")),
            ("pbkdf2 1", mod(lambda c: c.setdefault("auth", {}).update(pbkdf2_iterations=1)), (2, "E-CFG-INVALID")),
            ("authoritative without approval_ref", mod(lambda c: c.setdefault("capability_authority", {}).update(intake="authoritative")), (2, "E-CFG-INVALID")),
            ("runtime floor 3.99", mod(lambda c: c.setdefault("runtime", {}).update(floor="3.99")), (2, "E-CFG-INVALID")),
        ]
        observed, wrong = {}, []
        for name, cfg, want in cases:
            rc, code, tb = self.cli(cfg, st)
            observed[name] = [rc, code, tb]
            if (rc, code) != want or tb:
                wrong.append((name, rc, code, tb))
        self.assertEqual(wrong, [], "configuration fault not refused as designed")
        # Stage 27: S26-F-04 / S26-F-05 are fixed - these now refuse with a hub code, exit 2, no traceback
        reg = {}
        for name, cfg in (("file missing", "MISSING"), ("truncated JSON", '{"data_origin": "synth'), ("not JSON", "hello"), ("JSON array", []),
                          ("unknown top-level key", mod(lambda c: c.update(bogus_key=1))), ("unknown zone_h key", mod(lambda c: c.setdefault("zone_h", {}).update(holderz=["x"]))),
                          ("mistyped kill key", mod(lambda c: c.setdefault("hub", {}).update(kil=True)))):
            rc, code, tb = self.cli(cfg, st)
            reg[name] = [rc, code, tb]
            self.assertEqual((rc, code, tb), (2, "E-CFG-INVALID", False), name)
        self.assertEqual(T.diff(before, T.snapshot(st)), [], "a refused configuration changed state")
        T.write_evidence("config-faults.json", {"label": T.LABEL, "refused_as_designed": observed, "registered": reg, "registered_findings": REGISTERED})

    def fresh(self):
        st = self.store(loaded=False)
        st.new_case("C91000001")
        st.new_case("C91000002")
        st.con.commit()
        audit.write_anchor(st.con, st.anchor_path)
        self.addCleanup(lambda: open(st.anchor_path, "w").close())  # close() appends an anchor; leave it a readable (empty) file
        return st

    def drop_triggers(self, st):
        names = [r[0] for r in st.con.execute("SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = 'audit_log'")]
        for n in names:
            st.con.execute('DROP TRIGGER "%s"' % n)
        st.con.commit()
        return names

    def test_TST_HUB_STG26_C03_audit_tamper_is_detected_and_the_known_limit_is_shown(self):
        """C03 (RT-12, FD-05, T-15): SQL edits of audit_log are refused by the insert-only triggers; with the triggers removed (host-level access) an altered row, a
        missing middle row, a truncated tail covered by the anchor, an edited anchor line and an unreadable anchor are each reported by verify (and OP-SEC-04 over HTTP);
        a COMPLETE recompute of the chain and the anchor by someone with host access verifies ok - the documented limitation R-SEC-1 / RS-03 (the opt-in seal of
        Stage 24 is the mitigation; not enabled here)."""
        out = {}
        # (a) triggers refuse
        st = self.fresh()
        n0 = T.audit_n(st)
        for sql in ("UPDATE audit_log SET outcome = 'success' WHERE audit_seq = 3", "DELETE FROM audit_log WHERE audit_seq = 3", "DELETE FROM audit_log"):
            with self.assertRaises(Exception):
                st.con.execute(sql)
                st.con.commit()
            st.con.rollback()
        self.assertEqual(T.audit_n(st), n0)
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        out["trigger_refusal"] = "refused"
        # (b) altered row
        st = self.fresh()
        trg = self.drop_triggers(st)
        self.assertGreaterEqual(len(trg), 1)
        st.con.execute("UPDATE audit_log SET reason = 'tampered-s26' WHERE audit_seq = 5")
        st.con.commit()
        rep = audit.verify(st.con, st.anchor_path)
        self.assertEqual((rep["status"], rep["first_broken_seq"], rep["kind"]), ("broken", 5, "altered_record"), rep)
        tok = st.tokens["ql"]
        r = st.call("POST", "/api/v2/audit/verify", {}, token=tok)
        self.assertEqual(r.status, 201, r.text)
        self.assertEqual((r.json()["ok"], r.json()["failure_kind"], r.json()["first_broken_seq"]), (False, "altered", 5))
        out["altered_row"] = [rep["kind"], rep["first_broken_seq"]]
        # (c) missing middle row
        st = self.fresh()
        self.drop_triggers(st)
        st.con.execute("DELETE FROM audit_log WHERE audit_seq = 7")
        st.con.commit()
        rep = audit.verify(st.con, st.anchor_path)
        self.assertEqual((rep["status"], rep["first_broken_seq"], rep["kind"]), ("broken", 7, "missing_record"), rep)
        out["missing_row"] = [rep["kind"], rep["first_broken_seq"]]
        # (d) truncated tail, anchored
        st = self.fresh()
        head_seq = audit.head(st.con)[0]
        self.drop_triggers(st)
        st.con.execute("DELETE FROM audit_log WHERE audit_seq > ?", (head_seq - 3,))
        st.con.commit()
        rep = audit.verify(st.con, st.anchor_path)
        self.assertEqual(rep["status"], "broken", rep)
        out["truncated_tail_anchored"] = [rep["kind"], rep["first_broken_seq"]]
        # (e) anchor edited / unreadable / deleted
        for label, mutate in (("anchor_hash_edited", lambda txt: txt.replace('"hash":"', '"hash":"0', 1)), ("anchor_not_json", lambda txt: "not json\n" + txt)):
            st = self.fresh()
            with open(st.anchor_path, encoding="utf-8") as f:
                txt = f.read()
            with open(st.anchor_path, "w", encoding="utf-8") as f:
                f.write(mutate(txt))
            rep = audit.verify(st.con, st.anchor_path)
            self.assertEqual(rep["status"], "broken", (label, rep))
            out[label] = [rep["kind"], rep.get("first_broken_seq")]
        st = self.fresh()
        os.remove(st.anchor_path)
        rep = audit.verify(st.con, st.anchor_path)
        out["anchor_deleted"] = [rep["status"], rep.get("kind")]  # recorded: the chain alone still verifies (an anchor is an extra witness)
        # (f) the documented limit: full recompute by a host-level attacker
        st = self.fresh()
        self.drop_triggers(st)
        st.con.execute("UPDATE audit_log SET reason = 'rewritten-s26' WHERE audit_seq = 5")
        prev = "0" * 64
        rows = st.con.execute("SELECT " + ", ".join(audit.FIELDS) + ", prev_hash, hash FROM audit_log ORDER BY audit_seq").fetchall()
        newh = {}
        for row in rows:
            rec = audit._row_record(row)
            h = audit.record_hash(prev, rec)
            st.con.execute("UPDATE audit_log SET prev_hash = ?, hash = ? WHERE audit_seq = ?", (prev, h, row[0]))
            newh[row[0]] = h
            prev = h
        st.con.commit()
        lines = [json.dumps({"audit_seq": a["audit_seq"], "hash": newh[a["audit_seq"]], "occurred_at": a["occurred_at"]}, sort_keys=True, separators=(",", ":"))
                 for a in audit.read_anchors(st.anchor_path)]
        with open(st.anchor_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        rep = audit.verify(st.con, st.anchor_path)
        self.assertEqual(rep["status"], "ok", rep)
        out["full_rewrite_by_host_attacker"] = "verifies ok (R-SEC-1 / RS-03 limitation, seal opt-in)"
        T.write_evidence("audit-tamper.json", {"label": T.LABEL, "results": out})

    def test_TST_HUB_STG26_C04_concurrent_clients_on_the_loopback_listener(self):
        """C04 (RT-12, FD-06, T-19): 8 client threads x 8 requests (health, an authorised read, a CSRF-refused write, an unauthorised read, a valid evidence write, and the
        same idempotent write 3 times) against the real listener -> every answer is the expected 2xx / 4xx, no 5xx, every refusal audited, the idempotent write is applied
        once per key, integrity_check ok and the audit chain verifies."""
        st = self.store(loaded=False)
        case = st.new_case("C91000001")
        st.con.commit()
        n_threads, results, errors = 8, [], []
        lock = threading.Lock()
        a0 = T.audit_n(st)
        with H.Served(st.app) as srv:
            def worker(k):
                try:
                    rev = {"Authorization": "Bearer " + st.tokens["rev"], "X-Hub-Request": "1"}
                    got = []
                    got.append(("health", srv.request("GET", "/healthz").status, 200))
                    got.append(("read", srv.request("GET", "/api/v2/policies", headers=rev).status, 200))
                    got.append(("csrf", srv.request("POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "c%d" % k, "access_level": "quality"},
                                                    headers={"Authorization": "Bearer " + st.tokens["rev"]}).status, 403))
                    got.append(("forbidden", srv.request("GET", "/api/v2/audit/records", headers=rev).status, 403))
                    got.append(("write", srv.request("POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "w%d" % k, "access_level": "quality"},
                                                     headers=rev).status, 201))
                    for _ in range(3):
                        got.append(("idem", srv.request("POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": "i%d" % k, "access_level": "quality"},
                                                        headers=dict(rev, **{"Idempotency-Key": "s26-idem-%d" % k})).status, 201))
                    with lock:
                        results.extend(got)
                except Exception as e:  # noqa: BLE001
                    with lock:
                        errors.append(repr(e))
            threads = [threading.Thread(target=worker, args=(k,)) for k in range(n_threads)]
            t0 = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join(150)
            wall = round(time.time() - t0, 1)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), n_threads * 8)
        bad = [(k, got, want) for k, got, want in results if got != want]
        self.assertEqual(bad, [], "unexpected answers under concurrency")
        self.assertEqual(st.count("evidence_record", "source_ref LIKE 'w%'"), n_threads)
        self.assertEqual(st.count("evidence_record", "source_ref LIKE 'i%'"), n_threads, "an idempotent write was applied more than once")
        self.assertEqual(st.count("audit_log", "action = 'CSRF_REFUSED'"), n_threads)
        self.assertEqual(st.con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        rep = T.verify_chain(st)
        self.assertEqual(rep["status"], "ok", rep)
        T.write_evidence("concurrency.json", {"label": T.LABEL, "threads": n_threads, "requests": len(results), "unexpected": 0, "wall_seconds": wall,
                                             "audit_rows_added": T.audit_n(st) - a0, "integrity_check": "ok", "audit_chain": "ok",
                                             "note": "sandbox proxy only; no throughput or latency claim (class C)"})

    def test_TST_HUB_STG26_C05_clock_rollback_does_not_revive_sessions_or_proofs(self):
        """C05 (RT-12, FD-07): a session that expired is revoked on first sight; moving the clock back afterwards does not revive it, and a re-authentication proof of the
        dead session is refused; a Zone H action with the stale proof writes nothing."""
        st = self.store()
        proof = st.reauth_token("holder-1")
        zh0 = st.zh_counts()
        st.clock.advance(st.s["auth"]["session_idle_seconds"] + 600)
        r = st.zh("holder-1", "ZH-08", {"mode": "event", "values": ["accept"]}, reauth_token=proof)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-SESSION-EXPIRED"), r.text)
        st.clock.advance(-(st.s["auth"]["session_idle_seconds"] + 600))
        r = st.zh("holder-1", "ZH-08", {"mode": "event", "values": ["accept"]}, reauth_token=proof)
        self.assertEqual(r.status, 401, r.text)
        self.assertEqual(st.call("GET", "/api/v2/policies", token=st.tokens["holder-1"]).status, 401)
        self.assertEqual(st.zh_counts(), zh0)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("clock-rollback.json", {"label": T.LABEL, "revived": False, "zone_h_written": 0})

    def test_TST_HUB_STG26_C06_transport_anomalies_on_the_listener(self):
        """C06 (RT-12, T-19): raw-socket anomalies against the real loopback listener. Each ends in a defined 4xx or a closed socket, never a 5xx, and /healthz answers
        afterwards. S26-F-06 (fixed in Stage 27): the handler class has a read timeout (10 s) and a client that sends fewer body bytes than it declared is
        answered 408 E-REQ-TIMEOUT (here with a 1 s timeout) instead of holding a thread."""
        st = self.store(loaded=False)
        seen = {}
        with H.Served(st.app, read_timeout=1.0) as srv:
            host, port = srv.host, srv.port
            base = "Host: 127.0.0.1:%d\r\n" % port

            def rawreq(payload, timeout=4):
                try:
                    r = H.raw(host, port, payload, timeout=timeout)
                    return r.status, r.body[:200]
                except (ValueError, IndexError):
                    return "closed-or-unparsable", b""
                except OSError as e:
                    return "oserror:" + type(e).__name__, b""
            probes = {
                "chunked": ("POST /api/v2/policies HTTP/1.1\r\n" + base + "Transfer-Encoding: chunked\r\nContent-Type: application/json\r\n\r\n0\r\n\r\n").encode(),
                "cl-negative": ("POST /api/v2/policies HTTP/1.1\r\n" + base + "Content-Length: -5\r\nContent-Type: application/json\r\n\r\n").encode(),
                "cl-text": ("POST /api/v2/policies HTTP/1.1\r\n" + base + "Content-Length: abc\r\nContent-Type: application/json\r\n\r\n").encode(),
                "cl-duplicate": ("POST /api/v2/policies HTTP/1.1\r\n" + base + "Content-Length: 2\r\nContent-Length: 4\r\nContent-Type: application/json\r\n\r\n{}").encode(),
                "cl-huge": ("POST /api/v2/policies HTTP/1.1\r\n" + base + "Content-Length: 99999999999\r\nContent-Type: application/json\r\n\r\n{}").encode(),
                "header-line-70k": ("GET /healthz HTTP/1.1\r\n" + base + "X-Big: " + "a" * 70000 + "\r\n\r\n").encode(),
                "headers-200": ("GET /healthz HTTP/1.1\r\n" + base + "".join("X-H%d: v\r\n" % i for i in range(200)) + "\r\n").encode(),
                "garbage": b"\x00\x01\x02 not http\r\n\r\n",
                "http09": b"GET /healthz\r\n",
                "http10": b"GET /healthz HTTP/1.0\r\n\r\n",
                "absolute-uri": ("GET http://evil.example/healthz HTTP/1.1\r\n" + base + "\r\n").encode(),
                "pipelined": ("GET /healthz HTTP/1.1\r\n" + base + "\r\nGET /api/v2/policies HTTP/1.1\r\n" + base + "\r\n").encode(),
                "bare-lf": ("GET /healthz HTTP/1.1\n" + "Host: x\n\n").encode(),
                "long-uri": ("GET /" + "a" * 70000 + " HTTP/1.1\r\n" + base + "\r\n").encode(),
            }
            for name, payload in probes.items():
                seen[name] = rawreq(payload)[0]
            bad = dict((k, v) for k, v in seen.items() if isinstance(v, int) and v >= 500)
            self.assertEqual(bad, {}, "5xx from a transport anomaly")
            self.assertEqual(seen["chunked"], 400)
            self.assertEqual(seen["cl-negative"], 400)
            self.assertEqual(seen["cl-text"], 400)
            self.assertEqual(rawreq(("GET /healthz HTTP/1.1\r\n" + base + "\r\n").encode())[0], 200, "listener stopped answering")
            # idle connections do not starve the server
            idle = [socket.create_connection((host, port), timeout=3) for _ in range(40)]
            try:
                self.assertEqual(rawreq(("GET /healthz HTTP/1.1\r\n" + base + "\r\n").encode())[0], 200)
            finally:
                for s in idle:
                    s.close()
            # S26-F-06 (fixed): a short body is answered 408 after the read timeout
            s = socket.create_connection((host, port), timeout=5)
            try:
                s.sendall(("POST /api/v2/policies HTTP/1.1\r\n" + base + "Content-Type: application/json\r\nContent-Length: 1000\r\n\r\n{}").encode())
                t0 = time.time()
                head = s.recv(12)
                waited = time.time() - t0
            finally:
                s.close()
            self.assertEqual(head, b"HTTP/1.1 408", head)
            self.assertLess(waited, 4.0)
            self.assertEqual(server.make_handler(st.app).timeout, server.READ_TIMEOUT_SECONDS)
            self.assertEqual(server.READ_TIMEOUT_SECONDS, 10)
            self.assertEqual(rawreq(("GET /healthz HTTP/1.1\r\n" + base + "\r\n").encode())[0], 200)
        T.write_evidence("transport-anomalies.json", {"label": T.LABEL, "statuses": dict((k, str(v)) for k, v in seen.items()), "http_5xx": 0,
                                                     "short_body_answered": 408, "handler_timeout_seconds": server.READ_TIMEOUT_SECONDS, "registered": REGISTERED["S26-F-06"]})


if __name__ == "__main__":
    unittest.main()
