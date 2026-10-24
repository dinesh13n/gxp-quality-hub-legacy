"""Stage 24 mutation gate (DW-19 M1..M8): one mutant at a time in a THROWAWAY full copy of the repository (never the working
tree); the Stage 24 group (-k STG24) runs there with the standard runner; KILLED = at least one test fails. M1..M8 weaken one Stage 24 control each.

    python3 -B s24_mutation_gate.py --repo <clean clone> --backup <_data-backup-2026-10-17> --work <sandbox dir> --out <json> [--only H3,H5]
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

SEL = ["-k", "STG24"]
MUTANTS = [
    ("M1", "hub/security/transport.py", "    if not cookie_secure(settings):", "    if True:", "session cookie never gets Secure, even with TLS settings (A-INC08-3)"),
    ("M2", "hub/security/transport.py", '        req.query["reason"] = value', "        pass", "X-Hub-Reason header ignored (RTD-90)"),
    ("M3", "hub/security/tables.py", '"service_token": (RETAINED,', '"service_token": (MUTABLE,', "register disagrees with the store: a retained table called mutable (RF-02)"),
    ("M4", "hub/security/anchor_seal.py", 'entry.get("mac") != exp[i] or', "False or", "seal check ignores the MAC (RTD-29)"),
    ("M5", "hub/security/settings.py", '"lockout_threshold": 5,', '"lockout_threshold": 10,', "lockout threshold drifts from the register (RTD-26)"),
    ("M6", "hub/security/auth.py", '            self.con.execute("UPDATE session SET revoked_at = ? WHERE token_sha256 = ?", (self.clock(), sess.token_sha256))', "            pass",
     "logout does not revoke the session (ABU-10)"),
    ("M7", "hub/security/datamap.py", '{"pw_hash", "pw_salt", "token_sha256"}', '{"pw_hash", "token_sha256"}', "a credential column loses its secret tag (field map)"),
    ("M8", "hub/security/scan.py", "RETAINED_TABLES = tables.RETAINED_TABLES", 'RETAINED_TABLES = tables.RETAINED_TABLES[:18]', "scan list shrinks back (DW-19 gap reopened)"),
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
