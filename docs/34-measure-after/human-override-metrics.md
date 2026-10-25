---
stage: "34 — Measure After-Intervention KPIs"
artifact: "human-override-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/26-tevv/tevv-results.md (TR-7, TR-8)", "docs/26-tevv/walkthrough-records.md", "docs/12-specs (OVERRIDE_RECORDED event type)", "hub/decision schema (decision_events.event_type)", "docs/04-baseline-kpis/kpi-dictionary.md (no override KPI)", "docs/34-measure-after/evidence/hub-16-verify-audit.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
**Stage 4 defines no override KPI**, so none is created here (a new KPI would be a redefinition of the yardstick). This file reports only counts that exist, as descriptive counts, and says what is missing. Result: **0 overrides recorded anywhere in the hub path**, because no human has acted through the hub (0 principals; the audit log of the sandbox store holds 30 system-only records). 0 is "no opportunity", not "no need to override". On the legacy path there is no override record at all (K-01 has no action log), so the number is Unknown.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### HO-1 What exists [Verified Fact]
| Item | Observation | Source |
|---|---|---|
| Override capability in the hub | event type `OVERRIDE_RECORDED` in `decision_events`; reviewer pages offer override / dismiss / refuse for flags | decision schema; tevv-results TR-8 (agent rehearsal: offered for 3 of 3 flags) |
| Overrides recorded in the sandbox store | 0 (`decision_events` has only CASE_IMPORTED and FACT_RECEIVED, actor_kind system) | sandbox store query |
| Human actions in the audit log | 0 (30 records: CONFIG_LOADED 18, INTAKE_RUN 4, schema/seed/backfill/verify events; all system) | sandbox store query |
| Human gate for dispositions | Zone H requires an authenticated holder session and fresh re-auth; holders list EMPTY; authority switch ships off; the system cannot disposition by itself | OD-26, OD-31; Stage 26 A02..A04: 0 bypass |
| Walkthrough of the reviewer override path with a person | **not done**: TST-REV-03/04/08 unsigned; D02 was an agent rehearsal | walkthrough-records.md; OD-33 |

### HO-2 Legacy-path proxies (descriptive only, not an override KPI) [Verified Fact; meaning Unknown]
- `policy_exceptions.outcome = WAIVED`: 56 of 224 (25.0 %) and `manual_review_required` rule flags: 29 of 125 (K-16, 23.2 %). Whether a waiver is an "override" of a control is not defined by any owner (U-04-03); these are not counted as overrides in this report.
- Three divergent as-found approval/priority rule implementations (RC-4) mean that a legacy "override" cannot even be identified from code behaviour.

### HO-3 Measurements needed [Unknown; owner: Engagement lead (Dinesh Naik)]
| Measure | How | Prerequisite |
|---|---|---|
| Override count and rate | `OVERRIDE_RECORDED` events / reviewer decisions, per role, per reason, per week | real reviewers with sessions; Stage 4 v0.2 (new KPI id) if Dinesh wants a KPI |
| Override-then-reversal rate | CORRECTION events referencing an OVERRIDE_RECORDED | same |
| Overrides without approval ref / evidence | count where `basis` or `evidence_refs` empty | same; the hub is designed to refuse such an event (RH-1 'supported at mechanism level', tevv-results TR-7), so 0 is expected if the mechanism holds |
| Unsafe-action count (K-01) | disposition or closure without evidence and authorised exception | operational audit log; sandbox test result is 0 (see kpi sheet) |
| Legacy baseline of overrides | time-and-motion or ticket data from the real process | does not exist in the repo |

## Evidence References
`docs/26-tevv/tevv-results.md` TR-7, TR-8; `docs/26-tevv/walkthrough-records.md`; sandbox store queries (see adoption-metrics.md AD-1); `evidence/hub-16-verify-audit.json` (29 audit records verified; the AUDIT_VERIFIED record written by that command is the 30th).

## Assumptions
- A-34-10 [Assumption] Not creating an override KPI is the correct reading of "Exclude: redefined KPIs". Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-34-10 Every override measure in HO-3 and whether the real process has overrides at all.

## Unresolved Issues
- Walkthrough sign-off by a human (OD-33) is needed before override usability can be said to be verified.

## Residual Risks
- RR-34-08 "0 overrides" read as "reviewers agree with the hub". There are no reviewers.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
