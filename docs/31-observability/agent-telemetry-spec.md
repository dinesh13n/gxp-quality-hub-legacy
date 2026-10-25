---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "agent-telemetry-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/22-agentic-engineering/not-applicable.md", "docs/37-operating-model/agent-tool-ownership.md", ".fde/orchestrator-decisions.md (OD-27)", "docs/23-human-control/", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
**Not applicable: the product contains no AI agent** (no model, no tool-calling loop, no autonomous trajectory; Stage 22 NOT APPLICABLE, OD-27). What is observable instead are the hub's *automated actors that are not agents*: the service and rule actors. Their controls are already telemetry: `zone_h_service_actor_accepted` (must be 0, ALT-03), `zone_h_service_actor_rejections_total`, `zone_h_attempts_total{action,outcome}`, `override_total{action}` and the `actor_kind` field on every log line.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AG-1 N/A statement [Verified Fact]
No agent trajectory, plan, tool call, memory or handoff exists in `hub/`. Nothing is instrumented for them and none is invented.

### AG-2 The nearest real signals
| Signal | Meaning | Alert |
|---|---|---|
| `zone_h_service_actor_accepted` | a non-human actor completed a Zone H act | ALT-03 SEV-A, absent sensor fires |
| `zone_h_service_actor_rejections_total{action}` | service actors refused (AC-GATE-09 evidence) | none (expected non-zero when tested) |
| `actor_kind` on log lines | human / service / rule / system | trace summaries show it per span |
| `override_total{action}` | human overrides of flags | none (rate review, KPI) |

### AG-3 Engagement agents are not product telemetry
The orchestrator and stage agents (AT-01..AT-03 in `agent-tool-ownership.md`) are development tooling; their activity is evidenced by git history, regression logs and the decisions log, not by product telemetry (OD-08).

### AG-4 If agents are ever introduced
Re-open Stage 22 first. Telemetry would need trajectory ids, tool-call outcomes, step budgets and human-approval events under the same privacy rules (ids and hashes only).

## Evidence References
`docs/22-agentic-engineering/not-applicable.md`, `hub/obs/collect.py` (Zone H samples), `hub/obs/log.py` (`actor_kind`).

## Assumptions
- A-31-13 Stage 22 stays NOT APPLICABLE.

## Unknowns
- None.

## Unresolved Issues
- None.

## Residual Risks
- RR-31-09 None specific to this artifact.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
