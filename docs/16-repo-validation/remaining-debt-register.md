---
stage: "16 — Validate the Good Repo"
artifact: "remaining-debt-register.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/*.md (this stage's findings)", "docs/15-modernization/remaining-technical-debt.md (RTD-01..RTD-90)", "docs/15-modernization/modernization-summary.md (Stage 15 close-out hand-over)", "docs/07-repo-assessment/technical-debt-register.md (legacy debt)", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository. Owners are engagement roles; no real stakeholder is named beyond the engagement lead (OD-04). Due points are stage-relative, as in Stage 15.**

## Summary
16 new debt items were found in Stage 16 (S16-D01..S16-D16); none blocks Stage 17. Stage 16 also **partially closes** three Stage 15 items (RTD-42 boundary parity, RTD-76 / RTD-89 mutation gates) and **re-confirms** the Stage 15 open items that still stand (carried by reference, not copied, so the Stage 15 register stays the single source for them). Legacy debt (Stage 7) is unchanged because the legacy estate is unchanged.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### D-1 New debt found in Stage 16
| ID | Debt | Source finding | Impact | Risk | Owner | Due | Tag |
|---|---|---|---|---|---|---|---|
| S16-D01 | golden-compare still uses 7 **declared** new-side values; replace with observations of the built modules (the Stage 16 `s16_observe.py` shows how) | BD register, AC-05 | comparison gate cannot detect a module regression | Medium | orchestrator (build agent) | before any CUT step; plan at Stage 17 | [Verified Fact] |
| S16-D02 | Deviation register maintenance: DV-07 new value under-specified (outcome classification), DV-09 label `envelope_invalid` vs built `MISSING_ENVELOPE_FIELD`, DEV-29 partial-year match has no DV row (propose DV-10/DV-11) | BD-07, BD-09, BD-10 | decision-maker sees an incomplete list of behaviour changes | Medium | Engagement lead (Dinesh Naik) decides; agent drafts | Stage 17 addendum | [Verified Fact] |
| S16-D03 | Seven migration sets / version tables / runners | AC-01 | operator error on migrate / restore | Medium | orchestrator | Stage 17 design, Stage 27 | [Verified Fact] |
| S16-D04 | Zone H holder check implemented three times | AC-02 (RTD-46/51) | inconsistent rule changes | Medium | orchestrator | first increment that allows non-add edits | [Verified Fact] |
| S16-D05 | Two server entry points | AC-03 (RTD-81) | exposure ambiguity | Medium | Engagement lead (Dinesh Naik) | Stage 27/30 | [Verified Fact] |
| S16-D06 | Domain -> HTTP-layer imports; 6 two-package and 10 three-package module-level cycles | AC-2 / AC-04 | extraction / isolation cost | Medium | orchestrator | Stage 17 refactor plan | [Verified Fact] |
| S16-D07 | Runtime floor 3.10 vs ADR-018 3.12; Python 3.10 line end-of-life (Oct 2026); device 3.10.12 behind final 3.10 patches; SQLite version changes legacy float sums | DS-03, DS-04, ENV-4 | security support; comparison baseline | High (production) | Engagement lead (Dinesh Naik) - OD-S12-12 | Stage 17 decision, Stage 27 | [Inference] |
| S16-D08 | 12 pyflakes findings; 11 functions above McCabe 15 | TR-06 | maintainability | Low | orchestrator | with S16-D04 | [Verified Fact] |
| S16-D09 | Security test gaps: header **values** not asserted (H3), "loopback even with approval" bind refusal untested (H5) | SS-04, SS-08 | hardening regressions pass | Medium | orchestrator | Stage 23 test addendum | [Verified Fact] |
| S16-D10 | Orchestrator `full_regression.sh` omits TST-CO-03 (3 methods) | RG-03 | rule parity test may silently stop | Medium | orchestrator | next regression run (one-line fix) | [Verified Fact] |
| S16-D11 | Stage 12 schemas lag the code (intake-outcome, metric-value additive fields); 12 of 16 schemas not executed by any test | DC-02, DC-03 | consumers reject valid hub objects; drift unnoticed | Medium | Engagement lead (Dinesh Naik) approves addendum; orchestrator adds tests | Stage 17 addendum, Stage 23 | [Verified Fact] |
| S16-D12 | CLI error output not in the error-envelope shape | SS-07 | operator tooling | Low | Stage 17 author | Stage 17 | [Verified Fact] |
| S16-D13 | Human walkthroughs TST-REV-03/04/08 not run | TR-02 | reviewer UX unproven | Medium | Engagement lead (Dinesh Naik) | Stage 26 TEVV or accept-open | [Verified Fact] |
| S16-D14 | CT-H3 normaliser does not cover non-`~/fde_sbx` sandbox paths; no reviewed baseline for a non-3.10 runtime (ENV-1..6) | behavior-difference-report ENV | harness tied to one device | Medium | orchestrator; reviewed `--update-golden` needs Dinesh | Stage 27 | [Verified Fact] |
| S16-D15 | Source contract fails for 3 of 4 shipped sources; enforce mode unusable on this data | DC-04 | contract or data wrong - owner Unknown | Medium | Engagement lead (Dinesh Naik) | Stage 17 (OD-S12-11) | [Verified Fact] |
| S16-D16 | Hub tests validated on Python 3.13 only in Stage 16 (OD-23); the reference 3.10.12 hub run is the INC-09 one | regression-results A-16-RG-1 | small environment gap | Low | orchestrator | next laptop hub run | [Verified Fact] |

### D-2 Stage 15 items changed by Stage 16
| RTD | Change | Evidence | Tag |
|---|---|---|---|
| RTD-42 | **Partially closed**: 105 boundary cases (15 limits x 7 offsets down to 1e-10) identical between legacy JS doubles and the hub Decimal engine; untested: other functions and random amounts | boundary-cloud.json | [Verified Fact] |
| RTD-76 | **Partially closed**: INC-08 hub mutation gate run, 3/5 KILLED; survivors -> S16-D09 | hub-mutation.json | [Verified Fact] |
| RTD-89 | **Closed for the sampled mutants**: INC-09 5/5 KILLED | hub-mutation.json | [Verified Fact] |
| RTD-15 | Still open in code; evidence gap closed for Stage 16 by observation -> S16-D01 | behavior-difference-report | [Verified Fact] |
| RTD-52 / RTD-65 | Mutation gates for INC-05 / INC-07 still not run (not in Stage 15's Stage 16 hand-over list) | — | [Verified Fact] |

### D-3 Stage 15 items carried unchanged (by reference to `docs/15-modernization/remaining-technical-debt.md`)
- Human decisions (owner Engagement lead, Dinesh Naik): DV-01..DV-09 preserve-or-fix OD-S12-13 (RTD-20/41/57); Zone H holders OD-S12-06 (RTD-57/75/84); rule-set activation OD-S12-04; scheduler vs HAR-10 OPD-11 (RTD-59); retention OD-S12-09 (RTD-30); definitions OPD-01..06 (RTD-61); security values (RTD-26); FR-REV-04 keep/reject (RTD-87); labelled search set OPD-12 (RTD-80).
- Stage 12 addenda: RTD-13/23/24/38/47/55/58/66/78 (codes, exit codes, config keys, audit actions, DDL addenda).
- CI and environment: RTD-01/02/14 (CI), RTD-03/18/79 (runtimes), RTD-04 (coverage), RTD-05 (CT-17/18), RTD-31 (runner disk), RTD-28 (subTest recording).
- Security (Stage 24): RTD-29/34/36/70/77/82/83/90.
- Other open Stage 15 items keep their Stage 15 status.

## Evidence References
- See each source finding in this folder; Stage 15 register for carried items.

## Assumptions
- A-16-DR-1 [Assumption] Stage-relative due points are acceptable in place of calendar dates (no delivery calendar exists in the engagement). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-16-DR-1 Calendar dates and capacity for the debt (no plan beyond the stage sequence).

## Unresolved Issues
- All items above are open by definition.

## Residual Risks
- RR-DR-1 S16-D07 (EOL runtime) is the only High item; it matters only once anything leaves the sandbox shadow.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
