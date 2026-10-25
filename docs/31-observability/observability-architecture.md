---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "observability-architecture.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/web/app.py", "hub/web/cli.py", "hub/runs/cli.py", "hub/runs/reports.py", "hub/obs/catalog.py", "hub/obs/report.py", "hub/obs/cli.py", "docs/10-architecture/adrs/ADR-016-observability.md", "docs/28-reliability/resilience-architecture.md", "docs/29-incident-bcdr/incident-severity-matrix.md", "docs/32-finops/production-token-dashboard-spec.md", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
Observability for the hub is built from what already exists (structured JSON log lines, `obs_metric` rows, the audit log, run records, the three zero-tripwires) and adds, **additively and unwired**, a metric catalogue with a privacy/schema lint, SLO candidates with error-budget arithmetic, 13 alert rules with an evaluator, resilience telemetry, trace reconstruction from correlation ids, a text exposition and an offline CLI (`python -m hub.obs`). Nothing is sent anywhere and no shipped command changed behaviour. The zero-model-call tripwire (Stage 32) is observable end to end: store -> sample -> alert ALT-01 -> report, with a test that pulses the counter and puts it back.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OA-1 Signals and where they live today
| Signal | Source | Sink | Class |
|---|---|---|---|
| Logs | `hub.obs.log.Logger` (14-field whitelist, 21 declared events) | JSON lines to a caller-supplied sink; `hub web serve` writes them to **stderr** only | [Verified Fact] `hub/web/cli.py:62` |
| Metrics (store) | `hub.obs.collect.samples()` / `run_end_samples()` | insert-only `obs_metric` rows (`hub runs obs-snapshot`, and at every run end) | [Verified Fact] |
| Metrics (HTTP) | `hub.web.obs_http.HttpMetrics` | process memory; written to `obs_metric` by `WebApp.flush_metrics()` **only when `serve` stops** | [Verified Fact] `hub/web/cli.py:70-71` |
| Traces | none; the correlation id is on every log line, audit record and error envelope | n/a | [Verified Fact] BEH-OBS-01 |
| Audit | `audit_log` hash chain | store | [Verified Fact] (Stage 24/27) |
| Run health | `run_event` records, `hub report health`, missing-run detector | store, CLI | [Verified Fact] |
| Tripwires | `hub.obs.metrics` counters + `zone_h_service_actor_accepted` query | exported at every run end | [Verified Fact] BEH-OBS-06 |

### OA-2 What Stage 31 adds (all under `hub/obs/`, none called by any shipped command: S31-DEV-01)
| Module | Role |
|---|---|
| `catalog.py` | 36 catalogued metrics with kind, closed label set and status (19 implemented, 11 built-unwired including the evaluator's lint counter, 6 gap); `lint_samples` = privacy and schema lint |
| `slo.py` | 5 SLO candidates, 3 zero-tolerance invariants, error-budget states, burn rates |
| `alerts.py` | 13 alert rules as data and a deterministic evaluator |
| `resilience_samples.py` | counters of the Stage 28 breaker / retry budget / bulkhead / guarded gateway as samples |
| `trace.py` | traces rebuilt from log lines by correlation id |
| `expo.py` | Prometheus-style text exposition (file output; no HTTP route) |
| `report.py`, `cli.py`, `__main__.py` | one evaluation = lint -> SLO positions -> alerts; `python -m hub.obs catalog|evaluate|expo|traces` reads files only |

### OA-3 Data flow (target, with today's state marked)
```
request / run -> Logger (stderr JSON)  ----------------------> hub.obs traces   (offline, from a saved log file)
              -> HttpMetrics (memory) --flush at stop--------> obs_metric rows  -> samples -> lint -> SLO -> alerts -> report
run end / obs-snapshot -> collect.samples ------------------> obs_metric rows  /
resilience objects ----> resilience_samples (NOT CALLED) ---> samples          /
```
Today the right-hand chain is run by hand on a samples file. Wiring a periodic snapshot is decision D-31-01.

### OA-4 Principles
1. [Verified Fact] No external APM, no outbound telemetry (FR-CO-04, ADR-015/016). The new modules import no socket, HTTP client, clock, random or subprocess (test D01).
2. [Verified Fact] Privacy by construction: the log whitelist holds no free-text field; metric labels are closed identifiers; the lint refuses anything else and never echoes it (tests C02, D04).
3. [Verified Fact] Measurement is not a promise: SLOs are candidates, no SLA exists, a window with no events is NO_DATA never "met" (tests S01, A04).
4. [Inference] A single-process loopback product needs correlation ids, not distributed tracing (see tracing-spec TS-1).
5. [Verified Fact] A metric that is absent is "no data", except the tripwires where an absent sensor itself fires (A02), because a tripwire that reads 0 only because nothing counts is weak evidence (RR-32-01).

### OA-5 Coverage against the stage scope
| Scope item | Status |
|---|---|
| Requests | covered: `http_request` log line + `http_requests_total` / duration (flush gap F-31-02) |
| Retrieval, prompt/config versions | retrieval = FTS (`search_engine` gauge, `fts_engine_selected` event); no prompts exist (No-AI); `code_version` and `config_version` are on every log line |
| Model latency, tokens, tool calls, agent trajectories | N/A by OD-08 / OD-27; only the tripwire (ai-telemetry-spec, agent-telemetry-spec) |
| Errors | `error_code` on log lines, `auth_failures_total`, 5xx ratio alert |
| Business outcomes | intake outcomes, queue depths, decision events, overrides, defaulted outputs, run timeliness |
| Infrastructure | resilience telemetry (built, unwired); host metrics are Unknown (no host) |
| Data | intake counters, quarantine depth; freshness not exported (SLO-05 gap) |

## Evidence References
`hub/obs/*.py`, `hub/web/app.py` (lines 97-135, 186-200), `hub/web/cli.py` (60-72), `docs/12-specs/observability-spec.md` OBS-1..OBS-7, ADR-016, `docs/28-reliability/resilience-architecture.md`, tests STG31 (C01-C05, S01-S03, A01-A04, T01-T03, D01-D04).

## Assumptions
- A-31-01 Telemetry stays stdlib / file based; no collector, vendor or dashboard stack is chosen (ADR-015). Confirm: Engagement lead (Dinesh Naik).
- A-31-08 One person operates the hub; evaluation is on demand, so windows of 28-30 days are bookkeeping periods, not real-time evaluation.

## Unknowns
- U-31-01 Where the hub would run beyond loopback and what host metrics exist there.
- U-31-02 Whether any consumer needs a scrape endpoint (D-31-04).
- U-31-03 Where `hub web serve` stderr goes when started by `./run.sh` or a container (retention, rotation).

## Unresolved Issues
- Metrics are not persisted until `serve` stops; a killed process loses them (F-31-02, D-31-01).
- Resilience samples exist but the guarded gateway is not wired (D-28-01 / D-31-02).

## Residual Risks
- RR-31-01 Observability that nobody looks at: no on-call, no scheduler (HAR-10), no alert delivery. Medium.
- RR-31-02 Spec rot between catalogue, docs and code; mitigated by tests D03 (docs agree with code). Low.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
