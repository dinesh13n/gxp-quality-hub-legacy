"""Stage 16 hub mutation gate for INC-08 / INC-09 (RTD-76, RTD-89): apply one mutant at a time to a THROWAWAY full
copy of the repository (never the working tree), run the relevant hub test group there with the standard runner,
and record KILLED (at least one test fails) or SURVIVED. Each copy is deleted after its run.

    python3 -B s16_hub_mutation_gate.py --repo <clean clone> --backup <_data-backup-2026-10-17> --work <sandbox dir> --out <json>
The copy carries .git and a sibling copy of the backup so the runner's own guards (sandbox, manifest) apply unchanged.
Synthetic data, unvalidated - method validation only.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

I8 = ["-k", "TST_GATE", "-k", "TST_REV", "-k", "TST_CO_08", "-k", "TST_NFR", "-k", "I8_", "-k", "INC08_S", "-k", "TST_SEC_16"]
I9 = ["-k", "I9_", "-k", "INC09_S"]
MUTANTS = [
    ("H1", "INC-08", "hub/gate/service.py", "elif p.principal_id not in holders:", "elif False and p.principal_id not in holders:",
     "Zone H: a non-holder dispositioner is accepted", I8),
    ("H2", "INC-08", "hub/web/app.py", "        if not ok:\n            self.metrics.auth_failure(\"csrf\")",
     "        if False:\n            self.metrics.auth_failure(\"csrf\")", "CSRF check disabled", I8),
    ("H3", "INC-08", "hub/web/app.py", '("X-Frame-Options", "DENY")', '("X-Frame-Options", "SAMEORIGIN")',
     "security header weakened", I8),
    ("H4", "INC-08", "hub/web/server.py", "        return exposure.is_loopback(client_address[0])", "        return True",
     "non-loopback peers accepted", I8),
    ("H5", "INC-08", "hub/web/server.py", "    if not exposure.is_loopback(host):", "    if False:",
     "non-loopback bind accepted", I8),
    ("H6", "INC-09", "hub/search/settings.py", 'DEFAULTS = {"enabled": False,', 'DEFAULTS = {"enabled": True,',
     "search ships enabled", I9),
    ("H7", "INC-09", "hub/search/engine.py", 'if c3 and self.settings["require_c3_reason"]:', "if False:",
     "C3 reason not required in search (OP-REV-03)", I9),
    ("H8", "INC-09", "hub/r2/protection.py", "    if not why:\n        raise ReasonRequired", "    if False:\n        raise ReasonRequired",
     "C3 reason not required in the joined view / protection layer", I9),
    ("H9", "INC-09", "hub/r2/divergence.py", "vals = set(v for v in outputs.values() if v is not None)", "vals = set(outputs.values())",
     "divergence counts null (not comparable) outputs", I9),
    ("H10", "INC-09", "hub/search/settings.py", '.get("enabled", False)', '.get("enabled", True)',
     "template drafts ship enabled", I9),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    results = []
    for mid, inc, path, old, new, what, sel in MUTANTS:
        if a.only and mid not in a.only.split(","):
            continue
        t0 = time.time()
        base = os.path.join(a.work, "mut-" + mid)
        shutil.rmtree(base, ignore_errors=True)
        os.makedirs(base)
        repo = os.path.join(base, "repo")
        shutil.copytree(a.repo, repo, symlinks=True)
        shutil.copytree(a.backup, os.path.join(base, os.path.basename(a.backup.rstrip("/"))), symlinks=True)
        f = os.path.join(repo, path)
        src = open(f, encoding="utf-8").read()
        if src.count(old) != 1:
            results.append({"id": mid, "status": "NOT-APPLIED", "reason": "anchor found %d times" % src.count(old), "file": path})
            shutil.rmtree(base, ignore_errors=True)
            continue
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(src.replace(old, new))
        p = subprocess.run([sys.executable, "-B", "tests/hub/run_hub_tests.py", "--sandbox-root", os.path.join(base, "sbx"),
                            "--label", mid] + sel, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True, timeout=1200)
        summ = [l for l in p.stdout.splitlines() if l.startswith("summary")]
        counts = re.search(r"counts=(\{[^}]*\})", summ[-1]).group(1) if summ else None
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test\w+)", p.stdout, re.M)))
        status = "KILLED" if p.returncode == 1 and failed else ("SURVIVED" if p.returncode == 0 else "INCONCLUSIVE rc=%d" % p.returncode)
        results.append({"id": mid, "increment": inc, "file": path, "mutation": what, "status": status, "rc": p.returncode,
                        "counts": counts, "killed_by": failed[:12], "seconds": round(time.time() - t0, 1),
                        "tail": "" if status in ("KILLED", "SURVIVED") else p.stdout[-1500:]})
        print("%-4s %-8s %-11s %s %s" % (mid, inc, status, counts, failed[:3]), flush=True)
        shutil.rmtree(base, ignore_errors=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"label": "synthetic, unvalidated - method validation only", "results": results}, fh, indent=1)


if __name__ == "__main__":
    main()
