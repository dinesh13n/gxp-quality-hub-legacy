---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-003-legacy-coexistence-pattern.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/legacy_logic.py", "legacy_js/legacy_policy.js", "legacy_batch/shift_reconciliation.py", "docs/07-repo-assessment/characterization-test-plan.md", "docs/09-initial-prd/functional-requirements.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-003 — Coexistence pattern with the legacy estate (read-only adapters, shadow comparison, no dual-write). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-CO-01, FR-CO-02, FR-CO-03, FR-POL-04, FR-POL-06, FR-POL-05; PNFR-19; RC-4, RC-8, RC-6; Stage 7 CT-01..CT-18, CT-H1..H7; HAR-06; OPD-04, OPD-15.

### Context
[Verified Fact] Three unsynchronised rule implementations (`app/legacy_logic.py` >50,000; `legacy_js/legacy_policy.js` limit x1.05, default 999,999; `legacy_batch/shift_reconciliation.py` 2,500-8,500) and SQL/Java month-end paths with divergent totals (742,956.61 vs 622,826.44) are pinned as goldens (CT-01..03, CT-12). [Verified Fact] A legitimate parallel workflow for older customers exists, owner Unknown (OPD-15, FR-CO-02). [Verified Fact] Existing tests are destructive in the working tree (TQ-01); code runs only in a sandbox copy (OD-03a). [Inference] Which rule is "correct" is a decision (RC-3/OPD-04), so the architecture must not merge or fix them.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Big-bang cut-over | Replace legacy paths when new module is ready | Clean end state | No rollback; breaks FR-CO-01/02; 2025 rollback incident class (BR-13) | Poor resilience |
| B. Anti-corruption layer + shadow comparison - RECOMMENDED | New module reads legacy data via read-only adapters; the three rule sets are loaded as named rule data (as-found-python/js/batch); new outputs are compared to goldens in CI; legacy remains the operational path until each capability is cut over by an approved change; legacy parallel workflow never touched | Reversible per capability; as-found reproducible; divergence reportable (FR-POL-05) | Needs golden harness first (CT-H); adapter upkeep | High fit; resilience High; lock-in none |
| C. Dual-write to legacy and new stores | Write decisions to both | Keeps legacy reports populated | Legacy has no decision write path (RC-1) so there is nothing to mirror; consistency problems; violates read-only boundary | Poor |

### Decision / recommendation
Recommend B. Cut-over per capability, never before: executable golden harness green and mutation gate killing the mutants (R-1), hermetic fixtures (R-2), and an approved change (HAR-06) for any deviation. Legacy modules are not edited in R1.

### Consequences
- Positive: STOP-12 style regressions are detectable; legacy figures remain reproducible for comparison.
- Negative: reports exist twice until cut-over; two vocabularies (five status vocabularies, RC-7) mapped in adapters.
- The `defaulted` marker (FR-POL-06) is added in the new rule service only; legacy output is unchanged.

### Trigger to decide / revisit
Decide at Stage 14 (transformation plan); hard prerequisite for any Stage 15 code change.

## Evidence References
app/legacy_logic.py; legacy_js/legacy_policy.js; legacy_batch/shift_reconciliation.py; docs/07-repo-assessment/characterization-test-plan.md; docs/09-initial-prd/functional-requirements.md

## Assumptions
A-10-04 Goldens in docs/07 remain valid for baseline 125/4100 (OD-09).

## Unknowns
U-10-05 Who consumes the SQL/Java month-end outputs; U-10-06 owner of parallel workflow (OPD-15).

## Unresolved Issues
OPD-04 (which rule is authoritative) unresolved; ADR-007 keeps all three loadable.

## Residual Risks
Shadow comparison may be skipped under schedule pressure; golden drift.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

