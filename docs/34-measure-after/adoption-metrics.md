---
stage: "34 — Measure After-Intervention KPIs"
artifact: "adoption-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/kpi-dictionary.md (K-21)", "docs/34-measure-after/evidence/hub-01h-verify-chain.json", "docs/34-measure-after/evidence/hub-16-verify-audit.json", "docs/37-operating-model/ (OD-34)", ".fde/orchestrator-decisions.md (OD-19, OD-26, OD-31, OD-34)", "data/ listing of the working tree (no hub store)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
K-21 (frozen definition: **cases handled via the new capability / cases, %**, segmented by site) is **0 of 125 = 0 %** on the only basis that exists: the hub is not in production, no hub store exists in the working tree, no human principal exists, and no hub-side decision has ever been taken by a person. This is a repository-state fact plus the engagement-lead instruction for this stage. It is **not** production adoption telemetry. A sandbox shadow run (hub reads copies of the legacy data) is not adoption.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AD-1 K-21 value [Verified Fact: repo state; Assumption: not in production]
| Item | Observed | Source |
|---|---|---|
| Hub store in the working tree | none: `data/` holds `legacy.sqlite3`, `enterprise_legacy.sqlite3`, `documents/`, `archive_documents/`, `lake/` and no `hub.sqlite3` | `ls data/` 2026-10-25 |
| Cases handled via the hub (production) | 0 of 125 (K-21 = 0 %) | above + A-34-02 |
| By site (BR-12 segmentation) | 0 in each of BR-SP 25, DE-BY 30, GB-ENG 25, IN-BLR 13, JP-KN 16, US-TX 16 | 125 cases by site, Stage 4 |
| Human principals / sessions in a freshly migrated sandbox store | 0 / 0 (`principal`, `session` tables empty); `zone_h.holders` ships EMPTY (OD-31) | sandbox store query |
| Decisions recorded by a person through the hub | 0 (`decision_events`: 125 CASE_IMPORTED + 125 FACT_RECEIVED, all actor_kind `system`) | sandbox store query |
| Scheduler | OFF (OD-19); authority switch (DW-17) ships off (OD-26); CLI + approval_ref only (OD-31) | OD log |
| Steady-state owner accepted for any hub asset | 0 of 28 (OD-34); all roles except Dinesh VACANT | `docs/37-operating-model/` |

### AD-2 Adoption indicators that cannot be measured yet [Unknown]
| Indicator | Why Unknown | Exact measurement to supply |
|---|---|---|
| Active users per week by role (reviewer, finance, integration, Zone H holder) | no users exist | count of distinct authenticated principals with >= 1 audited action per week, from `audit_log` + `session`, per site |
| Share of new cases created or reviewed through the hub (K-21 numerator) | no production use, no cutover (Stage 30 not run) | count of cases whose first decision event is hub-authored / all new cases in the window, per site |
| Share of exceptions worked in the hub queue vs legacy | no hub queue use | reviewer-actioned queue items / queue items, per site, from the review tables |
| Parallel-run coverage | no parallel run defined | cases present in both the legacy record and hub with equal state / cases (hub `verify-projection` gives this for the backfill: 125 of 125, 0 mismatches) |
| Time-to-first-use, training, support tickets | no rollout plan executed | Stage 38+ items; none exist |

### AD-3 Coexistence parity (not adoption) [Verified Fact; sandbox]
The 125-case backfill into the hub projection has 0 mismatches against the legacy snapshot (`hub-01g-verify-projection.json`: projection_rows 125, mismatches 0) and the event chain verifies (`hub-01h`: 125 cases, 250 events, ok). This shows the hub *can* mirror the legacy state; it says nothing about use.

### AD-4 Adoption readiness blockers (carried, none new) [Verified Fact]
Zone H holders empty (OPD-06); owners vacant (OD-34); HAR-07 CI install pending; real tenant/regime/retention undecided; walkthroughs TST-REV-03/04/08 unsigned (OD-33); off-device backup HAR-09 and a live tabletop open (OD-35). These bound any near-term adoption number to zero or to a controlled pilot.

## Evidence References
`ls data/` of the working tree; sandbox store `~/fde_sbx/s34-scratch/data/hub.sqlite3` (queries recorded in this stage's run; not committed, regenerable with `evidence/run_hub_metrics.sh` then `run_hub_intake.sh`); `evidence/hub-01g-verify-projection.json`; `evidence/hub-01h-verify-chain.json`; OD-19, OD-26, OD-31, OD-34.

## Assumptions
- A-34-02 (see after-intervention-kpi-sheet.md): hub not in production. Confirm: Engagement lead (Dinesh Naik).
- A-34-08 [Assumption] K-21's "new path" means the hub (Stage 4 text: "new capability"); no narrower capability list was agreed. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-34-08 Whether any pilot, demo or parallel run with real people has happened outside the repo. Owner: Engagement lead (Dinesh Naik). If yes, supply dates, users and cases handled.

## Unresolved Issues
- No adoption target exists (Stage 3 targets are relative and provisional, A-03-13); none is set here.

## Residual Risks
- RR-34-06 "0 %" read as failure or as a baseline for growth. It is the expected state of an unreleased, unowned system.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
