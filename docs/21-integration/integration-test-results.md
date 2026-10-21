---
stage: "21 — Enterprise Integration"
artifact: "integration-test-results.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/21-integration/evidence/test-runs-laptop.json", "docs/21-integration/evidence/legacy-paths-and-checksums.txt", "docs/21-integration/evidence/contract-pack.json", "docs/21-integration/evidence/gateway-stub-conformance.json", "docs/21-integration/evidence/consumer-scan.json", "tests/hub/test_tst_hub_stg21_integration.py", "tests/hub/test_tst_hub_stg21_egress_guard.py", "tests/hub/_stg21.py", "tests/hub/regression_groups.json (groups S21, E21)"]
supersedes: "none"
---
**Label: synthetic, unvalidated. All runs on the reference laptop VM (Python 3.10.12) in sandbox copies built by `tests/hub/run_hub_tests.py` (OD-03a); no hub code ran from the working tree; sandboxes deleted after each run (OD-16); backup checksum manifest rc 0 before and after every run. Per OD-23 the build agent ran only its new / changed tests plus the DW-10 / DW-12 targeted sets; the orchestrator runs the full hub regression (now 426 methods) before merge.**

## Summary
| Run | Selection | Result | Runner wall | Checksum pre / post | Tag |
|---|---|---|---|---|---|
| Group **S21** (`run_hub_groups.py --group S21`) | STG21 S01-S07 | **7 / 7 ok**, expected 7 = executed 7 | 65.0 s | 0 / 0 | [Verified Fact] |
| Group **E21** (`--group E21`) | E21EGRESS S90 (STG21 under the egress guard) | **1 / 1 ok**; inner 7 ok, 0 skipped, 0 egress attempts, model_calls_total 0 | 68.8 s | 0 / 0 | [Verified Fact] |
| DW-12 targeted | TST-CO-04 (6), TST-CO-05 (3), STG20 S01 (manifest after the S21 / E21 registration) | **10 / 10 ok** | ~67 s | 0 / 0 | [Verified Fact] |
| DW-10 targeted | TST-INT-09..16 | **8 / 8 ok** | ~68 s | 0 / 0 | [Verified Fact] |
| Legacy-path diff | `git diff --name-status baseline-as-found -- app legacy_batch legacy_java legacy_js sql data services integration contracts scripts ops` | empty | — | rc 0 | [Verified Fact] |
| **S21-DEV-02 fix re-run** (after commit 4cd3985) | groups S21, B, A, C1, C3, I6, I7, I8b, E8, E21 (one device call each) | **all green**: 7, 41 + 1 skipped (as Stage 20), 45, 5, 1, 43, 59, 43, 1, 1; executed = expected 247 / 247 | 61-99 s per group | 0 / 0 each | [Verified Fact] `evidence/fix-regression-laptop.json` |
Every device call stayed under the 180 s cap (largest 82.9 s for the first S21 run, 6 tests); sandbox build time dominates (~55-60 s of each run).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TR-1 New tests (Stage 21)
| Test | Covers (analysis dimension) | Key assertions | Result | Tag |
|---|---|---|---|---|
| STG21 S01 source-contract pack | 1 contract conformance; 4 reconciliation | 0/8,567, 15/15, 0/1, 0/2,400; store = static; enforce effect; digests = Stage 16; = committed pack | ok | [Verified Fact] |
| STG21 S02 shipped stub conformance | 1, 3 retry/idempotency, 6 stale / duplicate | catalog; pages 50/50/25/0; clamp; checkpoint 125; stale re-pull 125 NOOP; contract 0/125 | ok | [Verified Fact] |
| STG21 S03 stub failure responses | 3, 7 dependency failure; 2 (no credential sent) | 503 + 429 retried (3 attempts, back-off [0.5, 1.0]); shape error bounded; 400 not retried; GET only | ok | [Verified Fact] |
| STG21 S04 timeout | 5 timeout; 7 | 2 attempts at timeout 0.3 s; TimeoutError; failed run, 0 rows, no checkpoint; shipped defaults 5 s / 3 / 0.5 | ok | [Verified Fact] |
| STG21 S05 consumer scan | DW-11 | LO-01..LO-13 rows; frozen legacy readers = committed scan; no CI reader of LO-09..LO-11 | ok | [Verified Fact] |
| STG21 S06 read-only re-proof | DW-12; 7 | FX-BASE125 tree byte-identical; OD-09 hash; read-only opens; one SQLite connect site | ok | [Verified Fact] |
| STG21 S07 late delivery | 6 stale / out-of-order | resumed job does not see a late item (RTD-61); catch-up stores exactly it; 2,234 partner rows source_ts > ingest_ts | ok | [Verified Fact] |
| E21EGRESS S90 | AC-CO-12 for STG21 | inner suite green, 0 egress, 0 model calls, nothing skipped | ok | [Verified Fact] |

### TR-2 Failure-mode coverage (Completion Gate: "integration tests cover failure modes")
| Failure mode | INT-01/02 DB | INT-03..05 legacy rows | INT-06 gateway | INT-07 CSV | Tag |
|---|---|---|---|---|---|
| unreachable / missing | fail closed: TST-CO-04 e/f (a missing DB file is not separately tested) | (via AD-01) | TST-INT-26 | sandbox guard TST-CO-06 | [Verified Fact] |
| timeout | n/a (local file) | n/a | **S04** | n/a | [Verified Fact] |
| transient 5xx / 429 | n/a | n/a | **S03**, INC06 S09 | n/a | [Verified Fact] |
| schema / shape drift | TST-CO-04 e | TST-INT-09/10 | **S03**, INC06 S09 | TST-INT-27 | [Verified Fact] |
| duplicate / replay | n/a | TST-INT-04/05/29 | **S02** | TST-INT-29 pattern (backfill) | [Verified Fact] |
| stale / late | TST-CO-04 e (hash) | **S07** | **S02** | n/a | [Verified Fact] |
| contract failure | n/a | TST-INT-12/13/14, **S01** | **S02** | **S01** | [Verified Fact] |
| write attempt / integrity | TST-CO-04 b/c, **S06** | TST-INT-03 | GET only **S03** | **S06** | [Verified Fact] |
| authn / authz | n/a (file) | binding change INC06 S04 | loopback-only TST-INT-25, no credential **S03** | n/a | [Verified Fact] |

### TR-3 Not run by the build agent (by design, OD-23)
- [Verified Fact] The full hub regression (`run_hub_groups.py --all`, 426 methods incl. S21 / E21) and the characterisation harness are run by the orchestrator before merge. Stage 21 changed no hub code, so no existing test outcome can change through Stage 21 code; the two edited data files (`regression_groups.json`, `non_add_edits.json`) were checked by STG20 S01 and TST-CO-05 c.

## Evidence References
- `evidence/test-runs-laptop.json` (per-test status, counts, runner seconds, checksum rc, Python version, commands).
- `evidence/legacy-paths-and-checksums.txt`.

## Assumptions
- A-21-TR-1 [Assumption] Replaying the stub's own failure bodies through a loopback double is equivalent evidence to a live fault on `/api/events`, which the unchanged stub cannot produce (AF-04). Confirm: Stage 26 TEVV agent.

## Unknowns
- U-21-TR-1 Full-regression result with the S21 / E21 groups on the cloud workspace (Python 3.13) - pending (orchestrator).

### TR-4 Defect found after hand-off (S21-DEV-02)
- [Verified Fact] The orchestrator's first full regression failed 8 groups because `tests/hub/_stg21.py` imported `urllib.request` (No-AI R2; TST-CO-11 d, TST-CO-15 a, TST-CO-12 e1/e3, INC06 S12, INC07 S14, TST-NFR-18, E06/E07/E08EGRESS). Fixed in 4cd3985 (raw-socket loopback client); the affected groups were re-run green on the laptop (row above). The S21 group alone could not catch it: R2 is enforced by group B / C tests, which the build agent did not run (process gap, see integration-readiness.md S21-DEV-02).

## Unresolved Issues
- None blocking.

## Residual Risks
- RR-21-TR-1 STG21 S01 / S02 / S05 compare against committed evidence; a legitimate change of shipped data or legacy docs requires regenerating the evidence (by design: drift becomes visible) (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
| v0.1 (amended) | 2026-10-21 | claude-fde-agent | S21-DEV-02 fix re-run results added (TR-4). |
