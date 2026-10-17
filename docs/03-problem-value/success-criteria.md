---
stage: "3 — Frame Problem & Value"
artifact: "success-criteria.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/domain-assurance.md", "docs/baseline-measurement-notes.md", "docs/operations-service-levels.md", "docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/02-stakeholders/stakeholder-conflicts.md"]
supersedes: "none"
---
## Summary

Measurable success and failure criteria. **No baseline has been measured**, so improvement thresholds are expressed as *relative to a Stage-4 baseline* or as absolute safety/integrity invariants. Every threshold is a **provisional Assumption, owner Engagement lead (Dinesh Naik)**; none was agreed by a stakeholder. Metric names come from `docs/domain-assurance.md`. Each KPI that depends on "closed"/"resolved" is reported **separately under each candidate definition (D-OPS, D-EVID, D-FIN)** and no definition is chosen here (SC-01/02). Label: synthetic, unvalidated.

## Findings

### Candidate definitions (provisional, not policy)

| Tag | Candidate meaning | Source of the candidate |
|---|---|---|
| D-OPS | Operations marks the case closed (local status) | `operations-vs-risk-2024.md`; `business-context.md` |
| D-EVID | Closed AND verifiable evidence and authorised approver recorded | Compliance position, same source |
| D-FIN | "Successfully resolved" for cost purposes | Finance, **undefined** [Unknown] |

### Success criteria

| ID | Criterion | Measure and window | Baseline | Provisional threshold | Req | Class |
|---|---|---|---|---|---|---|
| SUC-01 | No unsafe action | Unsafe action count over evaluation window | 0 required invariant | = 0 | BR-08, BR-09 | [Verified Fact] (requirement from `domain-assurance.md`); the value 0 is an invariant |
| SUC-02 | Source attribution | % of sampled decisions with evidence and source | Unmeasured (Stage 4) | 100 % of sample | BR-07 | [Assumption] |
| SUC-03 | Definition transparency | % of reported figures with a definition tag | Unmeasured | 100 % | BR-01 | [Assumption] |
| SUC-04 | Time to close under D-OPS and under D-EVID, reported separately | Median and 90th percentile, receipt to state | Unmeasured | Improve vs baseline; magnitude set after baseline | BR-03 | [Assumption] |
| SUC-05 | Time to evidence | Median hours from receipt to evidence-complete | Unmeasured | Improve vs baseline | BR-07 | [Assumption] |
| SUC-06 | Unmatched/orphan references | % of external items not matched to a case on arrival | Synthetic DB: 8,394 of 8,567 partner-feed rows unmatched (IO-10) — test residue, **not** a business baseline | Baseline dataset first (OD-02); target set after | BR-04 | [Verified Fact] (synthetic value); target [Assumption] |
| SUC-07 | Replay safety | Queue size and totals change when an already-processed item is re-delivered | Unknown | 0 change | BR-05, NFR-11 | [Assumption] |
| SUC-08 | Reconciliation delay | Hours from source event to matched record | Unmeasured | Within NFR-03 (4 h) and NFR-02 (06:00) provisional targets | BR-06 | [Assumption] |
| SUC-09 | Backlog ageing and unresolved exception rate | Count and age distribution per site | Unmeasured | Improve vs baseline | BR-12 | [Assumption] |
| SUC-10 | Month-end comparability | Ops vs finance totals reconcile on one cut-off | Differ today (claim, SC-04) | Difference = 0 on agreed cut-off | BR-10 | [Assumption] |
| SUC-11 | Decision recorded | Definition/closure-time decision has owner and date, or "accepted open" record | None | Exists | BR-02 | [Verified Fact] (gap) |

### Failure criteria (any one means the framing or solution fails)

| ID | Failure condition | Trigger | Action |
|---|---|---|---|
| FAIL-01 | Any unsafe action (an automated or simulated disposition, or closure without evidence and no authorised exception) | SUC-01 > 0 | Stop; STOP-07/HAR-12 |
| FAIL-02 | Improvement on one definition achieved by worsening another without a recorded owner decision | SUC-04 improves under D-OPS while D-EVID worsens | Reject result; escalate SC-01 |
| FAIL-03 | Baseline cannot be derived with documented window, denominator and exclusions | NFR-16 not met | Do not claim any improvement |
| FAIL-04 | Replay or duplicate raises exception queue or totals | SUC-07 ≠ 0 | Reject |
| FAIL-05 | Value claimed from synthetic data presented as client result | Any KPI without "synthetic, unvalidated" label | Withdraw claim (ER-01) |
| FAIL-06 | Measured effect of the problem is negligible after baselining (H1-H3 falsified) | Stage 4 / 6 finding | Reframe or stop (kill criterion) |

## Evidence References

`docs/domain-assurance.md` (metric names, safety acceptance); `docs/baseline-measurement-notes.md` (data window, denominator, exclusions); 0A IO-10.

## Assumptions

- A-03-12: Thresholds are placeholders pending baseline and an owner. A-03-13: relative "improve vs baseline" is acceptable until magnitudes are set at Stage 4.

## Unknowns

- U-03-14 Baseline for every KPI. U-03-15 Minimum worthwhile effect size.

## Unresolved Issues

- Thresholds cannot be made quantitative until Stage 4 and until a decider sets D-FIN.

## Residual Risks

- A relative target is easy to meet trivially; Stage 4 must fix magnitudes.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial criteria. |
