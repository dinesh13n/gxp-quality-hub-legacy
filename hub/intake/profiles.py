"""Per-source intake profiles: envelope mapping, closed value sets and checks (DC-01..DC-05, BEH-INT-05/11) as DATA.

Closed sets are the OBSERVED sets of the synthetic data (A-12-F04-2 / A-11-03): Assumptions, changeable by a reviewed edit of this file.
`None` for a set means "not constrained". `match` is the crosswalk rule-link code used for BEH-INT-08 (only the partner feed has a
registered feed-item -> case link type, LT-04; other sources are not matched and never get UNMATCHED_REF). `contract` is the bundled
declared-contract file the L3 check evaluates (default binding mode record_only for every source, SBR-INT-07).
Source names: partner_feed (legacy partner_feeds, AD-03), source_message (legacy source_messages, source column `external-feed`, DM-4),
gateway (AD-04 / legacy gateway_inbox), vendor_csv (AD-05).
"""
UNITS = ("lb", "kg", "hour", "each", "percent", "ppm")
CURRENCIES = ("USD", "GBP", "INR", "JPY", "EUR")

PROFILES = {
    "partner_feed": {
        "envelope_required": ("source_key", "partner", "schema_rev", "source_ts", "ref_id", "record_kind", "payload_text"),
        "envelope_names": {"source_key": "feed_id", "payload_text": "raw_json"},
        "schema_revs": ("1.0", "1.1", "2.0"), "record_kinds": ("OOS_RESULT", "DEVIATION", "CAPA_UPDATE"), "partners": None,
        "payload_required": ("object_type", "state", "source_version"), "business_key": "business_key",
        "quantity": "quantity", "unit": "unit", "units": UNITS, "currency": "currency", "currencies": CURRENCIES,
        "identifier": None, "identifier_pattern": None,
        "attrs": {"source_state": "state", "source_quality_flag": "quality_flag", "source_subtype": "subtype"},
        "notes": "notes", "match": "LT-04", "contract": "source-contract-v1",
    },
    "source_message": {
        "envelope_required": ("source_key", "partner", "schema_rev", "source_ts", "ref_id", "record_kind", "payload_text"),
        "envelope_names": {"source_key": "id", "partner": "source", "source_ts": "received_at", "payload_text": "body",
                           "ref_id": "body.ref", "schema_rev": "body.schema_version"},
        "schema_revs": ("1", "2"), "record_kinds": ("SOURCE_MESSAGE",), "partners": None,
        "payload_required": (), "business_key": None, "quantity": None, "unit": None, "units": None, "currency": None,
        "currencies": None, "identifier": None, "identifier_pattern": None,
        "attrs": {"source_state": "status"}, "notes": None, "match": None, "contract": "source-contract-v1",
    },
    "gateway": {
        "envelope_required": ("source_key", "partner", "source_ts", "ref_id", "record_kind", "payload_text"),
        "envelope_names": {"source_key": "message_id", "partner": "system", "source_ts": "occurred_at", "ref_id": "business_key",
                           "record_kind": "event_type", "payload_text": "raw_payload"},
        "schema_revs": None, "record_kinds": ("batch_created", "lab_test", "deviation_review", "qa_disposition"),
        "partners": ("mes", "lims", "qms"),
        "payload_required": (), "business_key": None, "quantity": None, "unit": None, "units": None, "currency": None,
        "currencies": None, "identifier": None, "identifier_pattern": None,
        "attrs": {"source_state": "payload.source_status"}, "notes": "payload.note", "match": None, "contract": "source-contract-v1",
    },
    "vendor_csv": {
        "envelope_required": ("source_key", "partner", "source_ts", "ref_id", "record_kind", "payload_text"),
        "envelope_names": {"source_key": "external_id", "partner": "tenant", "source_ts": "recorded_at", "ref_id": "external_id",
                           "record_kind": "kind", "payload_text": "(row)"},
        "schema_revs": None, "record_kinds": None, "partners": None,
        "payload_required": ("tenant", "external_id", "kind", "region", "amount", "currency", "recorded_at", "schema_version",
                             "status", "language", "reference_id"),
        "business_key": None, "quantity": "amount", "unit": None, "units": None, "currency": "currency", "currencies": CURRENCIES,
        "identifier": "external_id", "identifier_pattern": r"^GXP-[0-9]{8}$",
        "attrs": {"source_state": "status"}, "notes": None, "match": None, "contract": "source-contract-v1",
    },
}


def get_path(obj, path):
    """Dotted lookup in nested dicts; None when absent."""
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur
