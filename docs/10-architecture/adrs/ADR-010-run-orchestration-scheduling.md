---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-010-run-orchestration-scheduling.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/partner_feeds.py", "docs/06-root-cause/confirmed-root-causes.md RC-5", "docs/09-initial-prd/open-product-decisions.md OPD-11"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-010 — Run orchestration and scheduling (idempotent CLI jobs + run records; schedule held pending OPD-11). Status: PROPOSED - depends on open OPD-11 (is a deterministic scheduler an "automated action" under HAR-10?).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED - depends on open OPD-11 (is a deterministic scheduler an "automated action" under HAR-10?). Recommended option B.

### Traceability
FR-RUN-01..03, FR-INT-08, FR-MET-07; PNFR-02, PNFR-14; RC-5; HAR-10; OPD-11.

### Context
[Verified Fact] No scheduler anywhere; `reconcile(limit=1000)` against 8,567 backlog rows, 9 runs; no run record (RC-5). [Verified Fact] PNFR-02 target 06:00 is an archived working target (Assumption). [Verified Fact] No production host exists (OD-04), `.github/workflows` has never run (DM-06).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. In-process scheduler thread | Server spawns timers | Single process | Hidden automation in the server; harder to disable; Zone H risk if misconfigured | Weaker control |
| B. Idempotent CLI job entrypoints + run records; trigger is external and configurable - RECOMMENDED | `hub run <job>` writes a run record (start/end, trigger, inputs, outcomes, errors, limit flag) and a checkpoint; manual trigger requires a role; schedule is a documented OS-level entry (cron/Task Scheduler/CI) that stays DISABLED until OPD-11 is answered; jobs never touch Zone H (rejected by gate, ADR-006); no silent cap: remainder reported as backlog and resumed | Works in any environment; testable; disable = remove one entry; no new dependencies | External scheduler config lives outside the repo | High fit; lock-in none |
| C. Workflow engine (Airflow/Temporal) | Orchestration platform | Rich retries/UI | HAR-05/08; infra; cost; no scale evidence | Over-built |
| D. Manual only | Humans start runs | No automation question | Leaves RC-5 partly open (no timeliness) | Fallback mode, always supported |

### Decision / recommendation
Recommend B with default = manual only until OPD-11 is resolved by Dinesh. Decision in HAR-10 terms: a scheduler running only non-Zone-H deterministic jobs is proposed as permissible, but this is his call.

### Consequences
- Positive: run records feed delay/backlog metrics.
- Negative: timeliness (PNFR-02) unproven until a schedule is approved.

### Trigger to decide / revisit
Resolve OPD-11 before Stage 15; ADR then ACCEPTED/amended by Dinesh.

## Evidence References
app/partner_feeds.py; docs/06-root-cause/confirmed-root-causes.md RC-5; docs/09-initial-prd/open-product-decisions.md OPD-11

## Assumptions
A-10-11 Overnight window is the only timing constraint.

## Unknowns
U-10-15 Real run duration and backlog.

## Unresolved Issues
OPD-11.

## Residual Risks
Silent failure of external scheduler; mitigated by missing-run alert metric.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

