# INC-08 NFR measurements (sandbox, synthetic, unvalidated)
Verified Fact: figures printed by `test_tst_nfr_measurements.py` (one `NFR-REPORT` line per measurement test; captured with `HUB_NFR_REPORT_FILE`). Every figure is a MEASUREMENT with its method; none claims that a real-world target is met. Targets are Assumptions (A-09-04, OPD-14) and are shown only "against an unvalidated working target".

## NFR-01
```json
{
 "availability_pct": "99.50",
 "claim": "none: this figure is measured on the supplied probe log only; no claim is made about real availability",
 "down_minutes": 216,
 "label": "synthetic, unvalidated",
 "longest_outage_minutes": 100,
 "meets_working_target": true,
 "method": "1 - (down minutes / window minutes) from a /healthz self-probe every 60 s; downtime = consecutive failed probes",
 "outages": 3,
 "target": "99.5 % (Assumption A-09-04)",
 "verdict_label": "against an unvalidated working target",
 "window_minutes": 43200
}
```

## NFR-02
```json
{
 "claim": "production timeliness is unproven: measured on a sandbox with a fixed clock; the business time zone is Unknown (U-12-F06-1)",
 "deadline_local": "06:00",
 "finished_before_deadline": 27,
 "label": "synthetic, unvalidated",
 "nights_count": 30,
 "share_pct": "90.0",
 "verdict_label": "against an unvalidated working target"
}
```

## NFR-05
```json
{
 "checksum_match": true,
 "claim": "sandbox timing of a small synthetic store only; RTO/RPO attainment is unproven",
 "label": "synthetic, unvalidated",
 "restore_elapsed_seconds": 0.003,
 "verdict_label": "against an unvalidated working target",
 "verify_audit": "ok",
 "verify_projection_mismatches": 0,
 "within_working_target": true,
 "working_target_seconds": 28800
}
```

## NFR-06
```json
{
 "label": "synthetic, unvalidated; measure-only, no threshold (PNFR-06)",
 "latency": {
  "evidence_pack": {
   "calls": 30,
   "max_ms": 14.709,
   "p50_ms": 10.884,
   "p95_ms": 14.027
  },
  "queue": {
   "calls": 30,
   "max_ms": 9.44,
   "p50_ms": 6.276,
   "p95_ms": 8.591
  },
  "rule_trace": {
   "calls": 30,
   "max_ms": 9.323,
   "p50_ms": 6.327,
   "p95_ms": 8.811
  },
  "state": {
   "calls": 30,
   "max_ms": 8.703,
   "p50_ms": 6.151,
   "p95_ms": 7.999
  }
 },
 "threshold": null
}
```

## NFR-07
```json
{
 "anonymous_effects": 0,
 "public": [
  "OP-SEC-01",
  "OP-SYS-01",
  "UI-LOGIN",
  "UI-LOGIN-POST",
  "UI-STATIC"
 ],
 "routes_checked": 53
}
```

## NFR-13
```json
{
 "decision_digest_unchanged": true,
 "documents_found": 22,
 "feed_rows": 86,
 "regex_hit_fixture": "none (deviation)",
 "variants": 10
}
```

## NFR-17
```json
{
 "digest": "d66e09748857625475052fe330cc3f726c28a696cb0cefbebb0a717b3d05b6b9",
 "requests": 13,
 "runs": 3
}
```

Notes: NFR-01 is computed from a simulated probe log (3 outages of 100, 80 and 36 minutes in 43,200); the single real /healthz probe is logged as `http_request`. NFR-02 uses 30 simulated nights on a fixed clock; the business time zone is Unknown (U-12-F06-1, UTC used). NFR-05 times `backup.restore` on a small synthetic store. NFR-06 is 30 in-process calls per route on the 125-case baseline (one process, one writer, no network latency); no threshold. NFR-13: the "44 regex-hit strings" have no standalone fixture, the 10 injection variants stand in for them (DEV-89). NFR-17 digest is over 13 response (status + body) hashes, equal in all 3 environments.
