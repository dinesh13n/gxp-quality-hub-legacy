"""Stage 27 mutation gate (DW-27; closes S26-F-08 / F-09 / F-10 and checks every Stage 27 fix): the Stage 26 survivors M5, M9, M10 now targeted by Stage 27 tests, plus one mutant per Stage 27 fix, one at a time in a
THROWAWAY full copy of the repository (never the working tree). Each mutant runs the Stage 27 (or, X6, Stage 26) tests that target the weakened control.
KILLED = at least one test fails. SURVIVED = a test gap (reported, never hidden).

    python3 -B s27_mutation_gate.py --repo <clean clone> --backup <_data-backup-2026-10-17> --work <sandbox dir> --out <json> [--only M1,M2]
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
    # the three Stage 26 survivors, now targeted by Stage 27 tests (layer tests)
    ("M5", "INC-08", "hub/web/authz.py", '            raise AuthForbidden({"reason": "route not registered (deny by default)"})', "            return None",
     "unregistered route allowed in the authorizer layer (deny-by-default branch removed)", ["STG27_M5"]),
    ("M9", "INC-07", "hub/obs/collect.py", "AND outcome = 'success' AND actor_kind <> 'human'", "AND outcome = 'success' AND actor_kind = 'human'",
     "Zone H service-actor tripwire counts the wrong actor kind", ["STG27_M9"]),
    ("M10", "INC-07", "hub/runs/schedule.py", "        if not isinstance(authority_ref, str) or not authority_ref.strip():", "        if False:",
     "schedule enable without authority_ref accepted", ["STG27_M10"]),
    # the Stage 27 fixes: undo each one
    ("X1", "S27 F-01", "hub/gate/service.py", "if sess is None:  # Stage 27 S26-F-01", "if False:  # Stage 27 S26-F-01",
     "OP-GATE-02 validates the action name before authentication again", ["STG27_F01"]),
    ("X2", "S27 F-02", "hub/decision/service.py", "        return dict(ev, basis=WITHHELD_BASIS, basis_withheld=True)", "        return ev",
     "restricted-evidence note shown to every role again", ["STG27_F02"]),
    ("X3", "S27 F-03", "hub/web/wire.py", "if has_lone_surrogate(doc):", "if False:", "lone surrogate no longer refused at the wire", ["STG27_F03"]),
    ("X4", "S27 F-05", "hub/config.py", "    bad = unknown_keys(cfg)\n    if bad:", "    bad = unknown_keys(cfg)\n    if False:", "unknown configuration keys accepted again", ["STG27_F05"]),
    ("X5", "S27 F-07", "hub/web/app.py", "resp = self._error(StoreUnavailable() if _is_store_fault(exc) else HubError(), cid)", "resp = self._error(HubError(), cid)",
     "store fault is the generic error again", ["STG27_F07"]),
    ("X6", "S27 F-06", "hub/web/server.py", "        timeout = read_timeout  # StreamRequestHandler", "        timeout = None  # StreamRequestHandler",
     "listener read timeout removed", ["STG26_C06"]),
    ("X7", "S27 RS-04", "hub/web/ratelimit.py", "            if len(q) < self.limit:", "            if True:", "limiter never blocks", ["STG27_L0"]),
    ("X8", "S27 RS-12", "hub/store/hardening/H001_migration_ledger_triggers.sql",
     "CREATE TRIGGER IF NOT EXISTS schema_migrations_no_update BEFORE UPDATE ON schema_migrations BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;",
     "CREATE TRIGGER IF NOT EXISTS schema_migrations_no_update BEFORE UPDATE ON schema_migrations BEGIN SELECT RAISE(IGNORE); END;",
     "schema_migrations UPDATE no longer aborts", ["STG27_H0"]),
    ("X9", "S27 OD-27", "hub/store/migrate.py", "from hub.store import db\n", "from hub.store import db\nfrom hub.ops import backup as backup_mod\n",
     "package import cycle re-introduced (ops <-> store)", ["STG27_S01"]),
    ("X10", "S27 SBOM", "hub/security/sbom.py", "sorted(pkgs[pkg])).encode(\"utf-8\")).hexdigest()", "sorted(pkgs[pkg])[:0]).encode(\"utf-8\")).hexdigest()",
     "package digest no longer depends on file content", ["STG27_B01"]),
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
