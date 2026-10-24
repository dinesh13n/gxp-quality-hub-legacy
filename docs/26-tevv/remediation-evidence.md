---
stage: "26 — TEVV + AI Red Teaming"
artifact: "remediation-evidence.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/red-team-findings.md", "tests/hub/non_add_edits.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW.**

## Summary
Nothing was remediated in Stage 26. This is a VALIDATE stage: `hub/`, legacy code and `data/` are byte-identical to `main` (7c60c09); no threshold, dataset or test was changed after a result. This file records that fact and routes each finding for the next stage. A route is a proposal; no owner has accepted anything.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RE-1 Scope of change [Verified Fact]
- Files added: `tests/hub/_stg26.py`, `tests/hub/test_tst_hub_stg26_{control,input,wire,resilience,noai_walkthrough,egress_guard}.py`, `tests/hub/data_s26/adversarial_corpus_v1.json`, `docs/26-tevv/**`.
- Non-add edits (TST-CO-05 c, listed in `tests/hub/non_add_edits.json`, S26-DEV-01): `tests/hub/regression_groups.json` (groups S26 and E26 added) and `tests/hub/non_add_edits.json` (OD-27 reset). No file under `hub/` and no path under `tests/characterization/` was edited.
- Verified by `TST_CO_05` and `STG20` change-safety tests (green).

### RE-2 Routing of findings [Inference: proposal]
| Finding | Severity | Proposed route | Decision needed from |
|---|---|---|---|
| S26-F-02 restricted note in event basis | High | Stage 27 hardening: redact `basis` for restricted evidence or change the event read matrix; add a B07-style regression for the event list | Dinesh (access rule, A-15-05-1) |
| S26-F-01 pre-auth validation | Medium | Stage 27: authenticate before validating the action name | Stage 27 owner |
| S26-F-03 surrogate 500 | Medium | Stage 27: reject lone surrogates at the wire (400) or encode safely; unpin REGISTERED_500 in B02/B08 as part of the fix | Stage 27 owner |
| S26-F-05 unknown config keys | Medium | Stage 27: reject unknown keys in safety sections (or warn) | Stage 27 owner |
| S26-F-08, S26-F-09 test gaps | Medium | Stage 27: add a positive-direction tripwire test and an authority_ref refusal test on `set_enabled` | Stage 27 owner |
| S26-F-04, F-06, F-07, F-10, F-11 | Low | Stage 27 / 29 backlog | Stage 27 owner |
| RS-03 full chain rewrite | known | stays OPEN (Stage 24 seal is opt-in) | Dinesh |

### RE-3 Retest rule [Verified Fact]
Every finding is pinned by a test that fails on any OTHER occurrence (registered findings: A01, B02, B07, B08, C02, C06). When a finding is fixed, that test fails until its registration is removed in the same change, so the fix cannot go unnoticed.

## Evidence References
`tests/hub/non_add_edits.json`, `tests/hub/regression_groups.json`, `docs/26-tevv/red-team-findings.md`, `docs/26-tevv/evidence/regression/report-S26.json`.

## Assumptions
- A-26-16 [Assumption] Stage 27 is the hardening stage that consumes these findings (A-26-05).

## Unknowns
- U-26-09 Whether Stage 27 will adopt the proposed routes.

## Unresolved Issues
- All findings open.

## Residual Risks
- See `residual-tevv-risks.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
