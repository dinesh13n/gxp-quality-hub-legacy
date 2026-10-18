"""TST-CO-11 (AC-CO-11, FR-CO-04, PNFR-18, BEH-CO-07, ADR-002, OD-08) - a dependency `openai` added to the
project makes the deny-list check fail with E-CO-DENYLIST-IMPORT; the real hub tree is clean.
Fixture FX-UNIT-SYNTHETIC: throw-away project trees in the sandbox scratch area (scanned, never imported).
"""
import json
import os
import unittest

import _support as S
from hub.guards import no_ai


def setUpModule():
    S.require_sandbox()


def _write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


CLEAN_PYPROJECT = """[project]
name = "synthetic"
requires-python = ">=3.10"
dependencies = []
"""


class TST_CO_11_NoAiDenylist(unittest.TestCase):

    def test_TST_CO_11_a_openai_dependency_fails_build(self):
        """TST-CO-11 / AC-CO-11: pyproject dependency `openai` -> no-ai-check exit 9, E-CO-DENYLIST-IMPORT (rule R3)."""
        root = S.tmpdir("co11a-")
        _write(root, "pyproject.toml", CLEAN_PYPROJECT.replace("dependencies = []", 'dependencies = [\n  "openai>=1.0",\n]'))
        _write(root, "hub/core/ok.py", "import json\n")
        p = S.run_hub(["no-ai-check", os.path.join(root, "pyproject.toml"), os.path.join(root, "hub")])
        self.assertEqual(p.returncode, 9, p.stdout + p.stderr)
        env = json.loads(p.stderr)
        self.assertEqual(env["code"], "E-CO-DENYLIST-IMPORT")
        self.assertEqual([(f["rule"], f["item"]) for f in env["details"]], [("R3", "openai>=1.0")])

    def test_TST_CO_11_b_import_rules(self):
        """TST-CO-11: AI imports (incl. importlib strings) fail R1; HTTP clients fail R2 outside adapters/ only."""
        root = S.tmpdir("co11b-")
        cases = {
            "hub/core/a.py": ("raise SystemExit(99)\nimport openai\n", [("R1", "openai")]),
            "hub/core/b.py": ("from langchain_core import prompts\n", [("R1", "langchain_core")]),
            "hub/core/c.py": ("import importlib\nm = importlib.import_module('anthropic')\n", [("R1", "anthropic")]),
            "hub/core/d.py": ("import requests\n", [("R2", "requests")]),
            "hub/core/e.py": ("from urllib import request\n", [("R2", "urllib.request")]),
            "hub/adapters/f.py": ("import urllib.request\n", []),
            "hub/core/g.py": ("import sklearn.linear_model\nimport torchaudio\n", [("R1", "sklearn.linear_model"), ("R1", "torchaudio")]),
            "hub/core/h.py": ("import json, sqlite3, socket\n", []),
        }
        for rel, (src, expected) in sorted(cases.items()):
            with self.subTest(rel=rel):
                p = _write(root, rel, src)
                self.assertEqual([(f["rule"], f["item"]) for f in no_ai.scan([p])], expected)

    def test_TST_CO_11_c_requirements_manifest(self):
        """TST-CO-11: requirements*.txt entries (torch, langchain-openai, scikit-learn) fail R3."""
        root = S.tmpdir("co11c-")
        p = _write(root, "requirements-dev.txt", "# dev\nflake8\ntorch==2.3\nlangchain-openai\nscikit-learn>=1\n")
        self.assertEqual([f["item"] for f in no_ai.scan([p])], ["torch==2.3", "langchain-openai", "scikit-learn>=1"])

    def test_TST_CO_11_d_real_tree_is_clean(self):
        """TST-CO-11: hub/, tests/hub/ and the project pyproject.toml pass the deny-list (exit 0)."""
        p = S.run_hub(["no-ai-check"])
        self.assertEqual(p.returncode, 0, p.stderr)
        scanned = json.loads(p.stdout)["scanned"]
        self.assertEqual(scanned, ["hub", os.path.join("tests", "hub"), "pyproject.toml"])


if __name__ == "__main__":
    unittest.main()
