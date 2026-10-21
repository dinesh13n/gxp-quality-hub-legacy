---
stage: "21 — Enterprise Integration"
artifact: "reconciliation-rules.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/intake/service.py (run report, queue_snapshot, vendor_totals)", "hub/intake/replay.py (verify-replay, gate G2)", "hub/runs/jobs.py (run totals reconcile)", "docs/14-transformation/cutover-plan.md CUT-3 / CUT-4", "docs/16-repo-validation/evidence/obs-laptop.json", "docs/21-integration/evidence/contract-pack.json, gateway-stub-conformance.json", "tests/hub/test_tst_hub_stg21_integration.py S01, S02, S06, S07", "tests/hub/test_tst_int_01_08_core.py", "tests/hub/test_tst_run_01_15_runs.py TST-RUN-06", "tests/hub/test_tst_int_17_29_match_untrusted_sources.py TST-INT-27/29"]
supersedes: "none"
---
**Label: synthetic data, unvalidated. Reconciliation here means "prove the hub saw exactly what the source holds, and nothing changed in the source"; it never repairs a source and never overwrites a status (the legacy in-place reconcile, IL-04, is not reproduced).**

## Summary
Ten reconciliation rules (RR-01..RR-10) cover counts, content, replay, contract results, checkpoints and source integrity. RR-01..RR-08 are executable and green in Stage 21; RR-09 (legacy vs hub figures for CUT-4) belongs to Stage 30 (DW-39) and needs DV preserve-or-fix decisions; RR-10 (reconciliation against real systems of record) is Unknown because no real system exists. No reconciliation job is scheduled (scheduler OFF); every rule runs on demand or in tests.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RR-1 Rules
| ID | Rule | Check | Shipped-data result | Evidence | Tag |
|---|---|---|---|---|---|
| RR-01 | Run completeness | `received = stored + skipped_existing`; sum of per-item outcomes = `stored`; the run's audit record carries the same counts and the outcomes digest (`hub/intake/service.py`) | holds for every Stage 21 run (S01: received = stored for all 4 sources) | INC06 S06; TST-RUN-06; S01 | [Verified Fact] |
| RR-02 | Source count parity | items read per source = rows in the pinned source | partner 8,567; source_message 15; gateway inbox 1; vendor tiny 2,400; stub 125 | S06, S02 | [Verified Fact] |
| RR-03 | Replay safety (gate G2) | re-delivering a source changes no counted total; repeats are NOOP_DUPLICATE | 67 partner REPLAY rows -> NOOP; stale stub re-pull 125 -> NOOP, totals unchanged | TST-INT-04/05; S02; `hub.intake verify-replay` | [Verified Fact] |
| RR-04 | Backfill idempotency | second backfill stores 0 rows | 0 / 8,567 | TST-INT-29; S07 (catch-up stores only the missing item) | [Verified Fact] |
| RR-05 | Outcome reproducibility | per-source `outcomes_digest` equal across runs and runtimes | equal to Stage 16 laptop observation for all 4 sources (partner `4a50d715…`, message `1aa6d987…`, gateway `221e9a83…`, vendor `99be82fa…`) | S01 | [Verified Fact] |
| RR-06 | Contract-result parity | stored `contract_check` counts = static contract evaluation | equal for all 4 sources | S01 | [Verified Fact] |
| RR-07 | Checkpoint arithmetic | `next_offset = offset + len(items)`; last checkpoint = total pulled; empty page keeps it | 125 after pages 50/50/25/0 | S02 | [Verified Fact] |
| RR-08 | Source integrity | pinned source and every FX-BASE125 file byte-identical after all runs; legacy status columns never written | identical; backup checksum rc 0 | S06; TST-INT-03; TST-CO-04 c | [Verified Fact] |
| RR-09 | Legacy vs hub figures (CUT-4) | legacy value, hub value, explained delta (e.g. month-end 742,956.61 vs 622,826.44 fan-out; Java double vs Decimal, DV-04) | not run in Stage 21 | Stage 30 DW-39; TST-INT-27 (Decimal) | [Inference] scope |
| RR-10 | Reconciliation against real systems of record | — | none exists | — | [Unknown] |

### RR-2 Ownership and cadence
| Rule | When | Who | Tag |
|---|---|---|---|
| RR-01, RR-06 | every run (built in) | system | [Verified Fact] |
| RR-03 | `hub.intake verify-replay` on demand; gate G2 in tests | host operator | [Verified Fact] |
| RR-02, RR-05, RR-07, RR-08 | Stage 21 tests (STG21), full regression before each merge | orchestrator / build agent | [Verified Fact] |
| Any scheduled reconciliation | none (scheduler OFF, OPD-11 open) | Engagement lead (Dinesh Naik) | [Unknown] |

## Evidence References
- `evidence/contract-pack.json`, `evidence/gateway-stub-conformance.json`, `evidence/test-runs-laptop.json`.

## Assumptions
- A-21-RR-1 [Assumption] Count, digest and replay parity are sufficient reconciliation for shadow mode; value reconciliation is a cutover concern (Stage 30). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-RR-1 Reconciliation cadence and owner once any capability is authoritative (CUT-3 / CUT-4) - Engagement lead (Dinesh Naik), Stage 30.

## Unresolved Issues
- RR-09 waits for DQ-13 (DV preserve-or-fix) and DW-39.

## Residual Risks
- RR-21-RR-1 Without a schedule, reconciliation depends on an operator remembering to run it (Low in shadow mode; Medium after cutover).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
