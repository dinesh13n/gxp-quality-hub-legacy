---
stage: "10 — Target Architecture + ADRs"
artifact: "architecture-options.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Four whole-system options were compared across the seven required dimensions. Option B (modular monolith beside legacy, strangler/coexistence) is recommended; option D (buy) is un-evaluated (OPD-10) and kept open by design. Per-decision options are in ADR-001..018.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AO-1 System-level options
| Option | Description | Source of idea |
|---|---|---|
| A | In-place refactor of legacy `app/` | Stage 7 default path |
| B | Modular monolith beside legacy (new package, own SQLite DB, read-only adapters, shadow comparison) | Stage 7 sequence; 0C S1 |
| C | Service-oriented / event bus (microservices) | common pattern |
| D | Replace with commercial QMS (buy) / hybrid | OPD-10 |

### AO-2 Comparison on the seven dimensions (H = strong, M = mixed, L = weak, ? = unknown)
| Dimension | A in-place | B modular monolith (recommended) | C microservices | D buy |
|---|---|---|---|---|
| 1 Fit to FRs (52 FR; CAP-01..10) | M: net-new capabilities forced into god modules | H: capability modules map 1:1 to CAP groups | H but over-partitioned | ?: not evaluated |
| 2 NFRs (perf/avail/scale) | M | M-H at 125 cases (Assumption); availability 99.5% unproven | H scale, no demand evidence | ? |
| 3 Security and identity | L: `server.py` has no auth | H: greenfield authn/RBAC/audit designed in (ADR-005/013) | M: more attack surface | ? vendor-dependent |
| 4 Portability / lock-in | H (none) | H (stdlib; repo interfaces for DB/authn/gate) | M (broker) | L: vendor lock-in, no evidence |
| 5 Cost and latency vs 0C | H cost, low change | H: within 0C S1 (3-yr gross USD 7.9k-22.8k; infra 20-100/month, all Assumed) and S2 non-ML up to 39.0k | L: above S2 range | ? |
| 6 Resilience / change safety | L: edits pinned behaviour (PNFR-19) | H: legacy intact; per-module rollback | M | ? |
| 7 Brownfield / maintainability | L: Stage 7 no-go; store import-time global (DM-10) | H: honours harness-first sequence | L | ? |
| Verdict | Rejected | **Recommended (PROPOSED)** | Rejected (over-built) | Open (OPD-10) |

### AO-3 Cost/latency vs Stage 0C
[Verified Fact] 0C figures are Assumptions (no benefit modelled; OD-04). [Inference] Option B needs build effort at the upper part of S1 and into S2-non-ML because S1 as described in 0C excludes crosswalk, non-destructive intake, run records and shared metric definitions (`economics-baseline-reconciliation.md` line 43), so the 0C S1 range of 15/25/40 person-days is likely understated. Trade-off recorded: planning range USD 7.9k-39.0k 3-yr gross, mid 13.4k-22.1k. Model-call cost is zero by OD-08 (S3/S4 retired). Latency: no AI inference latency; interactive targets are Unknown (OPD-14); the 0C 8-10 s AI bounds do not apply.

### AO-4 Why not a deterministic rules engine or workflow engine product
Considered inside ADR-007 and ADR-010: three small rule tables (JS limit table 32 pairs; Python 5-line rule; batch threshold) do not justify a rules runtime; scheduling needs only a trigger plus run records.

## Evidence References
See evidence_sources; `docs/07-repo-assessment/repo-transformation-readiness.md`; `docs/00-preflight/ai-economics/preliminary-tco.md`; `docs/08-ai-qualification/economics-baseline-reconciliation.md`.

## Assumptions
A-10-01, A-10-02 (see ADR-001). 0C numbers are Assumptions.

## Unknowns
U-10-03 (OPD-10); real team capacity and cost.

## Unresolved Issues
Option D unevaluated.

## Residual Risks
Cost range may be understated (0C S1 scope gap).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

