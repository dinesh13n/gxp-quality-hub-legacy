"""Pre-release checklist G1-G10 (docs/12-specs/features/f10-coexistence-change-safety.md F10-3; AC-CO-10, AC-CO-15).

record_checklist(): records EVERY gate with result pass / fail / not_run and a non-empty evidence path (a gate with
                    no supplied result is recorded not_run). Insert-only rows, audited (RELEASE_CHECKLIST).
mark_ready():       refuses (E-CO-RELEASE-BLOCKED, audited RELEASE_READY denied) unless all 10 gates are 'pass';
                    the DB trigger release_record_ready_requires_all_gates enforces the same rule as a backstop.
"""
from hub.security import audit
from hub.security.errors import ReleaseBlocked

GATES = (
    ("G1", "golden diff: unapproved differences = 0", "FR-CO-01"),
    ("G2", "replay-safety suite (AC-INT-04/05) passes", "FR-CO-03, FR-INT-02"),
    ("G3", "verify-audit ok", "FR-SEC-02"),
    ("G4", "verify-projection 0 mismatches", "FR-DEC-02"),
    ("G5", "No-AI tripwire: deny-list clean, no egress, model_calls_total = 0", "FR-CO-04"),
    ("G6", "secret scan 0; deletion-path grep 0", "PNFR-08, PNFR-10"),
    ("G7", "backup/restore rehearsal checksum match", "PNFR-05, FR-CO-03"),
    ("G8", "Zone H negative tests (AC-GATE-09/11/12) pass", "FR-GATE-01/03"),
    ("G9", "planted-string fixture suite (86/22/44) 0 effects", "PNFR-13"),
    ("G10", "determinism: bit-identical across PYTHONHASHSEED/TZ/locale", "PNFR-17"),
)
GATE_IDS = tuple(g for g, _, _ in GATES)
RESULTS = ("pass", "fail", "not_run")
NOT_RUN_EVIDENCE = "none (gate not run in this build)"


def record_checklist(con, clock, release_id, results, actor, correlation_id, anchor=None):
    rows = []
    for gate, check, source in GATES:
        r = dict(results.get(gate) or {})
        result = r.get("result", "not_run")
        if result not in RESULTS:
            raise ValueError("bad result %r for %s" % (result, gate))
        evidence = (r.get("evidence_path") or "").strip() or NOT_RUN_EVIDENCE
        rows.append({"gate": gate, "check": check, "source": source, "result": result, "evidence_path": evidence,
                     "note": r.get("note")})
    blocking = [x["gate"] for x in rows if x["result"] != "pass"]
    now = clock()
    with audit.change(con, clock, anchor=anchor, actor=actor, actor_kind="human", action="RELEASE_CHECKLIST",
                      outcome="success", correlation_id=correlation_id, object_ref="release:" + release_id,
                      details={"results": {x["gate"]: x["result"] for x in rows}, "blocking": blocking}):
        con.execute("INSERT INTO release_record(release_id, created_at, status) VALUES (?,?,'candidate')", (release_id, now))
        for x in rows:
            con.execute("INSERT INTO release_gate_result(release_id, gate, result, evidence_path, note, recorded_at)"
                        " VALUES (?,?,?,?,?,?)", (release_id, x["gate"], x["result"], x["evidence_path"], x["note"], now))
    return {"release_id": release_id, "gates": rows, "blocking": blocking, "ready_allowed": not blocking}


def checklist(con, release_id):
    rows = con.execute("SELECT gate, result, evidence_path, note FROM release_gate_result WHERE release_id = ?",
                       (release_id,)).fetchall()
    order = {g: i for i, g in enumerate(GATE_IDS)}
    status = con.execute("SELECT status FROM release_record WHERE release_id = ?", (release_id,)).fetchone()
    return {"release_id": release_id, "status": status[0] if status else None,
            "gates": [{"gate": g, "result": r, "evidence_path": e, "note": n}
                      for g, r, e, n in sorted(rows, key=lambda x: order[x[0]])]}


def mark_ready(con, clock, release_id, actor, correlation_id, anchor=None):
    cl = checklist(con, release_id)
    blocking = [g["gate"] for g in cl["gates"] if g["result"] != "pass"]
    missing = [g for g in GATE_IDS if g not in {x["gate"] for x in cl["gates"]}]
    if cl["status"] is None or blocking or missing:
        audit.append(con, clock, anchor=anchor, actor=actor, actor_kind="human", action="RELEASE_READY",
                     outcome="denied", correlation_id=correlation_id, object_ref="release:" + release_id,
                     details={"blocking": blocking, "missing": missing})
        raise ReleaseBlocked({"release_id": release_id, "blocking": blocking, "missing": missing})
    with audit.change(con, clock, anchor=anchor, actor=actor, actor_kind="human", action="RELEASE_READY",
                      outcome="success", correlation_id=correlation_id, object_ref="release:" + release_id):
        con.execute("UPDATE release_record SET status = 'ready' WHERE release_id = ?", (release_id,))
    return checklist(con, release_id)
