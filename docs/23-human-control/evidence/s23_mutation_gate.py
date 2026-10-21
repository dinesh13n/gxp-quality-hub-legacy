"""Stage 23 mutation gate (DW-14 H3, DW-15 H5, DW-17 A1/A2, DW-18 H1): one mutant at a time in a THROWAWAY full copy of the repository (never the working
tree); the Stage 23 group (-k STG23) runs there with the standard runner; KILLED = at least one test fails. H1 / H3 / H5 are the Stage 16 mutants
(s16_hub_mutation_gate.py) that the Stage 16 hub tests did not kill (H3, H5) or that the new Zone H matrix must also kill (H1).

    python3 -B s23_mutation_gate.py --repo <clean clone> --backup <_data-backup-2026-10-17> --work <sandbox dir> --out <json> [--only H3,H5]
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

SEL = ["-k", "STG23"]
MUTANTS = [
    ("H1", "hub/security/zone_h.py", "    if principal.principal_id not in holders:", "    if False and principal.principal_id not in holders:",
     "Zone H: a non-holder dispositioner is accepted (Stage 16 mutant H1, rule moved to hub/security/zone_h.py in Stage 20; DW-18 matrix)"),
    ("H3", "hub/web/app.py", '("X-Frame-Options", "DENY")', '("X-Frame-Options", "SAMEORIGIN")', "security header weakened (DW-14)"),
    ("H5", "hub/web/server.py", "    if not exposure.is_loopback(host):", "    if False:", "non-loopback bind accepted (DW-15)"),
    ("A1", "hub/control/flags.py", "        if not valid_ref(refs.get(path)):", "        if False:", "non-default decision flag accepted without approval_ref (DW-17)"),
    ("A2", "hub/admin/cli.py", "        switch.record_authority_changes(self.con, self.clock, self.anchor, self.cfg, self.cid, self.args.cmd)", "        pass",
     "a config-file change of capability_authority is not audited (DW-17)"),
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
    for mid, path, old, new, what in MUTANTS:
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
        p = subprocess.run([sys.executable, "-B", "tests/hub/run_hub_tests.py", "--sandbox-root", os.path.join(base, "sbx"), "--label", mid] + SEL,
                           cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=1200)
        summ = [l for l in p.stdout.splitlines() if l.startswith("summary")]
        counts = re.search(r"counts=(\{[^}]*\})", summ[-1]).group(1) if summ else None
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test\w+)", p.stdout, re.M)))
        status = "KILLED" if p.returncode == 1 and failed else ("SURVIVED" if p.returncode == 0 else "INCONCLUSIVE rc=%d" % p.returncode)
        results.append({"id": mid, "file": path, "mutation": what, "status": status, "rc": p.returncode, "counts": counts, "killed_by": failed[:12],
                        "seconds": round(time.time() - t0, 1), "tail": "" if status in ("KILLED", "SURVIVED") else p.stdout[-1500:]})
        print("%-4s %-11s %s %s" % (mid, status, counts, failed[:3]), flush=True)
        shutil.rmtree(base, ignore_errors=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"label": "synthetic, unvalidated - method validation only", "results": results}, fh, indent=1)


if __name__ == "__main__":
    main()
