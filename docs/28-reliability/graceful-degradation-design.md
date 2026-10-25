---
stage: "28 — Reliability & Resilience Engineering"
artifact: "graceful-degradation-design.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
What keeps working when one dependency is lost, in priority order, and how the hub tells the operator. The design principle is **degrade by dependency, not by switch**: capabilities depend on few things (store, source, legacy snapshot, anchor file) and each failure removes only the capabilities that need that thing. The one proven degraded mode is **source down**: ingestion from that source stops, everything else (health, authorised reads, reviewer queue, audit verification) keeps working (STG28 F08). A store fault removes everything but fails closed and content-free (STG26 C01). No manual "degraded mode" switch exists or is added.

## Findings
### GD-1 Capability / dependency matrix [Verified Fact where a test is cited; Inference otherwise]
| Capability | Needs store | Needs source | Needs legacy snapshot | Needs anchor file | Behaviour when its dependency fails | Evidence |
|---|---|---|---|---|---|---|
| `/healthz` | yes | no | no | no | 503 E-STORE-UNAVAILABLE on a store fault; 200 otherwise (also with source down) | F08, STG26 C01 |
| Authorised reads (policies, cases, queue, reports) | yes | no | no | no | 200 with source down; 503 on store fault | F08, STG26 C01 |
| Reviewer actions / evidence writes / decisions | yes | no | no | audit write | 503 on store fault; refusals audited | STG26 C04 |
| Zone H actions | yes | no | no | audit | unchanged: need a real holder + approval ref (`zone_h.holders` EMPTY, so none is executable) | OD-31 |
| `gateway-pull` / job runs | yes | yes | no | audit | RUN_FAILED, 0 rows; guarded path adds reason + breaker | F01-F04, F08 |
| `ingest-legacy`, golden compare, backfill | yes (ingest) | no | yes | audit | adapters refuse on drift; web unaffected | TST-CO-04 e |
| `audit verify` | yes | no | no | optional | reports tamper / missing anchor | STG26 C03 |
| Reports needing the source | yes | no (reads stored rows) | no | no | show stored data only; staleness is visible through run records (RUN_FAILED, last checkpoint) | F08 [Inference for reports] |

### GD-2 Degradation levels (names for the operator; not switches)
| Level | Condition | What the operator sees | Still available | Not available |
|---|---|---|---|---|
| L0 normal | all dependencies healthy | 200s | all | - |
| L1 source degraded | breaker open or runs failing | RUN_FAILED records, `circuit_open` with `retry_after_seconds` | L0 minus pulls | new items from that source |
| L2 listener saturated | connection cap reached (component, not wired) | 429 + Retry-After 1 | existing connections, CLI | new connections until idle ones end |
| L3 store unavailable | read-only / corrupt / locked beyond busy wait | 503 E-STORE-UNAVAILABLE for all, nothing else | CLI diagnostics, backups | everything that needs the store |

### GD-3 Degraded-mode usefulness (analysis dimension 5)
- L1 is useful: the reviewer queue and decisions are made on already ingested evidence; the cost is freshness. Freshness is visible (last checkpoint, run records) but **no freshness alarm or SLO exists** (Stage 31; FG-02).
- L2 is useful only for the clients already connected; new interactive users must retry.
- L3 is deliberately not useful: GxP evidence must not be served or changed from an unverifiable store; it fails closed.
- Data written during an outage is never reconstructed from guesses: a failed pull is re-run, a late item is caught up by an idempotent run (STG21 S07).

### GD-4 Findings
| ID | Finding | Impact | Risk | Confidence |
|---|---|---|---|---|
| F-GD-01 | No operator-visible freshness indicator on reads | a reviewer may not notice that the source has been down | Medium | Medium (Inference: reports show stored data only) |
| F-GD-02 | L2 exists only as a component | see F-CAP-01 | Medium-Low | High |

## Evidence References
STG28 F07, F08; STG26 C01, C04, C06; `docs/21-integration/failure-semantics.md`; `docs/23-human-control/*` (Zone H); `hub/web/app.py`.

## Assumptions
- A-28-GD-1 [Assumption] Reviewers can work from already ingested evidence when a source is down. Confirm: Engagement lead (Dinesh Naik) with the quality reviewers (none named; OD-04).

## Unknowns
- U-28-07 Which reports are time-critical (OPD-01..03 definitions unanswered). U-28-08 Whether a freshness banner is wanted.

## Unresolved Issues
- F-GD-01 (freshness indicator) is a Stage 30/31 item.

## Residual Risks
- RR-28-08 Degraded L1 can go unnoticed (no alarm).

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
