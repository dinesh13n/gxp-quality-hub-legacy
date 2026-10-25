---
stage: "28 — Reliability & Resilience Engineering"
artifact: "capacity-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
There is **no capacity target** (no users, volumes or SLOs exist, OD-04; PNFR-01/05 are Assumptions) and **no production measurement**. This plan therefore (1) lists the limits that bound capacity today, (2) records sandbox **proxy** measurements with their method, and (3) states the headroom reasoning without claiming a capacity figure. All numbers are class C (sandbox proxy): one process, in-process calls or a loopback double, synthetic data, the reference laptop. They are not production capacity, availability or latency figures.

## Findings
### CP-1 Limits that bound capacity today [Verified Fact]
| ID | Limit | Value | Source |
|---|---|---|---|
| CL-01 | request body | 1 MiB | `hub/web/app.py` `BODY_LIMIT` |
| CL-02 | gateway response | 5 MiB | `gateway_client.MAX_BYTES` |
| CL-03 | listener read timeout | 10 s | `hub/web/server.py` |
| CL-04 | concurrent connections | **unbounded** (one thread each); Stage 28 component caps at 64 (not wired) | `LoopbackServer`; `bounded_server.py` |
| CL-05 | writers | 1 at a time (SQLite), 30 s busy wait | `app.py:109` |
| CL-06 | job batch | explicit `runs.batch_size` (no hidden constant) | `hub/runs/settings.py` |
| CL-07 | job concurrency | 1 per job (`run_lock`) | `hub/runs/service.py` |
| CL-08 | tracked rate-limit peers | 1024 | `hub/web/ratelimit.py` |
| CL-09 | data volume in the repo | 125 cases (confirmed baseline, OD-09); 8,567 partner rows, 15 messages, 1 gateway event | OD-09, STG21 S07 |

### CP-2 Sandbox proxy measurements (STG28 C01; `evidence/capacity-proxies.json`)
| Measure | Method | Result (reference laptop, Python 3.10.12) | Tag |
|---|---|---|---|
| `/healthz`, in-process `WebApp.handle` | 300 requests, one thread | 559 requests/s (second run 562/s) | [Verified Fact] proxy |
| authorised read `/api/v2/policies`, in-process | 300 requests, one thread | 41 requests/s (second run 129/s; the figure is noisy on this shared laptop) | [Verified Fact] proxy |
| intake ingest, 500 synthetic items | 5 batches of 100, private store | 1,326 items/s (second run 3,121/s) | [Verified Fact] proxy |
| 8 threads x 8 mixed requests on the real listener | Stage 26 C04 | no 5xx, every write applied once (Stage 26 evidence `docs/26-tevv/evidence/s26-tests`) | [Verified Fact] |
| TST-NFR-01/02/05 | Stage 20 / 26 runs (group I8b) | not re-run in Stage 28 (S28-DEV-07; the orchestrator's full regression covers them); earlier results stand as proxies | [Verified Fact] earlier stage |
| CT-17 concurrency, CT-18 container | characterisation harness, this run | CT-17 NOT-RUN: no golden exists (U-07-05); CT-18 NOT-RUN: Docker unavailable, HAR-05 not approved | [Verified Fact] |

### CP-3 Headroom reasoning [Inference]
The shipped data volume (125 cases, 8,567 partner rows total in the frozen legacy) is three to four orders of magnitude below what the ingest proxy handles per second in the sandbox; the binding constraints are therefore not CPU or store throughput but (a) the single writer under concurrent clients, (b) the uncapped thread-per-connection listener, and (c) the 30 s busy wait. None has been hit in testing. A real target (volumes per day, concurrent reviewers) is **Unknown** and must come from the engagement lead before any capacity statement is made (Stage 31).

### CP-4 Overload behaviour (what happens beyond the limits)
| Overload | Behaviour | Evidence |
|---|---|---|
| refused-request flood from one peer | 429 after 100 / 60 s, no audit growth | Stage 27 limiter tests |
| more than the cap of connections (bounded server) | 429 shed, service recovers when idle ones end | F07 |
| concurrent pulls | second refused at once (bulkhead) / E-RUN-ALREADY-RUNNING | F06, TST-RUN |
| oversize body | 413, nothing written | Stage 26 |
| source slower than the timeout | per-attempt timeout, breaker counts one failure | F03 |

### CP-5 Findings
| ID | Finding | Impact | Risk | Confidence |
|---|---|---|---|---|
| F-CAP-01 | listener connection cap not enforced in the shipped server | see failure-mode-analysis | Medium-Low | High |
| F-CAP-02 | no capacity target exists; proxies cannot be compared with anything | no PASS/FAIL possible on capacity | Low | High |

## Evidence References
`evidence/capacity-proxies.json`, `tests/hub/test_tst_hub_stg28_ai_capacity.py` C01, `docs/09-initial-prd` PNFR-01/05/06, `docs/26-tevv/evidence/s26-tests`, `evidence/characterization-summary.txt`, OD-04, OD-09.

## Assumptions
- A-28-CAP-1 [Assumption] Loopback single-operator load for the foreseeable future. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-02 Volumes, concurrency, growth: no data (OD-04). U-28-06 Behaviour on the production host and on Python 3.12+.

## Unresolved Issues
- F-CAP-02 (target needed at Stage 31).

## Residual Risks
- RR-28-07 Proxy numbers may be mistaken for capacity; every figure carries its label.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
