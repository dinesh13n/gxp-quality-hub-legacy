---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "approved-behavior-changes.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
**No behaviour change was made or approved in INC-01.** The legacy code is byte-identical to `baseline-as-found` on all legacy paths. Deviation rows DV-01..DV-09 stay `proposed`; none is needed until a cutover step (Stage 30).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Behaviour | Legacy value | New value | Approval (HAR-06) | Increment | Tag |
|---|---|---|---|---|---|---|
| — | none | — | — | — | INC-01 | [Verified Fact] |
[Verified Fact] The INC-01 supplement golden v1 is a new *observation* of unchanged behaviour (captured on the unmodified code), not a behaviour change.

### INC-02
| ID | Behaviour | Legacy value | New value | Approval (HAR-06) | Increment | Tag |
|---|---|---|---|---|---|---|
| — | none approved; no legacy behaviour changed | — | — | — | INC-02 | [Verified Fact] |
| DV-01..DV-09 | registered in `deviation_register` with status **proposed** (F10-2 values; `hub/coexistence/seed_inc02.json`) | see `evidence/inc02/deviation-register.json` | see same | **none** - Dinesh's per-item decision OD-S12-13 is open; the product has no approve command | recorded INC-02; implemented INC-04..INC-08 | [Verified Fact] |
[Verified Fact] Because every DV row is `proposed`, `hub golden-compare` reports DV-01..DV-09 UNAPPROVED and exits 6 - the specified AC-CO-01 behaviour, not a defect. The "approved" rows used in TST-CO-01 c/d are throw-away test fixtures in a sandbox DB (approval_ref `TEST-FIXTURE-NOT-A-HAR06-APPROVAL-*`), not approvals.

## Evidence References
- `behavior-preservation-evidence.md` BP-2 (D3/D4 = 0, D5 = 0); `docs/14-transformation/transformation-gates.md` TG-4.

## Assumptions
- None.

## Unknowns
- None.

## Unresolved Issues
- DV-01..DV-09 and OD-S12-13 remain open (not needed for INC-01).
- INC-02: OD-S12-13 (preserve vs fix per DV-01..DV-09) must be decided by Dinesh before the owning modules can pass gate G1.

## Residual Risks
- None for INC-01.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
