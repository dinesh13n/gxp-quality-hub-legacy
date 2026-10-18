"""In-sandbox unittest driver used by run_hub_tests.py (and by TST-CO-12 for the egress-guarded inner run).

  python -B tests/hub/_driver.py --out result.json [--egress-guard] [-k PATTERN ...]

Discovers tests/hub (top level tests/hub), runs them verbosely, and writes per-test results as JSON.
With --egress-guard the hub egress guard is installed for the whole run (AC-CO-12) and the recorded
attempts plus the zero-tripwires are written to the result.
"""
import argparse
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.realpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)


class _Recorder(unittest.TextTestResult):
    def __init__(self, *a, **kw):
        unittest.TextTestResult.__init__(self, *a, **kw)
        self.records = []

    def _rec(self, test, status, detail=None):
        self.records.append({"id": test.id(), "status": status, "detail": detail})

    def addSuccess(self, test):
        unittest.TextTestResult.addSuccess(self, test)
        self._rec(test, "ok")

    def addFailure(self, test, err):
        unittest.TextTestResult.addFailure(self, test, err)
        self._rec(test, "FAIL", self._exc_info_to_string(err, test)[-1500:])

    def addError(self, test, err):
        unittest.TextTestResult.addError(self, test, err)
        self._rec(test, "ERROR", self._exc_info_to_string(err, test)[-1500:])

    def addSkip(self, test, reason):
        unittest.TextTestResult.addSkip(self, test, reason)
        self._rec(test, "skipped", reason)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--egress-guard", action="store_true")
    ap.add_argument("-k", dest="patterns", action="append", default=[])
    a = ap.parse_args()
    if a.egress_guard:
        from hub.guards import egress
        from hub.obs import metrics
        metrics.reset()
        egress.install()
    loader = unittest.TestLoader()
    if a.patterns:
        loader.testNamePatterns = ["*%s*" % p for p in a.patterns]
    suite = loader.discover(start_dir=HERE, top_level_dir=HERE)
    runner = unittest.TextTestRunner(verbosity=2, resultclass=_Recorder, stream=sys.stdout)
    res = runner.run(suite)
    out = {"tests_run": res.testsRun, "successful": res.wasSuccessful(), "records": res.records}
    if a.egress_guard:
        out["egress_attempts"] = egress.attempts()
        out["tripwires"] = metrics.tripwires()
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
