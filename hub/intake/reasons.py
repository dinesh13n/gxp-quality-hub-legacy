"""Reason-code catalogue (SCH-REASON, schema-specifications.md SC-3) and the fixed precedence (SBR-INT-03). Pure, no I/O.

Classification is a pure deterministic function of the reason set (BEH-INT-07, PNFR-17): the first applicable code in PRECEDENCE is the
primary reason, all applicable codes are listed in precedence order, exactly one queue (the primary reason's), and the outcome follows the
class of the primary reason (QUARANTINE -> QUARANTINED, EXCEPTION -> EXCEPTION, FLAG -> VALIDATED_WITH_FLAGS, none -> VALIDATED).
The precedence list is class-monotone (all QUARANTINE codes, then EXCEPTION, then FLAG), so the primary reason always carries the highest class.
"""
Q, E, F = "QUARANTINE", "EXCEPTION", "FLAG"

PRECEDENCE = (
    "UNSUPPORTED_REVISION", "INVALID_JSON", "MISSING_ENVELOPE_FIELD", "UNKNOWN_RECORD_KIND", "MISSING_PAYLOAD_FIELD",
    "CONTRACT_VIOLATION", "REVISED_CONFLICT", "UNPARSABLE_AMOUNT", "NO_BUSINESS_KEY", "AMBIGUOUS_MATCH", "UNMATCHED_REF",
    "NEGATIVE_VALUE", "UNKNOWN_UNIT", "UNKNOWN_CURRENCY", "IDENTIFIER_PATTERN",
)
CATALOG = {
    "UNSUPPORTED_REVISION": (Q, "quarantine_invalid"), "INVALID_JSON": (Q, "quarantine_invalid"),
    "MISSING_ENVELOPE_FIELD": (Q, "quarantine_invalid"), "UNKNOWN_RECORD_KIND": (Q, "quarantine_invalid"),
    "MISSING_PAYLOAD_FIELD": (Q, "quarantine_invalid"), "CONTRACT_VIOLATION": (Q, "quarantine_invalid"),
    "REVISED_CONFLICT": (Q, "revision_review"), "UNPARSABLE_AMOUNT": (Q, "quarantine_invalid"),
    "NO_BUSINESS_KEY": (E, "unmatched"), "AMBIGUOUS_MATCH": (E, "ambiguous_match"), "UNMATCHED_REF": (E, "unmatched"),
    "NEGATIVE_VALUE": (F, "flagged_value"), "UNKNOWN_UNIT": (F, "flagged_value"), "UNKNOWN_CURRENCY": (F, "flagged_value"),
    "IDENTIFIER_PATTERN": (F, "flagged_value"),
}
OUTCOME_OF_CLASS = {Q: "QUARANTINED", E: "EXCEPTION", F: "VALIDATED_WITH_FLAGS"}
QUEUES = ("quarantine_invalid", "revision_review", "unmatched", "ambiguous_match", "flagged_value")
# Reasons that stop the matching step (SBR-INT-04: match runs after validation; a quarantined item is not linked, and an item
# without business_key is never auto-linked, DC-02).
NO_MATCH_REASONS = frozenset([c for c in PRECEDENCE if CATALOG[c][0] == Q] + ["NO_BUSINESS_KEY"])


def classify(reasons):
    """reasons: iterable of reason codes -> {outcome, primary_reason, all_reasons, queue}."""
    unknown = sorted(set(reasons) - set(PRECEDENCE))
    if unknown:
        raise ValueError("unknown reason code(s): %s" % unknown)
    codes = [c for c in PRECEDENCE if c in set(reasons)]
    if not codes:
        return {"outcome": "VALIDATED", "primary_reason": None, "all_reasons": [], "queue": None}
    cls, queue = CATALOG[codes[0]]
    return {"outcome": OUTCOME_OF_CLASS[cls], "primary_reason": codes[0], "all_reasons": codes, "queue": queue}
