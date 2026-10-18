---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-017-buy-vs-build.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/09-initial-prd/open-product-decisions.md OPD-10", "docs/08-ai-qualification/qualification-decision.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-017 — Buy versus build (commercial QMS) - NOT EVALUATED. Status: PROPOSED / OPEN - OPD-10 is unanswered.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED / OPEN - OPD-10 is unanswered. Recommendation limited to: keep the architecture reversible and run a bounded evaluation before Stage 13 if Dinesh wants it. No selection made.

### Traceability
OPD-10, OPD-05, CD-4 (qualification), QD-5 DN-5; whole PRD; HAR-08, HAR-09.

### Context
[Verified Fact] OPD-10 is "OPEN (not evaluated)"; the PRD assumes build. [Verified Fact] No requirements document names a commercial QMS, no vendor data exists in the repo. [Unknown] Whether a QMS already exists at the organisation (it may hold the disposition record - links to OPD-05). [Inference] The client is synthetic; a vendor evaluation would be unverifiable here.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Build (modular monolith, ADR-001) | As designed | Fits unique gaps (decision events, definitions without defaults, coexistence) | Build effort 15-70 person-days (0C S1/S2, Assumed); regulatory validation burden on the builder | Working assumption |
| B. Buy/configure a commercial QMS | Adopt vendor platform for case, CAPA, audit, e-signature | Mature validated features | No evidence of fit/cost; lock-in; integration of legacy rules and feeds unknown; requirements still undecided (OPD-01..05) | Un-evaluated |
| C. Hybrid: build the neutral policy/intake/metrics core, integrate vendor for record/e-signature through `external_ref` mode | Use ADR-006 mode `external_ref` | Keeps decision flexible | Integration cost unknown | Plausible; supported by design |

### Decision / recommendation
No selection. Recommend: proceed with A as working assumption; keep records, gate and identity behind interfaces (ADR-004/006/009) so B/C stay open; if Dinesh wants a vendor comparison, run it as a time-boxed Stage 11-12 task with explicit criteria (fit to 52 FRs, audit, e-signature, cost, export/exit terms).

### Consequences
- Positive: no lock-in created.
- Negative: residual blind spot persists until evaluated; possible rework if buy is chosen.

### Trigger to decide / revisit
Dinesh to answer OPD-10 before Stage 13 (specs).

## Evidence References
docs/09-initial-prd/open-product-decisions.md OPD-10; docs/08-ai-qualification/qualification-decision.md

## Assumptions
A-10-18 Build is acceptable for a capstone-scale pilot.

## Unknowns
U-10-23 Existence/identity of any incumbent QMS; U-10-24 vendor costs.

## Unresolved Issues
OPD-10.

## Residual Risks
A vendor decision later invalidates parts of the build.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

