"""Stage 28 tests, part 3: AI-disabled operation and capacity proxies. Synthetic, unvalidated.

  A01  the AI-disabled mode is the only mode: results are byte-identical with AI-style environment variables set and unset
  A02  no hub module reads an AI / model / provider environment variable and no configuration key names one
  A03  the dependency deny-list scan is clean over hub/, tests/hub and the manifests; model_calls_total and egress_attempts_total are 0 after a core flow
  C01  capacity proxies (sandbox, class C, NOT a measure of production): in-process request rate, intake ingest rate, bounded work per request
"""
import ast
import os
import re
import time
import unittest
from unittest import mock

import _inc06 as I
import _inc08 as W
import _stg28 as T
import _support as S
from hub import config as hubconfig
from hub.guards import no_ai
from hub.obs import collect
from hub.web.app import Request

AI_ENV = {"OPENAI_API_KEY": "synthetic-value", "AZURE_OPENAI_API_KEY": "synthetic", "AZURE_OPENAI_ENDPOINT": "https://example.invalid", "ANTHROPIC_API_KEY": "synthetic",
          "HUB_AI_ENABLED": "1", "HUB_MODEL": "gpt-synthetic", "LLM_PROVIDER": "synthetic"}
AI_WORDS = re.compile(r"openai|anthropic|azure|llm|gpt|embedding|model|provider|prompt|completion", re.I)


def setUpModule():
    T.skip_in_inner_egress_run()


def core_flow():
    st = I.IStore()
    try:
        rep = st.isvc.ingest("partner_feed", I.batch(20), "s28-core", "s28")
        out = {"report": dict((k, rep[k]) for k in ("received", "stored", "outcomes")), "counts": st.isvc.counts(),
               "queue": st.isvc.queue_snapshot(st.clock()), "digest": st.table_digest(st.INTAKE_TABLES)}
        return out
    finally:
        st.close()


class TST_HUB_STG28_AiCapacity(unittest.TestCase):
    def test_TST_HUB_STG28_A01_ai_disabled_is_the_only_mode(self):
        """A01 (AD-1): the same intake flow with AI-style environment variables absent and present gives identical reports, queue snapshot and table digest."""
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in AI_ENV:
                os.environ.pop(k, None)
            a = core_flow()
        with mock.patch.dict(os.environ, AI_ENV):
            b = core_flow()
        self.assertEqual(a, b)
        self.assertEqual(a["counts"]["raw"], 20)

    def test_TST_HUB_STG28_A02_no_ai_environment_or_configuration(self):
        """A02: the environment variables read by hub/ are exactly the operator ones (HUB_OPERATOR, HUB_NEW_USER_PASSWORD, HUB_RUN_PASSWORD, HUB_ANCHOR_SEAL_KEY and the test-only guards); none matches an AI word; the
        configuration key set (DEFAULTS and KNOWN_KEYS, every depth) has no AI word."""
        names = set()
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                for n in ast.walk(ast.parse(open(os.path.join(d, fn), encoding="utf-8").read())):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("get", "getenv", "pop") and n.args \
                            and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                        v = ast.unparse(n.func.value) if hasattr(ast, "unparse") else ""
                        if "environ" in v or n.func.attr == "getenv":
                            names.add(n.args[0].value)
        self.assertTrue({"HUB_OPERATOR", "HUB_NEW_USER_PASSWORD", "HUB_RUN_PASSWORD"} <= names, sorted(names))
        self.assertEqual([x for x in names if AI_WORDS.search(x)], [])

        def keys(o, acc):
            if isinstance(o, dict):
                for k, v in o.items():
                    acc.append(str(k))
                    keys(v, acc)
            elif isinstance(o, (set, frozenset, list, tuple)):
                for v in o:
                    keys(v, acc)
            return acc
        allk = keys(hubconfig.DEFAULTS, []) + keys(hubconfig.KNOWN_KEYS, [])
        self.assertTrue(allk)
        self.assertEqual([k for k in allk if AI_WORDS.search(k)], [])

    def test_TST_HUB_STG28_A03_denylist_and_tripwires(self):
        """A03: hub.guards.no_ai.check over default_targets (hub, tests/hub, manifests) finds nothing; after a core flow the tripwires model_calls_total and egress_attempts_total read 0."""
        self.assertEqual(no_ai.check(no_ai.default_targets(S.CODE_ROOT)), [])
        core_flow()
        st = W.WStore(loaded=False)
        self.addCleanup(st.close)
        r = st.app.handle(Request("GET", "/healthz", {}, {}, b"", peer="127.0.0.1"))
        self.assertEqual(r.status, 200)
        t = collect.tripwires(st.con)
        self.assertEqual((t["model_calls_total"], t["egress_attempts_total"]), (0, 0))

    def test_TST_HUB_STG28_C01_capacity_proxies(self):
        """C01 (sandbox proxy, class C - no production claim): 300 in-process /healthz and 300 authorised reads; 500 intake items in 5 batches of 100; every answer is the expected one; the rates are
        recorded as evidence, not asserted against a threshold (no capacity target exists - Unknown U-28-02)."""
        st = W.WStore(loaded=False)
        self.addCleanup(st.close)
        rev = {"Authorization": "Bearer " + st.tokens["rev"], "X-Hub-Request": "1"}
        out = {"label": T.LABEL}
        for name, path, hdr in (("healthz", "/healthz", {}), ("authorised_read", "/api/v2/policies", rev)):
            t0 = time.perf_counter()
            for _ in range(300):
                r = st.app.handle(Request("GET", path, {}, hdr, b"", peer="127.0.0.1"))
                st.app.last_exception = None
                self.assertEqual(r.status, 200)
            dt = time.perf_counter() - t0
            out[name] = {"requests": 300, "seconds": round(dt, 3), "per_second": round(300 / dt, 1)}
        ist = I.IStore()
        self.addCleanup(ist.close)
        t0 = time.perf_counter()
        for b in range(5):
            rep = ist.isvc.ingest("partner_feed", I.batch(100, start=b * 100), "s28-cap-%d" % b, "s28")
            self.assertEqual(rep["stored"], 100)
        dt = time.perf_counter() - t0
        out["ingest"] = {"items": 500, "batches": 5, "seconds": round(dt, 3), "per_second": round(500 / dt, 1)}
        self.assertEqual(ist.isvc.counts()["raw"], 500)
        out["note"] = "sandbox proxy on the reference laptop: one process, in-process calls or a loopback double, synthetic data; not a production capacity, availability or latency figure"
        T.write_evidence("capacity-proxies.json", out)


if __name__ == "__main__":
    unittest.main()
