"""Shared helpers for the Stage 20 hub tests (Application & Services Engineering; DW-02..DW-09). Synthetic, unvalidated.

Stage 20 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and are run under the egress guard by
test_tst_hub_stg20_egress_guard.py (E20EGRESS) instead - the INC-05..INC-09 split, so the frozen group C does not grow.
Everything lives under HUB_SANDBOX_ROOT (S.tmpdir); never inside the repository working tree (OD-03a).
"""
import os
import unittest

import _support as S

_OBS = {}


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 20 module: covered by test_tst_hub_stg20_egress_guard.py (E20EGRESS)")
    S.require_sandbox()


def observation():
    """(record path, data dir) of ONE `golden-observe` run per process (5 s on the reference laptop)."""
    if "path" not in _OBS:
        d = S.tmpdir("s20obs-")
        p = S.run_hub(["golden-observe", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT])
        assert p.returncode == 0, p.stderr[-2000:]
        _OBS["path"] = os.path.join(d, "runs", "golden-observe", "observation.json")
        _OBS["stdout"] = p.stdout
    return _OBS["path"]
