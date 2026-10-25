---
stage: "28 — Reliability & Resilience Engineering"
artifact: "failure-mode-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
Seventeen failure modes (FM-01..FM-17) are analysed with blast radius, recovery behaviour and the test that exercises each. **Ratings are qualitative agent inferences** (no incident history, no production telemetry exist, OD-04): severity S (1-5), likelihood L (1-5, for a single-operator loopback deployment), detectability D (1 = always visible, 5 = silent). Priority = S x L x D is a ranking aid, not a risk acceptance. Of the 17, 14 are injected or exercised by a test that runs in the regression (Result column; FM-14 is trivially satisfied because the product has no AI dependency); FM-12 is proven for mechanics only, FM-17 is characterised with an open gap, and FM-11 needs a real host (Stage 29).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FMEA table
| ID | Failure mode | Effect / blast radius | Recovery behaviour (as built) | S | L | D | Prio | Injection / test | Result | Tag |
|---|---|---|---|---|---|---|---|---|---|---|
| FM-01 | Gateway source down (connection refused) | one pull fails; no other capability affected (hub stays useful) | bounded attempts then E-INT-SOURCE-UNREACHABLE; RUN_FAILED, 0 rows; guarded path: breaker opens after 3 failed calls, later calls refused unseen | 2 | 4 | 1 | 8 | STG28 F01, F08; STG21 S03; TST-INT-26 | PASS | [Verified Fact] |
| FM-02 | Retry storm (sustained 5xx / 429) | multiplies load on a struggling source (up to 4x per call; unbounded across calls if callers loop) | guarded: retry budget + breaker: 200 calls -> 12 source requests (vs 800); shipped client: <= 4 per call, per-caller only | 3 | 3 | 2 | 18 | STG28 F02, P03 | PASS (guarded path); shipped path bounded, unguarded | [Verified Fact] |
| FM-03 | Source accepts and never answers | a pull holds a process for up to 4 x 5 s + 3.5 s = 23.5 s (shipped); caller threads in a service would pile up | per-attempt timeout; guarded: bulkhead keeps one in flight, breaker counts one failure | 3 | 3 | 2 | 18 | STG28 F03, F06; STG21 S04 | PASS | [Verified Fact] |
| FM-04 | Source recovers while breaker open | needless prolonged outage if the breaker never closes; or a thundering herd if it closes at once | cooldown then ONE probe; fail -> re-open, cooldown restarts; success -> closed | 2 | 3 | 2 | 12 | STG28 F04, P04 | PASS | [Verified Fact] |
| FM-05 | Malformed (200) or client-error (4xx) response | retrying a deterministic fault wastes the budget and can open a breaker wrongly | guarded: shape error fails fast (S28-DEV-02), 4xx never retried and never counts; shipped client retries shape errors (AF-02 / FG-01) | 2 | 3 | 2 | 12 | STG28 F05; STG21 S03 | PASS | [Verified Fact] |
| FM-06 | Concurrent pulls of the same source | duplicate load; double checkpoint writes | job runs: `run_lock` single flight (E-RUN-ALREADY-RUNNING); guarded: bulkhead refuses at once | 3 | 2 | 2 | 12 | STG28 F06; TST-RUN (run lock) | PASS | [Verified Fact] |
| FM-07 | Many / idle / slow client connections on the listener | one thread per connection with no cap: memory and thread exhaustion of the hub process (loopback clients only) | read timeout 10 s ends idle ones; Stage 28 cap component sheds the excess with 429 (not wired) | 3 | 2 | 3 | 18 | STG28 F07; STG26 C06 | PASS for the component; **shipped listener uncapped** (F-CAP-01) | [Verified Fact] |
| FM-08 | Store unavailable (read-only, corrupt header) | every request fails closed; no data change | 503 E-STORE-UNAVAILABLE, content-free, also /healthz | 4 | 2 | 1 | 8 | STG26 C01; STG27 store tests | PASS (regression) | [Verified Fact] |
| FM-09 | Audit tamper / clock rollback | evidence integrity | insert-only triggers; `verify` detects an edited row; rolled-back clock does not revive a session | 5 | 1 | 2 | 10 | STG26 C03, C05 | PASS (regression) | [Verified Fact] |
| FM-10 | Crash mid-run (process kill) | partial run | one transaction per run: nothing persists; job resumes from checkpoint (RUN_ABANDONED), result equals an uninterrupted run | 3 | 3 | 2 | 18 | TST-RUN-07; INC06 S06/S07 | PASS (regression) | [Verified Fact] |
| FM-11 | Disk full / power loss during a write | possible WAL/journal loss; SQLite atomic commit protects committed rows | SQLite journaling; not injected here (needs a disk-quota or power-cut harness on an approved host) | 4 | 2 | 2 | 16 | none | **NOT INJECTED** (Unknown) | [Unknown] |
| FM-12 | Store lost / restore needed | RPO window: writes after the backup are lost from the live store (RTD-33) | backup-before-migrate, rollback rehearsals (TST-CO-09, INC rehearsals); RTO/RPO 8 h / 24 h are Assumptions | 5 | 2 | 2 | 20 | TST-CO-07/09 (regression) | PASS for mechanics; targets unproven | [Verified Fact] mechanics, [Assumption] targets |
| FM-13 | Legacy snapshot drift / hash mismatch | backfill and golden compare refuse; hub store unaffected | fail closed E-FX-HASH / E-CO-LEGACY-SCHEMA-DRIFT; adapters never write | 2 | 2 | 1 | 4 | TST-CO-04 e; STG21 S06 | PASS (regression) | [Verified Fact] |
| FM-14 | AI / model / provider unavailable | none: the product has no AI dependency | AI-disabled is the only mode | 1 | 1 | 1 | 1 | STG28 A01-A03, E28 | PASS | [Verified Fact] |
| FM-15 | Invalid configuration | start-up refusal | E-CFG-INVALID, exit 2, no traceback; unknown keys refused (Stage 27) | 2 | 3 | 1 | 6 | STG26 C02; STG27 | PASS (regression) | [Verified Fact] |
| FM-16 | Concurrent writers / clients | lost update, duplicate | SQLite single writer + busy_timeout; idempotency keys; 8 threads x 8 requests: no 5xx, writes applied once | 3 | 3 | 2 | 18 | STG26 C04 | PASS (regression) | [Verified Fact] |
| FM-17 | Late / out-of-order delivery | item not seen by a resumed job (RTD-61) | delayed, not lost, if an idempotent catch-up run is started by an operator (scheduler OFF) | 3 | 3 | 3 | 27 | STG21 S07 | characterised, **gap FG-02 open** | [Verified Fact] |

### Findings (ordered by priority)
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved |
|---|---|---|---|---|---|---|
| F-LATE-01 | FM-17: no automatic catch-up while the scheduler is OFF; late items wait for an operator | `hub/runs/sources.py` docstring RTD-61; STG21 S07 | late evidence invisible until a manual run | Medium | High | catch-up policy (D-28-04) |
| F-CAP-01 | FM-07: the listener has no connection cap; the 10 s read timeout bounds hold time only | `hub/web/server.py:27` (`ThreadingHTTPServer`, `daemon_threads`); STG28 F07 shows the cap component works | local flood can exhaust threads; loopback-only limits who | Medium-Low (loopback) | High | wire the component? (D-28-02) |
| F-RET-01 | FM-02: shipped client has no jitter, cap, budget or cross-run breaker | `gateway_client.py:60-79` | harmless for one operator; a storm source if ever called in a loop or by several callers | Low now / Medium at scale | High | D-28-01 |
| F-RET-02 | FM-05: shipped client retries shape errors (FG-01) | `gateway_client.py` (`ValueError` caught and retried) | wasted attempts only | Low | High | DQ-S21-03 (answered by default in the guarded path) |
| F-DB-01 | FM-16/FM-03: `busy_timeout` 30 s lets a request hold a listener thread for 30 s on a locked store | `hub/web/app.py:109` | combined with F-CAP-01, slow-lock amplification | Low | Medium (not injected) | D-28-09 |
| F-DR-01 | FM-11: disk-full / power-loss not injected | none | unknown behaviour at the edge of SQLite guarantees | Medium | Low | Stage 29 on an approved host |
| F-OBS-01 | The guarded path counts rejections and attempts in memory only; no metric is emitted | `GuardedGateway.attempts_total`, `Breaker.rejected` | Stage 31 SLO inputs (breaker open time, shed count) do not exist yet | Low | High | D-28-01 (wiring adds metrics) |

## Evidence References
`hub/resilience/*`, `tests/hub/test_tst_hub_stg28_*.py`, `docs/21-integration/failure-semantics.md` (FS-1 matrix, FG-01..03), `docs/26-tevv/tevv-results.md`, `docs/26-tevv/residual-tevv-risks.md`, `docs/13-traceability/*` (RTD-33, RTD-61).

## Assumptions
- A-28-FM-1 [Assumption] S / L / D ratings are agent judgement for a single-operator loopback deployment. Confirm: Engagement lead (Dinesh Naik) before any rating is used for acceptance.

## Unknowns
- U-28-02 Real incident rates and source error mix (none exist). U-28-03 Disk-full / power-loss behaviour on the target host.

## Unresolved Issues
- F-LATE-01, F-CAP-01, F-RET-01, F-DR-01 open (see resilience-readiness.md open items).

## Residual Risks
- RR-28-02 FM-11 and FM-12 targets unproven (Stage 29). RR-28-03 Ratings are not telemetry.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
