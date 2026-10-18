---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-001-architecture-style.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/07-repo-assessment/dependency-map.md DM-08, DM-10", "docs/07-repo-assessment/repo-transformation-readiness.md", "app/server.py", "app/store.py", "docs/00-preflight/ai-economics/preliminary-tco.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-001 — Overall architecture style: modular monolith built beside the legacy estate. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B). Conditional on OPD-10 (buy-vs-build) staying open or resolving to build. Not ACCEPTED: only Dinesh Naik can accept.

### Traceability
FR/PNFR: all 10 capabilities CAP-01..10; PNFR-17, PNFR-19, FR-CO-01, FR-CO-03. Root causes: RC-1..RC-8 (structural answer to all); Stage 7 R-1..R-12 readiness; OPD-10.

### Context
[Verified Fact] The estate is stdlib-only Python (`app/`), plus single-file Java (`legacy_java/ReconcileLegacy.java`), Node (`legacy_js/legacy_policy.js`), SQL (`sql/`) and a batch module (`legacy_batch/shift_reconciliation.py`); no third-party libraries (`docs/07-repo-assessment/dependency-map.md` DM-08). [Verified Fact] `app/store.py` is imported by 11 app modules and fixes the DB path at import time (DM-10); `app/server.py` is a GET-only god handler. [Verified Fact] Stage 7 verdict: NOT READY FOR CODE CHANGE until the golden harness and hermetic fixtures exist (`repo-transformation-readiness.md` R-1, R-2). [Verified Fact] The core need is net-new (decision write path, audit, policy, run records) - Stage 7 heat map marks "missing capabilities" as highest risk. [Inference] A new bounded module can be added without editing the legacy code, which keeps FR-CO-01 (as-found reproducible) cheap to prove. [Unknown] Real team size, load and deployment target (no production, OD-04).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. In-place refactor of `app/` | Evolve legacy modules (decouple `store`, add write endpoints to `server.py`) | Smallest new surface; one codebase | Edits behaviour that is pinned only by non-executable goldens; Stage 7 no-go; mixes new regulated paths with wrong-but-pinned logic (RC-4, RC-8) | Fit ok; brownfield risk High; resilience poor; lock-in none |
| B. Modular monolith beside legacy (strangler/coexistence) - RECOMMENDED | New package (working name `hub/`) with bounded modules per capability group, own SQLite file, thin adapters reading legacy data; legacy left untouched until goldens are executable and a change is approved (HAR-06) | Legacy behaviour unchanged by construction; incremental cut-over; single deployable keeps ops cost at S1 range (USD 7.9k-22.8k 3-yr gross, 0C); replaceable modules | Two code paths coexist for a time; adapter maintenance; discipline needed to avoid a second god module | Fit High; NFR ok at 125-case scale (Assumption); security design is greenfield; lock-in none; cost within S1; resilience good (rollback = disable module); brownfield High |
| C. Microservices / event bus | Separate services per capability with broker | Independent scaling | No evidence of scale (125 cases; 167/month base, 0C); needs broker/infra (HAR-05, HAR-08); ops cost far above S1; more failure modes | Fit over-built; cost exceeds 0C S1/S2 planning range; resilience mixed; brownfield poor |
| D. Rewrite / replace with commercial QMS (buy) | Adopt an off-the-shelf quality management product | Possibly covers audit/e-signature natively | Not evaluated (OPD-10); vendor lock-in decision needs evidence we lack; legacy data/rules mapping unknown; Zone H location unknown (OPD-05) | Unknown - no evidence; see ADR-017 |

### Decision / recommendation
Recommend option B. The architecture is a modular monolith with a strict dependency rule (modules talk through in-process interfaces; only `adapters/legacy_*` may read legacy stores, read-only). Option D is not rejected on merit; it is un-evaluated and handled in ADR-017 so that B stays reversible.

### Consequences
- Positive: legacy untouched; every new capability testable in hermetic fixtures; matches Stage 7 sequencing.
- Negative: temporary duplication (three rule sets are loaded as data, not merged - ADR-007); extra adapter layer.
- Constraint: no module may import `app.store` (import-time global, DM-10); adapters open legacy DBs with `mode=ro` URIs.
- Reversibility: high (module can be abandoned; legacy path intact).

### Trigger to decide / revisit
Decide when Stage 11/12 start. Revisit if OPD-10 resolves to buy, or if a measured concurrency/load need appears (ADR-004, ADR-015).

## Evidence References
docs/07-repo-assessment/dependency-map.md DM-08, DM-10; docs/07-repo-assessment/repo-transformation-readiness.md; app/server.py; app/store.py; docs/00-preflight/ai-economics/preliminary-tco.md

## Assumptions
A-10-01 Build (not buy) is the working assumption (PRD assumes build; OPD-10). A-10-02 125-case baseline scale is representative of near-term load (OD-09; real volume Unknown). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
U-10-01 Team size/skills; U-10-02 real load; U-10-03 OPD-10 outcome.

## Unresolved Issues
Stage 14 must sequence B against the Stage 7 harness-first gate.

## Residual Risks
Module boundary drift (second monolith); adapter coupling to legacy schemas that have no contracts.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

