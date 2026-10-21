"""Stage 23 control tests (DW-14, DW-15, DW-17; FAC-07, FAC-08; SS-04, SS-08; mutants H3, H5; FF-2 rules 3 and 4). Synthetic, unvalidated.

  S01-S02  DW-14  security response headers asserted by EXACT value on every kind of response (in-process and over the loopback wire)  [kills H3]
  S03-S05  DW-15  a non-loopback bind is refused even WITH exposure approval + approval reference + TLS keys (library, server, CLI exit 9)  [kills H5]
  S10-S16  DW-17  approval-gated authority switch: ships OFF, refused without approval_ref, accepted + audited CONFIG_CHANGED with it, L3 flip back to
                  `shadow`, out-of-band config edits audited, both modes (default / decided) leave every other control unchanged
"""
import json
import os
import unittest

import _support as S
import _inc03 as H3
import _inc08 as W
import _http8 as H
import _stg23 as T
from hub import config
from hub.control import flags
from hub.core.errors import ConfigInvalid
from hub.security import audit, exposure
from hub.security.errors import ExposureNotApproved
from hub.web import server
from hub.web.app import Request, SECURITY_HEADERS

EXPECTED_HEADERS = {"x-content-type-options": "nosniff", "content-security-policy": "default-src 'self'", "cache-control": "no-store",
                    "referrer-policy": "no-referrer", "x-frame-options": "DENY"}
APPROVED_NET = {"exposure_approved": True, "exposure_approval_ref": "SYNTHETIC-HAR-05-REF (test marker)",
                "tls": {"cert_file": "/etc/hub/synthetic.crt", "key_file": "/etc/hub/synthetic.key"}}
NON_LOOPBACK = ("0.0.0.0", "192.168.1.10", "10.0.0.5:8081", "::", "[::]:8081", "example.org")


def setUpModule():
    T.skip_in_inner_egress_run()


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

    def hstore(self, prefix="s23-", extra=None):
        st = H3.Store(prefix, extra=extra)
        self.stores.append(st)
        return st


class TST_HUB_STG23_Headers(_Base):

    def _check_headers(self, pairs, what):
        names = [k.lower() for k, _ in pairs]
        for k, v in EXPECTED_HEADERS.items():
            self.assertEqual(names.count(k), 1, "%s: header %s must appear exactly once" % (what, k))
            self.assertEqual(dict((a.lower(), b) for a, b in pairs)[k], v, "%s: header %s" % (what, k))
        self.assertEqual([n for n in names if n.startswith("access-control-")], [], what + ": no CORS header")

    def test_TST_HUB_STG23_S01_security_header_values_exact_in_process(self):
        """S01 (DW-14, FAC-07, SS-04): the SECURITY_HEADERS constant and the headers of every kind of response carry the exact values (CSP default-src
        'self', X-Frame-Options DENY, Referrer-Policy no-referrer, nosniff, Cache-Control no-store), once each, no CORS header. Weakening one value fails here."""
        self.assertEqual(sorted((k.lower(), v) for k, v in SECURITY_HEADERS), sorted(EXPECTED_HEADERS.items()))
        st = self.wstore(loaded=False)
        seen = {}
        cases = [("GET", "/healthz", None), ("GET", "/ui/login", None), ("GET", "/ui/static/app.css", None), ("GET", "/api/v2/cases/CASE-1", None),
                 ("GET", "/no/such/route", None), ("POST", "/api/v2/auth/login", b"{not json"), ("GET", "/ui/queue", None)]
        for method, path, body in cases:
            req = Request(method, path, {}, {"Content-Type": "application/json"} if body else {}, body or b"")
            resp = st.app.handle(req)
            seen[method + " " + path] = resp.status
            self._check_headers(resp.headers, "%s %s -> %s" % (method, path, resp.status))
        self.assertEqual(seen["GET /healthz"], 200)
        self.assertEqual(seen["GET /ui/login"], 200)
        self.assertIn(seen["GET /api/v2/cases/CASE-1"], (401, 403))
        self.assertIn(seen["GET /no/such/route"], (403, 404))
        self.assertGreaterEqual(len(set(seen.values())), 3, "a spread of status classes is exercised: %s" % seen)
        T.write_evidence("header-values.json", {"label": T.LABEL, "expected": EXPECTED_HEADERS, "requests": seen, "mutant": "H3 (X-Frame-Options DENY -> SAMEORIGIN)"})

    def test_TST_HUB_STG23_S02_security_header_values_exact_over_the_wire(self):
        """S02 (DW-14): the same exact values on the loopback listener, including the responses the server itself builds before the app runs
        (Transfer-Encoding refused, malformed Content-Length)."""
        st = self.wstore(loaded=False)
        with H.Served(st.app) as srv:
            replies = [("healthz", srv.request("GET", "/healthz")),
                       ("login-page", srv.request("GET", "/ui/login")),
                       ("unknown-route", srv.request("GET", "/nope")),
                       ("transfer-encoding", srv.request("POST", "/api/v2/auth/login", raw_body=b"", extra_lines=("Transfer-Encoding: chunked",))),
                       ("bad-content-length", srv.request("POST", "/api/v2/auth/login", headers={"Content-Length": "-5"}))]
        statuses = {}
        for name, rep in replies:
            statuses[name] = rep.status
            for k, v in EXPECTED_HEADERS.items():
                self.assertEqual(rep.headers.get(k), v, "%s: %s" % (name, k))
            self.assertFalse([h for h in rep.headers if h.startswith("access-control-")], name)
        self.assertEqual(statuses["healthz"], 200)
        self.assertEqual((statuses["transfer-encoding"], statuses["bad-content-length"]), (400, 400))


class TST_HUB_STG23_BindRefusal(_Base):

    def test_TST_HUB_STG23_S03_start_up_guard_alone_accepts_approved_exposure_and_the_server_refuses(self):
        """S03 (DW-15, FAC-08, SS-08, DEV-75): with exposure_approved + approval reference + TLS keys the INC-03 start-up guard ACCEPTS a non-loopback
        bind (TST-SEC-16 c); hub.web.server.bind_address (INC-08) still REFUSES it - for every non-loopback form - and accepts loopback forms."""
        for bind in NON_LOOPBACK:
            with self.subTest(bind=bind):
                net = dict(APPROVED_NET, bind=bind)
                st = self.wstore(loaded=False, extra={"network": net})
                self.assertEqual(exposure.check_startup(st.app.s)["exposure"], "approved")  # layer 1 passes: this is the case DEV-75 is about
                with self.assertRaises(ExposureNotApproved) as cm:
                    server.bind_address(st.app.s)
                self.assertEqual(cm.exception.code, "E-SEC-EXPOSURE-NOT-APPROVED")
                self.assertIn("loopback", json.dumps(cm.exception.details))
        for bind in ("127.0.0.1", "localhost", "[::1]:8081", "127.0.0.2"):
            with self.subTest(loopback=bind):
                st = self.wstore(loaded=False, extra={"network": dict(APPROVED_NET, bind=bind)})
                self.assertEqual(server.bind_address(st.app.s), bind)

    def test_TST_HUB_STG23_S04_make_server_refuses_before_any_listener_exists(self):
        """S04 (DW-15): make_server raises for an approved non-loopback bind and the start-up record (CONFIG_LOADED) is NOT written (refusal comes first)."""
        st = self.wstore(loaded=False, extra={"network": dict(APPROVED_NET, bind="0.0.0.0")})
        n0 = st.con.execute("SELECT count(*) FROM audit_log WHERE action = 'CONFIG_LOADED'").fetchone()[0]
        with self.assertRaises(ExposureNotApproved):
            server.make_server(st.app, 0)
        self.assertEqual(st.con.execute("SELECT count(*) FROM audit_log WHERE action = 'CONFIG_LOADED'").fetchone()[0], n0)

    def test_TST_HUB_STG23_S05_serve_command_exits_9_for_an_approved_non_loopback_bind(self):
        """S05 (DW-15): `hub.web serve` with approval + reference + TLS keys and bind 0.0.0.0 exits 9 E-SEC-EXPOSURE-NOT-APPROVED (exit 9 is the
        documented clash with E-CO-DENYLIST-IMPORT, OD-29) and prints no 'listening' line; a hang (= a listener started) is a failure."""
        st = self.wstore(loaded=False)
        cfg = H3.write_config(S.tmpdir("s23s05-"), {"network": dict(APPROVED_NET, bind="0.0.0.0")})
        try:
            p = T.module_cli("hub.web", ["serve", "--data-dir", st.data, "--port", "0"], cfg, timeout=40)
        except Exception as e:  # noqa: BLE001 - subprocess.TimeoutExpired: the server started
            self.fail("serve did not exit: %r" % (e,))
        self.assertEqual((p.returncode, T.code_of(p)), (9, "E-SEC-EXPOSURE-NOT-APPROVED"))
        self.assertNotIn("listening", p.stderr)


class TST_HUB_STG23_AuthoritySwitch(_Base):
    CAP = "C4"
    FLAG = "capability_authority.C4"

    def test_TST_HUB_STG23_S10_ships_off(self):
        """S10 (DW-17, FF-2 rule 1): defaults - no capability is authoritative, no decision flag is non-default, zone_h.holders is EMPTY; `hub.control
        flags` reports the same and exits 0."""
        cfg = config.load()
        self.assertEqual(flags.nondefault(cfg), [])
        self.assertEqual(config.authority(cfg, self.CAP), "shadow")
        self.assertEqual(cfg.get("capability_authority"), {})
        st = self.hstore()
        p = T.control(["flags"], st.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual(out["non_default"], [])
        self.assertEqual(sorted(r["flag"] for r in out["flags"]), sorted(f[0] for f in flags.DECISION_FLAGS))
        self.assertEqual([r["value"] for r in out["flags"] if r["flag"] == "zone_h.holders"], [[]])
        self.assertEqual(T.audit_changes(st), [])

    def test_TST_HUB_STG23_S11_refused_without_approval_ref(self):
        """S11 (DW-17, FF-2 rule 3): authoritative / any non-default decision flag is refused without a usable approval_ref (missing, blank, non-string,
        too long); the CLI refuses with exit 2 E-CFG-INVALID, leaves the config file byte-identical and writes no CONFIG_CHANGED record."""
        for over in ({"capability_authority": {self.CAP: "authoritative"}},
                     {"capability_authority": {self.CAP: "authoritative"}, "approval_refs": {self.FLAG: ""}},
                     {"capability_authority": {self.CAP: "authoritative"}, "approval_refs": {self.FLAG: "   "}},
                     {"capability_authority": {self.CAP: "authoritative"}, "approval_refs": {self.FLAG: 123}},
                     {"capability_authority": {self.CAP: "authoritative"}, "approval_refs": {self.FLAG: "x" * 201}},
                     {"capability_authority": {self.CAP: "authoritative"}, "approval_refs": {"capability_authority.C9": "OK-REF"}},
                     {"capability_authority": {self.CAP: "live"}, "approval_refs": {self.FLAG: "OK-REF"}},
                     {"capability_authority": {"bad name": "shadow"}},
                     {"approval_refs": ["not", "an", "object"]}):
            with self.subTest(over=over):
                with self.assertRaises(ConfigInvalid):
                    config.load(overrides=over)
        for path, value in (("disposition.mode", "event"), ("closure.unconfigured_behaviour", "none"), ("workflow.transition_table", "strict"),
                            ("case_creation.enabled", True), ("search.enabled", True), ("search.fts", "auto"), ("templates.enabled", True),
                            ("zone_h.holders", ["synthetic-holder-1"])):
            with self.subTest(flag=path):
                over = {}
                cur = over
                parts = path.split(".")
                for part in parts[:-1]:
                    cur = cur.setdefault(part, {})
                cur[parts[-1]] = value
                with self.assertRaises(ConfigInvalid) as cm:
                    config.load(overrides=over)
                self.assertEqual(cm.exception.details["flag"], path)
                config.load(overrides=dict(over, approval_refs={path: T.SYNTHETIC_REF}))  # accepted once the reference exists
        st = self.hstore()
        before = open(st.cfg_path, "rb").read()
        n0 = len(st.audit_rows())
        p = T.control(["set-flag", "--flag", self.FLAG, "--value", '"authoritative"', "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, T.code_of(p)), (2, "E-CFG-INVALID"), p.stderr)
        self.assertEqual(open(st.cfg_path, "rb").read(), before)
        self.assertEqual(T.audit_changes(st), [])
        self.assertEqual(len(st.audit_rows()) - n0, 1)  # only the CONFIG_LOADED record of the refused command
        p = T.control(["set-flag", "--flag", "no.such.flag", "--value", "1", "--approval-ref", T.SYNTHETIC_REF, "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, T.code_of(p)), (2, "E-CFG-INVALID"))

    def test_TST_HUB_STG23_S12_accepted_and_audited_with_approval_ref(self):
        """S12 (DW-17, FF-2 rules 3-4): with --approval-ref the switch is accepted, the config file validates, and ONE CONFIG_CHANGED record carries the
        flag, old / new value, approval_ref, direction and the config hashes before / after; the audit chain still verifies."""
        st = self.hstore()
        h0 = open(st.cfg_path, "rb").read()
        p = T.control(["set-flag", "--flag", self.FLAG, "--value", '"authoritative"', "--approval-ref", T.SYNTHETIC_REF, "--data-dir", st.data], st.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual((out["changed"], out["old"], out["new"], out["approval_ref"], out["direction"]),
                         (True, "shadow", "authoritative", T.SYNTHETIC_REF, "to_non_default"))
        doc = T.read_cfg(st.cfg_path)
        self.assertEqual((doc["capability_authority"][self.CAP], doc["approval_refs"][self.FLAG]), ("authoritative", T.SYNTHETIC_REF))
        self.assertNotEqual(open(st.cfg_path, "rb").read(), h0)
        cfg = config.load(st.cfg_path)
        self.assertEqual(config.authority(cfg, self.CAP), "authoritative")
        self.assertEqual([f[0] for f in flags.nondefault(cfg)], [self.FLAG])
        ch = T.audit_changes(st)
        self.assertEqual(len(ch), 1)
        d = ch[0][1]
        self.assertEqual((d["flag"], d["old"], d["new"], d["approval_ref"], d["direction"], d["source"]),
                         (self.FLAG, "shadow", "authoritative", T.SYNTHETIC_REF, "to_non_default", "hub.control set-flag"))
        self.assertNotEqual(d["config_hash_before"], d["config_hash_after"])
        row = [r for r in st.audit_rows() if r["audit_seq"] == ch[0][0]][0]
        self.assertEqual((row["action"], row["actor_kind"], row["outcome"], row["object_ref"]), ("CONFIG_CHANGED", "human", "success", "flag:" + self.FLAG))
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        p = T.control(["set-flag", "--flag", self.FLAG, "--value", '"authoritative"', "--approval-ref", T.SYNTHETIC_REF, "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, json.loads(p.stdout)["changed"]), (0, False))  # idempotent: no second record
        self.assertEqual(len(T.audit_changes(st)), 1)
        T.write_evidence("authority-switch-audit.json", {"label": T.LABEL, "approval_ref_note": "synthetic test marker, not a human approval",
                                                         "config_changed": [d for _, d in T.audit_changes(st)]})

    def test_TST_HUB_STG23_S13_l3_flip_back_to_shadow(self):
        """S13 (DW-17, rollback L3, CO-2 step 3): flip-to-shadow needs a reason but NO approval, restores `shadow`, removes the approval reference,
        writes CONFIG_CHANGED direction to_default with rollback L3, is idempotent, and the hub works before and after."""
        st = self.hstore()
        T.control(["set-flag", "--flag", self.FLAG, "--value", '"authoritative"', "--approval-ref", T.SYNTHETIC_REF, "--data-dir", st.data], st.cfg_path)
        p = T.control(["flip-to-shadow", "--capability", self.CAP, "--reason", "  ", "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, T.code_of(p)), (2, "E-CFG-INVALID"))
        self.assertEqual(config.authority(config.load(st.cfg_path), self.CAP), "authoritative")
        p = T.control(["flip-to-shadow", "--capability", self.CAP, "--reason", "synthetic rehearsal of the L3 rollback", "--data-dir", st.data], st.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual((out["changed"], out["old"], out["new"], out["approval_ref"], out["direction"]), (True, "authoritative", "shadow", None, "to_default"))
        doc = T.read_cfg(st.cfg_path)
        self.assertEqual(doc["capability_authority"][self.CAP], "shadow")
        self.assertNotIn("approval_refs", doc)
        cfg = config.load(st.cfg_path)
        self.assertEqual((config.authority(cfg, self.CAP), flags.nondefault(cfg)), ("shadow", []))
        ch = [d for _, d in T.audit_changes(st)]
        self.assertEqual([(d["old"], d["new"], d["direction"], d["approval_ref"]) for d in ch],
                         [("shadow", "authoritative", "to_non_default", T.SYNTHETIC_REF), ("authoritative", "shadow", "to_default", None)])
        self.assertEqual((ch[1]["rollback"], ch[1]["source"]), ("L3", "hub.control flip-to-shadow"))
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        p = T.control(["flip-to-shadow", "--capability", self.CAP, "--reason", "again", "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, json.loads(p.stdout)["changed"]), (0, False))
        self.assertEqual(len(T.audit_changes(st)), 2)
        T.write_evidence("l3-flip-log.json", {"label": T.LABEL, "sequence": ["set-flag authoritative with approval_ref", "flip-to-shadow (reason, no approval)",
                                                                              "flip again: no-op"], "config_changed": ch})

    def test_TST_HUB_STG23_S14_out_of_band_config_edits_are_audited_or_refused(self):
        """S14 (DW-17, FF-2 rule 4): editing the config FILE by hand cannot flip a capability silently - without approval_refs every command refuses
        (exit 2); with it the next start-up audits the change (source config-file) once, and a hand-made flip back is audited too."""
        st = self.hstore()
        doc = T.read_cfg(st.cfg_path)
        T.write_cfg(st.cfg_path, dict(doc, capability_authority={self.CAP: "authoritative"}))
        p = T.module_cli("hub.admin", ["anchor", "--data-dir", st.data], st.cfg_path)
        self.assertEqual((p.returncode, T.code_of(p)), (2, "E-CFG-INVALID"))
        self.assertEqual(T.audit_changes(st), [])
        T.write_cfg(st.cfg_path, dict(doc, capability_authority={self.CAP: "authoritative"}, approval_refs={self.FLAG: T.SYNTHETIC_REF}))
        for _ in range(2):
            p = T.module_cli("hub.admin", ["anchor", "--data-dir", st.data], st.cfg_path)
            self.assertEqual(p.returncode, 0, p.stderr)
        ch = T.audit_changes(st)
        self.assertEqual(len(ch), 1)
        self.assertEqual((ch[0][1]["source"], ch[0][1]["new"], ch[0][1]["approval_ref"], ch[0][1]["command"]), ("config-file", "authoritative", T.SYNTHETIC_REF, "anchor"))
        T.write_cfg(st.cfg_path, doc)
        p = T.module_cli("hub.admin", ["anchor", "--data-dir", st.data], st.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        ch = T.audit_changes(st)
        self.assertEqual([(d["old"], d["new"], d["direction"]) for _, d in ch], [("shadow", "authoritative", "to_non_default"), ("authoritative", "shadow", "to_default")])
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")

    def test_TST_HUB_STG23_S15_both_modes_leave_every_other_control_unchanged(self):
        """S15 (DW-17, FF-2 rule 2; class-B pattern): the shipped default mode (OFF) and the decided mode (C4 authoritative with a synthetic approval)
        differ ONLY in that flag: same security settings, holders EMPTY, kill switch honoured, exposure guard and start-up check unchanged, other flags at default."""
        results = {}
        for mode, extra in (("default", None), ("decided", {"capability_authority": {self.CAP: "authoritative"}})):
            st = self.hstore("s23m-%s-" % mode, extra=extra)
            cfg = config.load(st.cfg_path)
            from hub.security import settings
            s = settings.resolve(cfg)
            self.assertEqual(s["zone_h"]["holders"], [], mode)
            self.assertEqual(s["network"]["bind"], "127.0.0.1")
            self.assertEqual(exposure.check_startup(s)["exposure"], "loopback")
            p = T.module_cli("hub.admin", ["startup-check"], st.cfg_path)
            self.assertEqual(p.returncode, 0, p.stderr)
            p = T.module_cli("hub.admin", ["status", "--data-dir", st.data], st.cfg_path)
            self.assertEqual(p.returncode, 0, p.stderr)
            doc = T.read_cfg(st.cfg_path)
            T.write_cfg(st.cfg_path, dict(doc, hub={"kill": True}))
            p = T.module_cli("hub.admin", ["status", "--data-dir", st.data], st.cfg_path)
            self.assertEqual((p.returncode, T.code_of(p)), (3, "E-HUB-KILLED"), mode)  # kill beats authority
            s["audit"]["anchor_path"] = None  # differs per sandbox directory only
            results[mode] = {"authority": config.authority(cfg, self.CAP), "non_default": [f[0] for f in flags.nondefault(cfg)],
                             "security_settings_sha": settings.config_hash(s)}
        self.assertEqual(results["default"]["authority"], "shadow")
        self.assertEqual(results["decided"]["authority"], "authoritative")
        self.assertEqual(results["default"]["non_default"], [])
        self.assertEqual(results["decided"]["non_default"], [self.FLAG])
        self.assertEqual(results["default"]["security_settings_sha"], results["decided"]["security_settings_sha"])

    def test_TST_HUB_STG23_S16_shipped_configuration_is_off_and_holders_empty(self):
        """S16 (DW-17, OD-17): no shipped config file in the repository sets a capability authoritative, names a Zone H holder or carries an approval
        reference; the hub DEFAULTS are all non-adopting; the sandbox test configs that set flags carry only the labelled synthetic marker."""
        offenders = []
        for base, dirs, files in os.walk(S.CODE_ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "data", "docs", "tests", "node_modules")]
            for fn in files:
                if fn.endswith(".json"):
                    p = os.path.join(base, fn)
                    try:
                        with open(p, encoding="utf-8") as f:
                            doc = json.load(f)
                    except ValueError:
                        continue
                    if isinstance(doc, dict) and any(k in doc for k in ("capability_authority", "approval_refs", "zone_h")):
                        offenders.append(os.path.relpath(p, S.CODE_ROOT))
        self.assertEqual(offenders, [])
        self.assertEqual(config.DEFAULTS["capability_authority"], {})
        self.assertEqual(flags.nondefault(config.load()), [])
        self.assertEqual(H3.TEST_APPROVAL_REF[:14], "TEST-SYNTHETIC")


if __name__ == "__main__":
    unittest.main()
