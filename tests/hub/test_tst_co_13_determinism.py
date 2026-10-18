"""TST-CO-13 (AC-CO-13, PNFR-17, BEH-CO-08) - core functions run under PYTHONHASHSEED 0/1/random, TZ
UTC/Asia/Kolkata/America/Los_Angeles and locale C/en_IN: output hashes are all equal; no `random` import in
core modules. INC-02 core = golden-compare (compare engine, baseline reference queries, read-only adapters,
deviation register fold) and the canonical / Untrusted helpers.
Note: the en_IN locale is not installed on the dev device (`locale -a`); LC_ALL=en_IN.UTF-8 is still set
(the C library falls back), which is recorded as a limitation in the INC-02 evidence.
"""
import ast
import itertools
import os
import unittest

import _support as S

SEEDS = ("0", "1", "random")
TZS = ("UTC", "Asia/Kolkata", "America/Los_Angeles")
LOCALES = ("C", "en_IN.UTF-8")
CORE_DIRS = ("core", "golden", "adapters", "coexistence", "guards", "obs")


def setUpModule():
    S.require_sandbox()


class TST_CO_13_Determinism(unittest.TestCase):

    def test_TST_CO_13_a_bit_identical_across_hashseed_tz_locale(self):
        """TST-CO-13 / AC-CO-13: golden-compare --json and deviations output hash-equal across 3x3x2 = 18 environments."""
        digests = {}
        for seed, tz, loc in itertools.product(SEEDS, TZS, LOCALES):
            env = {"PYTHONHASHSEED": seed, "TZ": tz, "LC_ALL": loc, "LANG": loc}
            d = S.tmpdir("co13-")
            gc = S.golden_compare(d, env=env)
            self.assertEqual(gc.returncode, 6, gc.stderr)
            dv = S.run_hub(["deviations", "--data-dir", d], extra_env=env)
            self.assertEqual(dv.returncode, 0, dv.stderr)
            digests[(seed, tz, loc)] = (S.sha256_bytes(gc.stdout.encode()), S.sha256_bytes(dv.stdout.encode()))
        self.assertEqual(len(digests), 18)
        self.assertEqual(len(set(digests.values())), 1, digests)

    def test_TST_CO_13_b_no_random_or_wallclock_in_core(self):
        """TST-CO-13: no `random`/`secrets` import anywhere in hub/; no time/datetime import in the pure core
        (only hub/store/db.py stamps schema_migrations.applied_at, with an injectable clock)."""
        offenders = []
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(d, fn)
                rel = os.path.relpath(p, os.path.join(S.CODE_ROOT, "hub"))
                for n in ast.walk(ast.parse(open(p, encoding="utf-8").read())):
                    mods = []
                    if isinstance(n, ast.Import):
                        mods = [a.name.split(".")[0] for a in n.names]
                    elif isinstance(n, ast.ImportFrom) and n.module:
                        mods = [n.module.split(".")[0]]
                    for m in mods:
                        if m in ("random", "secrets"):
                            offenders.append((rel, m))
                        if m in ("time", "datetime") and rel.split(os.sep)[0] in CORE_DIRS:
                            offenders.append((rel, m))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
