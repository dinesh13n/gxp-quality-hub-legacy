---
stage: "28 — Reliability & Resilience Engineering"
artifact: "failure-injection-results.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
All planned laptop injections ran and met their pass rule: **STG28 19/19, E28 1/1 (zero egress attempts, `model_calls_total` 0), group B 42 executed = 42 expected (41 ok, 1 skipped: no `python3.9` on the device, simulated in TST-CO-14 b), characterisation harness 133/134 (CT-13 fails only from Node patch drift, known S24-DEV-04; CT-17 NOT-RUN: no golden, U-07-05; CT-18 NOT-RUN: Docker unavailable, HAR-05)**. Data checksums (`../_data-backup-2026-10-17/SHA256SUMS.txt`) rc 0 before and after; the working tree contains only the committed branch files. Two injections (disk full / power loss, container restart) were not run (FI-13, FI-14). All results are sandbox proxies, labelled synthetic, unvalidated; the Stage 26 injections (FI-11) and Stage 21 / 15 tests (FI-12) are covered by the orchestrator's full regression, not re-run here (speed rule).

## Findings
### FR-1 Results by injection
| Inj. | Result | Observed (Verified Fact) |
|---|---|---|
| FI-01 | PASS | 3 failed calls = 12 attempts with sleeps [0.5, 1.0, 2.0] x 3; breaker OPEN; call 4 refused `circuit_open` with `retry_after_seconds` >= 1, attempts_total still 12 (`evidence/f01-source-down.json`) |
| FI-02 | PASS | (a) budget only: requests at the double == attempts_total <= 250 (unguarded would be 800); (b) default: exactly 12 requests for 200 calls, reasons {retries_exhausted: 3, circuit_open: 197} (`evidence/f02-retry-storm.json`); retry-budget bound holds for 1 / 10 / 100 / 1000 calls (`evidence/retry-budget-bound.json`: 1000 calls -> retries granted far below 3,000 and <= 210) |
| FI-03 | PASS | 2 attempts, each ended by the 0.3 s timeout, 2 GETs seen by the silent listener, call < 3 s, 1 breaker failure |
| FI-04 | PASS | 59 s: refused, no request; probe at 60 s used the drained budget (one retry then `retry_budget_exhausted`, 2 attempts) and re-opened the breaker; +30 s refused; +60 s probe against a healthy double -> closed, next call 1 attempt; concurrent second caller during a probe -> `circuit_open` |
| FI-05 | PASS | shape: 1 request (`shape_error`), 4 with `retry_shape_errors`; non-JSON 1 request; 400 x 10 = 10 requests, breaker closed, 0 failures; 429 retried (4 requests) |
| FI-06 | PASS | second pull refused with `bulkhead_full` in < 0.5 s; 1 request at the source; breaker failures 1 (from the first call only), bulkhead rejected 1, in_flight 0 afterwards |
| FI-07 | PASS | 4th connection answered 429 `E-REQ-RATE-LIMITED` + `Retry-After: 1`; audit row count unchanged; in_flight returned to 0 at the read timeout; `/healthz` 200 afterwards; peak <= 3 |
| FI-08 | PASS | RUN_FAILED recorded, 0 raw / 0 outcomes; `/healthz` 200; authorised read 200; audit chain `ok`; restored OPEN snapshot refused until cooldown, then the probe returned the page |
| FI-09 | PASS | A01 equal results (counts raw 20) with and without the AI environment; A02 no AI environment variable or key; A03 deny-list clean, tripwires 0; E28 0 egress attempts, model_calls_total 0, nothing skipped |
| FI-10 | recorded | see `capacity-plan.md` CP-2 (`evidence/capacity-proxies.json`); no threshold |
| FI-11 / FI-12 | not re-run here | green in the Stage 27 orchestrator regression (27 groups, OD-34); the orchestrator re-runs all 29 groups for this branch |
| FI-13 / FI-14 | NOT RUN | needs an approved host (D-28-07, D-28-08) |

### FR-2 Gate-relevant verdicts
| Gate condition | Verdict | Basis |
|---|---|---|
| Failure-injection results exist for critical failure modes | MET for FM-01..FM-10, FM-13..FM-17 (injected here or by earlier-stage tests); NOT MET for FM-11 (disk full / power loss) - documented gap | FR-1; failure-mode-analysis.md |
| AI-disabled mode defined and tested | MET | ai-disabled-mode.md AI-2 |
| Retry storms prevented | MET for the guarded path (F02); the shipped `gateway-pull` is bounded (<= 4 attempts per run, 23.5 s) but not guarded across runs | F02 vs F-RET-01 |

### FR-3 Anomalies recorded
- Authorised-read and ingest rates differ by 3x between two runs on the same laptop (shared machine); proxies are noisy, which is why no threshold is asserted.
- The first draft of F04 expected a full retry sequence for the half-open probe; the run showed the drained budget gives it one retry. The test was corrected to the observed (and intended) behaviour: a probe against a struggling source is deliberately cheap.
- No defect was found in hub code. A few test-authoring errors were fixed before the first commit (P07 regex, F04 and F08 expectations, a helper escape, the tripwire API call).

## Evidence References
`evidence/f01-source-down.json`, `f02-retry-storm.json`, `retry-budget-bound.json`, `capacity-proxies.json`, `regression-S28.json`, `regression-E28.json`, `regression-B.json`, `characterization-summary.txt`.

## Assumptions
- A-28-FR-1 [Assumption] The orchestrator's cloud regression (Python 3.13) will confirm the unchanged groups; the characterisation goldens are 3.10.12-specific (OD-23).

## Unknowns
- U-28-11 Results on Python 3.12+ (no evidence yet, RTR-08).

## Unresolved Issues
- FI-13 and FI-14 not run.

## Residual Risks
- RR-28-11 Proxy results; no production-like environment.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
