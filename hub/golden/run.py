"""Orchestrates one golden-compare run: guarded data dir, hub store (M000 + register), read-only snapshots,
new-side observations, comparison. The run directory is <data_dir>/runs/golden-compare (recreated each run,
deleted only inside the guarded data directory)."""
import json
import os
import shutil

from hub.adapters import legacy_sqlite
from hub.adapters.legacy_captures import CaptureSet, DEFAULT_GOLDEN_DIR
from hub.coexistence import register
from hub.golden import baseline_probes, compare
from hub.guards import sandbox
from hub.store import db


def run(data_dir, legacy_root=None, probes_path=None, golden_dir=None, observations_path=None):
    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    if legacy_root:
        sandbox.assert_safe_path(legacy_root, "legacy source root")
    probes = compare.load_probes(probes_path or compare.PROBES_PATH)
    captures = CaptureSet.from_golden_dir(golden_dir or DEFAULT_GOLDEN_DIR)
    con = db.open_hub(data_dir)
    try:
        rows = register.rows(con)
    finally:
        con.close()
    new_values = {}
    ro_names = sorted(set(p["new"]["query"] for p in probes if p["new"]["provider"] == "baseline_ro"))
    handles = {}
    baseline = {}
    if ro_names:
        if not legacy_root:
            err = ValueError("--legacy-root is required for baseline_ro probes")
            for p in probes:
                if p["new"]["provider"] == "baseline_ro":
                    new_values[p["golden_ref"]] = err
        else:
            run_dir = os.path.join(data_dir, "runs", "golden-compare")
            if os.path.exists(run_dir):
                sandbox.assert_safe_path(run_dir, "run directory")
                for d, _, fns in os.walk(run_dir):
                    for fn in fns:
                        os.chmod(os.path.join(d, fn), 0o644)
                shutil.rmtree(run_dir)
            os.makedirs(run_dir)
            for store in baseline_probes.stores_needed(ro_names):
                handles[store] = legacy_sqlite.open_snapshot(legacy_root, store, run_dir, pinned=True)
                baseline[store] = handles[store].provenance
    try:
        for p in probes:
            spec = p["new"]
            if spec["provider"] == "declared":
                new_values[p["golden_ref"]] = (spec["value"], "declared:%s (target; owning module not built yet)" % spec.get("basis", "F10-2"))
            elif spec["provider"] == "baseline_ro" and handles:
                new_values[p["golden_ref"]] = (baseline_probes.run(spec["query"], handles),
                                               "baseline_ro:%s (read-only snapshot)" % spec["query"])
    finally:
        for h in handles.values():
            h.close()
    if observations_path:  # test seam: substitute new-side observations (simulates a changed new module)
        with open(observations_path, encoding="utf-8") as f:
            for ref, value in sorted(json.load(f).items()):
                new_values[ref] = (value, "observation-override")
    report = compare.compare(probes, captures, new_values, rows)
    report["baseline"] = baseline
    return report
