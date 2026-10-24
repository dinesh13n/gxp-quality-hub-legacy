"""Stage 26 mutation gate (DW-23; A-26-03): a sample of 10 INC-05 / INC-07 / INC-08 mutants plus the Stage 16 survivors H3 and H5, one mutant at a time in a
THROWAWAY full copy of the repository (never the working tree). Each mutant runs the Stage 26 tests that target the weakened control (selectors per mutant; H3 / H5
use the Stage 23 tests that killed them in Stage 23). KILLED = at least one test fails. SURVIVED = a registered test gap (nothing is fixed in Stage 26).
Mutants M9 / M10 weaken INC-07 controls that the Stage 26 tests do not target; a survival there is expected and is reported as such, not hidden.

    python3 -B s26_mutation_gate.py --repo <clean clone> --backup <_data-backup-2026-10-17> --work <sandbox dir> --out <json> [--only M1,M2]
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

MUTANTS = [
    ("M1", "INC-08", "hub/security/zone_h.py", '    if parse(now()).timestamp() - parse(reauth_at).timestamp() > zone_h["reauth_window_seconds"]:', "    if False:",
     "re-authentication window never enforced", ["STG26_Control"]),
    ("M2", "INC-08", "hub/security/zone_h.py", "    if principal.principal_id not in holders:", "    if False:", "holder membership never checked", ["STG26_Control"]),
    ("M3", "INC-08", "hub/web/csrf.py", "    return headers.get(HEADER) == HEADER_VALUE", "    return True", "CSRF header never required", ["STG26_Control"]),
    ("M4", "INC-08", "hub/web/app.py", "        if len(req.body) > self.body_limit:", "        if False:", "request body limit never enforced", ["STG26_Wire"]),
    ("M5", "INC-08", "hub/web/authz.py", '            raise AuthForbidden({"reason": "route not registered (deny by default)"})', "            return None",
     "unregistered route allowed (deny-by-default removed)", ["STG26_Control", "STG26_Wire"]),
    ("M6", "INC-05", "hub/decision/access.py", '    "restricted": ("quality_lead", "compliance", "dispositioner"),', '    "restricted": ("reviewer", "quality_lead", "compliance", "dispositioner"),',
     "reviewer may read restricted evidence", ["STG26_Input"]),
    ("M7", "INC-05", "hub/decision/service.py", "        if row[0] != body_hash:", "        if False:", "idempotency key reuse with a different body accepted", ["STG26_Input", "STG26_Resilience"]),
    ("M8", "INC-05", "hub/policy/engine.py", '    if function not in FUNCTIONS or function not in ruleset["functions"]:', "    if False:",
     "unknown rule function not refused", ["STG26_Input"]),
    ("M9", "INC-07", "hub/obs/collect.py", "AND outcome = 'success' AND actor_kind <> 'human'", "AND outcome = 'success' AND actor_kind = 'human'",
     "Zone H service-actor tripwire counts the wrong actor kind", ["STG26_Control", "STG26_NoAI"]),
    ("M10", "INC-07", "hub/runs/schedule.py", "        if not isinstance(authority_ref, str) or not authority_ref.strip():", "        if False:",
     "schedule enable without authority_ref accepted", ["STG26_Control", "STG26_NoAI"]),
    ("H3", "INC-08 (Stage 16 survivor)", "hub/web/app.py", '("X-Frame-Options", "DENY")', '("X-Frame-Options", "SAMEORIGIN")', "security header weakened",
     ["STG23_S01", "STG23_S02"]),
    ("H5", "INC-08 (Stage 16 survivor)", "hub/web/server.py", "    if not exposure.is_loopback(host):", "    if False:", "non-loopback bind accepted",
     ["STG23_S03", "STG23_S04", "STG23_S05"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    ap.add_argument("--sel", default=None, help="second look: comma-separated selectors of EARLIER groups replace the per-mutant selectors")
    a = ap.parse_args()
    results = []
    for mid, inc, path, old, new, what, sel in MUTANTS:
        if a.only and mid not in a.only.split(","):
            continue
        if a.sel:
            sel = a.sel.split(",")
            mid = mid + "+earlier"
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
            results.append({"id": mid, "status": "NOT-APPLIED", "reason": "anchor found %d times" % src.count(old), "file": path, "increment": inc})
            shutil.rmtree(base, ignore_errors=True)
            continue
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(src.replace(old, new))
        p = subprocess.run([sys.executable, "-B", "tests/hub/run_hub_tests.py", "--sandbox-root", os.path.join(base, "sbx"), "--label", mid] + [x for s in sel for x in ("-k", s)],
                           cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=1200)
        summ = [l for l in p.stdout.splitlines() if l.startswith("summary")]
        counts = re.search(r"counts=(\{[^}]*\})", summ[-1]).group(1) if summ else None
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test\w+)", p.stdout, re.M)))
        status = "KILLED" if p.returncode == 1 and failed else ("SURVIVED" if p.returncode == 0 else "INCONCLUSIVE rc=%d" % p.returncode)
        results.append({"id": mid, "increment": inc, "selectors": sel, "file": path, "mutation": what, "status": status, "rc": p.returncode, "counts": counts, "killed_by": failed[:12],
                        "seconds": round(time.time() - t0, 1), "tail": "" if status in ("KILLED", "SURVIVED") else p.stdout[-1500:]})
        print("%-4s %-11s %s %s" % (mid, status, counts, failed[:3]), flush=True)
        shutil.rmtree(base, ignore_errors=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"label": "synthetic, unvalidated - method validation only", "results": results}, fh, indent=1)


if __name__ == "__main__":
    main()
