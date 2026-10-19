"""Rule-output registry and flag ids (BEH-GATE-08, FR-GATE-06, PNFR-15, AC-GATE-20; INC-08).

Every rule-generated item a human can see has a `flag_id`:
  FLG-RT-nnnnnnnn          a stored rule trace (hub.review.trace) of function PRIORITY, MANUAL_REVIEW, AMOUNT_LIMIT or SHIFT_FLAG
  FLG-IQ-<raw_id>-<seq>    an intake outcome row that put an item into an exception queue (queue assignment)
`OUTPUT_REGISTRY` lists every output type; the automated test iterates it. Read-only helpers only (no write here); the write is
DispositionService.act_on_flag.
"""
import re

from hub.review.errors import ReviewNotFound

QUEUES = ("quarantine_invalid", "revision_review", "unmatched", "ambiguous_match", "flagged_value")
FUNCTIONS = ("PRIORITY", "MANUAL_REVIEW", "AMOUNT_LIMIT", "SHIFT_FLAG")
OUTPUT_REGISTRY = tuple(
    [{"output_type": "rule_%s" % f.lower(), "flag_kind": "rule_trace", "function": f, "flag_id_form": "FLG-RT-nnnnnnnn"} for f in FUNCTIONS] +
    [{"output_type": "queue_%s" % q, "flag_kind": "intake_queue", "queue": q, "flag_id_form": "FLG-IQ-<raw_id>-<seq>"} for q in QUEUES])
ACTIONS = ("override", "dismiss", "refuse")
_RT = re.compile(r"^FLG-RT-([0-9]{8})$")
_IQ = re.compile(r"^FLG-IQ-(RAW-[0-9]{10})-([0-9]{1,6})$")


def trace_flag_id(number):
    return "FLG-RT-%08d" % number


def intake_flag_id(raw_id, seq):
    return "FLG-IQ-%s-%d" % (raw_id, seq)


def resolve(con, flag_id):
    """{flag_id, flag_kind, case_id (or None), ...} for a known flag; E-REV-NOT-FOUND otherwise (also for a malformed id)."""
    m = _RT.match(flag_id) if isinstance(flag_id, str) else None
    if m:
        row = con.execute('SELECT trace_id, case_id, "function" FROM rule_trace WHERE flag_id = ?', (flag_id,)).fetchone()
        if row:
            return {"flag_id": flag_id, "flag_kind": "rule_trace", "case_id": row[1], "trace_id": row[0], "function": row[2]}
    m = _IQ.match(flag_id) if isinstance(flag_id, str) else None
    if m:
        row = con.execute("SELECT o.raw_id, o.outcome_seq, o.queue, o.matched_link FROM intake_outcome o WHERE o.raw_id = ? AND o.outcome_seq = ?"
                          " AND o.queue IS NOT NULL", (m.group(1), int(m.group(2)))).fetchone()
        if row:
            case_id = None
            if row[3]:
                l = con.execute("SELECT from_type, from_id, to_type, to_id FROM crosswalk_link WHERE link_id = ?", (row[3],)).fetchone()
                if l:
                    case_id = l[1] if l[0] == "case" else (l[3] if l[2] == "case" else None)
            return {"flag_id": flag_id, "flag_kind": "intake_queue", "case_id": case_id, "raw_id": row[0], "queue": row[2]}
    raise ReviewNotFound({"flag_id": str(flag_id)[:60]})
