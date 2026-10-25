"""Stage 31 tests, part 3: trace reconstruction from the structured log, the offline CLI. Synthetic, unvalidated.

  T01  traces: grouping by correlation id, ordering, outcome, error codes; bad / leaky / over-wide lines are counted and dropped, never reproduced
  T02  the web log really is traceable: a request through the in-process WebApp yields one correlated line that build_traces turns into a trace
  T03  CLI: catalog, evaluate (exit 0 / 1 / 2), expo and traces; same input -> byte-identical output; the CLI writes no file and opens no store
"""
import json
import os
import subprocess
import sys
import unittest

import _stg31 as T
import _support as S
from hub.core.errors import HubError
from hub.obs import log as obslog, trace


def setUpModule():
    T.skip_in_inner_egress_run()


class _Clock(object):
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        return "2026-10-25T00:00:%02d.000000Z" % self.i


class TST_HUB_STG31_Trace(unittest.TestCase):

    def lines(self):
        out = []
        lg = obslog.Logger(_Clock(), out.append, "test+31", "cfg-test")
        with lg.step("OP-A", "cid-1", actor="u1", actor_kind="human"):
            pass
        with lg.step("OP-B", "cid-2", event="intake_received"):
            pass
        try:
            with lg.step("OP-C", "cid-1"):
                raise _Denied()
        except HubError:
            pass
        lg.emit("run_started", correlation_id=None, run_id="run-1")
        return out

    def test_TST_HUB_STG31_T01_build_traces(self):
        """T01: two correlation ids, one uncorrelated line, junk lines dropped; the worst outcome and the error codes summarise the trace."""
        out = self.lines()
        junk = ["not json", "[1,2]", json.dumps({"ts": "x", "event": "http_request", "unknown_field": "<script>alert(1)</script>"}),
                json.dumps({"ts": "2026-10-25T01:00:00Z", "event": "http_request", "correlation_id": "cid-9", "object_ref": "token_sha256=" + "a" * 64})]
        res = trace.build_traces(out + junk)
        self.assertEqual(sorted(res["traces"]), ["cid-1", "cid-2"])
        self.assertEqual((res["uncorrelated"], res["rejected"]), (1, 4))
        t1 = res["traces"]["cid-1"]
        self.assertEqual((t1["spans"], t1["outcome"], t1["error_codes"]), (2, "denied", ["E-AUTH-FORBIDDEN"]))
        self.assertEqual(t1["events"], ["http_request", "http_request"])
        self.assertLess(t1["first_ts"], t1["last_ts"])
        self.assertEqual(res["traces"]["cid-2"]["outcome"], "success")
        blob = json.dumps(res)
        self.assertNotIn("script", blob)
        self.assertNotIn("token_sha256", blob)
        self.assertEqual(trace.build_traces([]), {"traces": {}, "uncorrelated": 0, "rejected": 0})
        self.assertEqual(trace.build_traces(out), trace.build_traces(list(out)))

    def test_TST_HUB_STG31_T02_web_request_is_traceable(self):
        """T02: one in-process request through the real WebApp -> one log line with the response's X-Correlation-Id -> a one-span trace."""
        import _inc08 as W
        lines = []
        st = W.WStore(app_kw={"log_sink": lines.append})
        try:
            resp = st.get("/healthz")
            cid = resp.headers.get("x-correlation-id")
        finally:
            st.close()
        self.assertEqual(resp.status, 200)
        res = trace.build_traces(lines)
        self.assertIn(cid, res["traces"])
        self.assertEqual(res["traces"][cid]["spans"], 1)
        self.assertEqual(res["rejected"], 0)


class _Denied(HubError):
    code = "E-AUTH-FORBIDDEN"

    def __init__(self):
        pass


class TST_HUB_STG31_Cli(unittest.TestCase):

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", "-m", "hub.obs"] + list(args), cwd=S.CODE_ROOT, env=S.child_env(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)

    def write(self, name, doc):
        p = os.path.join(S.tmpdir("s31cli-"), name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(doc if isinstance(doc, str) else json.dumps(doc))
        return p

    def test_TST_HUB_STG31_T03_cli(self):
        """T03: catalog lists metrics / SLOs / alerts; evaluate exits 0 clean, 1 on a firing alert or lint finding, 2 on unreadable input; deterministic; no file written."""
        c = self.run_cli("catalog")
        self.assertEqual(c.returncode, 0, c.stderr)
        doc = json.loads(c.stdout)
        self.assertEqual(sorted(doc), ["alert_rules", "invariants", "label", "metrics", "slos"])
        self.assertTrue(all(s["status"] == "CANDIDATE" for s in doc["slos"]))
        zero = [T.sample(n, value=0) for n in ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted")]
        ok = self.write("ok.json", zero)
        r1, r2 = self.run_cli("evaluate", "--samples", ok), self.run_cli("evaluate", "--samples", ok)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertEqual(r1.stdout, r2.stdout)
        self.assertEqual(json.loads(r1.stdout)["alerts"]["firing"], [])
        tripped = self.write("trip.json", [T.sample("model_calls_total", value=1)] + zero[1:])
        r = self.run_cli("evaluate", "--samples", tripped)
        self.assertEqual(r.returncode, 1)
        self.assertEqual([x["id"] for x in json.loads(r.stdout)["alerts"]["firing"]], ["ALT-01"])
        self.assertEqual(self.run_cli("evaluate", "--samples", self.write("missing-sensors.json", [])).returncode, 1)   # an absent tripwire is a finding
        self.assertEqual(self.run_cli("evaluate", "--samples", os.path.join(os.path.dirname(ok), "nope.json")).returncode, 2)
        self.assertEqual(self.run_cli("evaluate", "--samples", self.write("bad.json", "{")).returncode, 2)
        self.assertEqual(self.run_cli().returncode, 2)
        e = self.run_cli("expo", "--samples", ok)
        self.assertEqual(e.returncode, 0)
        self.assertIn("model_calls_total 0", e.stdout)
        logf = self.write("log.jsonl", "\n".join(TST_HUB_STG31_Trace.lines(TST_HUB_STG31_Trace())))
        t = self.run_cli("traces", "--log", logf)
        self.assertEqual(t.returncode, 0, t.stderr)
        self.assertEqual(sorted(json.loads(t.stdout)["traces"]), ["cid-1", "cid-2"])
        self.assertEqual(sorted(os.listdir(os.path.dirname(ok))), ["ok.json"])


if __name__ == "__main__":
    unittest.main()
