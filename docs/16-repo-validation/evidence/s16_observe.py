"""Stage 16 behaviour observation (TG-4 step 2 extended): observe the BUILT hub modules (INC-04..INC-09) on the
FX-BASE125 fixture for every DV-01..DV-09 golden reference, beside `python -m hub golden-compare` (whose DV-02..07/09
new-side values are still the F10-2 *declared* targets, DEV-08).

Usage (from the repository root; everything executes in a hash-gated sandbox copy, never in the working tree):
    python3 -B docs/16-repo-validation/evidence/s16_observe.py --sandbox-root <dir outside the repo> --out <json>
Read-only for the repository: it imports only tests/characterization/harness.py (sandbox guard + fixture gate),
builds <sandbox-root>/c_pristine from the working tree code + the Stage 0A backup data, and runs the hub CLIs there.
Synthetic data, unvalidated - method validation only.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time

REPO = os.path.realpath(os.environ.get("S16_REPO") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tests", "characterization"))
os.environ.setdefault("CHAR_WORKTREE_ROOT", REPO)
import harness  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = harness.assert_safe_sandbox(a.sandbox_root)
    t0 = time.time()
    pristine = harness.build_pristine(root, "c_pristine")
    work = os.path.join(root, "work")
    os.makedirs(work, exist_ok=True)
    env = harness.child_env({"HUB_WORKTREE_ROOT": REPO, "PYTHONHASHSEED": "0"})
    cfg_path = os.path.join(work, "hub-config.json")
    with open(cfg_path, "w") as f:
        json.dump({"audit": {"anchor_path": os.path.join(work, "anchor", "audit-anchor.json"), "anchor_every": 100}}, f)
    obs = {"label": "synthetic, unvalidated - method validation only", "steps": {}}

    def run(mod, args, cfg=True):
        cmd = [sys.executable, "-B", "-m", mod] + (["--config", cfg_path] if cfg else []) + args
        p = subprocess.run(cmd, cwd=pristine, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, timeout=600)
        try:
            out = json.loads(p.stdout) if p.stdout.strip() else None
        except ValueError:
            out = p.stdout[-3000:]
        key = "%s %s" % (mod, args[0])
        obs["steps"].setdefault(key, []).append({"rc": p.returncode, "stderr_tail": p.stderr[-400:] if p.returncode else ""})
        return p.returncode, out

    legacy_db = os.path.join(pristine, "data", "legacy.sqlite3")
    ent_db = os.path.join(pristine, "data", "enterprise_legacy.sqlite3")
    pre = {n: sha(os.path.join(pristine, "data", n)) for n in sorted(os.listdir(os.path.join(pristine, "data")))
           if n.endswith(".sqlite3")}

    # 1. golden-compare at HEAD (TG-4 step 2 as built)
    rc, gc = run("hub", ["golden-compare", "--data-dir", os.path.join(work, "gc"), "--legacy-root", pristine, "--json"], cfg=False)
    obs["golden_compare"] = {"rc": rc, "report": gc}

    # 2. full store: M001..M007
    data, bk, rdir = os.path.join(work, "data"), os.path.join(work, "bk"), os.path.join(work, "run")
    for mod in ("hub.admin", "hub.policy", "hub.decision", "hub.intake", "hub.runs", "hub.web", "hub.search"):
        run(mod, ["migrate", "--data-dir", data, "--backup-root", bk])
    run("hub.policy", ["seed", "--data-dir", data])
    rc, lf = run("hub.policy", ["load-as-found", "--data-dir", data, "--legacy-root", pristine, "--run-dir", rdir])
    obs["load_as_found"] = lf
    rc, bf = run("hub.decision", ["backfill", "--data-dir", data, "--legacy-root", pristine, "--run-dir", rdir])
    obs["backfill"] = bf if not isinstance(bf, dict) else {k: bf[k] for k in bf if k in ("imported", "cases", "count", "status", "summary")} or bf

    # DV-05 / DV-06 / DEV-29: policy evaluation through the CLI (explicit as-found ruleset ref; nothing is active)
    ev = {}
    for name, inp in (("APAC_2019", {"amount": 0, "region": "APAC", "year": 2019}),
                      ("APAC_2026_abc", {"amount": "abc", "region": "APAC", "year": 2026}),
                      ("APAC_2026_null", {"amount": None, "region": "APAC", "year": 2026}),
                      ("APAC_202_partial", {"amount": 0, "region": "APAC", "year": 202})):
        rc, out = run("hub.policy", ["evaluate", "--data-dir", data, "--function", "AMOUNT_LIMIT", "--input", json.dumps(inp),
                                     "--ruleset-ref", "as-found-js@1"])
        ev[name] = {"rc": rc, "out": out}
    rc, out = run("hub.policy", ["evaluate", "--data-dir", data, "--function", "AMOUNT_LIMIT", "--input",
                                 json.dumps({"amount": 0, "region": "APAC", "year": 2026})])
    ev["no_ref_no_active"] = {"rc": rc, "out": out}
    obs["policy_evaluate"] = ev

    # DV-02 / DV-03 / DV-04 / DV-07 / DV-09: shadow intake of the shipped sources
    lsha0 = sha(legacy_db)
    rc, ing = run("hub.intake", ["ingest-legacy", "--data-dir", data, "--legacy-root", pristine, "--run-dir", rdir, "--csv-tier", "tiny"])
    obs["ingest"] = {"rc": rc, "runs": (ing or {}).get("runs") if isinstance(ing, dict) else ing,
                     "counts": (ing or {}).get("counts") if isinstance(ing, dict) else None,
                     "legacy_db_sha256_before": lsha0, "legacy_db_sha256_after": sha(legacy_db)}
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(data, "hub.sqlite3"), uri=True)
    try:
        cols = [r[1] for r in con.execute("PRAGMA table_info(raw_intake)")]
        src_col = "source" if "source" in cols else cols[1]
        q = ("SELECT r.%s, o.outcome, o.primary_reason, count(*) FROM raw_intake r JOIN intake_outcome o ON o.raw_id = r.raw_id "
             "WHERE o.outcome_seq = (SELECT max(outcome_seq) FROM intake_outcome x WHERE x.raw_id = r.raw_id) "
             "GROUP BY 1,2,3 ORDER BY 1,2,3" % src_col)
        obs["intake_current_outcomes"] = [list(r) for r in con.execute(q)]
        obs["intake_reason_mentions"] = {k: con.execute("SELECT count(DISTINCT raw_id) FROM intake_outcome WHERE all_reasons LIKE ?",
                                                        ("%" + k + "%",)).fetchone()[0]
                                         for k in ("NEGATIVE_VALUE", "UNPARSABLE_AMOUNT", "BLANK_AMOUNT", "REVISED_CONFLICT",
                                                   "MISSING_ENVELOPE_FIELD", "QUANTITY")}
    except sqlite3.Error as e:
        obs["intake_query_error"] = str(e)
    finally:
        con.close()
    lc = sqlite3.connect("file:%s?mode=ro" % legacy_db, uri=True)
    try:
        obs["legacy_partner_status_after_hub_intake"] = [list(r) for r in lc.execute(
            "SELECT processing_status, count(*) FROM partner_feeds GROUP BY 1 ORDER BY 1")]
    except sqlite3.Error as e:
        obs["legacy_partner_status_after_hub_intake"] = "error: %s" % e
    finally:
        lc.close()

    # DV-01: month-end total from the metric service
    rc, me = run("hub.metrics", ["month-end", "--data-dir", data, "--cutoff", "2030-01-01T00:00:00.000000Z",
                                 "--denominator", "cases:125 (FX-BASE125)", "--legacy-root", pristine, "--run-dir", rdir])
    obs["month_end"] = {"rc": rc, "out": me}
    # INC-09 divergence over the 125 shipped cases with the as-found rule sets loaded
    rc, dv = run("hub.r2", ["divergence", "--data-dir", data, "--legacy-root", pristine])
    obs["divergence"] = {"rc": rc, "out": dv}
    rc, va = run("hub.admin", ["verify-audit", "--data-dir", data])
    obs["verify_audit_rc"] = rc
    obs["fixture_sha256_unchanged"] = all(sha(os.path.join(pristine, "data", n)) == h for n, h in pre.items())
    obs["fixture_sha256"] = pre
    obs["python"] = sys.version.split()[0]
    obs["sqlite"] = sqlite3.sqlite_version
    obs["seconds"] = round(time.time() - t0, 1)
    with open(a.out, "w") as f:
        json.dump(obs, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({"out": a.out, "seconds": obs["seconds"]}))


if __name__ == "__main__":
    main()
