---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "approved-behavior-changes.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
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

### ABC-INC03 INC-03
[Verified Fact] No legacy behaviour changed in INC-03 and no approval was needed or recorded: all new behaviour (authentication, audit chain, migrations, backup/restore, release checklist) lives in new hub modules that the legacy estate does not call. DV-01..DV-09 remain `proposed` (OD-15; decided at Stage 30).
[Verified Fact] New-module behaviour that differs from a DRAFT spec is recorded as a deviation (DEV-17..DEV-27), not as an approved change.
[Assumption] The security control VALUES (PBKDF2 600,000 iterations, lockout 5 / 15 min / 15 min, session 30 min idle / 8 h absolute, step-up re-auth 300 s, password length 12) are Stage 12 proposals (A-12-F09-1) implemented as configuration; they are NOT approved values. Confirm: Engagement lead (Dinesh Naik) at Stage 24.

### ABC-INC04 INC-04
[Verified Fact] No legacy behaviour changed and no approval was needed or recorded: the rule service is a new module that the legacy estate does not call. DV-01..DV-09 remain `proposed` (OD-15; decided at Stage 30). DV-06 (the `defaulted` marker on the 999999 fallback) is now implemented in the new module as specified; it is a new-module behaviour, not an approved change of legacy output.
[Verified Fact] The three rule sets ship **inactive** (OD-16 / OD-S12-04). Loading them is not an approval of any rule, and no rule was declared correct (U-12-F03-1, RC-4 stay open).
| ID | Behaviour | Legacy value | New value | Approval (HAR-06) | Increment | Tag |
|---|---|---|---|---|---|---|
| DEV-29 | JS threshold lookup for partial years | `startsWith` prefix match (year 202 -> 15000) | 4-digit year only; else 999999, `defaulted` | **none** - Dinesh's OD-S12-13 call is open | INC-04 | [Verified Fact] |
| DEV-30 | amount 'abc' / null in the JS rule | not allowed / allowed (coercion) | `E-POL-INPUT-INVALID`, no outcome | **none** - OD-S12-13 open (BEH-POL-11 is the specified default) | INC-04 | [Verified Fact] |
[Assumption] "A recorded human decision" (OD-16) is implemented as an audit-chain record `POLICY_DECISION_RECORDED` by a configured Zone H holder (DEV-35). Confirm: Engagement lead (Dinesh Naik). `zone_h.holders` ships empty (OD-S12-06): until Dinesh names holders, nothing can be adopted or activated.

### ABC-INC07 INC-07
[Verified Fact] No legacy behaviour changed and no approval was needed or recorded. The schedule flag ships OFF and can be switched only by a Zone H holder (none configured); no metric definition, clock duration or cut-off was adopted. The month-end total differs from the legacy report by design (single-table sum, BB-08), which is a defect correction pending the owner's acceptance, not an approved behaviour change.

### ABC-INC09 INC-09
- [Verified Fact] No legacy behaviour change: legacy code and `data/` are byte-identical; the INC-01 harness is OVERALL PASS.
- [Verified Fact] New R2 behaviours are new hub capabilities in shadow, all OFF in the shipped configuration (`search.enabled` false, `search.fts` off, `templates.enabled` false); the R2 reports are read-only (audit records and consistency finding rows only). They are approved as scope by OD-22 (PRD baseline approved, refine at Stage 17); no deviation DV is approved or created by INC-09.
- [Verified Fact] Visible R2 change against INC-08 inside the hub: the five operations that answered 501 (DEV-82) now answer in `R2WebApp`; `WebApp` (R1) is unchanged.

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
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
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
