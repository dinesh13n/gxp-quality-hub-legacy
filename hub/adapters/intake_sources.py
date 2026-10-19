"""AD-03 / AD-04 mapping / AD-05 intake source readers (INC-06): legacy partner feeds, source messages, gateway inbox and the vendor CSV
-> normalised deliveries for hub.intake.service.IntakeService.ingest.

Read-only by construction: the legacy tables are read through the hash-gated snapshot handle of hub.adapters.legacy_sqlite (`mode=ro&immutable=1`
on a sandbox copy; the working-tree data/ is never opened). Only identity / payload columns are selected: the legacy status columns and
`error_reason` are never read as truth (BEH-INT-01). The CSV is parsed by header names, never by position (BEH-INT-11).
"""
import csv
import hashlib
import json
import os

from hub.guards import sandbox

CSV_REL = os.path.join("data", "lake", "%s", "partner_export.csv")


def _delivery(source_key, partner, schema_rev, source_ts, ref_id, record_kind, payload_text, raw):
    return {"source_key": source_key, "partner": partner, "schema_rev": schema_rev, "source_ts": source_ts, "ref_id": ref_id,
            "record_kind": record_kind, "payload_text": payload_text, "raw": raw}


def partner_feed_deliveries(handle):
    """All legacy partner_feeds rows in delivery order (ingest_ts, feed_id)."""
    out = []
    for (feed_id, partner, rev, sts, its, ref, kind, raw_json) in handle.execute(
            "SELECT feed_id, partner, schema_rev, source_ts, ingest_ts, ref_id, record_kind, raw_json FROM partner_feeds ORDER BY ingest_ts, feed_id"):
        out.append(_delivery(feed_id, partner, rev, sts, ref, kind, raw_json,
                             {"feed_id": feed_id, "partner": partner, "schema_rev": rev, "source_ts": sts, "ingest_ts": its, "ref_id": ref,
                              "record_kind": kind, "raw_json": raw_json}))
    return out


def source_message_deliveries(handle):
    out = []
    for (mid, source, received_at, body) in handle.execute("SELECT id, source, received_at, body FROM source_messages ORDER BY received_at, id"):
        try:
            doc = json.loads(body)
        except ValueError:
            doc = None
        doc = doc if isinstance(doc, dict) else {}
        out.append(_delivery(mid, source, doc.get("schema_version"), received_at, doc.get("ref"), "SOURCE_MESSAGE", body,
                             {"id": mid, "source": source, "received_at": received_at, "body": body}))
    return out


def gateway_inbox_deliveries(handle):
    out = []
    for (mid, ref, system, etype, etime, rec, payload) in handle.execute(
            "SELECT message_id, external_ref, source_system, event_type, event_time, received_at, raw_payload FROM gateway_inbox ORDER BY received_at, message_id"):
        out.append(_delivery(mid, system, None, etime, ref, etype, payload,
                             {"message_id": mid, "external_ref": ref, "source_system": system, "event_type": etype, "event_time": etime,
                              "received_at": rec, "raw_payload": payload}))
    return out


def gateway_event_deliveries(items):
    """Events returned by the gateway client (GET /api/events items) -> deliveries (the whole event object is the payload)."""
    out = []
    for e in items:
        e = e if isinstance(e, dict) else {}
        out.append(_delivery(e.get("message_id"), e.get("system"), e.get("schema_version"), e.get("occurred_at"), e.get("business_key"),
                             e.get("event_type"), json.dumps(e, sort_keys=True, ensure_ascii=True, default=str), e))
    return out


def csv_path(legacy_root, tier="tiny"):
    sandbox.assert_safe_path(legacy_root, "legacy source root")
    return os.path.join(legacy_root, CSV_REL % tier)


def vendor_csv_deliveries(path):
    """Vendor CSV -> deliveries (+ the file's sha256). `amount` stays text; a blank / negative amount is classified by the service."""
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    rows = csv.DictReader(raw.decode("utf-8").splitlines(), restkey="_extra", restval=None)
    out = []
    for row in rows:
        row = dict(row)
        out.append(_delivery(row.get("external_id"), row.get("tenant"), row.get("schema_version"), row.get("recorded_at"),
                             row.get("external_id"), row.get("kind"), json.dumps(row, sort_keys=True, ensure_ascii=True), row))
    return out, sha
