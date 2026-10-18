---
stage: "10 — Target Architecture + ADRs"
artifact: "architecture-risk-register.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Eighteen architecture risks with likelihood, impact, mitigation and owner. Ratings are inferences, not measurements.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AR-1 Register (L = likelihood, I = impact; H/M/L; all [Inference])
| ID | Risk | L | I | Mitigation | Related | Owner |
|---|---|---|---|---|---|---|
| AR-01 | Build starts before executable golden harness exists | M | H | Hard gate in Stage 14/15; CT-H1..H7 first | ADR-003; R-1, R-2 | Engagement lead (Dinesh Naik) |
| AR-02 | OPD-05 unanswered; pilot has no usable Zone H | H | M | Dual-mode design; default blocked; resolve before pilot | ADR-006 | Engagement lead (Dinesh Naik) |
| AR-03 | OPD-01..04 unanswered; no KPI targets or verdicts | H | M | Policy mechanism with no defaults; record accepted-open | ADR-007 | Engagement lead (Dinesh Naik) |
| AR-04 | A user treats `event` mode as validated e-signature | M | H | Labels; DR-29 framing; HAR-12 | ADR-006 | Engagement lead (Dinesh Naik) |
| AR-05 | SQLite single-writer/contention (H-14 unmeasured) | M | M | V-13 test; Postgres trigger | ADR-004 | Engagement lead (Dinesh Naik) |
| AR-06 | Trigger-only immutability bypassed offline | L | H | Hash chain + external anchor | ADR-005 | Engagement lead (Dinesh Naik) |
| AR-07 | Hand-rolled HTTP/authn flaws | M | H | Small surface, threat model Stage 24, tests | ADR-013/014 | Engagement lead (Dinesh Naik) |
| AR-08 | Prompt-injection-like strings influence logic | L | H | Untrusted typing, fixture gate | ADR-002/008 | Engagement lead (Dinesh Naik) |
| AR-09 | Hidden AI/ML dependency or egress | L | H | Deny-list, egress gate, tripwire | ADR-002 | Engagement lead (Dinesh Naik) |
| AR-10 | Availability/RTO targets unattainable on single host | H | M | State as Assumption; restore rehearsal; HA only on evidence | ADR-015 | Engagement lead (Dinesh Naik) |
| AR-11 | Buy-vs-build un-evaluated; rework if buy chosen | M | M | Interfaces keep options open | ADR-017 | Engagement lead (Dinesh Naik) |
| AR-12 | Effort understated (0C S1 scope gap) | M | M | Plan against S1-hi/S2 non-ML range | architecture-options AO-3 | Engagement lead (Dinesh Naik) |
| AR-13 | New vs legacy figures differ and are misread | M | M | Definition tags, golden diff, labelling | ADR-011 | Engagement lead (Dinesh Naik) |
| AR-14 | Scheduler considered automated action (HAR-10) | M | L | Manual default; OPD-11 | ADR-010 | Engagement lead (Dinesh Naik) |
| AR-15 | Requirements rest on unapproved PRD (OPD-13) | H | M | Treat ADRs PROPOSED; re-check at approval | all | Engagement lead (Dinesh Naik) |
| AR-16 | Python 3.10 EOL / interpreter drift | M | L | 3.12 baseline, CT-H5 | ADR-018 | Engagement lead (Dinesh Naik) |
| AR-17 | FTS5 unavailable in target SQLite | L | L | Fallback index | ADR-012 | Engagement lead (Dinesh Naik) |
| AR-18 | Legacy rules (999,999 default) propagated unmarked | M | M | `defaulted` marker; HAR-06 | ADR-007 | Engagement lead (Dinesh Naik) |

## Evidence References
ADRs; docs/07-repo-assessment/technical-debt-register.md.

## Assumptions
Ratings are judgement.

## Unknowns
Real operating profile.

## Unresolved Issues
All AR items open.

## Residual Risks
Register may omit risks arising from real environments.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

