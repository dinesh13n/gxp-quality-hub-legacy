"""Stage 44 CLI tests (OD-40): `python -m hub.ai` end to end against a LOCAL FAKE endpoint on loopback. Synthetic, unvalidated. No real endpoint, key or call.

  L01  OFF by default: no `ai` section, ai.enabled false, a decision flag that needs approval_refs; the CLI refuses with exit 40 and touches nothing
  L02  environment: missing variables / bad endpoints -> exit 40 E-AI-NOT-CONFIGURED naming the NAMES only; no request reaches the fake
  L03  kill switch -> exit 3, no request
  L04  success: JSON and --text, the label, citations, audit records; `status` is read-only and shows booleans, never values
  L05  failures through the CLI: provider timeout / 429 -> exit 41; no retrieval / budget / rate -> exit 40; non-synthetic corpus -> exit 40
  L06  the key is in no stdout, stderr, audit row, anchor file, config or store file after success and failure runs
"""
import json
import os
import unittest

import _stg44 as T
import _support as S
from hub import config
from hub.adapters import azure_openai
from hub.ai import LABEL, settings as aisettings
from hub.control import flags
from hub.core.errors import ConfigInvalid


def setUpModule():
    T.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def rig(self, **kw):
        st = T.AiRig(**kw)
        self.addCleanup(st.close)
        return st

    def fake(self, mode="ok", **kw):
        f = T.FakeAoai(mode, **kw)
        f.__enter__()
        self.addCleanup(f.__exit__)
        return f

    def audit_count(self, st):
        return st.con.execute("SELECT count(*) FROM audit_log").fetchone()[0]


class TST_HUB_STG44_Cli(_Base):

    def test_TST_HUB_STG44_L01_off_by_default_and_a_decision_flag(self):
        """L01: the shipped configuration has no `ai` key; the resolved defaults are enabled=false with EMPTY provider placeholders and no key setting; ai.enabled is a registered
        decision flag (default false) so true needs approval_refs['ai.enabled']; the CLI on the default config refuses with exit 40 E-AI-DISABLED even with every variable set, writes
        no audit record and sends nothing."""
        cfg = config.load()
        self.assertNotIn("ai", cfg)
        s = aisettings.resolve(cfg)
        self.assertIs(s["enabled"], False)
        self.assertEqual((s["azure_openai"]["endpoint"], s["azure_openai"]["deployment"], s["azure_openai"]["api_version"]), ("", "", ""))
        self.assertNotIn("api_key", json.dumps(aisettings.DEFAULTS).lower())
        self.assertEqual(flags.default_of("ai.enabled"), False)
        self.assertEqual(flags.nondefault(cfg), [])
        self.assertEqual(flags.nondefault(config.load(None, {"ai": {"enabled": True}, "approval_refs": {"ai.enabled": "X"}})), [("ai.enabled", True, flags.DECISION_FLAGS[-1][2])])
        with self.assertRaises(ConfigInvalid):
            config.load(None, {"ai": {"enabled": True}})
        with self.assertRaises(ConfigInvalid):
            config.load(None, {"ai": {"api_key": "x"}})  # there is no key setting
        with self.assertRaises(ConfigInvalid):
            config.load(None, {"ai": {"azure_openai": {"api_key": "x"}}})
        st = self.rig(extra={"ai": {"enabled": False}})
        f = self.fake()
        n = self.audit_count(st)
        p = st.cli(st.ask_args("How long are batch records retained?"), env=st.env(f))
        self.assertEqual((p.returncode, T.err_code(p)), (40, "E-AI-DISABLED"), p.stderr)
        self.assertEqual((f.requests, self.audit_count(st)), ([], n))
        self.assertEqual(p.stdout, "")

    def test_TST_HUB_STG44_L02_missing_or_invalid_environment_refuses_naming_only_names(self):
        """L02: each missing variable, and endpoints that are not allowed (non-Azure https host, http to a non-loopback host, user info, a path, a wrong port), give exit 40
        E-AI-NOT-CONFIGURED; the error names variables, never values; nothing is sent."""
        st = self.rig()
        f = self.fake()
        n = self.audit_count(st)
        for gone in azure_openai.ENV_NAMES:
            with self.subTest(missing=gone):
                p = st.cli(st.ask_args("How long are batch records retained?"), env=dict(st.env(f), **{gone: None}))
                self.assertEqual((p.returncode, T.err_code(p)), (40, "E-AI-NOT-CONFIGURED"), p.stderr)
                self.assertEqual(json.loads(p.stderr)["details"]["missing"], [gone])
        key = T.fake_key()
        for bad in ("https://evil.example.com", "http://example.openai.azure.com", "https://user:pw@r.openai.azure.com", "https://r.openai.azure.com/openai",
                    "https://r.openai.azure.com:8443", "https://openai.azure.com", "ftp://r.openai.azure.com", "https://r.openai.azure.com.evil.example", "not a url"):
            with self.subTest(endpoint=bad):
                p = st.cli(st.ask_args("How long are batch records retained?"), env=st.env(f, key, {"AZURE_OPENAI_ENDPOINT": bad}))
                self.assertEqual((p.returncode, T.err_code(p)), (40, "E-AI-NOT-CONFIGURED"), p.stderr)
                self.assertNotIn(key, p.stderr + p.stdout)
                self.assertNotIn("pw@", p.stderr)
        self.assertEqual((f.requests, self.audit_count(st)), ([], n))

    def test_TST_HUB_STG44_L03_kill_switch(self):
        """L03: hub.kill true -> exit 3 E-HUB-KILLED for ask and status; no request, no audit record."""
        st = self.rig(extra={"hub": {"kill": True}})
        f = self.fake()
        n = self.audit_count(st)
        for args in (st.ask_args("How long are batch records retained?"), ["status", "--data-dir", st.data]):
            p = st.cli(args, env=st.env(f))
            self.assertEqual((p.returncode, T.err_code(p)), (3, "E-HUB-KILLED"), p.stderr)
        self.assertEqual((f.requests, self.audit_count(st)), ([], n))

    def test_TST_HUB_STG44_L04_success_json_text_and_status(self):
        """L04: success through the CLI: JSON with label + citations; --text starts with the label banner; the audit log holds REQUESTED + ANSWERED; `status` shows which variables are set
        (booleans), the limits and the corpus origins, makes no model call."""
        key = T.fake_key()
        st = self.rig()
        f = self.fake("ok", key)
        p = st.cli(st.ask_args("How long are batch records retained?"), env=st.env(f, key))
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual((out["label"], out["status"], out["advisory_model_calls"]), (LABEL, "answered", 1))
        self.assertEqual([c["doc_id"] for c in out["citations"]], ["DOC-90000001"])
        self.assertEqual(len(f.requests), 1)
        pt = st.cli(st.ask_args("How long are batch records retained?", extra=["--text"]), env=st.env(f, key))
        self.assertEqual(pt.returncode, 0, pt.stderr)
        self.assertTrue(pt.stdout.startswith("*** " + LABEL + " ***"), pt.stdout[:120])
        self.assertIn("[S1] DOC-90000001", pt.stdout)
        self.assertEqual(st.audit_actions(), ["AI_QA_REQUESTED", "AI_QA_ANSWERED"] * 2)
        n = len(f.requests)
        ps = st.cli(["status", "--data-dir", st.data], env=st.env(f, key))
        self.assertEqual(ps.returncode, 0, ps.stderr)
        so = json.loads(ps.stdout)
        self.assertEqual((so["enabled"], so["model_call_made"], so["corpus_origins"]), (True, False, ["synthetic"]))
        self.assertEqual(so["environment_variables_set"], dict((k, True) for k in azure_openai.ENV_NAMES))
        self.assertEqual((so["limits"]["units_today"], so["limits"]["requests_last_minute"]), (880, 2))
        self.assertNotIn(key, ps.stdout)
        self.assertEqual(len(f.requests), n)
        T.write_evidence("l04-cli-success.json", {"label": T.LABEL, "fake_only": True, "stdout": out, "status": so})

    def test_TST_HUB_STG44_L05_failures_through_the_cli_have_distinct_exit_codes(self):
        """L05: provider timeout and 429 -> exit 41 (E-AI-PROVIDER-TIMEOUT / -RATE-LIMITED); no retrieval, rate limit and budget -> exit 40; a corpus loaded with a non-synthetic
        origin -> exit 40 E-AI-NON-SYNTHETIC; an ungrounded answer -> exit 40 E-AI-UNGROUNDED with no answer on stdout."""
        q = "How long are batch records retained?"
        st = self.rig(ai={"azure_openai": {"timeout_seconds": 0.5}})
        for mode, code, rc in (("slow", "E-AI-PROVIDER-TIMEOUT", 41), ("s429", "E-AI-PROVIDER-RATE-LIMITED", 41), ("invented", "E-AI-UNGROUNDED", 40)):
            with self.subTest(mode=mode):
                f = self.fake(mode, delay=2.0)
                p = st.cli(st.ask_args(q), env=st.env(f))
                self.assertEqual((p.returncode, T.err_code(p)), (rc, code), p.stderr)
                self.assertEqual(p.stdout, "")
        f = self.fake()
        p = st.cli(st.ask_args("What is the zeppelin interval?"), env=st.env(f))
        self.assertEqual((p.returncode, T.err_code(p), f.requests), (40, "E-AI-NO-RETRIEVAL", []))
        p = st.cli(st.ask_args(q, principal="nobody"), env=st.env(f))
        self.assertEqual((p.returncode, T.err_code(p), f.requests), (40, "E-AI-PRINCIPAL-REFUSED", []))
        lim = self.rig(ai={"rate_limit": {"max_requests_per_minute": 1}})
        f2 = self.fake()
        self.assertEqual(lim.cli(lim.ask_args(q), env=lim.env(f2)).returncode, 0)
        p = lim.cli(lim.ask_args(q), env=lim.env(f2))
        self.assertEqual((p.returncode, T.err_code(p), len(f2.requests)), (40, "E-AI-RATE-LIMITED", 1))
        bud = self.rig(ai={"budget": {"daily_token_budget": 1000, "max_request_tokens": 200}})
        p = bud.cli(bud.ask_args(q), env=bud.env(f2))
        self.assertEqual((p.returncode, T.err_code(p), len(f2.requests)), (40, "E-AI-BUDGET-EXCEEDED", 1))
        real = self.rig(origin="customer")
        p = real.cli(real.ask_args(q), env=real.env(f2))
        self.assertEqual((p.returncode, T.err_code(p), len(f2.requests)), (40, "E-AI-NON-SYNTHETIC", 1))
        with self.assertRaises(ConfigInvalid):
            config.load(None, {"data_origin": "production"})

    def test_TST_HUB_STG44_L06_the_key_is_nowhere(self):
        """L06: after a success, a key-echoing 401 and a timeout run through the CLI the generated key is in no stdout / stderr and in no file of the store directory
        (hub.sqlite3, audit anchor, config)."""
        key = T.fake_key()
        st = self.rig(ai={"azure_openai": {"timeout_seconds": 0.5}})
        seen = []
        for mode in ("ok", "s401", "slow", "s429"):
            f = self.fake(mode, key, delay=2.0)
            p = st.cli(st.ask_args("How long are batch records retained?"), env=st.env(f, key))
            seen += [p.stdout, p.stderr]
            self.assertEqual(f.requests[0]["headers"]["api-key"], key)
        for t in seen:
            self.assertNotIn(key, t)
        hits = []
        for d, _, fns in os.walk(st.base):
            for fn in fns:
                with open(os.path.join(d, fn), "rb") as fh:
                    if key.encode() in fh.read():
                        hits.append(fn)
        self.assertEqual(hits, [])
        self.assertNotIn(key.encode(), open(st.cfg_path, "rb").read())
        rows = json.dumps(st.con.execute("SELECT * FROM audit_log").fetchall())
        self.assertNotIn(key, rows)


if __name__ == "__main__":
    unittest.main()
