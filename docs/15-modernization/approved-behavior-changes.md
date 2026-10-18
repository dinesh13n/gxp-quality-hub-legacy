---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "approved-behavior-changes.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)"]
supersedes: "none"
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

## Evidence References
- `behavior-preservation-evidence.md` BP-2 (D3/D4 = 0, D5 = 0); `docs/14-transformation/transformation-gates.md` TG-4.

## Assumptions
- None.

## Unknowns
- None.

## Unresolved Issues
- DV-01..DV-09 and OD-S12-13 remain open (not needed for INC-01).

## Residual Risks
- None for INC-01.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
