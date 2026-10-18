"""TST-CO-03 (AC-CO-03, FR-CO-01, FR-POL-04, AD-06, A-14-07; class A) - the Stage 7 goldens CT-01..CT-03 (and CT-13,
the night-shift reconciliation) run through the `as-found-*` rule sets with ZERO differences, and the rule sets agree
with the legacy code itself, executed in the sandbox copy (app/legacy_logic.py under python, legacy_js under node).
Fixture: FX-BASE125 sandbox copy (S.LEGACY_ROOT) + a loaded INC-04 store.
"""
import shutil
import unittest

import _support as S
import _inc04 as P
from hub.adapters import legacy_sqlite
from hub.policy import engine

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
STATUSES = ["OPEN", "UNDER_REVIEW", "CLOSED", "ESCALATED", "REOPENED"]


def setUpModule():
    S.require_sandbox()


class TST_CO_03_GoldenParity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.st = P.PStore(loaded=True)

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    def test_TST_CO_03_a_ct01_ct03_ct13_goldens_zero_difference(self):
        """TST-CO-03 / AC-CO-03: CT-01 (120 priority rows), CT-03 (20 manual-review rows), CT-13 (32 JS thresholds + allow cases)."""
        svc = self.st.svc
        diffs = []
        prio = P.golden(["priority_truth_table"])
        self.assertEqual(len(prio), 120)
        for status, sev, amount, want in prio:
            got = svc.evaluate("PRIORITY", {"status": status, "severity": sev, "amount": amount}, "as-found-python@1")["outcome"]
            if got != want:
                diffs.append(("PRIORITY", status, sev, amount, want, got))
        mr = P.golden(["manual_review_truth_table"])
        self.assertEqual(len(mr), 20)
        for status, sev, want in mr:
            got = svc.evaluate("MANUAL_REVIEW", {"status": status, "severity": sev}, "as-found-python@1")["outcome"]
            if got is not want:
                diffs.append(("MANUAL_REVIEW", status, sev, want, got))
        table = P.golden(["js_policy_table", "table"])
        self.assertEqual(len(table), 32)
        for region, year, want in table:
            got = svc.evaluate("AMOUNT_LIMIT", {"amount": 0, "region": region, "year": year}, "as-found-js@1")["outcome"]["threshold"]
            if got != want:
                diffs.append(("THRESHOLD", region, year, want, got))
        allows = P.golden(["js_policy_table", "allows"])
        self.assertEqual(len(allows), 9)
        compared = 0
        for amount, region, year, want in allows:
            if amount is None or isinstance(amount, str):
                continue  # 'abc' / null: legacy coercion accidents, now E-POL-INPUT-INVALID (TST-POL-23, DEV-30)
            compared += 1
            got = svc.evaluate("AMOUNT_LIMIT", {"amount": amount, "region": region, "year": year}, "as-found-js@1")["outcome"]["allowed"]
            if got is not want:
                diffs.append(("ALLOWS", amount, region, year, want, got))
        self.assertEqual(compared, 7)
        self.assertEqual(diffs, [])

    def test_TST_CO_03_b_night_shift_reconciliation_golden(self):
        """TST-CO-03: the per-row SHIFT_FLAG predicate reproduces the golden flagged_count of shift_reconciliation for limits
        50/100/500/12500 when the test performs the legacy LEFT JOIN itself (the service evaluates ONE row at a time)."""
        gold = P.golden(["shift_reconciliation"])
        self.assertEqual(sorted(gold), ["100", "12500", "50", "500"])
        doc = self.st.svc.get_ruleset("as-found-batch@1")
        run_dir = S.tmpdir("co03b-")
        sql = ("SELECT x.status, x.value, p.threshold FROM operational_objects x LEFT JOIN policy_register p "
               "ON p.region = x.region AND p.active = 1 ORDER BY x.object_id LIMIT ?")
        with legacy_sqlite.open_snapshot(S.LEGACY_ROOT, "enterprise_legacy.sqlite3", run_dir, pinned=True) as lg:
            for limit in (50, 100, 500, 12500):
                rows = lg.execute(sql, (limit,))
                self.assertEqual(len(rows), gold[str(limit)]["processed"])
                flagged = sum(1 for status, value, thr in rows
                              if engine.evaluate(doc, "SHIFT_FLAG", {"status": status, "value": value, "threshold": thr})["outcome"])
                self.assertEqual(flagged, gold[str(limit)]["flagged_count"], limit)

    def test_TST_CO_03_c_rule_sets_equal_the_legacy_code_run_in_the_sandbox(self):
        """TST-CO-03: python grid (5 statuses x 4 severities x 12 amounts) vs legacy app/legacy_logic.py, and a JS grid
        (5 regions x 9 years x 14 amounts incl. every x1.05 boundary) vs legacy_js/legacy_policy.js under node; zero differences."""
        node = shutil.which("node")
        self.assertIsNotNone(node, "node is required for the JS characterisation (device has Node v22)")
        svc = self.st.svc
        amounts = [0, 1, 49999.99, 50000, 50000.01, 50001, 99999, -1, -0.5, 1e6, 123456.789, 5e4]
        rows = [[s, v, a] for s in STATUSES for v in SEVERITIES for a in amounts]
        legacy = P.legacy_python(rows)
        bad = []
        for (s, v, a), (lp, lm) in zip(rows, legacy):
            if svc.evaluate("PRIORITY", {"status": s, "severity": v, "amount": a}, "as-found-python@1")["outcome"] != lp:
                bad.append(("PRIORITY", s, v, a))
            if svc.evaluate("MANUAL_REVIEW", {"status": s, "severity": v}, "as-found-python@1")["outcome"] is not lm:
                bad.append(("MANUAL_REVIEW", s, v))
        self.assertEqual(len(rows), 240)
        self.assertEqual(bad, [])
        regions = ["APAC", "EMEA", "AMER", "IN", "MARS"]
        years = [2019, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 3000]
        jrows = []
        for r in regions:
            for y in years:
                for a in (0, 1, 15750, 15750.01, 25000, 26250, 26250.01, 27000, 28560, 28560.01, 1000, 1048948.95, 1048948.96, 1049998.95):
                    jrows.append([a, r, y])
        legacy_js = P.legacy_node(jrows)
        bad = []
        for (a, r, y), (lt, la) in zip(jrows, legacy_js):
            got = svc.evaluate("AMOUNT_LIMIT", {"amount": a, "region": r, "year": y}, "as-found-js@1")["outcome"]
            if got["threshold"] != lt or got["allowed"] is not la:
                bad.append((a, r, y, lt, la, got))
        self.assertEqual(len(jrows), 630)
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
