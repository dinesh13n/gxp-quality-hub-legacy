---
stage: "28 — Reliability & Resilience Engineering"
artifact: "resilience-readiness.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
**Gate outcome (agent's computation, a recommendation to the Engagement lead): CONDITIONAL PASS.** The three Stage 28 gate conditions are met on the evidence available on the laptop: injection results exist for the critical failure modes (14 of 17 modes injected or exercised by a regression test; FM-12 mechanics only, FM-17 characterised with an open gap, FM-11 not injected), AI-disabled operation is defined and tested (it is the only mode), and retry storms are prevented where the Stage 28 mechanisms apply (200 calls -> 12 source requests instead of 800). It is not a PASS because: (1) the mechanisms are **built and tested but not wired** into `gateway-pull` or `hub web serve` (wiring is a behaviour change and needs edits to existing files and a persistence decision, D-28-01 / D-28-02), so the shipped commands remain bounded but unguarded; (2) disk-full / power-loss and container-restart injections need an approved host (D-28-07 / D-28-08); (3) no capacity, RTO / RPO or freshness target exists, so nothing here claims attainment. No blocking condition remains: Stage 29 may proceed. Nothing here accepts a risk (OD-32); all behaviour defaults are agent assumptions awaiting Dinesh Naik.

## Findings
### RD-1 Completion gate
| Condition | Status | Evidence |
|---|---|---|
| Failure injection results exist for critical failure modes | MET with a documented gap (FM-11) | failure-injection-results.md FR-1/FR-2 |
| AI-disabled mode defined and tested | MET | ai-disabled-mode.md; STG28 A01-A03, E28 |
| Retry storms prevented | MET for the guarded path; shipped path bounded, unguarded | F02, P03; F-RET-01 |
| All required artifacts exist (11) | MET | `docs/28-reliability/` (path per the engagement lead's instruction; the prompt names `docs/28-resilience/`, S28-DEV-05) |
| Critical gaps resolved or documented | MET | RD-4 open items with owners |
| Evidence supports the conclusion | MET | `evidence/` |

### RD-2 What was built (all additive)
| Path | Purpose | Tests |
|---|---|---|
| `hub/resilience/policy.py` | validated defaults, back-off, RetryBudget, Breaker (+ snapshot / restore), Bulkhead | STG28 P01-P07 |
| `hub/resilience/guarded.py` | `GuardedGateway` around the AD-04 client | F01-F06, F08 |
| `hub/web/bounded_server.py` | `BoundedLoopbackServer` / `make_bounded_server` | F07 |
| `tests/hub/_stg28.py`, `test_tst_hub_stg28_{policy,injection,ai_capacity,egress_guard}.py` | 19 + 1 tests | - |
| `tests/hub/regression_groups.json` | groups S28 (STG28) and E28 (E28EGRESS) appended | `_groups` static coverage |
| `tests/hub/non_add_edits.json` | reset for this stage | TST-CO-05 c |
No legacy path, `data/` file or existing hub module was edited.

### RD-3 Deviations (proposed; none approved by Dinesh)
| ID | Deviation | Default taken | Why safest |
|---|---|---|---|
| S28-DEV-01 | New package `hub/resilience/`, nothing wired into shipped commands | no behaviour change in any shipped command | Stage 27 behaviour and goldens untouched; wiring needs a decision (D-28-01 / D-28-02) |
| S28-DEV-02 | Guarded path fails fast on shape errors (shipped client retries them, FG-01 / DQ-S21-03) | fail fast; `retry_shape_errors` true restores bounded retries | a deterministic fault must not consume the retry budget or hide a contract break |
| S28-DEV-03 | Breaker counts failed CALLS (3, cooldown 60 s, 1 probe); retry budget 20 % / cap 10; back-off capped at 8 s (A-28-01..03) | numbers chosen conservatively, not measured | fewer requests to a struggling source |
| S28-DEV-04 | Listener cap component default 64, sheds with the existing 429 `E-REQ-RATE-LIMITED` instead of a new code | no new error code, registry unchanged (P07) | keeps the Stage 27 error registry closed |
| S28-DEV-05 | Artifact directory `docs/28-reliability/` (engagement-lead instruction) instead of the prompt's `docs/28-resilience/` (also named in DW-32) | follow the instruction; DW-32's path is superseded by this note | explicit instruction wins; no content difference |
| S28-DEV-06 | The only non-add edits: `tests/hub/regression_groups.json` (two groups appended) and `tests/hub/non_add_edits.json` (reset) | listed in `non_add_edits.json` | required by the Stage 20 DW-02 / DW-05 mechanism |
| S28-DEV-07 | TST-NFR-01/02/05 and the other 26 groups not re-run on the laptop; CT-17 / CT-18 NOT-RUN | orchestrator's cloud regression covers them; CT-17 has no golden (U-07-05), CT-18 needs Docker / HAR-05 | speed rule of the run; no claim made from them |

### RD-4 Open items and decisions for Dinesh Naik (recommended default in brackets; defaults are NOT approvals)
| ID | Item | Owner | Due |
|---|---|---|---|
| D-28-01 | Wire `GuardedGateway` into `hub.intake gateway-pull` and persist breaker state across runs (file beside the audit anchor [recommended: file, atomic write, malformed = refuse] vs store table + migration); adds `resilience` config section (closed key set) and metrics for Stage 31 | Engagement lead (Dinesh Naik) | Stage 30 |
| D-28-02 | Wire `BoundedLoopbackServer` into `hub web serve` / `hub r2 serve` with a cap [64] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-28-03 | Confirm or change defaults A-28-01..A-28-03 once a real source exists | Engagement lead (Dinesh Naik) | before real data |
| D-28-04 | Late-delivery catch-up (FG-02 / DQ-S21-06) [manual idempotent catch-up run now; scheduled catch-up only after the scheduler decision HAR-10] | Engagement lead (Dinesh Naik) | Stage 29 / 30 |
| D-28-05 | Shape errors: fail fast [yes, as built in the guarded path] (DQ-S21-03) | Engagement lead (Dinesh Naik) | Stage 30 |
| D-28-06 | Capacity, freshness and RTO / RPO targets (none exist) [declare as SLO candidates at Stage 31, not requirements] | Engagement lead (Dinesh Naik) | Stage 31 |
| D-28-07 | Approved host / harness for disk-full and power-loss injection and restore timing | Engagement lead (Dinesh Naik) | Stage 29 |
| D-28-08 | CT-18 container restart: approve HAR-05 or keep NOT-RUN | Engagement lead (Dinesh Naik) | Stage 30 |
| D-28-09 | Lower SQLite `busy_timeout` (30 s) [5 s] - behaviour change in `hub/web/app.py` | Engagement lead (Dinesh Naik) | Stage 30 |
| D-28-10 | Freshness indicator on reads / reports (F-GD-01) [add run-age to the status view] | Engagement lead (Dinesh Naik) | Stage 30 / 31 |

### RD-5 Hand-off
- **Stage 29 (incident / BC-DR)** consumes: FMEA (FM-01..FM-17), degradation levels L0-L3, recovery behaviour per mode, the unrun injections FI-13 / FI-14, RTD-33 (restore loses post-backup writes), the runbook gap SUF-02.
- **Stage 31 (SLOs)** consumes: SLI candidates that do not exist as metrics yet - source freshness (last successful checkpoint age), failed-run count, breaker-open time, shed-connection count, 503 rate - plus the proxy capacity figures with their labels; no target is proposed as a requirement.
- **Stage 30 (cutover / decommission)** consumes: D-28-01, D-28-02, D-28-09, D-28-10 as wiring items.

## Evidence References
All artifacts in `docs/28-reliability/`, `docs/28-reliability/evidence/`, `.fde/orchestrator-decisions.md` (OD-08, OD-32, OD-34), `tests/hub/non_add_edits.json`.

## Assumptions
- A-28-01..A-28-03 (defaults), A-28-00, A-28-FM-1, A-28-FB-1, A-28-CAP-1, A-28-GD-1, A-28-AI-1, A-28-FI-1, A-28-FR-1: see the individual artifacts. All owned by the Engagement lead (Dinesh Naik); none confirmed.

## Unknowns
- U-28-01 source behaviour; U-28-02 volumes; U-28-03 disk-full / power loss; U-28-06 Python 3.12+ / production host; U-28-11 Python 3.12+ results.

## Unresolved Issues
- D-28-01 .. D-28-10 above.

## Residual Risks
- RR-28-01 not wired; RR-28-02 FM-11 / FM-12 unproven; RR-28-03 ratings are not telemetry; RR-28-07 proxy numbers; RR-28-08 L1 degradation can go unnoticed; RR-28-10 doubles are not a real network; RR-28-11 sandbox only. The Stage 24-27 residual risks RS-01..RS-16 remain OPEN and none is accepted by this stage.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
