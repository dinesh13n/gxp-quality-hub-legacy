---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "modernization-summary.md"
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
**Stage 15 status: IN PROGRESS (INC-01 of 9 delivered).** INC-01 status: **DONE WITH CONDITIONS** — the executable characterisation harness, hermetic FX-BASE125 fixture gate and mutation gate exist on branch `stage-15-inc01-harness` as new files only; on the unmodified legacy code CT-01..CT-16 pass (134/134 checks) in two identical runs, the mutation gate kills 15/15 (the shipped suite kills 1/15), the shipped tests still give their as-found result, and working-tree data were verified intact after every session. Conditions: CI cannot yet run the harness (fixture git-ignored, workflow untouched), no 3.12 parity run, AC links for CT-04..CT-16 are proposed metadata awaiting a Stage 12/13 addendum.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
1. [Verified Fact] Stage 7 verdict "NO-GO for refactoring until an executable harness and hermetic fixtures exist" — the harness and fixtures now exist and are proven to detect all 15 reference behaviour changes.
2. [Verified Fact] Legacy behaviour reproduces exactly: 132/134 checks equal with no normalisation at all, 2 equal after path/tail normalisation (D1); D5 = 0.
3. [Verified Fact] CT-11 (Java) runs: JDK 11 is present on the device, contrary to the Stage 13 gap note (ACC-8).
4. [Verified Fact] New observations pinned for later increments: `sql/legacy_reports.sql` (unrounded floats) reproduces the Stage 7 report rows when rounded to 2 dp; every write method on every route of both services returns 501; only `app/generate.py` writes the `cases` table; no disposition/release/e-signature handler exists (HAR-12 guard baseline).
5. [Inference] TG-3 INC-01 gate: exit criteria met; CG-1..CG-11 relevant items met except CG-7's No-AI guard (INC-02 by plan) and the CI aspects (RTD-01/02).

### How to run (for CI / PR description)
```sh
# from the repository root; sandbox defaults to ~/fde_sbx/s15-inc01, fixture to ../_data-backup-2026-10-17
python3 -B tests/characterization/run_characterization.py --mutation-gate
sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt
```
Details: `tests/characterization/README.md` and `how-to-run-characterization-harness.md`.

### Next
Orchestrator: review + PR + squash-merge INC-01 (OD-13). INC-02 (`hub/` skeleton, guards, RO adapters, golden-compare) uses OD-12 defaults; decide RTD-01 (CI fixture provisioning) early.

## Evidence References
- All INC-01 artifacts in this folder; `evidence/inc01/`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 CI fixture provisioning; U-15-02 3.12 behaviour.

## Unresolved Issues
- RTD-01..RTD-12 (`remaining-technical-debt.md`).

## Residual Risks
- RR-MS-1 Harness evidence is device-specific until it runs in CI on the target runtime.
- RR-MS-2 Goldens and fixture are only as trustworthy as the backup; the hash gate detects but cannot repair drift.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
