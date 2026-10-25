"""Stage 28 tests, part 1: the resilience primitives (policy.py). Synthetic, unvalidated. No network, no store.

  P01  settings: defaults, every invalid value refused with ConfigInvalid
  P02  deterministic back-off schedule, cap, clamped jitter
  P03  retry budget: retries <= cap + calls * percent / 100 for any number of calls (the retry-storm bound); deposits never exceed the cap
  P04  breaker state machine (closed / open / half-open), consecutive-failure semantics, probe limit, clock rollback
  P05  breaker snapshot / restore, malformed snapshot refused
  P06  bulkhead under threads: exactly max enter, the rest are refused at once
  P07  static: hub/resilience imports no clock, random, socket or HTTP client, defines no error code, and nothing in hub/ imports it (not wired)
"""
import ast
import os
import re
import threading
import unittest

import _stg28 as T
import _support as S
from hub.core.errors import ConfigInvalid
from hub.resilience import policy


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG28_Policy(unittest.TestCase):
    def test_TST_HUB_STG28_P01_settings_defaults_and_validation(self):
        """P01: defaults are the documented ones (assumptions A-28-01..03); wrong types, bools, NaN / inf, out-of-range values, unknown sections / keys and cap < base are ConfigInvalid."""
        d = policy.resolve()
        self.assertEqual(d["retry"]["max_retries"], 3)
        self.assertEqual((d["breaker"]["failure_threshold"], d["breaker"]["cooldown_seconds"]), (3, 60))
        self.assertEqual(policy.resolve({"retry": {"max_retries": 0}})["retry"]["max_retries"], 0)
        self.assertEqual(policy.DEFAULTS["retry"]["max_retries"], 3, "resolve() must not mutate DEFAULTS")
        bad = [{"retry": {"max_retries": -1}}, {"retry": {"max_retries": 11}}, {"retry": {"max_retries": True}}, {"retry": {"max_retries": 1.5}},
               {"retry": {"base_seconds": 0}}, {"retry": {"base_seconds": "1"}}, {"retry": {"base_seconds": float("nan")}}, {"retry": {"base_seconds": float("inf")}},
               {"retry": {"factor": 0}}, {"retry": {"cap_seconds": 0.001}}, {"retry": {"timeout_seconds": 0}}, {"retry": {"retry_shape_errors": "yes"}},
               {"retry": {"budget_percent": 101}}, {"retry": {"budget_cap": -1}}, {"breaker": {"failure_threshold": 0}}, {"breaker": {"cooldown_seconds": 0}},
               {"breaker": {"half_open_probes": 0}}, {"bulkhead": {"max_concurrent": 0}}, {"bulkhead": {"max_concurrent": None}},
               {"retry": {"nope": 1}}, {"nope": {}}, {"retry": 5}, {"retry": {"base_seconds": 10, "cap_seconds": 5}}]
        for b in bad:
            with self.assertRaises(ConfigInvalid, msg=repr(b)):
                policy.resolve(b)
        for b in ("x", 5, [], True):
            with self.assertRaises(ConfigInvalid, msg=repr(b)):
                policy.resolve(b)

    def test_TST_HUB_STG28_P02_backoff_schedule(self):
        """P02: min(cap, base * factor**i); the shipped client's 0.5 / 1.0 / 2.0 is the prefix; jitter is clamped into [0, d]."""
        sched = [policy.backoff_delay(i, 0.5, 2, 8) for i in range(6)]
        self.assertEqual(sched, [0.5, 1.0, 2.0, 4.0, 8.0, 8.0])
        self.assertEqual(policy.backoff_delay(1000, 0.5, 2, 8), 8.0)
        self.assertEqual(policy.backoff_delay(3, 0.5, 2, 8, jitter=lambda d: d * 2), 4.0)
        self.assertEqual(policy.backoff_delay(3, 0.5, 2, 8, jitter=lambda d: -5), 0.0)
        self.assertEqual(policy.backoff_delay(3, 0.5, 2, 8, jitter=lambda d: d / 2), 2.0)

    def test_TST_HUB_STG28_P03_retry_budget_bounds_the_storm(self):
        """P03: for 1 / 10 / 100 / 1000 calls that all want 3 retries, granted retries <= cap + calls * percent / 100; a long run of deposits never exceeds the cap; percent 0 and cap 0 grant none."""
        rows = []
        for n in (1, 10, 100, 1000):
            b = policy.RetryBudget(20, 10)
            granted = 0
            for _ in range(n):
                b.deposit()
                for _r in range(3):
                    granted += 1 if b.withdraw() else 0
            self.assertLessEqual(granted, 10 + n * 20 / 100.0, n)
            unbudgeted = n * 3
            rows.append({"calls": n, "retries_granted": granted, "retries_unbudgeted": unbudgeted, "bound": 10 + n * 0.2})
            self.assertEqual(b.retries_granted + b.retries_denied, 3 * n)
        self.assertLess(rows[-1]["retries_granted"], rows[-1]["retries_unbudgeted"] / 10)
        b = policy.RetryBudget(20, 10)
        for _ in range(10000):
            b.deposit()
        self.assertEqual(b.tokens, 10.0)
        z = policy.RetryBudget(0, 0)
        z.deposit()
        self.assertFalse(z.withdraw())
        self.assertFalse(policy.RetryBudget(0, 5, initial=0).withdraw())
        T.write_evidence("retry-budget-bound.json", {"label": T.LABEL, "percent": 20, "cap": 10, "rows": rows})

    def test_TST_HUB_STG28_P04_breaker_state_machine(self):
        """P04: closed -> open after N CONSECUTIVE failures (a success resets the count); open rejects with a wait >= 1 that shrinks; after the cooldown exactly `probes` calls pass;
        a failed probe re-opens and restarts the cooldown; a successful probe closes; cancel() frees a probe slot; a clock that moves back restarts the cooldown."""
        c = T.FakeClock()
        b = policy.Breaker(3, 60, c, half_open_probes=1)
        for _ in range(2):
            self.assertEqual(b.allow(), (True, 0))
            b.record_failure()
        b.allow()
        b.record_success()
        for _ in range(2):
            b.allow()
            b.record_failure()
        self.assertEqual(b.state, policy.CLOSED, "two failures after a success must not open the breaker")
        b.allow()
        b.record_failure()
        self.assertEqual(b.state, policy.OPEN)
        ok, wait = b.allow()
        self.assertEqual((ok, wait), (False, 61))
        c.advance(59)
        ok, wait = b.allow()
        self.assertFalse(ok)
        self.assertGreaterEqual(wait, 1)
        c.advance(1)
        self.assertEqual(b.state, policy.HALF_OPEN)
        self.assertEqual(b.allow(), (True, 0))
        self.assertEqual(b.allow()[0], False, "only one probe at a time")
        b.record_failure()
        self.assertEqual(b.state, policy.OPEN)
        c.advance(30)
        self.assertFalse(b.allow()[0], "the cooldown restarted at the failed probe")
        c.advance(30)
        self.assertEqual(b.allow(), (True, 0))
        b.cancel()
        self.assertEqual(b.allow(), (True, 0), "cancel() frees the probe slot without counting")
        b.record_success()
        self.assertEqual((b.state, b.snapshot()["failures"]), (policy.CLOSED, 0))
        self.assertEqual(b.opened_count, 2)
        for _ in range(3):
            b.allow()
            b.record_failure()
        c.advance(-500)
        self.assertEqual(b.state, policy.OPEN)
        self.assertFalse(b.allow()[0])
        c.advance(60)
        self.assertEqual(b.state, policy.HALF_OPEN)
        p2 = policy.Breaker(1, 10, c, half_open_probes=2)
        p2.allow()
        p2.record_failure()
        c.advance(10)
        self.assertEqual([p2.allow()[0] for _ in range(3)], [True, True, False])

    def test_TST_HUB_STG28_P05_breaker_snapshot_restore(self):
        """P05: snapshot / restore carries an OPEN breaker to another process; a malformed snapshot is ConfigInvalid and changes nothing."""
        c = T.FakeClock(500)
        a = policy.Breaker(1, 60, c)
        a.allow()
        a.record_failure()
        snap = a.snapshot()
        self.assertEqual(snap["state"], policy.OPEN)
        b = policy.Breaker(1, 60, c)
        b.restore(snap)
        self.assertFalse(b.allow()[0])
        c.advance(60)
        self.assertTrue(b.allow()[0])
        for bad in (None, [], {}, {"state": "weird", "failures": 0, "opened_at": None}, {"state": "open", "failures": 0, "opened_at": None},
                    {"state": "closed", "failures": True, "opened_at": None}, {"state": "closed", "failures": 0, "opened_at": "x"}):
            z = policy.Breaker(1, 60, c)
            with self.assertRaises(ConfigInvalid, msg=repr(bad)):
                z.restore(bad)
            self.assertEqual(z.state, policy.CLOSED)

    def test_TST_HUB_STG28_P06_bulkhead_under_threads(self):
        """P06: 12 threads race for 3 slots -> exactly 3 enter, 9 are refused immediately, peak 3, in_flight returns to 0; leaving frees a slot."""
        bh = policy.Bulkhead(3)
        gate, start, results = threading.Event(), threading.Barrier(12), []
        lock = threading.Lock()

        def w():
            start.wait(5)
            ok = bh.try_enter()
            with lock:
                results.append(ok)
            if ok:
                gate.wait(5)
                bh.leave()
        ts = [threading.Thread(target=w) for _ in range(12)]
        for t in ts:
            t.start()
        for _ in range(100):
            if len(results) == 12:
                break
            threading.Event().wait(0.05)
        self.assertEqual((results.count(True), results.count(False), bh.in_flight, bh.rejected), (3, 9, 3, 9))
        gate.set()
        for t in ts:
            t.join(5)
        self.assertEqual((bh.in_flight, bh.peak), (0, 3))
        self.assertTrue(bh.try_enter())

    def test_TST_HUB_STG28_P07_static_rules(self):
        """P07: hub/resilience imports no time / datetime / random / secrets / socket / urllib / http.client (clock, sleep and jitter are injected; only guarded.py may reach the HTTP client, through
        hub.adapters), names no E-code except the two existing ones it reuses, and no other hub module imports it (nothing is wired - D-28-01 / D-28-02)."""
        root = os.path.join(S.CODE_ROOT, "hub")
        banned = {"time", "datetime", "random", "secrets", "socket", "urllib", "http", "requests"}
        for fn in sorted(os.listdir(os.path.join(root, "resilience"))):
            if not fn.endswith(".py"):
                continue
            src = open(os.path.join(root, "resilience", fn), encoding="utf-8").read()
            self.assertEqual(sorted(set(re.findall(r"E-[A-Z]+-[A-Z0-9-]+", src)) - {"E-INT-SOURCE-UNREACHABLE", "E-REQ-RATE-LIMITED"}), [], fn)  # only existing codes may be named
            for n in ast.walk(ast.parse(src)):
                mods = [a.name.split(".")[0] for a in n.names] if isinstance(n, ast.Import) else ([n.module.split(".")[0]] if isinstance(n, ast.ImportFrom) and n.module else [])
                self.assertEqual(sorted(set(mods) & banned), [], fn)
        users = []
        for d, _, fns in os.walk(root):
            if os.sep + "resilience" in d + os.sep or d.endswith("__pycache__"):
                continue
            for fn in fns:
                if fn.endswith(".py") and "hub.resilience" in open(os.path.join(d, fn), encoding="utf-8").read():
                    users.append(os.path.relpath(os.path.join(d, fn), root))
        self.assertEqual(sorted(users), [os.path.join("obs", "resilience_samples.py"), os.path.join("web", "bounded_server.py")])  # S28-DEV-08: the capped listener lives in hub/web (S20-S22); S31-DEV-08: hub/obs/resilience_samples.py also reads it (read-only telemetry, not wired); neither is wired into `hub web serve`


if __name__ == "__main__":
    unittest.main()
