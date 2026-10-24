---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "security-test-results.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Results of the Stage 24 run. New tests: 21 methods in group S24 (21 ok) and 1 in E24 (1 ok), both executed = expected. Mutation gate: 8 of 8 mutants killed. Re-run groups: B 42 (41 ok, 1 skipped), A 45, I8a 35, I8b 43, I9 33, all green. Characterization harness: 133 of 134 pass, OVERALL FAIL due to one environment drift (CT-13 batch:node_cwd_other, Node.js patch version in a stderr tail changed from v22.23.2 to v22.23.4). That is not caused by this stage and was not fixed (S24-DEV-04). Backup checksums rc 0 before and after.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TR-1 Counts [Verified Fact: runner output saved as `evidence/regression-s24.json`]
| Group | Executed | Expected | Result |
|---|---|---|---|
| S24 | 21 | 21 | ok |
| E24 | 1 | 1 | ok |
| B | 42 | 42 | 41 ok, 1 skipped (inner egress run) |
| A | 45 | 45 | ok |
| I8a | 35 | 35 | ok |
| I8b | 43 | 43 | ok |
| I9 | 33 | 33 | ok |
### TR-2 Mutation gate [Verified Fact] 8 of 8 killed (`evidence/hub-mutation-s24.json`).
### TR-3 Findings from the work [Verified Fact]
| ID | Finding | Severity | Outcome |
|---|---|---|---|
| F-S24-01 | Scan guarded 18 of 44 tables (RF-02) | Medium | closed: register + S01..S04 |
| F-S24-02 | Cookie lacked `Secure` when TLS exists (A-INC08-3) | Low | closed (conditional) |
| F-S24-03 | C3 reason only in URL | Low | header added, query kept (RS-09) |
| F-S24-04 | Anchor file editable by anyone with host access | Medium | seal built, OFF (RS-03) |
| F-S24-05 | No lint for dynamic SQL | Low | baseline test S32 (59 sites reviewed) |
| F-S24-06 | `schema_migrations` has no trigger; `case_state`, `active_ruleset` mutable | Low | recorded (RS-12) |
| F-S24-07 | Login POST has no CSRF token; token in login body | Low | accepted proposal (RS-07) |
| F-S24-08 | No per-source rate limiting | Low (loopback) | open (RS-04) |
| F-S24-09 | Hostile corpus: no 500, no active markup, no header injection | none | pass |
### TR-4 Characterization [Verified Fact]
133/134; failing case CT-13 `batch:node_cwd_other`; cause Node patch drift on the laptop. Interpretation: [Inference] environment, not product regression, because hub and legacy code paths were not changed by this stage (legacy byte-identical, TST-CO-05).
### TR-5 Deviations
S24-DEV-01 groups and allow-list reset; S24-DEV-02 `scan.py` edit; S24-DEV-03 `app.py` edit; S24-DEV-04 CT-13 drift; docs path `docs/24-security-privacy/` per the stage instructions; one `python3` run in the working tree at the start (pycache removed); git lock files removed after the delete permission; earlier-stage families not re-run except the groups above.

## Evidence References
`evidence/regression-s24.json`, `evidence/hub-mutation-s24.json`, harness output in the sandbox log, `non_add_edits.json`.

## Assumptions
- A-S24-TR-1 The CT-13 failure is environmental; the orchestrator's cloud run is the authority for full regression.

## Unknowns
- U-S24-TR-1 Full-regression result at this commit (not run here).

## Unresolved Issues
- Characterization OVERALL FAIL (1 case) pending an environment decision: update the golden or pin Node.

## Residual Risks
RS-10, RS-14.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
