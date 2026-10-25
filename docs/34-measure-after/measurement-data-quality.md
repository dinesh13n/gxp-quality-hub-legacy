---
stage: "34 — Measure After-Intervention KPIs"
artifact: "measurement-data-quality.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/baseline-data-quality.md", "docs/04-baseline-kpis/evidence/measure_baseline.output.json (dq_* keys)", "docs/34-measure-after/evidence/", "../_data-backup-2026-10-17/SHA256SUMS.txt (1,512 files)", "docs/12-specs/features/f07-metrics-definition-tags.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
Data quality of the **measurement itself**: (a) the sandbox run is sound and the working tree was not touched (checksums rc 0 before and after, baseline output byte-identical); (b) the underlying data keep every Stage 4 defect (they are the same data), so the same figures stay "not decision-grade"; (c) the hub path adds four measurement-quality issues: wall-clock `as_of`, non-deterministic `computed_at`/value ids, 100 % open exception rate in an unworked queue, and differences between hub and Stage 4 counts that are not yet explained.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DQ-1 Run integrity [Verified Fact]
| Check | Result |
|---|---|
| Working-tree data backup `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` (1,512 files) | rc 0 before the runs; rc 0 after all sandbox runs; rc 0 again at hand-off (see commit message) |
| Work location | worktree `~/fde_sbx/wt-s34` (branch `stage-34-measure-after`, created from `main` fea785c); runs in full-copy sandbox `~/fde_sbx/s34-run` with the hub store in `~/fde_sbx/s34-scratch`; the Stage 31 working tree (`$HOME/mnt/Case-Execution/gxp-quality-hub-legacy`, branch `stage-31-observability`) was not switched, written or run against |
| Sandbox DB | sha256 `c254649f57e2…d70aa` = baseline pin; `hub.adapters.legacy_sqlite.open_snapshot` verifies the pin again at every run (FixtureMismatch otherwise) and opens the snapshot `mode=ro&immutable=1` |
| Frozen script output | `cmp`-identical to the Stage 4 JSON; second pass not needed (Stage 4 already showed determinism) |
| Hub store integrity | `verify-projection` ok (125 cases, 0 mismatches); `verify-chain` ok (125 cases, 250 events); `verify-audit` ok (29 records, 22 anchors, head seq 29) |
| Egress | the hub CLIs install the egress guard; no network access was needed; no model call (No-AI, OD-08) |

### DQ-2 Defects inherited from Stage 4 (unchanged because the data are unchanged) [Verified Fact]
- 2,234 of 8,567 feed rows (26.1 %) have negative reconciliation delay (ingest before source): K-08 is not decision-grade.
- 99 % of external references (feeds, exceptions) do not match any of the 125 cases (generator residue, IO-10): K-06, K-09U are proxies (OD-07).
- `operating_costs.total_cases` is random (OD-07): K-10, K-12, K-13 compare unrelated populations.
- 163 negative-quantity feed rows, 86 rows with injection-marker notes, six inconsistent units and five currencies in the feed (`dq_*` keys).
- Case amounts: 259.78 .. 26,894.94, mean 4,982.61 (matches `app.baseline` `mean_amount`).

### DQ-3 Hub-path measurement issues [Verified Fact unless marked]
| ID | Issue | Effect | Handling here |
|---|---|---|---|
| DQ-34-01 | `hub.metrics snapshot` uses the wall clock as `as_of` (no parameter) | age buckets cannot be compared with the frozen AS_OF 2025-12-19 (310 days apart) | age comparison declared not comparable; routed D-34-03 |
| DQ-34-02 | Every snapshot appends new value ids (MV-00000001..4, then 5..8, and 9.. after intake) with new `computed_at`; contents equal except `as_of`/`window_end`/`computed_at`/`value_id` | two runs are not byte-identical, so AC-MET-21 ("byte-identical apart from computed_at") holds only if as_of is also excluded [Inference from the observed diff] | comparisons made on `value` and `detail` fields, not on files |
| DQ-34-03 | `raw_intake` grows with every re-delivery (8,583 to 17,150); outcome counts do not | storage growth under replay; outcome-level safety holds | recorded in K-07 row |
| DQ-34-04 | K-06 matched rows 173 vs hub `linked` 168; negative-quantity rows 163 (Stage 4) vs 161 NEGATIVE_VALUE reason entries (hub) | counts differ by 5 and 2 | not investigated [Unknown]; U-34-02, U-34-11 |
| DQ-34-05 | Unresolved-exception rate 1.0000 over 8,335 items in an unworked queue | not a performance value | explained in every place it appears |
| DQ-34-06 | The first `snapshot` attempt on a store without seeded candidate policies failed with `E-MET-DEFINITION-REQUIRED` (unknown tag D-OPS); `hub.policy seed` (idempotent, candidates only, adopts nothing) fixed it | shows the hub cannot produce a tagged figure until at least candidate policies exist; consistent with ADR-011 | recorded; `evidence/run_hub_metrics.sh` includes the seed step |
| DQ-34-07 | Sandbox timings are from a shared laptop | no latency claim | none made |

### DQ-4 Data-quality gaps that block real after-measurement [Unknown / Verified Fact]
- No closure, evidence-complete or approver timestamp exists in any legacy table (K-04, K-05, K-09-EVID, K-22). The hub can record such events (`FACT_OPS_CLOSED`, `FACT_EVIDENCE_COMPLETE`, `ESIGNATURE_RECORDED`) but none has been recorded: n = 0 completed cycles.
- No production data source is identified for any KPI (U-04-04).
- Synthetic data cannot validate any target (A-03-13).

## Evidence References
`evidence/hub-01g-verify-projection.json`, `hub-01h-verify-chain.json`, `hub-16-verify-audit.json`, `hub-03-snapshot.json`, `hub-04-snapshot-again.json`, `hub-06-values.json`, `hub-14-snapshot-after-intake.json`, `hub-15-values-after-intake.json`; `docs/04-baseline-kpis/baseline-data-quality.md`.

## Assumptions
- A-34-11 [Assumption] Seeding the hub's candidate policy objects (`hub.policy seed`) before measurement is an acceptable sandbox step: it adopts nothing and mirrors what the INC-07 tests do. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-34-11 Why hub counts 161 NEGATIVE_VALUE reasons against 163 negative-quantity feed rows (Stage 4).
- U-34-12 Python 3.12+ behaviour of the measurement scripts (verified on 3.10.12 only).

## Unresolved Issues
- Wall-clock `as_of` (D-34-03), unexplained count differences (U-34-02, U-34-11).

## Residual Risks
- RR-34-09 Reusing sandbox figures later without re-running the scripts at the recorded hashes. Mitigation: `evidence/SHA256SUMS.txt` and the script copies.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
