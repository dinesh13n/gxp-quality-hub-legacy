"""The Stage 30 release register: what a release and each cutover step would need (docs/30-release/go-no-go-criteria.md, release-approvals.md).

Technical criteria are evidence: each one is recorded as pass / fail / not_run with an evidence path (docs/30-release/evidence/gate-results.json).
Approvals are HUMAN decisions: each one is a record in docs/30-release/evidence/approvals-register.json that ships OPEN. This module defines the ids and
which approvals each step needs; it records nothing and approves nothing. Every default is an AGENT ASSUMPTION (OD-32) until Dinesh Naik confirms it.

Cutover steps and their DV rows follow docs/14-transformation/cutover-plan.md CO-1 and docs/17-implementation-prd/implementation-prd.md (DV-10, DV-11 proposed).
"""
from hub.ops import release as ops_release

GATE_IDS = ops_release.GATE_IDS
DV_IDS = tuple("DV-%02d" % i for i in range(1, 12))

TECHNICAL = (
    ("T-01", "backup manifest of the legacy baseline verifies (rc 0) before and after every rehearsal"),
    ("T-02", "L1 code revert rehearsed on a sandbox clone"),
    ("T-03", "L2 hub-state backup / restore rehearsed on a sandbox copy"),
    ("T-04", "L3 authority flip and flip back rehearsed on a sandbox copy, audit chain verifies"),
    ("T-05", "full hub regression: every group green and executed = expected"),
    ("T-06", "characterization harness: no failure except the registered CT-13 Node drift"),
    ("T-07", "shipped configuration posture: shadow, empty Zone H holders, loopback, schedule off, synthetic data"),
    ("T-08", "F-29-01 fixed with a test (verify-audit exits 17 on a malformed anchor line)"),
    ("T-09", "monitoring coverage for the release window: persisted metrics, alert delivery and an owner"),
    ("T-10", "every High vulnerability and every open High finding has a recorded decision by the Engagement lead"),
)
TECHNICAL_IDS = GATE_IDS + tuple(t for t, _ in TECHNICAL)

CUT_STEPS = (
    {"id": "CUT-1", "capability": "decision and evidence record, audit", "dv": (),
     "decisions": ("OD-S12-01", "OD-S12-03", "OD-S12-07", "OD-S12-15", "OD-S12-16", "OD-S12-19")},
    {"id": "CUT-2", "capability": "rule evaluation", "dv": ("DV-05", "DV-06", "DV-11"), "decisions": ("OD-S12-04", "OD-S12-13", "HAR-06")},
    {"id": "CUT-3", "capability": "intake and reconcile outcomes", "dv": ("DV-02", "DV-03", "DV-07", "DV-09", "DV-10"),
     "decisions": ("OD-S12-11", "OD-S12-13", "HAR-06", "stop the in-place legacy reconcile")},
    {"id": "CUT-4", "capability": "metrics, month-end and night-shift figures", "dv": ("DV-01", "DV-04", "DV-08"),
     "decisions": ("OD-S12-01", "OD-S12-02", "OD-S12-08", "OD-S12-13", "HAR-06")},
    {"id": "CUT-5", "capability": "automation and exposure", "dv": (), "decisions": ("OD-S12-10", "HAR-10", "HAR-05")},
)
CUT_IDS = tuple(c["id"] for c in CUT_STEPS)

# (id, what the human decides, scope: "REL" = needed for any release, or the CUT ids that need it)
OPS_APPROVALS = (
    ("AP-OPS-01", "target host and promotion path named and approved (environment-promotion-plan.md)", "REL"),
    ("AP-OPS-02", "rollback authority, rollback triggers and who may call them", "REL"),
    ("AP-OPS-03", "cutover window, change freeze and communications", "REL"),
    ("AP-OPS-04", "off-device copy of the baseline and the hub backups (HAR-09, F-29-02)", "REL"),
    ("AP-OPS-05", "monitoring owner and alert channel for the release window (D-31-08, F-29-03)", "REL"),
    ("AP-OPS-06", "manual walkthroughs TST-REV-03 / 04 / 08 signed or explicitly left open (D-27-08)", "REL"),
    ("AP-OPS-07", "runtime floor and Python 3.12+ evidence (D-27-02)", "REL"),
    ("AP-OPS-08", "install the hardening CI file under .github with pinned SHAs, or not (D-27-03, HAR-07)", "REL"),
    ("AP-OPS-09", "legacy Dockerfile / compose hardening, or leave the legacy files as they are (D-27-06)", "REL"),
    ("AP-OPS-10", "wire the Stage 28 / 31 mechanisms before release, or release without them (D-28-01, D-28-02, D-31-01, D-31-02)", "REL"),
    ("AP-OPS-11", "residual risks RS / RP / VA / RTR / F-xx accepted, rejected or carried (none is accepted by any stage)", "REL"),
    ("AP-OPS-12", "consumers of the legacy outputs identified and a re-pointing owner named (U-14-01)", ("CUT-2", "CUT-3", "CUT-4")),
    ("AP-OPS-13", "real Zone H holders named, only if the Zone H gate is to be used (OD-S12-05 / 06, HAR-12)", ("CUT-1",)),
)


def approval_ids():
    ids = ["AP-REL-01"]
    ids += ["AP-GATE-" + g for g in GATE_IDS]
    ids += ["AP-" + d for d in DV_IDS]
    ids += ["AP-" + c for c in CUT_IDS]
    ids += [a for a, _, _ in OPS_APPROVALS]
    return tuple(ids)


def required_for_release():
    """Approvals every release needs: the release decision, a human acknowledgement of each gate's evidence, and the REL operational decisions."""
    return ("AP-REL-01",) + tuple("AP-GATE-" + g for g in GATE_IDS) + tuple(a for a, _, s in OPS_APPROVALS if s == "REL")


def required_for_step(step_id):
    step = [c for c in CUT_STEPS if c["id"] == step_id][0]
    ops = [a for a, _, s in OPS_APPROVALS if s != "REL" and step_id in s]
    return ("AP-" + step_id,) + tuple("AP-" + d for d in step["dv"]) + tuple(ops)
