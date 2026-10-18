---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-016-observability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "ops/legacy_log_sampler.py", "docs/09-initial-prd/nfrs.md PNFR-14"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-016 — Observability: structured logs + run records + metrics tables (stdlib). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-RUN-02, FR-INT-08, FR-MET-07, FR-SEC-02; PNFR-14, PNFR-06, PNFR-09; RC-5.

### Context
[Verified Fact] Shipped code has no logging beyond `log_message` to stderr (Stage 0A; PNFR-14 gap). [Verified Fact] `ops/legacy_log_sampler.py` exists as a legacy sampler. [Unknown] Any monitoring platform at the client (none).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Do nothing / print | stderr only | Nothing | Fails PNFR-14 | Poor |
| B. stdlib `logging` JSON lines + run-record tables + latency timers - RECOMMENDED | Correlation id per request/run; logs to stdout/file; p50/p95 timers on key calls (needed for PNFR-06 measurement); no personal/sensitive fields in logs; missing-run detector | No dependency; feeds KPIs | No dashboards or alerting out of the box | High |
| C. OpenTelemetry + hosted APM | Standard telemetry | Rich tooling | HAR-08/09 egress; vendor; no backend exists | Defer |

### Decision / recommendation
Recommend B, with log format compatible with later OTel ingestion.

### Consequences
- Positive: R1 measurement of latency baseline.
- Negative: manual log review until a platform exists.

### Trigger to decide / revisit
Revisit with ADR-015.

## Evidence References
ops/legacy_log_sampler.py; docs/09-initial-prd/nfrs.md PNFR-14

## Assumptions
A-10-17 Local log files acceptable.

## Unknowns
U-10-22 Monitoring target.

## Unresolved Issues
None.

## Residual Risks
Logs may capture untrusted strings; log-injection escaping needed.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

