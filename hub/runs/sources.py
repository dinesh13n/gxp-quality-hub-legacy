"""Ordered, checkpointable sources for the intake jobs (BEH-RUN-05).

A source gives an ordered list of deliveries (the dicts hub.intake.service.IntakeService.ingest takes). The ORDER KEY of a delivery is
[source_ts, source_key, n] (n = index among deliveries with the same two values, so the key is unique); the checkpoint of a job stores the
key of the last processed delivery per source and the next run takes the deliveries strictly after it. DEV-66: the spec names the key
(receipt_time, raw_id) of an already stored raw queue, but INC-06 stores raw rows and outcomes in one transaction, so the ordering is taken
from the source itself. Limitation (RTD-61): a delivery that appears LATER with an order key before the checkpoint is not seen by a resumed
run; `hub.intake ingest-legacy` (idempotent by content hash) remains the catch-up path.
"""
from hub.intake.errors import SourceUnreachable


def _t(v):
    return "" if v is None else str(v)


def valid_key(key):
    return (isinstance(key, list) and len(key) == 3 and isinstance(key[0], str) and isinstance(key[1], str)
            and isinstance(key[2], int) and not isinstance(key[2], bool) and key[2] >= 0)


class OrderedSource(object):
    def __init__(self, source, deliveries):
        self.source = source
        ordered = sorted(enumerate(deliveries), key=lambda x: (_t(x[1].get("source_ts")), _t(x[1].get("source_key")), x[0]))
        self.items, seen = [], {}
        for _, d in ordered:
            base = (_t(d.get("source_ts")), _t(d.get("source_key")))
            n = seen.get(base, 0)
            seen[base] = n + 1
            self.items.append(([base[0], base[1], n], d))

    def items_after(self, key):
        """[(key, delivery)] strictly after `key` (None = from the start). A malformed key raises ValueError (E-RUN-CHECKPOINT-INVALID)."""
        if key is None:
            return list(self.items)
        if not valid_key(key):
            raise ValueError("order key must be [text, text, non-negative integer]")
        k = tuple(key)
        return [(a, d) for a, d in self.items if tuple(a) > k]


class UnreachableSource(object):
    """A source that cannot be read (AC-RUN-13): items_after raises E-INT-SOURCE-UNREACHABLE; the job reports SOURCE_UNREACHABLE."""

    def __init__(self, source, details=None):
        self.source, self.details = source, details or {}

    def items_after(self, key):
        raise SourceUnreachable(dict(self.details, source=self.source))


def legacy_sources(handle):
    """The three legacy streams from a hash-gated read-only snapshot handle (hub.adapters.legacy_sqlite)."""
    from hub.adapters import intake_sources
    return {"partner_feed": OrderedSource("partner_feed", intake_sources.partner_feed_deliveries(handle)),
            "source_message": OrderedSource("source_message", intake_sources.source_message_deliveries(handle)),
            "gateway": OrderedSource("gateway", intake_sources.gateway_inbox_deliveries(handle))}


def vendor_csv_source(path):
    from hub.adapters import intake_sources
    rows, sha = intake_sources.vendor_csv_deliveries(path)
    return OrderedSource("vendor_csv", rows), sha
