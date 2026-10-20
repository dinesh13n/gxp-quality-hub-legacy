"""Intake delay / missing / revised report and source freshness (OP-INT-04, BEH-INT-12, FR-INT-08, PNFR-03, PNFR-04; INC-09).

Read-only over the INC-06 intake records (raw_intake, intake_item_attr, intake_current); no manual step, no state change.
  delay_hours   = receipt_time - source_ts, in hours (exact decimal, 3 places). A negative delay is flagged FUTURE_SOURCE_TS and excluded from the
                  timeliness share; a missing / unparsable source_ts is flagged MISSING_SOURCE_TS; a delivery that conflicts with or duplicates an
                  earlier identity is flagged REVISED.
  share         = items with 0 <= delay <= threshold / items with a usable, non-future delay (PNFR-03 measure; threshold `intake_reports.
                  delay_threshold_hours`, default 4 - an Assumption, not a target).
  freshness     = per source, age of the newest ACCEPTED item (current outcome VALIDATED / VALIDATED_WITH_FLAGS) at the injected `as_of` instant;
                  stale when age > `intake_reports.freshness_hours` (default 24, PNFR-04 Assumption: 'risk signal' is undefined, so the newest
                  accepted item is measured).
"""
import datetime
import decimal

from hub.core.errors import ConfigInvalid

ROLES = ("quality_lead", "compliance")
ACCEPTED = ("VALIDATED", "VALIDATED_WITH_FLAGS")
DEFAULTS = {"delay_threshold_hours": 4, "freshness_hours": 24}


def settings(cfg):
    s = dict(DEFAULTS)
    s.update((cfg or {}).get("intake_reports") or {})
    for k in DEFAULTS:
        if isinstance(s[k], bool) or not isinstance(s[k], (int, float)) or s[k] <= 0:
            raise ConfigInvalid({"intake_reports." + k: "positive number"})
    return s


def parse_ts(value):
    if not isinstance(value, str) or not value.strip():
        return None
    v = value.strip().replace("Z", "+00:00")
    try:
        t = datetime.datetime.fromisoformat(v)
    except ValueError:
        try:
            t = datetime.datetime.strptime(value.strip()[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.timezone.utc)
    return t.astimezone(datetime.timezone.utc)


def hours_between(start, stop):
    td = stop - start
    micro = decimal.Decimal(td.days * 86400 * 10 ** 6 + td.seconds * 10 ** 6 + td.microseconds)
    return (micro / decimal.Decimal(3600 * 10 ** 6)).quantize(decimal.Decimal("0.001"), rounding=decimal.ROUND_HALF_EVEN)


def _items(con, source):
    q = ("SELECT r.raw_id, r.source, r.receipt_time, r.duplicate_of, a.source_ts, a.ref_id, c.outcome, c.conflicts_with"
         " FROM raw_intake r LEFT JOIN intake_item_attr a ON a.raw_id = r.raw_id JOIN intake_current c ON c.raw_id = r.raw_id"
         + (" WHERE r.source = ?" if source else "") + " ORDER BY r.source, r.receipt_time, r.raw_id")
    return con.execute(q, (source,) if source else ()).fetchall()


def delay_report(con, source, threshold_hours=4):
    items, within, usable, future, missing, revised = [], 0, 0, 0, 0, 0
    thr = decimal.Decimal(str(threshold_hours))
    for raw_id, src, receipt, dup, sts, ref_id, outcome, conflicts in _items(con, source):
        flags = []
        rt, st = parse_ts(receipt), parse_ts(sts)
        delay = None
        if st is None or rt is None:
            flags.append("MISSING_SOURCE_TS")
            missing += 1
        else:
            delay = hours_between(st, rt)
            if delay < 0:
                flags.append("FUTURE_SOURCE_TS")
                future += 1
            else:
                usable += 1
                if delay <= thr:
                    within += 1
        if dup or conflicts:
            flags.append("REVISED")
            revised += 1
        items.append({"raw_id": raw_id, "ref_id": ref_id, "source_ts": sts, "receipt_time": receipt, "outcome": outcome,
                      "delay_hours": None if delay is None else str(delay), "flag": flags[0] if flags else None, "flags": flags})
    share = None if usable == 0 else (decimal.Decimal(within) / decimal.Decimal(usable) * 100).quantize(decimal.Decimal("0.1"))
    return {"source": source, "items": items,
            "summary": {"items": len(items), "usable_delays": usable, "within_threshold": within, "threshold_hours": str(thr),
                        "share_within_threshold_pct": None if share is None else str(share), "future_source_ts": future,
                        "missing_source_ts": missing, "revised": revised,
                        "basis": "delay = receipt_time - source_ts; future and missing source_ts excluded from the share",
                        "target_status": "Assumption (PNFR-03); not a validated target"},
            "label": "synthetic, unvalidated"}


def freshness_report(con, as_of, freshness_hours=24):
    now = parse_ts(as_of)
    out = []
    srcs = [r[0] for r in con.execute("SELECT DISTINCT source FROM raw_intake ORDER BY source")]
    for s in srcs:
        r = con.execute("SELECT max(r.receipt_time) FROM raw_intake r JOIN intake_current c ON c.raw_id = r.raw_id WHERE r.source = ? AND c.outcome IN (?, ?)",
                        (s,) + ACCEPTED).fetchone()
        newest = r[0]
        age = None if newest is None else hours_between(parse_ts(newest), now)
        stale = age is None or age > decimal.Decimal(str(freshness_hours))
        out.append({"source": s, "newest_accepted_at": newest, "age_hours": None if age is None else str(age), "older_than_threshold": stale})
    return {"as_of": as_of, "threshold_hours": str(freshness_hours), "sources": out, "stale": [x["source"] for x in out if x["older_than_threshold"]],
            "basis": "age of the newest accepted item per source (PNFR-04 'risk signal' is undefined: Unknown)", "label": "synthetic, unvalidated"}
