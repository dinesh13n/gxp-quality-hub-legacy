---
stage: "28 — Reliability & Resilience Engineering"
artifact: "failure-injection-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
Plan for injecting the failure modes of `failure-mode-analysis.md` **only into approved environments**: private sandbox stores (copies outside the working tree, OD-03a), loopback doubles and fake clocks on the reference laptop. **No failure is injected into production, a shared service, the working-tree `data/`, the legacy estate or any real system** (none exist, OD-04). The plan selects at least one injection per critical failure mode, states the expected behaviour before the run, and the pass rule. Injection tooling: counting loopback HTTP double (`tests/hub/_stg28.py` `Stub`), the repo's silent listener (`_stg21.hanging_server`), a closed port (`refused_url`), an injectable clock (`FakeClock`), raw sockets (`_http8.raw`; `urllib.request` / `http.client` are forbidden outside `hub/adapters`).

## Findings
### FI-1 Plan
| Inj. ID | Failure mode | Method | Expected (stated before the run) | Pass rule | Test | Env |
|---|---|---|---|---|---|---|
| FI-01 | FM-01 source refused | closed loopback port | 3 calls x (1+3) attempts, back-off 0.5 / 1 / 2; breaker opens; 4th call `circuit_open`, 0 attempts | attempts_total 12 and unchanged by call 4 | STG28 F01 | sandbox |
| FI-02 | FM-02 retry storm | 200 calls vs a 503 double; (a) breaker effectively off, (b) default | (a) requests <= 250; (b) exactly 12 | counted at the double | STG28 F02, P03 | sandbox |
| FI-03 | FM-03 silent source | `hanging_server`, timeout 0.3 s, 1 retry | 2 attempts, < 3 s, 2 requests seen, 1 breaker failure | | STG28 F03 | sandbox |
| FI-04 | FM-04 recovery | fake clock around a 503 -> 200 switch; probe failure; concurrent probe | refused at 59 s, probe at 60 s, closed on success; failed probe re-opens; second caller refused | state and request counts | STG28 F04 | sandbox |
| FI-05 | FM-05 bad responses | doubles returning 200 wrong shape, non-JSON, 400, 429 | shape fails fast (1 request; 4 when `retry_shape_errors`), 400 once and never opens the breaker, 429 retried | request counts, breaker state | STG28 F05 | sandbox |
| FI-06 | FM-06 concurrent pull | second call while the first is hung | refused < 0.5 s, 1 request at the source, breaker not charged | | STG28 F06 | sandbox |
| FI-07 | FM-07 connection flood | bounded listener (cap 3), 3 idle sockets + 1 request | 429 + Retry-After, no audit row; recovers after the 1 s read timeout | audit count, status | STG28 F07 | sandbox store + loopback |
| FI-08 | FM-01 degraded mode | source down, then restore breaker snapshot into a new guard | RUN_FAILED with 0 rows; health and a read stay 200; chain verifies; probe after cooldown succeeds | counts, status | STG28 F08 | sandbox store |
| FI-09 | FM-14 AI-disabled | AI-style environment on/off; static scans; egress guard | identical results; no AI word; 0 egress / model calls | digest equality | STG28 A01-A03, E28 S90 | sandbox |
| FI-10 | capacity proxies | in-process request and ingest loops | all answers expected; rates recorded | no threshold | STG28 C01 | sandbox |
| FI-11 | FM-08 store fault, FM-09 tamper / clock, FM-15 config, FM-16 concurrency, FM-06 transport anomalies | Stage 26 injections (read-only store file, corrupt header, SQL tamper, rolled-back clock, bad config, 8 x 8 clients, raw-socket anomalies) | defined 4xx / 503, nothing written | Stage 26 tests | STG26 C01-C06 | sandbox (regression, re-run by the orchestrator) |
| FI-12 | FM-10 crash mid-run, FM-13 drift, FM-17 late delivery | Stage 21 / 15 tests | one transaction, resume equals uninterrupted run; fail closed; catch-up stores the late item | | TST-RUN-07, INC06 S06/S07, TST-CO-04 e, STG21 S07 | sandbox (regression) |
| FI-13 | FM-11 disk full / power loss | **not planned for the laptop**: needs a quota-limited filesystem or power-cut harness on an approved host | - | - | none | needs approval (D-28-07) |
| FI-14 | FM-12 restore timing, container restart (CT-18) | **not run**: no production-like host, Docker unavailable, HAR-05 not approved | - | - | none | open |

### FI-2 Safety rules for every injection
1. Sandbox copy outside the working tree; `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after (done: see failure-injection-results.md).
2. Loopback only; the egress guard stays installed in the E28 run (zero attempts).
3. No retry without back-off and a limit: the guarded client's every retry path is counted by the test that provokes it.
4. Clean up own sandbox copies afterwards; no `pkill -f`.

## Evidence References
`tests/hub/_stg28.py`, `tests/hub/test_tst_hub_stg28_injection.py`, `test_tst_hub_stg28_ai_capacity.py`, `docs/26-tevv/failure-dataset-spec.md`, `docs/28-reliability/failure-mode-analysis.md`.

## Assumptions
- A-28-FI-1 [Assumption] Loopback doubles are an adequate model of the one source the repo has (the shipped gateway stub was conformance-tested in Stage 21 S02). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-03 Disk-full / power-loss behaviour. U-28-10 Container restart behaviour (CT-18).

## Unresolved Issues
- FI-13 and FI-14 are unplanned until an approved environment exists.

## Residual Risks
- RR-28-10 Doubles do not reproduce real network pathologies (partial reads, slow trickle, TLS) - the source is loopback HTTP only.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
