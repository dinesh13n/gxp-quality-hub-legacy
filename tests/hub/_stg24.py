"""Shared helpers for the Stage 24 hub tests (security, privacy and responsible-AI controls; DW-19). Synthetic, unvalidated.

Stage 24 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg24_egress_guard.py (E24EGRESS) instead (same split as Stages 20, 21 and 23). Evidence JSON is written under HUB_SANDBOX_ROOT/s24-evidence
and copied into docs/24-security-privacy/evidence/ by the build agent. Nothing here changes hub behaviour, a binding, a legacy path or the working tree
(OD-03a). No helper in this directory imports a deny-listed module (hub.guards.no_ai rule R2): wire tests use the raw-socket client of _http8.py.

  write_evidence()         JSON under HUB_SANDBOX_ROOT/s24-evidence
  module_cli()             run `python -m hub.security ...` in the sandbox copy
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
EVIDENCE_REL = os.path.join("docs", "24-security-privacy", "evidence")


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 24 module: covered by test_tst_hub_stg24_egress_guard.py (E24EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s24-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def module_cli(module, args, env=None, timeout=150):
    return subprocess.run([sys.executable, "-B", "-m", module] + list(args), cwd=S.CODE_ROOT, env=S.child_env(env), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


def code_of(proc):
    try:
        return json.loads(proc.stderr)["code"]
    except ValueError:
        return None
