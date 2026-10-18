"""Evaluators for the gates INC-03 can check mechanically (G3, G5, G6, G7). The others (G1 needs approved
deviations - OD-S12-13 open, G2/G4/G8/G9 need modules from INC-04+, G10 is a test-suite gate) are recorded
not_run / fail by the caller with their evidence path - never assumed 'pass'."""
import os

from hub.guards import no_ai, sandbox
from hub.obs import metrics
from hub.ops import backup as backup_mod
from hub.security import audit, scan
from hub.store import db


def g3_verify_audit(con, anchor_path):
    rep = audit.verify(con, anchor_path)
    return {"result": "pass" if rep["status"] == "ok" else "fail", "evidence": rep}


def g5_no_ai():
    findings = no_ai.scan(no_ai.default_targets(sandbox.PACKAGE_ROOT))
    trip = metrics.tripwires()
    ok = not findings and all(v == 0 for v in trip.values())
    return {"result": "pass" if ok else "fail", "evidence": {"denylist_findings": findings, "tripwires": trip}}


def g6_scan(con):
    rep = scan.run(sandbox.PACKAGE_ROOT, con)
    return {"result": "pass" if rep["clean"] else "fail", "evidence": rep}


def g7_backup_restore(data_dir, anchor_path, scratch_root, clock):
    """Back up the live store + anchor, restore into a scratch data dir + scratch anchor, compare checksums and
    verify the audit chain of the restored copy against the restored anchor."""
    label = "g7-" + backup_mod._stamp(clock())
    bk = backup_mod.backup(data_dir, anchor_path, os.path.join(scratch_root, "backups"), label, clock)
    rdata = os.path.join(scratch_root, "restore-" + label, "data")
    ranchor = os.path.join(scratch_root, "restore-" + label, "anchor", backup_mod.ANCHOR_NAME)
    rep = backup_mod.restore(bk["path"], rdata, ranchor, clock)
    con = db.open_hub(rdata)
    try:
        ver = audit.verify(con, ranchor)
    finally:
        con.close()
    ok = rep["checksum_match"] and ver["status"] == "ok"
    return {"result": "pass" if ok else "fail", "evidence": {"backup": bk["label"], "restore": rep, "verify_audit": ver}}
