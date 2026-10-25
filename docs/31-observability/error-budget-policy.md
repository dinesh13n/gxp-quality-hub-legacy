---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "error-budget-policy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/slo.py", "hub/obs/alerts.py (ALT-13)", "docs/37-operating-model/change-governance.md", "docs/37-operating-model/escalation-model.md", "tests/hub/test_tst_hub_stg31_slo_alerts.py", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
A candidate policy for what to do as an error budget is used up. It is **not enforced by any code, gate or freeze**; the only automatic part is alert ALT-13, which lists SLOs in RED or EXHAUSTED. Enforcement would need an owner who can approve exceptions, and today that is Dinesh Naik alone (all other roles VACANT, OD-34), so the policy is a decision aid and a record format.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EB-1 Definitions
Budget = events x (1 - target). Remaining % = (allowed bad - actual bad) / allowed bad. Computed by `slo.evaluate`; a window with no events is NO_DATA; a target of 100 % has no budget (any bad event exhausts it).

### EB-2 States and consequences (candidate)
| State | Remaining | Consequence |
|---|---|---|
| NO_DATA | no events | no consequence; state the gap in the next status note |
| GREEN | >= 50 % | normal change flow (change-governance.md) |
| AMBER | 10 % to < 50 % | review the top error contributors (log lines by `op_id` / `error_code`) before the next behaviour change |
| RED | > 0 % to < 10 % | only reliability, security and corrective changes ship; record why for any other change |
| EXHAUSTED | <= 0 % | change freeze for behaviour changes until a post-incident review is written and Dinesh decides; ALT-13 lists it |

### EB-3 Procedure when ALT-13 fires
1. Run the evaluation again with the same inputs (determinism check). 2. Identify the SLO and its SLI source. 3. Use RB-10. 4. Write one paragraph in the run notes: cause, change decision, who decided. 5. A waiver is Dinesh's decision and is recorded; the agent never waives (HAR-11, TP-14).

### EB-4 Exemptions
Planned restore rehearsals, sandbox work and test traffic are not product traffic; they must not be counted (the evaluator is fed product samples only). Client errors (4xx) do not consume SLO-03 budget.

### EB-5 Invariants and integrity
Invariants INV-01..03 and SLO-04 have no budget; a breach is an incident under the Stage 29 severity matrix, not a budget conversation.

### EB-6 Review
Re-derive all numbers after 30 days of real use (D-31-10). Before then the policy is expected to be adjusted; changes are recorded as versions of this file (never silent overwrites).

## Evidence References
`hub/obs/slo.py` `evaluate` / `state_of`, test S01 (state boundaries), `docs/37-operating-model/change-governance.md`.

## Assumptions
- A-31-03 50 / 10 % thresholds from common SRE practice, not from this hub's history.

## Unknowns
- U-31-12 Whether a change freeze is workable with one engagement lead.

## Unresolved Issues
- No enforcement hook by design; a release-gate link would be a behaviour change (not proposed).

## Residual Risks
- RR-31-14 A freeze rule nobody can enforce becomes theatre. Low; the policy says it is a decision aid.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
