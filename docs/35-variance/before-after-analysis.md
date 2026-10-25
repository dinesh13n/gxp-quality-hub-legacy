---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "before-after-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/34-measure-after/kpi-comparability-check.md", "docs/03-problem-value/value-hypothesis.md", "docs/03-problem-value/success-criteria.md", "docs/32-finops/tco-model.md", "docs/37-operating-model/target-operating-model.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-32, OD-33, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Master analysis. **Result: no production after-data exists, so no real before-vs-after variance can be stated. The only comparable pairs are three sandbox, synthetic parity results (K-09-OPS count/site split, K-15, K-11), none an improvement.** Value leakage is therefore analysed as *intended value that cannot yet be realised or is at risk*, traced to the repository's own findings (unwired controls, vacant roles, unsigned walkthroughs, open risks, unpriced cost terms). Nothing is monetised.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BA-1 What was compared [Verified Fact]
| Side | Source | Nature |
|---|---|---|
| Before | Stage 4 `baseline-kpi-sheet.md`, `measure_baseline.output.json` (sha256 `31ffa1b2…1ba`), 125-case `data/legacy.sqlite3` (sha256 `c254649f…d70aa`, OD-02/OD-09), AS_OF 2025-12-19T07:11Z | Synthetic, test-residue DB, method validation only |
| After | Stage 34 `after-intervention-kpi-sheet.md`: (a) legacy path re-measured (identical by construction); (b) hub path in a sandbox copy | Sandbox, not production; no users, no operating period |
| Cost | Stage 32 (model spend USD 0 by design; other costs Unknown) and Stage 0C ranges (Assumptions) | Assumption / Unknown |

### BA-2 Headline findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BA-F1 | [Verified Fact] There is no production after-window, no telemetry and no adopted users; the after state is a sandbox fixture | Stage 34 CC-2, `adoption-metrics.md` AD-1 | Variance and ROI cannot be stated | High (misreading) | High | D-34-01, D-34-02 |
| BA-F2 | [Verified Fact] Exactly 3 of 22 KPI ids (27 rows) have a like-for-like pair; all are parity or a record that nobody decided | Stage 34 section C | No improvement evidence | Medium | High | none beyond BA-F1 |
| BA-F3 | [Verified Fact] 16 KPI ids are 'unchanged by construction' on the legacy path; this is a property of an additive, read-only hub, not an outcome | Stage 34 section D; RR-34-04 | Cannot support a 'no regression' claim | Medium | High | none |
| BA-F4 | [Inference] The intended value (V0, VD-01..VD-05) depends on people using the hub (reviewers spending less time on reconciliation and rework). Reasoning: all five drivers are time or incident reductions by people; K-21 = 0 of 125 and 0 principals | `value-hypothesis.md`; `adoption-metrics.md` AD-1 | Realised value today is nil by construction of adoption, not by evidence of ineffectiveness | High | Medium | Whether the hub, once adopted, reduces time (untestable without time capture, K-22 Unknown) |
| BA-F5 | [Verified Fact] The hub adds controls (evidence-required decisions, definition tags, replay safety) whose mechanism is tested in the sandbox (K-03 4 of 4 tagged values; K-07 replay `ok: true`; Stage 26 attack suite 0 unsafe actions) but whose operational effect is Unknown | Stage 34 rows K-01, K-03, K-07 | A control that is built and tested is not value realised | Medium | High (tests) / Low (effect) | Stage 30/31 data |
| BA-F6 | [Verified Fact] Value leakage exists as *potential* in 17 documented places (see `value-leakage-analysis.md`), none priced | `value-leakage-analysis.md` | Intended value at risk before it starts | Medium | Medium | priced inputs: 0C C-1..C-5 |

### BA-3 What can honestly be said
1. Legacy numbers are unchanged; the hub reproduces the legacy backlog count and site split and the reopen count in a sandbox (parity).
2. A K-11 record exists; it records that DR-20/DR-21 are undecided.
3. No time, cost, quality, adoption or benefit claim is supported. This follows Stage 34 CC-6 and Stage 3 FAIL-03/FAIL-05.

### BA-4 Method (Execution Method steps 1-5)
1. Variance per KPI: `kpi-variance-table.md`. 2. Confounders: `confounder-analysis.md`. 3. Leakage: `value-leakage-analysis.md`, `adoption-leakage.md`, `cost-leakage.md`. 4. Attribution: `causal-findings.md`. 5. Actions: `corrective-action-backlog.md`. Benefit view: `benefit-variance.md`.

### BA-5 Stage 35 gate (agent computation; a recommendation, not a decision)
**CONDITIONAL PASS.** Met: confounders analysed; leakage quantified by repository counts only (no money); corrective actions recorded with owner; all nine artifacts exist (in `docs/35-variance/`, A-35-01). Not PASS because the analysis rests on sandbox evidence and the user-visible value cannot be measured until Stage 30/31 data exist. Not BLOCKED because recording 'no after-data' honestly is a valid Stage 35 result under the scope fixed by the orchestrator; the non-blocking gaps have an owner (Engagement lead, Dinesh Naik) and the due condition 'before any pilot or production use' (no calendar date exists). Stage 36 may proceed only on the basis that it will find no benefit to compute (Stage 34 section F).

## Evidence References
`docs/34-measure-after/*` (all seven documents); `docs/04-baseline-kpis/*`; `docs/03-problem-value/value-hypothesis.md`, `success-criteria.md`; `docs/32-finops/*`; `docs/37-operating-model/target-operating-model.md`, `raci.md`; `.fde/orchestrator-decisions.md`.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-03 Whether any real reviewer time is saved (no time capture; K-22 Unknown).
- U-35-04 Real volumes, labour rate, cost per case (Stage 0C C-1..C-5 open).

## Unresolved Issues
- Open from earlier stages and not touched here: RS-01..RS-16, F-11 remainder, RP-01..RP-12, VA-01..VA-07, RTR-01..RTR-15, D-27-01..09, D-28-01..10, Q-29-xx, Stage 32 items, Stage 34 D-34-01..08. None is accepted by this stage.

## Residual Risks
- RR-35-03 Stage 36 builds an ROI on parity numbers. Mitigation: Stage 34 section F, this file BA-3.
- RR-35-04 'Conditional pass' read as 'value delivered'. Mitigation: BA-5 wording.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
