---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-002-no-ai-boundary-enforcement.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", ".fde/orchestrator-decisions.md OD-08", "docs/08-ai-qualification/qualification-decision.md", "docs/09-initial-prd/nfrs.md PNFR-13, PNFR-18"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-002 — Enforcing the No-AI decision (OD-08) in the architecture. Status: The decision "product is No-AI" is made and approved by Dinesh (OD-08, 2026-10-18).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
The decision "product is No-AI" is made and approved by Dinesh (OD-08, 2026-10-18). This ADR records only the enforcement mechanism: PROPOSED.

### Traceability
FR-CO-04, FR-GATE-01, FR-INT-07, FR-REV-01; PNFR-13, PNFR-17, PNFR-18; RC-1, RC-6 (injection exposure); HAR-10; BR-AI-1..7.

### Context
[Verified Fact] OD-08: product is No-AI (rules / keyword-FTS / templates / deterministic core); Stage 19 not applicable, Stage 22 not triggered, Stage 32 tracks zero model calls. [Verified Fact] Planted instruction-like strings exist in data (86 feed rows; 22 of 1,200 document bodies; 44 regex hits - `nfrs.md` PNFR-13). [Verified Fact] Today 0 model calls and no third-party libs (DM-08). [Inference] "No AI" must be an architectural property that can be tested, not just a statement.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Policy statement only | Document the rule; rely on review | Zero effort | Unenforced; a dependency could introduce a model call silently | Poor |
| B. Structural enforcement - RECOMMENDED | (1) Dependency allow-list: stdlib only until HAR-08; CI check fails on any import from a deny-list (openai, anthropic, transformers, torch, langchain, etc.) or any HTTP client import outside `adapters/`; (2) runtime egress: product process makes no outbound network calls (loopback only, ADR-015); (3) all inbound text passes through a typed `Untrusted` wrapper that cannot reach decision fields; (4) planted-string fixture suite (86/22/44) as a release gate; (5) Stage 32 tripwire counts model calls = 0 | Testable (PNFR-18); cheap; matches deterministic zone D | Deny-list is heuristic; needs maintenance | Fit High; lock-in none; cost near zero; brownfield High |
| C. Optional AI plug-in point kept in the architecture | Reserve a Zone A adapter slot, disabled | Easier future T3 Q&A | Violates the spirit of OD-08 now; creates a surface to attack; BR-AI-6 requires proven shortfall first | Not selected; re-qualification path remains RQ-1..RQ-3 |

### Decision / recommendation
Recommend B. No Zone A component exists in the target architecture. A future AI element requires a new Dinesh decision and Stage 8 re-qualification (BR-AI-1); this ADR would then be superseded.

### Consequences
- Positive: PNFR-13/17/18 become automated gates; injection risk reduced because text never drives logic.
- Negative: CI deny-list needs upkeep; no NL document Q&A (accepted by OD-08; U-S01 unknown).
- AI coding assistants used to build are dev tooling, not product AI (BR-AI-7).

### Trigger to decide / revisit
Accept with the Stage 10 package; revisit only on RQ-1..RQ-3 triggers.

## Evidence References
.fde/orchestrator-decisions.md OD-08; docs/08-ai-qualification/qualification-decision.md; docs/09-initial-prd/nfrs.md PNFR-13, PNFR-18

## Assumptions
A-10-03 Stdlib-only remains acceptable through R1 (HAR-08 not triggered). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
U-10-04 Whether real corpus defeats keyword search (RQ-1..RQ-3).

## Unresolved Issues
Deny-list contents to be fixed at Stage 12/24.

## Residual Risks
Transitive tooling introduced at BUILD time slipping past the deny-list.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

