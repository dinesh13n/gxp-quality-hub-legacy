"""Hash-chained, insert-only audit trail with an out-of-DB anchor (ADR-005, BEH-SEC-05/06, SCH-AUDIT).

record  = {audit_seq, occurred_at, actor, actor_kind, action, object_ref, outcome, reason, correlation_id, details}
hash    = sha256(prev_hash || canonical(record))       (prev_hash of seq 1 = 64 x "0")
anchor  = JSON lines {audit_seq, hash, occurred_at} appended to audit.anchor_path every audit.anchor_every
          records and at the end of every run (`write_anchor`).
`change()` writes the change and its audit record in ONE transaction: if the audit insert fails the change is
rolled back and E-SEC-AUDIT-WRITE-FAILED is raised (AC-SEC-14). `details` never carries credentials
(BEH-SEC-07): credential-like keys are refused (E-SEC-SECRET-IN-AUDIT).
Known limitation (R-SEC-1, AC-SEC-12): records appended after the last anchor and then removed are not
detectable by `verify`.
"""
import contextlib
import json
import os
import sqlite3

from hub.security.canonical import GENESIS, canonical, sha256_hex
from hub.security.errors import AuditWriteFailed, SecretInAudit

FIELDS = ("audit_seq", "occurred_at", "actor", "actor_kind", "action", "object_ref", "outcome", "reason",
          "correlation_id", "details")
FORBIDDEN_KEY_PARTS = ("password", "passwd", "secret", "token", "pw_hash", "pw_salt", "credential", "api_key",
                       "apikey", "authorization", "cookie", "private_key")
LIMITATION = "records appended after the last anchor and then deleted are not detectable (residual risk R-SEC-1)"


class Anchor(object):
    def __init__(self, path, every=100):
        self.path, self.every = path, int(every)


def _check_details(obj, path="details"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if any(part in lk for part in FORBIDDEN_KEY_PARTS):
                raise SecretInAudit({"key": "%s.%s" % (path, k)})
            _check_details(v, "%s.%s" % (path, k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_details(v, "%s[%d]" % (path, i))


def record_hash(prev_hash, record):
    return sha256_hex(prev_hash + canonical(record))


def head(con):
    row = con.execute("SELECT audit_seq, hash, occurred_at FROM audit_log ORDER BY audit_seq DESC LIMIT 1").fetchone()
    return (0, GENESIS, None) if row is None else (row[0], row[1], row[2])


def _insert(con, clock, actor, actor_kind, action, outcome, correlation_id, object_ref=None, reason=None, details=None):
    details = dict(details or {})
    _check_details(details)
    seq, prev, _ = head(con)
    rec = {"audit_seq": seq + 1, "occurred_at": clock(), "actor": actor, "actor_kind": actor_kind, "action": action,
           "object_ref": object_ref, "outcome": outcome, "reason": reason, "correlation_id": correlation_id,
           "details": details}
    h = record_hash(prev, rec)
    con.execute("INSERT INTO audit_log(audit_seq, occurred_at, actor, actor_kind, action, object_ref, outcome, reason,"
                " correlation_id, details, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (rec["audit_seq"], rec["occurred_at"], actor, actor_kind, action, object_ref, outcome, reason,
                 correlation_id, canonical(details), prev, h))
    rec.update(prev_hash=prev, hash=h)
    return rec


class _Ctx(object):
    def __init__(self, fields):
        self.fields = fields
        self.record = None


@contextlib.contextmanager
def change(con, clock, anchor=None, **fields):
    """with change(con, clock, actor=..., actor_kind=..., action=..., outcome=..., correlation_id=...) as ctx:
           con.execute(<the change>)          # ctx.fields may be adjusted (e.g. outcome, details)
    The change and its audit record commit together; audit failure -> rollback + E-SEC-AUDIT-WRITE-FAILED."""
    if con.in_transaction:
        raise RuntimeError("audit.change needs a connection with no open transaction")
    con.execute("BEGIN IMMEDIATE")
    ctx = _Ctx(dict(fields))
    try:
        yield ctx
    except BaseException:
        con.rollback()
        raise
    try:
        ctx.record = _insert(con, clock, **ctx.fields)
    except SecretInAudit:
        con.rollback()
        raise
    except sqlite3.Error as e:
        con.rollback()
        raise AuditWriteFailed({"action": ctx.fields.get("action"), "sqlite": str(e)})
    con.commit()
    if anchor is not None and ctx.record["audit_seq"] % anchor.every == 0:
        write_anchor(con, anchor.path)
    return


def append(con, clock, anchor=None, **fields):
    """Append one audit record in its own transaction (an event with no other state change)."""
    with change(con, clock, anchor=anchor, **fields) as ctx:
        pass
    return ctx.record


def read_anchors(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                a = json.loads(line)
                out.append({"audit_seq": int(a["audit_seq"]), "hash": str(a["hash"]), "occurred_at": a.get("occurred_at"),
                            "line": n})
    return out


def write_anchor(con, path):
    """Append the current head to the anchor file (no-op if empty chain or already anchored at this head)."""
    seq, h, ts = head(con)
    if seq == 0:
        return None
    anchors = read_anchors(path)
    if anchors and anchors[-1]["audit_seq"] == seq and anchors[-1]["hash"] == h:
        return anchors[-1]
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    line = canonical({"audit_seq": seq, "hash": h, "occurred_at": ts})
    # Stage 27 S27-DEV-14: a NEW anchor file is created owner-only (0600); an existing file keeps its mode. Content and fsync are unchanged.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600), "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    return {"audit_seq": seq, "hash": h, "occurred_at": ts}


def _row_record(row):
    rec = dict(zip(FIELDS, row[:10]))
    rec["details"] = json.loads(rec["details"])
    return rec


def verify(con, anchor_path=None):
    """Recompute the chain from seq 1 and check every anchored head. Returns a report dict:
    status 'ok' or 'broken' with first_broken_seq and kind in
    {altered_record, missing_record, reordered, head_mismatch, anchor_unreadable}."""
    rows = con.execute("SELECT " + ", ".join(FIELDS) + ", prev_hash, hash FROM audit_log ORDER BY audit_seq").fetchall()
    n = len(rows)

    def broken(seq, kind, **extra):
        r = {"status": "broken", "first_broken_seq": seq, "kind": kind, "records": n, "limitation": LIMITATION}
        r.update(extra)
        return r

    prev, expected, by_seq = GENESIS, 1, {}
    for row in rows:
        seq, prev_hash, stored = row[0], row[10], row[11]
        if seq != expected:
            return broken(expected, "missing_record")
        try:
            rec = _row_record(row)
        except ValueError:
            return broken(seq, "altered_record", detail="details is not JSON")
        if prev_hash != prev or record_hash(prev_hash, rec) != stored:
            if prev_hash != prev:
                for s in range(1, n + 2):  # does the row verify under another position? -> moved
                    if s != seq and record_hash(prev_hash, dict(rec, audit_seq=s)) == stored:
                        return broken(seq, "reordered", original_seq=s)
            return broken(seq, "altered_record")
        by_seq[seq] = stored
        prev, expected = stored, expected + 1
    try:
        anchors = read_anchors(anchor_path)
    except (ValueError, KeyError, TypeError, AttributeError) as e:  # S30-DEV-01: a line that is valid JSON but not an object raised TypeError and escaped
        return broken(None, "anchor_unreadable", detail=str(e)[:200])
    for a in anchors:
        if by_seq.get(a["audit_seq"]) != a["hash"]:
            return broken(a["audit_seq"], "head_mismatch", anchor_line=a["line"],
                          chain_head=(rows[-1][0] if rows else 0))
    return {"status": "ok", "records": n, "head_seq": rows[-1][0] if rows else 0,
            "head_hash": prev, "anchors_checked": len(anchors), "limitation": LIMITATION}
