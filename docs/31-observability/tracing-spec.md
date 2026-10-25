---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "tracing-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/trace.py", "hub/obs/log.py", "hub/web/app.py", "hub/adapters/gateway_client.py", "docs/10-architecture/adrs/ADR-016-observability.md", "tests/hub/test_tst_hub_stg31_trace_cli.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
The hub has one process, one SQLite store and one outbound call type (a GET to the gateway). A distributed-tracing stack would add a dependency (deny-listed or unchosen, ADR-015) for no cross-service join, so the **correlation id is the trace id and each log line is a span**. `hub.obs.trace.build_traces` rebuilds traces from a saved log file. The one real gap is the outbound call, which carries no correlation id (F-31-07).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TS-1 Decision [Inference]
OpenTelemetry-style spans were considered and not adopted: no collector exists, adding a library needs the supply-chain controls of Stage 27 (SBOM, pinning) and the dependency deny-list, and a trace here would never leave one process. Revisit if a second service or a real source integration appears (RQ trigger: D-31-07).

### TS-2 Model [Verified Fact: trace.py, tests T01, T02]
- Trace id = `correlation_id` (BEH-OBS-01: echoed from `X-Correlation-Id` when valid, else generated; also on the audit record and error envelope).
- Span = one structured log line: `event`, `op_id`, `outcome`, `error_code`, `duration_ms`, `ts`, `actor` (pseudonymous), `run_id`, `object_ref`.
- Parent/child links do not exist; spans are ordered by timestamp, ties by input order.
- Summary per trace: span count, first / last timestamp, total span milliseconds, worst outcome (error > denied > success), error codes, event list.
- Lines that are not JSON objects, carry a field outside the log whitelist, or match a prohibited pattern are counted in `rejected` and dropped; lines without a usable correlation id are counted in `uncorrelated`. Nothing from a rejected line is returned.

### TS-3 Joins
| From | To | Key | State |
|---|---|---|---|
| log line | audit record (writes) | `correlation_id` | [Verified Fact] AC-OBS-01 |
| log line | error envelope | `correlation_id` | [Verified Fact] |
| log line | run record | `run_id` | [Verified Fact] for `OP-RUN-01` |
| run | source-side logs | none | **gap**: gateway GET has no correlation header (F-31-07) |

### TS-4 Sampling and retention
No sampling: every request is a span. Retention follows the log (LS-5): hold-all, no deletion.

### TS-5 Use
`python -m hub.obs traces --log FILE` for an incident (operational-runbook RB-05 step 2). Deterministic: the same lines give the same output.

## Evidence References
`hub/obs/trace.py`; `hub/web/app.py:186-200` (the span-producing emit); `hub/adapters/gateway_client.py` (no correlation header); tests T01 (grouping, ordering, drop of junk and leaky lines) and T02 (real WebApp request -> one correlated span).

## Assumptions
- A-31-11 A single-process hub does not need span ids or a collector for its current scope. Confirm: Dinesh.

## Unknowns
- U-31-07 Whether the real gateway would log or echo a correlation header.

## Unresolved Issues
- Outbound correlation id (D-31-07; non-add edit in `hub/adapters`).

## Residual Risks
- RR-31-07 Without parent/child links a nested operation cannot be shown as a tree. Low at current scope.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
