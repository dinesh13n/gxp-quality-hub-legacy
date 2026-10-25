---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "slo-sla-definitions.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/slo.py", "docs/09-initial-prd/nfrs.md (PNFR-01..06, 14, 18)", "docs/operations-service-levels.md", "docs/28-reliability/resilience-readiness.md D-28-06", "docs/29-incident-bcdr/rto-rpo.md", "hub/web/nfr.py", "tests/hub/test_tst_hub_stg31_slo_alerts.py", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
Five SLO **candidates** and three zero-tolerance invariants, with the arithmetic to compute an error budget. **No SLA exists: no customer, contract, penalty or business owner exists (OD-04), and none is created here.** The numbers come from archived working targets the source itself calls "not measured guarantees" (A-09-04) or are agent candidates; none is measured on real traffic. Two SLOs have no SLI source yet (audit chain, source freshness). The arithmetic is tested (S01-S03) and returns NO_DATA, not 100 %, for an empty window.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SD-1 SLO candidates (generated from `hub.obs.slo.SLOS`; every status is CANDIDATE)
| ID | Objective | SLI (good / total) | Target | Window | Basis | SLI source | SLI available today |
|---|---|---|---|---|---|---|---|
| SLO-01 | Availability in scheduled hours | minutes with a successful /healthz self-probe / window minutes | 99.5 % | 30 d | PNFR-01 / A-09-04 (archived working target, not measured) | hub.web.nfr.availability_report | yes |
| SLO-02 | Overnight run finished before 06:00 local | scheduled nights finished before the deadline / scheduled nights | 95 % | 28 d | PNFR-02 asks 100 % of nights (a zero budget); 95 % is the agent's budgetable candidate (D-31-03) | hub.web.nfr.timeliness_report | yes |
| SLO-03 | Requests answered without a server error | HTTP responses with status < 500 / HTTP responses | 99 % | 30 d | agent candidate (Assumption A-31-02); 4xx are client outcomes and count as good | http_requests_total | yes |
| SLO-04 | Audit chain verifies | audit_chain_verify_ok readings equal to 1 / readings | 100 % | 30 d | PNFR-09; integrity, so no budget (an exhausted budget = SEV-A) | audit_chain_verify_ok (GAP: not exported; F-29-01) | NO (gap) |
| SLO-05 | Partner source freshness | pulls newer than the staleness limit / pulls | 95 % | 30 d | PNFR-04 (stale signal max 24 h, R2); no freshness timestamp is exported | none (GAP) | NO (gap) |

### SD-2 Invariants (zero tolerance, no error budget)
| ID | Metric | Basis |
|---|---|---|
| INV-01 | `model_calls_total` = 0 | PNFR-18, OD-08 |
| INV-02 | `egress_attempts_total` = 0 | FR-CO-04 |
| INV-03 | `zone_h_service_actor_accepted` = 0 | FR-GATE-03 |
An invariant breach is an incident (SEV-A/B), not a budget event.

### SD-3 What is deliberately not an SLO
| Item | Why |
|---|---|
| Latency | PNFR-06 has no target (Unknown, OPD-14): measure-only; an invented p95 target would be a fabricated number |
| RTO / RPO | Stage 29 targets (RTO 4 working hours, RPO 1 working day) are agent targets verified by restore rehearsal, not by a running SLI; they stay in `rto-rpo.md` |
| Throughput / capacity | no target exists (D-28-06); `capacity-proxies.json` is a measurement |
| Reviewer response time | no reviewers exist (all roles VACANT) |

### SD-4 SLA statement
**No SLA is committed, drafted for signature, or implied.** An SLA would additionally need: a named customer and provider owner, an agreed measurement point and exclusions (planned maintenance, client errors), credits or remedies, a reporting cadence and an approval record. None of these exist; creating them is Dinesh Naik's decision (D-31-10) and would follow, not precede, at least one measured window. Until then the figures above are internal engineering targets for the engagement.

### SD-5 Appropriateness review (analysis dimension 4)
| SLO | Verdict | Reasoning |
|---|---|---|
| SLO-01 availability 99.5 % | Appropriate as a *measurement* | matches PNFR-01 archived target; `hub.web.nfr.availability_report` computes it from a 60 s `/healthz` probe log (missing probe = down). 99.5 % over 30 d = 216 minutes budget. The product is loopback, one person, scheduled hours only: real availability is not a promise |
| SLO-02 overnight run before 06:00 | Needs decision D-31-03 | PNFR-02 asks for 100 % of nights, a zero budget that makes any miss a breach and the budget arithmetic degenerate. 95 % over 28 nights allows 1 miss (1.4 nights); reported as an agent candidate. The business time zone is Unknown (U-12-F06-1) |
| SLO-03 non-5xx 99 % | Reasonable engineering guard | 4xx are client outcomes. Needs volume: below 100 requests one error exceeds the budget (the `low_volume` flag says so) |
| SLO-04 audit chain | Right objective, no SLI | integrity has no budget; the metric is blocked by F-29-01 (G-1) |
| SLO-05 freshness | Right objective (R2), no SLI | no freshness timestamp is exported; the source is Unknown |

### SD-6 Measuring (how a window is evaluated)
`slo.evaluate(slo, good, total)` returns SLI %, allowed bad events, budget remaining % and a state (NO_DATA, GREEN >= 50 %, AMBER 10-50 %, RED < 10 %, EXHAUSTED). `slo.burn_rate` and `slo.burn_verdict` implement two-window burn rates (pairs 5m/1h at 14.4, 30m/6h at 6, 6h/3d at 1: A-31-04; the hub has no time series, so these apply only once a snapshot job exists, D-31-01). Counts come from `slo.counts_http`, `counts_availability`, `counts_timeliness`.

## Evidence References
`hub/obs/slo.py`, `hub/web/nfr.py` (availability / timeliness reports with their own 'unvalidated working target' labels), `docs/09-initial-prd/nfrs.md`, tests S01-S03, A04.

## Assumptions
- A-31-02 SLO-03 99 %. A-31-03 state thresholds 50 / 10 %. A-31-04 burn-rate pairs. A-31-08 windows of 28-30 days. All agent assumptions; confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-31-06 Real traffic. U-12-F06-1 business time zone. U-31-11 Any consumer expectation (none known, OD-28).

## Unresolved Issues
- D-31-03 SLO-02 target; D-31-10 whether and when to turn a candidate into a commitment.

## Residual Risks
- RR-31-13 Targets without data can be read as promises; mitigated by the CANDIDATE label in code, output and documents (test S03). Medium.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
