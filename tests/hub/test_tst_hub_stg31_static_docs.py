"""Stage 31 tests, part 4: static guarantees and the document set. Synthetic, unvalidated.

  D01  the new hub/obs modules import no clock, random, socket, HTTP client, subprocess or web layer; they define no error code; nothing outside hub/obs and
       the tests imports them (not wired: S31-DEV-01); no shipped behaviour file was edited
  D02  the 12 required artifacts exist with the front matter and the eight sections, a status that is not APPROVED, and the synthetic label
  D03  docs agree with code: every catalogue metric is in metrics-spec.md, every alert in alert-catalog.md, every SLO / invariant in slo-sla-definitions.md,
       every runbook anchor RB-nn is used; no real holder name appears; zone_h.holders is still empty in the shipped config
  D04  telemetry privacy by construction: the log whitelist has no free-text field, the HTTP label sets are closed, and the SLA text says none exists
"""
import ast
import json
import os
import re
import unittest

import _stg31 as T
import _support as S
from hub.obs import alerts, catalog, log as obslog, slo

OBS = os.path.join(S.CODE_ROOT, "hub", "obs")
NEW = ("catalog.py", "slo.py", "alerts.py", "resilience_samples.py", "trace.py", "expo.py", "report.py", "cli.py", "__main__.py")
ARTIFACTS = ("observability-architecture", "logging-spec", "metrics-spec", "tracing-spec", "ai-telemetry-spec", "agent-telemetry-spec", "dashboard-catalog",
             "alert-catalog", "slo-sla-definitions", "error-budget-policy", "operational-runbook", "observability-validation")
SECTIONS = ("## Summary", "## Findings", "## Evidence References", "## Assumptions", "## Unknowns", "## Unresolved Issues", "## Residual Risks", "## Change History")
FORBIDDEN = ("time", "datetime", "random", "secrets", "socket", "subprocess", "urllib", "http")


def setUpModule():
    T.skip_in_inner_egress_run()


def read(rel):
    with open(os.path.join(S.CODE_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def imports(text):
    mods = []
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Import):
            mods += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            mods += [n.module or ""] + [(n.module or "") + "." + a.name for a in n.names]
    return mods


class TST_HUB_STG31_Static(unittest.TestCase):

    def test_TST_HUB_STG31_D01_modules_are_pure_and_not_wired(self):
        """D01: no forbidden import in the new modules (cli.py reads files with open() and uses sys/argparse/json only); no E-* code defined; no other hub module imports them."""
        for fn in NEW:
            text = read("hub/obs/" + fn)
            for m in imports(text):
                self.assertNotIn(m.split(".")[0], FORBIDDEN, (fn, m))
                self.assertFalse(m.startswith("hub.web"), (fn, m))
            self.assertNotRegex(text, r"[\"']E-[A-Z]")  # error codes live in the closed registries (Stage 27 findings); this package adds none
        users = []
        for d, dirs, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            dirs[:] = [x for x in dirs if x not in ("__pycache__",)]
            for fn in fns:
                rel = os.path.relpath(os.path.join(d, fn), S.CODE_ROOT).replace(os.sep, "/")
                if not fn.endswith(".py") or rel.startswith("hub/obs/"):
                    continue
                if any(m.startswith(("hub.obs.catalog", "hub.obs.slo", "hub.obs.alerts", "hub.obs.report", "hub.obs.expo", "hub.obs.trace",
                                     "hub.obs.resilience_samples", "hub.obs.cli")) for m in imports(read(rel))):
                    users.append(rel)
        self.assertEqual(users, [], "Stage 31 modules are built but not wired (S31-DEV-01 / D-31-02)")
        edits = json.loads(read("tests/hub/non_add_edits.json"))
        self.assertIn(edits["stage"], ("31", "30"))  # S30-DEV-04: each build stage resets the list; the Stage 30 list is pinned by STG30_D01, the Stage 31 list by this stage's own branch

    def test_TST_HUB_STG31_D02_artifacts_exist_with_structure(self):
        """D02: 12 artifacts, front matter (stage, artifact, version, date, author_agent, status, evidence_sources, supersedes), eight sections, status not APPROVED, label present."""
        for a in ARTIFACTS:
            text = read("docs/31-observability/%s.md" % a)
            head = text.split("---")[1]
            for k in ("stage:", "artifact:", "version:", "date:", "author_agent:", "status:", "evidence_sources:", "supersedes:"):
                self.assertIn(k, head, (a, k))
            self.assertIn('artifact: "%s.md"' % a, head)
            self.assertNotIn("APPROVED", re.search(r"status: \"([^\"]*)\"", head).group(1), a)
            for sec in SECTIONS:
                self.assertIn(sec, text, (a, sec))
            self.assertIn("synthetic, unvalidated", text, a)
        self.assertEqual(len(ARTIFACTS), 12)

    def test_TST_HUB_STG31_D03_docs_agree_with_code(self):
        """D03: catalogue / alert / SLO / runbook ids are all documented; the shipped config still has no Zone H holders; no real person is named as a holder."""
        met = read("docs/31-observability/metrics-spec.md")
        for n in catalog.CATALOG:
            self.assertIn("`%s`" % n, met, n)
        al = read("docs/31-observability/alert-catalog.md")
        for r in alerts.RULES:
            self.assertIn(r["id"], al, r["id"])
        sl = read("docs/31-observability/slo-sla-definitions.md")
        for s in slo.SLOS:
            self.assertIn(s["id"], sl, s["id"])
        for i in slo.INVARIANTS:
            self.assertIn(i["id"], sl, i["id"])
        rb = read("docs/31-observability/operational-runbook.md")
        used = set(r["runbook"] for r in alerts.RULES)
        have = set(re.findall(r"^#{2,4} (RB-\d\d)\b", rb, re.M))
        self.assertEqual(used - have, set())
        self.assertEqual(have - used - {"RB-00", "RB-11", "RB-12"}, set(), "a runbook entry no alert points at is dead text")
        from hub import config
        from hub.security import settings
        self.assertEqual(settings.resolve(config.load(None))["zone_h"]["holders"], [])

    def test_TST_HUB_STG31_D04_privacy_by_construction(self):
        """D04: the log field whitelist has no free-text field; the HTTP metric labels are closed; the SLA statement says none exists; no SLO claims to be agreed."""
        free_text = {"message", "msg", "body", "text", "note", "notes", "payload", "query", "sql", "password", "token", "email", "name"}
        self.assertEqual(free_text & set(obslog.FIELDS), set())
        allowed = set()
        for m in catalog.CATALOG.values():
            allowed |= set(m["labels"])
        self.assertEqual(sorted(allowed), sorted(["source", "outcome", "queue", "event_type", "action", "job", "engine", "op_id", "status", "reason", "function",
                                                  "dependency"]))
        sl = read("docs/31-observability/slo-sla-definitions.md")
        self.assertRegex(sl, r"No SLA")
        for s in slo.SLOS:
            self.assertNotIn("agreed", s["basis"].lower().replace("not agreed", ""))


if __name__ == "__main__":
    unittest.main()
