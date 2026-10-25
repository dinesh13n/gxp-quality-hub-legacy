"""Shared helpers for the Stage 30 release-readiness tests (Synthetic, unvalidated).

Stage 30 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg30_egress_guard.py (E30EGRESS), the same split as Stages 20-31. Every store, config and git repository used here is a private copy under the
sandbox scratch root; nothing opens the network and nothing touches the working tree or its data/ (OD-03a).

  Rig                a private store + config + anchor path under the sandbox, with admin() / control() subprocess helpers
  write_evidence()   JSON under HUB_SANDBOX_ROOT/s30-evidence
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
DOCS = os.path.join(S.CODE_ROOT, "docs", "30-release")
EVID = os.path.join(DOCS, "evidence")
SANDBOX_REF = "REHEARSAL-SANDBOX-NOT-AN-APPROVAL"


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 30 module: covered by test_tst_hub_stg30_egress_guard.py (E30EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s30-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Rig(object):
    """A private hub store, config file and anchor file in a sandbox scratch directory."""

    def __init__(self, prefix, config_extra=None):
        self.root = S.tmpdir(prefix)
        self.data = os.path.join(self.root, "data")
        self.anchor = os.path.join(self.root, "anchor", "audit-anchor.jsonl")
        self.cfg_path = os.path.join(self.root, "config.json")
        os.makedirs(self.data)
        doc = {"audit": {"anchor_path": self.anchor}}
        doc.update(config_extra or {})
        with open(self.cfg_path, "w", encoding="utf-8") as f:
            json.dump(doc, f)

    def _run(self, module, args):
        cmd = [sys.executable, "-B", "-m", module, "--config", self.cfg_path] + list(args)
        return subprocess.run(cmd, cwd=S.CODE_ROOT, env=S.child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=170)

    def admin(self, *args):
        return self._run("hub.admin", args)

    def control(self, *args):
        return self._run("hub.control", args)

    def migrate(self):
        p = self.admin("migrate", "--data-dir", self.data, "--backup-root", os.path.join(self.root, "premigration"))
        assert p.returncode == 0, p.stderr[-800:]
        return p

    def anchor_bytes(self):
        with open(self.anchor, "rb") as f:
            return f.read()

    def audit_actions(self):
        import sqlite3
        con = sqlite3.connect(os.path.join(self.data, "hub.sqlite3"))
        try:
            return [(r[0], r[1], r[2]) for r in con.execute("SELECT action, object_ref, details FROM audit_log ORDER BY audit_seq")]
        finally:
            con.close()
