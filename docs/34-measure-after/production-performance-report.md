---
stage: "34 — Measure After-Intervention KPIs"
artifact: "production-performance-report.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "docs/28-reliability/failure-injection-results.md", "docs/28-reliability/evidence/capacity-proxies.json", "docs/29-incident-bcdr/evidence/s29-rehearsal-summary.txt", "docs/34-measure-after/evidence/hub-*.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
**There is no production performance to report.** The hub has never run in production; no production telemetry exists; Stage 30 (cutover/release) has not been executed and Stage 31 (observability/SLOs) is not merged (`docs/30*`, `docs/31*` absent on `main`). This report therefore states (1) what sandbox evidence exists, with its limits, (2) what is Unknown, and (3) the exact measurements Dinesh or a production owner must supply. Sandbox figures are labelled **synthetic, sandbox, not production** and carry no threshold, SLO or target.

## Findings
### PP-1 Production measurements [Unknown]
| Dimension | Status | What must be supplied (owner: Engagement lead (Dinesh Naik) until a real owner exists) |
|---|---|---|
| Latency / throughput under real load | Unknown | p50/p95/p99 per route and per CLI command over a stated window from a running instance; request counts; host spec |
| Availability / error rate | Unknown | uptime and non-2xx share per route over a stated window, plus the definition of "available" |
| KPI values in production (K-04, K-05, K-09-EVID, K-22 included) | Unknown | closure, evidence and approver timestamps from the real QMS/LIMS or from hub `decision_events` after real use (RH-4) |
| Cost per case, effort | Unknown | labour hours and rates; hosting invoices (Stage 32 items) |

### PP-2 Sandbox evidence that exists [Verified Fact; synthetic, sandbox]
| Evidence | Result | Limit |
|---|---|---|
| Stage 26 TEVV (`tevv-results.md` TR-1) | S26 23/23, E26 1/1, group B 41 ok + 1 skipped, I6 43/43; CT-01..CT-16 PASS except CT-13 (Node patch drift S24-DEV-04) | Python 3.10.12 only; 3.12+ not run |
| Stage 26 mutation gate | 9 of 12 mutants killed by some group; M5, M9, M10 survive | sample of 12, not the mutant space |
| Stage 28 failure injections | FI-01..FI-09 PASS (breaker, retry budget, timeout, bulkhead, 429, no-AI); FI-13/FI-14 NOT RUN | mechanisms not wired into gateway-pull / web serve (OD-35) |
| Stage 28 capacity proxies | authorised read 41.2 /s (300 req, 7.28 s), healthz 558.9 /s, ingest 1,326 items/s (500 items) | one process on a shared laptop; 3x run-to-run variation; no threshold |
| Stage 29 sandbox rehearsal | backup, tamper detection, restore, corrupt-backup refusal, kill switch: all behaved as documented except F-29-01 (verify-audit KeyError after tamper; documented exit 17, observed rc 1) | tabletop had no human participants; RTO/RPO are agent targets |
| Stage 34 sandbox run (this stage) | metrics CLI ran end to end on the 125-case copy; backfill verify rc 0 (0 mismatches); chain verify ok (125 cases, 250 events); `verify-audit` ok (29 records); replay check ok; `hub.metrics` repeat snapshot gives equal values but new value ids and a new `computed_at` | fresh sandbox store; wall-clock as_of |
| Stage 34 timing of the hub CLIs | the shadow ingest of the 8,567 feed rows took 2 s and the replay check 2 s wall clock (`evidence/intake.log`) | tooling time on a laptop, NOT a latency, RTO or SLO figure |

### PP-3 What the sandbox evidence does not allow [Verified Fact]
- It does not show the hub is faster, cheaper, safer or more accurate than the legacy flow in operation. Stage 26 TR-7 already limits the business-outcome proxies RH-1..RH-7 to "mechanism evidence only, no value, time or cost claim"; this stage found nothing to change that.
- It does not support an SLO or SLA (no Stage 31; thresholds are agent assumptions under OD-32).

### PP-4 Performance-relevant defects still open [Verified Fact from earlier stages]
F-11 and 9 complex functions (Stage 27), F-29-01..16 (Stage 29), D-28-01..10 (Stage 28), mutants M5/M9/M10 (Stage 26). None was fixed in this stage; none is accepted.

## Evidence References
`docs/26-tevv/tevv-results.md`; `docs/28-reliability/failure-injection-results.md`; `docs/28-reliability/evidence/capacity-proxies.json`; `docs/29-incident-bcdr/evidence/s29-rehearsal-summary.txt`; `docs/34-measure-after/evidence/hub-12-verify-replay.json`, `hub-16-verify-audit.json`, `hub-01g-verify-projection.json`, `hub-01h-verify-chain.json`.

## Assumptions
- A-34-07 [Assumption] Earlier-stage test results are cited as recorded; they were not re-run in this stage (the orchestrator owns full regressions, OD-23). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-34-06 Every row of PP-1. Resolution: first production or approved pilot window plus Stage 31 telemetry.
- U-34-07 Python 3.12+ results (RTR-08, U-28-11).

## Unresolved Issues
- Stage 30 not executed and Stage 31 not merged: no cutover, no telemetry, no SLO. The Stage 34 prompt depends on both (`depends_on: 4, 30, 31`).

## Residual Risks
- RR-34-05 Sandbox proxies quoted as production capacity. Mitigation: label and the absence of any threshold here.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
