"""Non-functional measurement reports (nfr-spec PNFR-01, PNFR-02, PNFR-06; INC-08). Pure functions over supplied records: no clock, no I/O, no network.

Every figure is a MEASUREMENT with its method, never a promise: where the target is an Assumption (A-09-04: 99.5 % availability, 'finished before 06:00')
the verdict, when shown, is labelled 'against an unvalidated working target' and the report states that nothing is claimed about real availability or
production timeliness. Latency has no threshold (PNFR-06 measure-only).
"""
import decimal

WORKING_TARGET_LABEL = "against an unvalidated working target"
DATA_LABEL = "synthetic, unvalidated"
AVAILABILITY_TARGET = decimal.Decimal("99.5")


def availability_report(probes, window_minutes):
    """probes: iterable of (minute_index, ok) - one /healthz self-probe per minute, logged as http_request. downtime = minutes whose probe failed
    (consecutive failed probes make one outage); a minute with no probe counts as down (a missing probe is not evidence of service)."""
    window_minutes = int(window_minutes)
    ok_minutes = set(m for m, ok in probes if ok and 0 <= m < window_minutes)
    down = window_minutes - len(ok_minutes)
    avail = (decimal.Decimal(window_minutes - down) * 100 / decimal.Decimal(window_minutes)).quantize(decimal.Decimal("0.01"),
                                                                                                           rounding=decimal.ROUND_HALF_EVEN)
    outages, run = [], 0
    for m in range(window_minutes):
        if m in ok_minutes:
            if run:
                outages.append(run)
            run = 0
        else:
            run += 1
    if run:
        outages.append(run)
    return {"availability_pct": format(avail, "f"), "window_minutes": window_minutes, "down_minutes": down, "outages": len(outages),
            "longest_outage_minutes": max(outages) if outages else 0,
            "method": "1 - (down minutes / window minutes) from a /healthz self-probe every 60 s; downtime = consecutive failed probes",
            "target": "99.5 % (Assumption A-09-04)", "meets_working_target": avail >= AVAILABILITY_TARGET,
            "verdict_label": WORKING_TARGET_LABEL,
            "claim": "none: this figure is measured on the supplied probe log only; no claim is made about real availability", "label": DATA_LABEL}


def timeliness_report(rows, deadline="06:00"):
    """rows: hub.runs.detector.timeliness()['runs'] (one per finished scheduled run). Reports run_finished_before_0600_local per night and the share."""
    nights = [{"run_id": r["run_id"], "ended_local": r["ended_local"], "deadline_local": r["deadline_local"],
               "run_finished_before_0600_local": bool(r["finished_before_deadline"])} for r in rows]
    n = len(nights)
    ok = sum(1 for x in nights if x["run_finished_before_0600_local"])
    share = None if n == 0 else format((decimal.Decimal(ok) * 100 / decimal.Decimal(n)).quantize(decimal.Decimal("0.1")), "f")
    return {"deadline_local": deadline, "nights": nights, "nights_count": n, "finished_before_deadline": ok, "share_pct": share,
            "verdict_label": WORKING_TARGET_LABEL,
            "claim": "production timeliness is unproven: measured on a sandbox with a fixed clock; the business time zone is Unknown (U-12-F06-1)",
            "label": DATA_LABEL}


def latency_report(samples_ms):
    """samples_ms: {name: [milliseconds, ...]} -> p50 / p95 (nearest rank) per name, no threshold, no verdict."""
    out = {}
    for name, ms in sorted(samples_ms.items()):
        s = sorted(ms)
        n = len(s)
        rank = lambda q: s[min(n, max(1, -(-q * n // 100))) - 1]  # noqa: E731
        out[name] = {"calls": n, "p50_ms": round(rank(50), 3), "p95_ms": round(rank(95), 3), "max_ms": round(s[-1], 3)}
    return {"latency": out, "threshold": None, "label": DATA_LABEL + "; measure-only, no threshold (PNFR-06)"}
