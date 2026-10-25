---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "causal-findings.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/35-variance/confounder-analysis.md", "docs/35-variance/kpi-variance-table.md", "docs/34-measure-after/kpi-comparability-check.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Causal attribution is **not supported for any KPI**. For each Stage 34 observation the table gives what it can and cannot be attributed to. The intervention is the hub (Stages 15-29), a sandbox-only deliverable; its causal effect on business outcomes is Unknown, not zero.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CA-1 Attribution table
Attribution levels: **A0** not attributable; **A1** mechanism evidence only (a test shows the mechanism works); **A2** plausible association (not used); **A3** attributable (not reached).

| ID | Observation | Candidate cause | Attribution | Reasoning | Conf. | Unresolved question |
|---|---|---|---|---|---|---|
| CSL-1 | K-09-OPS 89 = 89, sites equal | Hub backfill copies legacy state | A0 (explained by construction, not an effect) | Equality follows from import (CNF-02); no counterfactual | High | none |
| CSL-2 | K-15 6.4 % = 6.4 % | Same | A0 | Same | High | none |
| CSL-3 | K-11 0 -> 2 'accepted open' records | Decision OD-22 recording OPD-01..03 as accepted open | A0 for the hub; the record is the result of an engagement-lead decision, not of the intervention | No decider exists; a deferral was recorded | Medium | DR-20/21 decider |
| CSL-4 | K-07 replay leaves queues and totals unchanged (hub, sandbox) | Hub idempotent intake design (natural key, NOOP_DUPLICATE) | A1 (mechanism evidence on fixtures) | Verified by `verify-replay` `ok: true`, 0 conflicts; legacy value Unknown so no effect size; `raw_intake` grows 8,583 to 17,150 | Medium | Legacy replay behaviour (U-34-03) |
| CSL-5 | K-03 4 of 4 hub values definition-tagged vs 0 of 6 legacy | Hub metric registry/definition tags | A1 | Different report populations (CC-4); mechanism only | Medium | Adoption of reports |
| CSL-6 | K-01 0 unsafe actions in Stage 26 attack suite | Zone H gate and control design | A1 | Test result, not operational; mutants M5/M9/M10 survive | Medium | Operational count |
| CSL-7 | K-09U 1.0000 in the sandbox | No reviewer has acted | A0 (not performance) | 0 principals | High | none |
| CSL-8 | Legacy-path values identical | Additive, read-only hub | A0 (property of construction) | CNF-03 | High | none |
| CSL-9 | K-04..K-06, K-08, K-10, K-12..K-14, K-16..K-20, K-22 | n/a | A0 | Unknown, not comparable, or unchanged by construction | High | D-34-02 |

### CA-2 Findings
| ID | Finding | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|
| CAU-1 | [Verified Fact] No observation reaches A3; none can be attributed to the intervention | No outcome claim is allowed | Medium | High | Real window with control (CA-04) |
| CAU-2 | [Inference] The A1 items show the hub's mechanisms behave as specified on fixtures. Reasoning: tests and sandbox replays pass; this is a precondition for value, not value | Supports readiness, not benefit | Low | Medium | Operational data |
| CAU-3 | [Verified Fact] 'The intervention caused no harm' is also unproven: legacy identical by construction, hub untested in operation | Neither benefit nor harm is demonstrated | Medium | High | Pilot |
| CAU-4 | [Verified Fact] Per the prompt, change is not attributed to the intervention where confounders exist; all rows have confounders (CNF-01 at minimum) | Constraint met | Low | High | none |

### CA-3 What would make attribution possible [Inference]
A defined after-window with named exposure; a comparable unexposed population or a stable pre-trend; time-stamped closure/evidence/effort capture; hub `as_of` at the frozen reference time; adopted definitions; independent review of measurements.

## Evidence References
`docs/35-variance/confounder-analysis.md` CNF-01..CNF-13; `docs/34-measure-after/kpi-comparability-check.md`; `docs/34-measure-after/evidence/hub-12-verify-replay.json`; `docs/26-tevv/tevv-results.md` TR-4, TR-7.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-13 The true effect size of the hub on any business outcome.

## Unresolved Issues
- Same as confounder-analysis.md.

## Residual Risks
- RR-35-14 A1 mechanism evidence quoted as A3 attribution.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
