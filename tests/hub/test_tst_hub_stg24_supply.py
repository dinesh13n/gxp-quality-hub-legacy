"""Stage 24 supply-chain and code-hygiene tests (DW-19; SS-03, SS-01; threat classes supply chain, secrets, injection into SQL / shell). Synthetic, unvalidated.

  S30  every import in hub/ and tests/hub is the standard library or this repository (no third-party package); pyproject.toml declares no dependency;
       no requirements / lock file exists
  S31  hub/ uses no shell, eval, exec, pickle, marshal, ctypes, subprocess or os.system / os.popen; `__import__` only with a string literal
  S32  SQL built by formatting or concatenation, and SQL passed in a variable, are the REVIEWED sites only (SS-03 lint rule): a new one fails here
  S33  the secret scan is clean over hub/, tests/hub and the Stage 24 document tree (docs/24-security-privacy)
"""
import ast
import os
import sys
import unittest

import _support as S
import _stg24 as T
from hub.security import scan

def setUpModule():
    T.skip_in_inner_egress_run()


# Reviewed 2026-10-24 (Stage 24): per file, the number of execute() calls whose first argument is built by formatting / concatenation ("dynamic") or is a
# variable ("indirect"). Stage 16 triaged the 35 bandit B608 hits as constant column lists, placeholder strings or regex-validated names with bound values
# (security-scan-summary SS-1); this table freezes that state. [Inference] "constants only" is a review result, not a proof; a changed count needs a review.
SQL_REVIEWED = {
    "adapters/legacy_sqlite.py": {"dynamic": 1, "indirect": 1},
    "crosswalk/service.py": {"dynamic": 4, "indirect": 2},
    "decision/schema.py": {"indirect": 1},
    "decision/service.py": {"dynamic": 7, "indirect": 1},
    "gate/pack.py": {"dynamic": 1},
    "golden/baseline_probes.py": {"indirect": 1},
    "intake/schema.py": {"indirect": 1},
    "intake/service.py": {"dynamic": 2},
    "metrics/registry.py": {"dynamic": 2, "indirect": 1},
    "metrics/sources.py": {"dynamic": 1, "indirect": 1},
    "policy/schema.py": {"indirect": 1},
    "policy/service.py": {"dynamic": 7},
    "r2/consistency.py": {"dynamic": 2, "indirect": 1},
    "r2/facts.py": {"indirect": 1},
    "r2/intake_reports.py": {"indirect": 1},
    "r2/joined.py": {"indirect": 1},
    "r2/source_quality.py": {"dynamic": 1},
    "review/service.py": {"dynamic": 2},
    "runs/schema.py": {"indirect": 1},
    "runs/service.py": {"dynamic": 1},
    "search/corpus.py": {"dynamic": 1},
    "search/engine.py": {"dynamic": 1, "indirect": 1},
    "search/fts.py": {"dynamic": 1, "indirect": 1},
    "search/schema.py": {"indirect": 1},
    "security/audit.py": {"dynamic": 1},
    "store/db.py": {"indirect": 1},
    "store/hardening.py": {"indirect": 2},  # Stage 27 H001: the ledger DDL constant and the migration file text; both are constants (reviewed in Stage 27)
    "store/migrate.py": {"indirect": 1},
    "web/api.py": {"dynamic": 1, "indirect": 1},
    "web/schema.py": {"indirect": 1},
    "web/ui.py": {"indirect": 1},
}

DANGEROUS_CALLS = {"eval", "exec", "compile", "system", "popen", "popen2", "popen3", "spawnl", "spawnv", "execv", "execl", "load", "loads"}
DANGEROUS_MODULES = {"pickle", "marshal", "shelve", "ctypes", "subprocess", "cPickle", "dill", "yaml"}


def _py_files(sub):
    base = os.path.join(S.CODE_ROOT, sub)
    for d, dirs, fns in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for fn in sorted(fns):
            if fn.endswith(".py"):
                yield os.path.join(d, fn)


def _tree(p):
    with open(p, encoding="utf-8") as f:
        return ast.parse(f.read(), p)


def _sql_kind(a):
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return "literal"
    if isinstance(a, (ast.JoinedStr, ast.BinOp)) or (isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "format"):
        return "dynamic"
    return "indirect"


class TST_HUB_STG24_Supply(unittest.TestCase):

    def test_TST_HUB_STG24_S30_only_standard_library_and_repository_imports(self):
        """S30 (DW-19, SS-01): top-level imports of hub/ and tests/hub are in sys.stdlib_module_names or are hub / test-local modules; pyproject has no
        dependency table; no requirements*.txt, Pipfile, poetry.lock or package manifest sits in hub/ or tests/hub or at the repository root."""
        local = {"hub", "_support", "_driver"} | set(os.path.splitext(f)[0] for f in os.listdir(os.path.join(S.CODE_ROOT, "tests", "hub")) if f.endswith(".py"))
        extra = []
        for sub in ("hub", os.path.join("tests", "hub")):
            for p in _py_files(sub):
                for n in ast.walk(_tree(p)):
                    names = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 else [])
                    for m in names:
                        top = m.split(".")[0]
                        if top not in sys.stdlib_module_names and top not in local and top != "harness":
                            extra.append((os.path.relpath(p, S.CODE_ROOT), m))
        self.assertEqual(extra, [])
        with open(os.path.join(S.CODE_ROOT, "pyproject.toml"), encoding="utf-8") as f:
            toml = f.read()
        self.assertNotIn("dependencies", toml)
        names = ("requirements.txt", "requirements-dev.txt", "Pipfile", "poetry.lock", "package.json", "package-lock.json", "setup.py", "setup.cfg", "uv.lock")
        self.assertEqual([n for n in names if os.path.exists(os.path.join(S.CODE_ROOT, n))], [])
        self.assertEqual([p for p in os.listdir(os.path.join(S.CODE_ROOT, "hub")) if p.startswith("requirements")], [])

    def test_TST_HUB_STG24_S31_no_dangerous_apis_in_hub(self):
        """S31 (DW-19): AST scan of hub/ finds no import of pickle / marshal / ctypes / subprocess / yaml, no call to eval / exec / compile / os.system /
        os.popen / pickle loads, no `shell=True`, and `__import__` only with a string literal (3 sites, all constant)."""
        bad, dyn = [], 0
        for p in _py_files("hub"):
            rel = os.path.relpath(p, S.CODE_ROOT)
            for n in ast.walk(_tree(p)):
                if isinstance(n, ast.Import):
                    bad += [(rel, a.name) for a in n.names if a.name.split(".")[0] in DANGEROUS_MODULES]
                elif isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] in DANGEROUS_MODULES:
                    bad.append((rel, n.module))
                elif isinstance(n, ast.Call):
                    f = n.func
                    name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
                    if name == "__import__":
                        if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                            dyn += 1
                        else:
                            bad.append((rel, "__import__ with a non-literal"))
                    elif isinstance(f, ast.Name) and f.id in ("eval", "exec", "compile"):
                        bad.append((rel, f.id))
                    elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "os" and f.attr in ("system", "popen"):
                        bad.append((rel, "os." + f.attr))
                    for kw in n.keywords:
                        if kw.arg == "shell":
                            bad.append((rel, "shell="))
        self.assertEqual(bad, [])
        self.assertEqual(dyn, 3)

    def test_TST_HUB_STG24_S32_formatted_and_indirect_sql_are_the_reviewed_sites(self):
        """S32 (DW-19, SS-03): per file, the count of formatted ('dynamic') and variable ('indirect') execute() statements equals SQL_REVIEWED; the
        check detects a planted site."""
        def survey(paths):
            out = {}
            for rel, p in paths:
                for n in ast.walk(_tree(p)):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany", "executescript") and n.args:
                        k = _sql_kind(n.args[0])
                        if k != "literal":
                            out.setdefault(rel, {}).setdefault(k, 0)
                            out[rel][k] += 1
            return out
        base = os.path.join(S.CODE_ROOT, "hub")
        found = survey((os.path.relpath(p, base).replace(os.sep, "/"), p) for p in _py_files("hub"))
        self.assertEqual(found, SQL_REVIEWED)
        d = S.tmpdir("s24-sql-")
        planted = os.path.join(d, "planted.py")
        with open(planted, "w", encoding="utf-8") as f:
            f.write("def f(con, x):\n    con.execute('SELECT ' + x)\n    con.execute(f'SELECT {x}')\n    con.execute('SELECT %s' % x)\n    con.execute(x)\n")
        self.assertEqual(survey([("planted.py", planted)]), {"planted.py": {"dynamic": 3, "indirect": 1}})
        T.write_evidence("sql-dynamic-sites.json", {"label": T.LABEL, "files": len(found), "dynamic": sum(v.get("dynamic", 0) for v in found.values()),
                                                    "indirect": sum(v.get("indirect", 0) for v in found.values()), "by_file": found})

    def test_TST_HUB_STG24_S33_secret_scan_clean_including_the_stage24_documents(self):
        """S33 (DW-19, PNFR-08): scan.secret_scan over hub/, tests/hub and docs/24-security-privacy (when present) reports nothing."""
        paths = [os.path.join(S.CODE_ROOT, "hub"), os.path.join(S.CODE_ROOT, "tests", "hub")]
        docs = os.path.join(S.CODE_ROOT, "docs", "24-security-privacy")
        if os.path.isdir(docs):
            paths.append(docs)
        self.assertEqual(scan.secret_scan(paths), [])
        d = S.tmpdir("s24-sec-")
        with open(os.path.join(d, "planted.md"), "w", encoding="utf-8") as f:
            f.write("api_" + "key = " + chr(34) + "abcdef123456" + chr(34) + "\n")
        self.assertEqual([x["kind"] for x in scan.secret_scan([d])], ["credential_assignment"])


if __name__ == "__main__":
    unittest.main()
