---
stage: "28 — Reliability & Resilience Engineering"
artifact: "fallback-matrix.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
For each dependency: what the hub does when it fails, and what the fallback is. The honest result is short: **there are no fallback providers or models** (none exist, OD-08) and **no result cache**; the fallbacks are "fail closed and keep the rest working" plus operator re-run. This artifact records that so Stage 29 (incident / BC-DR) and Stage 31 (SLOs) do not assume mechanisms that are absent.

## Findings
### FB-1 Matrix
| Dependency | Failure | Primary behaviour | Fallback | Data effect | Operator action | Evidence | Tag |
|---|---|---|---|---|---|---|---|
| Source gateway | down / slow / 5xx / 429 | bounded retries, run failed | none (no second source); hub keeps serving reads; guarded path refuses while the breaker is open | 0 rows, RUN_FAILED + audit | re-run after the cooldown / when the source is back; late items via idempotent catch-up | F01-F04, F08, STG21 S03/S04/S07 | [Verified Fact] |
| Source gateway | malformed / 4xx | run failed (shipped retries shape errors, guarded fails fast) | none | 0 rows | fix the source or the request | F05 | [Verified Fact] |
| Legacy snapshot | hash mismatch / drift | adapters refuse (fail closed) | none by design (frozen baseline); restore from `_data-backup` | none | restore / re-pin through the change process | TST-CO-04 e, TST-CO-07 | [Verified Fact] |
| Store file | read-only / corrupt / locked | 503 E-STORE-UNAVAILABLE for every request | restore from backup (L2 restore, RTD-33: writes after the backup lost) | none changed | restore procedure (Stage 29 runbook) | STG26 C01, TST-CO-09 | [Verified Fact] |
| Audit anchor file | missing / altered | `verify` reports tamper; opt-in HMAC seal (Stage 24) | none | none | investigate (Stage 29) | STG26 C03 | [Verified Fact] |
| Clock | rolled back | sessions stay dead; breaker restarts cooldown | none | none | fix host clock | STG26 C05, STG28 P04 | [Verified Fact] |
| Model / provider / embedding service | n/a | not a dependency | **not applicable** | n/a | n/a | STG28 A01-A03 | [Verified Fact] |
| Response cache | n/a | no cache exists | n/a | n/a | n/a | grep hub/ (only a per-load token-statistics memo) | [Verified Fact] |
| Second node / replica | n/a | single node | none | n/a | n/a | `docs/10-architecture/deployment-architecture.md` | [Verified Fact] |
| Scheduler | not enabled (HAR-10) | no unattended runs | operator-started runs | late deliveries wait (FG-02) | scheduled catch-up only after the scheduler decision | STG21 S07 | [Verified Fact] |

### FB-2 Findings
| ID | Finding | Impact | Risk | Confidence |
|---|---|---|---|---|
| F-FB-01 | Any real source outage stops ingestion from that source until an operator acts; there is no standby source and none is planned | ingestion latency = outage + operator reaction | Medium (unmeasured) | High |
| F-FB-02 | RTO / RPO of the store are mechanics-only (RTD-33) | Stage 29 must turn them into a procedure with timings | Medium | High |

## Evidence References
`docs/21-integration/failure-semantics.md`, `docs/10-architecture/deployment-architecture.md`, `docs/08-ai-qualification/qualification-decision.md` (No-AI), `docs/26-tevv/tevv-results.md`, STG28 F01-F08, A01-A03.

## Assumptions
- A-28-FB-1 [Assumption] No second source or standby store will be provided before real data exists. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-05 Whether a business-continuity requirement for ingestion exists (none recorded; Stage 29).

## Unresolved Issues
- F-FB-01, F-FB-02.

## Residual Risks
- RR-28-06 Single point of failure: one process, one SQLite file, one host.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
