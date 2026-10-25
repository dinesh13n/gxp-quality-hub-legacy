---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "production-token-dashboard-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/finops-ownership.md FO-1..FO-3", "docs/33-vendor-risk/vendor-inventory.md V-01..V-11", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "hub/obs/metrics.py", "hub/obs/collect.py", "hub/ops/release.py (G5)", "docs/27-hardening/evidence/regression/final-*.json (schema hub-regression-log/v1)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
**Spec only; nothing is built or deployed.** Because the product is No-AI (OD-08), a "token dashboard" has no token series to show: ER-1 retired the token, context, loop and call budgets and says Stage 32 "should not track token metrics". This spec therefore defines a **zero-model-call and cost-control dashboard**: one tripwire panel that must read 0, a toolchain-cost panel that is manually fed because no meter exists, and a test-time panel fed from regression logs that do exist. No dashboard stack is chosen (ADR-015 "no vendor chosen"); Stage 31 telemetry has not been produced, so every production panel has no live source today.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DS-1 Panels
| Panel | Metric / source | Today's value | Source exists today? | Class |
|---|---|---|---|---|
| P1 Zero-model-call tripwire | `model_calls_total` (`hub/obs/metrics.py`, exported by `hub/obs/collect.py`) | 0 in every egress-guarded test group (E8, E9, E20, E21, E23, E24, E26, E27, C1..C3) | Yes, process-local counter and `obs_metric` rows; no production host runs it | [Verified Fact] in tests; [Unknown] in production |
| P2 Egress tripwire | `egress_attempts_total` (egress guard) | 0 in the same groups | Same | [Verified Fact] in tests; [Unknown] in production |
| P3 Zone H service-actor tripwire | `zone_h_service_actor_accepted` | 0 | Yes (query on `audit_log`) | [Verified Fact] in tests. Not a cost metric; shown because it shares the tripwire family |
| P4 Release gate G5 | `hub/ops/release.py` G5 "deny-list clean, no egress, model_calls_total = 0" | Gate defined; result per release | Yes | [Verified Fact] definition |
| P5 Deny-list scan | `hub/guards/no_ai.py` findings (`docs/27-hardening/evidence/no-ai-check.json`) | `findings: []` over hub, tests/hub, pyproject.toml | Yes (one-off evidence file) | [Verified Fact] at Stage 27 |
| P6 Regression wall time per group | `wall_seconds`, `runner_seconds` in `final-*.json` | 25 groups, 2,403 s summed on the laptop, longest 144 s (see `cost-per-request.md` CR-3) | Yes (files) | [Verified Fact] |
| P7 Run duration and backlog | `run_duration_seconds`, `run_backlog_remaining`, `run_missed_total` | no production runs | Metric implemented; no data | [Unknown] |
| P8 Toolchain and hosting cost lines FC-02..FC-06 | manual entry from invoices | none exist | **No** | [Unknown] (U-33-01, U-33-02) |
| P9 Human review time per rule-flagged item | not instrumented | none | No | [Unknown] (U-24) |
| P-X Token panels (input/output/cache/retry) | none | **Deliberately not specified** | n/a | Retired by ER-1; reinstated only if a Dinesh-approved re-qualification (RQ-1..RQ-3) creates a model client |

### DS-2 Alert rules (proposed, role-based)
- P1 or P2 > 0: SEV-B per `docs/37-operating-model/escalation-model.md` (ER-04 route: L1 blocks release, L3 decides). The agent may not clear or waive it.
- P8 gets its first non-zero entry: raise a C6 change check (`finops-ownership.md` FO-2 item 2) because a paid dependency exists.

### DS-3 Viewer roles
Cost owner role RL-09 (VACANT); toolchain owner RL-12 (Dinesh INTERIM); service owner RL-02. Access follows the permission matrix TP-01..TP-15 (OD-31); this spec grants nothing.

### DS-4 What the dashboard must never show
A forecast built from S3/S4 numbers (USD 533 / 719 per month at Base) as if it were the No-AI run cost (FF-03).

## Evidence References
`hub/obs/collect.py` header lists implemented metrics; `hub/obs/metrics.py` TRIPWIRES; `tests/hub/test_tst_hub_stg27_egress_guard.py` asserts `tripwires == {egress_attempts_total: 0, model_calls_total: 0}`.

## Assumptions
- A-32-01 The tripwire panel is the right primary "cost" panel for a product whose model spend is zero by design. Confirm: Engagement lead (Dinesh Naik).
- A-32-02 P8 is fed by hand until a meter exists. Confirm: Dinesh.

## Unknowns
- U-32-01 Where the dashboard would be hosted (ADR-015: no vendor chosen).
- U-32-02 Whether Stage 31 will produce production telemetry (no `docs/31-*` exists).
- U-32-03 Real run counts (no production runs).

## Unresolved Issues
- No Stage 31 telemetry spec exists to join to; this spec is built from code in `hub/obs/`.
- Panels P7 to P9 have no data.

## Residual Risks
- RR-32-01 A tripwire that reads 0 because nothing increments it is weak evidence on its own (see `cost-guardrails.md` CG-2). Medium.
- RR-32-02 Dashboard never built; the spec rots. Low.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
