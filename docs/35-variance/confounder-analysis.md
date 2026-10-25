---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "confounder-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/34-measure-after/kpi-comparability-check.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/04-baseline-kpis/measurement-methodology.md", "docs/04-baseline-kpis/baseline-data-quality.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-32, OD-33, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Confounders that prevent attributing any before/after difference (or equality) to the intervention. **Because no production after-window exists, the dominant confounder is that the 'after' is a sandbox fixture; the second is that the hub imports the legacy state, so parity is built in.** Eleven confounders are recorded with their effect on each C1 row.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CF-1 Confounder register
| ID | Confounder | Evidence | Direction/effect on interpretation | Affects | Controllable? | Confidence |
|---|---|---|---|---|---|---|
| CNF-01 | [Verified Fact] No after-window, no exposure, no users: after = sandbox fixture | Stage 34 CC-2 | Nothing about real use can be inferred | all | Only by a real pilot/window (D-34-02) | High |
| CNF-02 | [Verified Fact] The hub backfills legacy status (125 cases, 250 events, 0 mismatches), so K-09 count/site and K-15 equal the baseline by construction | AD-3; K-15 row | Parity cannot distinguish 'works' from 'copied' | K-09-OPS, K-15 | No (property of backfill) | High |
| CNF-03 | [Verified Fact] Legacy data and script are untouched, so legacy re-measure is identical by construction | Stage 34 CC-1, RR-34-04 | 'Unchanged' is not 'no regression' | 16 KPI ids | No | High |
| CNF-04 | [Verified Fact] Synthetic, generator-bounded data; test-residue DB; K-06/K-08/K-09U/P-01..P-04 are proxies | OD-07; baseline-data-quality | Neither side represents an organisation | all | No | High |
| CNF-05 | [Verified Fact] A-04-01 refuted: `operating_costs.total_cases` is not 'cases created'; K-10 compares unrelated populations; K-12/K-13 divisor 108 not 125 | OD-07 | Baseline cost KPIs are mis-specified on both sides | K-10, K-12, K-13 | Yes: Stage 4 v0.2 addendum (D-34-04) | High |
| CNF-06 | [Verified Fact] Reference time differs: frozen AS_OF 2025-12-19T07:11Z vs hub wall clock 2026-10-25 (310 days later) | CC-2 | Ageing differs by construction | K-09 age | Yes: `as_of` parameter (D-34-03) | High |
| CNF-07 | [Verified Fact] Population/classification differs for exceptions and feeds (8,335 queue items vs 224 policy exceptions; 173 vs 168 linked) | CC-3, CC-4 | Rates not comparable | K-06, K-09U | Partly | High |
| CNF-08 | [Verified Fact] Definitions are candidates: `D-OPS@1` policy status `candidate`, none adopted; D-FIN undefined | CC-4; A-34-06 | A different adopted definition would move K-09, K-04 | K-09-OPS, K-04 | Needs Dinesh/decider (DR-20/21) | High |
| CNF-09 | [Verified Fact] Many concurrent changes between baseline and sandbox: Stages 15-29 changed behaviour (401 for anonymous unknown action, 400 lone surrogate, rate limit 429, 408, 503, restricted-evidence placeholder, etc.) | OD-34, OD-35 | Even a real after-difference could not be assigned to a single change | all hub-path values | No | High |
| CNF-10 | [Verified Fact] Environment differences: laptop Python 3.10.12 vs cloud 3.13 (10/16 CT goldens differ by environment only); Python 3.12+ target unproven | OD-23, OD-33 | Test-based evidence is environment-specific | K-01, K-07 (test-sourced) | Partly | Medium |
| CNF-11 | [Inference] Single analyst/operator: every measurement, definition and approval passes through one person and one agent; no independent review | OD-04 | Measurement bias cannot be detected | all | Needs a second reviewer | Medium |
| CNF-12 | [Verified Fact] Stage 4 freeze unsigned; baseline dataset confirmed (OD-09) but Q-02-05 (closed/resolved/48h) accepted open | `kpi-baseline-signoff.md` | Yardstick provisional | all | Yes | High |
| CNF-13 | [Inference] No control group or parallel unexposed population; no pre-trend (one snapshot, AS_OF 2025-12-19) | Stage 4 | No counterfactual; time trend and seasonality unknowable | all | Pilot design | High |

### CF-2 Confounder effect per computed variance
| Row | Confounders that apply | Net effect on the reading |
|---|---|---|
| K-09-OPS count/site | CNF-01, 02, 04, 08, 12, 13 | Parity is expected; no information about performance |
| K-15 | CNF-01, 02, 04, 12 | Imported status equals itself |
| K-11 | CNF-01, 08, 11 | A record exists because a decision was deferred in OD-22; process artefact |

### CF-3 Rule applied
Prompt constraint 'do not attribute change to the intervention without addressing confounders': every row above is addressed; none can be neutralised from repository evidence, so **no attribution is made** (see `causal-findings.md`).

## Evidence References
`docs/34-measure-after/kpi-comparability-check.md` CC-1..CC-6; `after-intervention-kpi-sheet.md`; `docs/04-baseline-kpis/baseline-data-quality.md`, `kpi-baseline-signoff.md`; OD-04, OD-07, OD-09, OD-23, OD-33..OD-35.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-11 Seasonality/trend of the real process (unknowable from one snapshot).
- U-35-12 Whether any real reviewer behaviour would differ from the sandbox.

## Unresolved Issues
- CNF-05, CNF-06 can be reduced by D-34-03/D-34-04; the rest need a real window.

## Residual Risks
- RR-35-13 A future pilot repeats these confounders (no control, concurrent changes). Mitigation: corrective actions CA-04, CA-05.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
