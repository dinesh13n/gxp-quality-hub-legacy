"""Shared helpers for the Stage 31 observability tests (Synthetic, unvalidated).

Stage 31 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg31_egress_guard.py (E31EGRESS), the same split as Stages 20-28. Nothing here opens the network; stores are private sandbox copies.

  tripwire_pulse(name)   a context manager that raises a process-local tripwire counter by one and ALWAYS puts it back (the guarded run must end at 0)
  write_evidence()       JSON under HUB_SANDBOX_ROOT/s31-evidence
"""
import contextlib
import json
import os
import unittest

import _support as S
from hub.obs import metrics as tripwire_metrics

LABEL = "synthetic, unvalidated"
DOCS = os.path.join(S.CODE_ROOT, "docs", "31-observability")


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 31 module: covered by test_tst_hub_stg31_egress_guard.py (E31EGRESS)")
    S.require_sandbox()


@contextlib.contextmanager
def tripwire_pulse(name):
    tripwire_metrics.inc(name)
    try:
        yield
    finally:
        tripwire_metrics.inc(name, -1)


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s31-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def sample(name, kind="counter", value=0, **labels):
    return {"name": name, "kind": kind, "labels": labels, "value": str(value)}
