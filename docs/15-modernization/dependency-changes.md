---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "dependency-changes.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "pyproject.toml (unchanged)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
**No dependency was added, removed or upgraded in INC-01** (HAR-07/HAR-08 not triggered; CG-7). The harness uses the Python standard library only (`unittest`, `subprocess`, `sqlite3`, `json`, `hashlib`, `shutil`, `urllib`, `concurrent.futures`). It invokes the JDK and Node that are already installed on the device, exactly as Stage 7 did. No network install was made.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| Item | Before | After | Change | Tag |
|---|---|---|---|---|
| Python packages | none beyond stdlib (pyproject `>=3.10`) | same | none | [Verified Fact] |
| Interpreter used | 3.10.12 (device) | 3.10.12 | none (E-4) | [Verified Fact] |
| JDK (CT-11) | OpenJDK 11.0.32.1 present | used, not changed | none | [Verified Fact] |
| Node (CT-13) | v22.23.2 present | used, not changed | none | [Verified Fact] |
| SQLite | 3.37.2 | same | none | [Verified Fact] |
| Network egress | — | servers bound to 127.0.0.1 only; no outbound call | none | [Verified Fact] |
[Verified Fact] No AI/LLM/ML import or call was added (OD-08); the No-AI deny-list guard itself is INC-02 (TB-07).

## Evidence References
- `evidence/inc01/final-A_report.json` `tools`; `pyproject.toml`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-02 3.12 behaviour (CT-H5).

## Unresolved Issues
- OD-S12-12 runtime decision (INC-02).

## Residual Risks
- RR-DC-1 CI pins Python 3.12 while INC-01 evidence is 3.10.12 only.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
