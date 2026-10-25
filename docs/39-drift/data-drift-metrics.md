---
stage: "39 — Drift + Continuous Improvement"
artifact: "data-drift-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["hub/adapters/baseline_pins.json", "tests/characterization/fixtures/FX-BASE125.sha256", "tests/characterization/golden/MANIFEST.sha256", "../_data-backup-2026-10-17/SHA256SUMS.txt", "docs/04-baseline-kpis/", "docs/11-data-context/", "docs/34-measure-after/", ".fde/orchestrator-decisions.md (OD-02, OD-03, OD-03a, OD-07, OD-09)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
Data drift for this product is drift of the **synthetic baseline** and of the schemas around it. There is no production data (OD-04). Six metrics (DM-01..DM-06): four are hash or structure checks that exist today, one needs a distribution snapshot that does not exist yet (GAP G-39-01), one is a count-parity check. The result of each is binary or a count; none needs a statistical test, and none is evidence about real-world data.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DD-1 Metrics
| ID | Metric | How measured (offline, sandbox copy only) | Baseline (preserved) | Candidate threshold (Assumption) | Tier on breach | State |
|---|---|---|---|---|---|---|
| DM-01 | Backup checksum parity | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root, rc | rc 0 (OD-03a; Stage 26 RT-04 required rc 0 before and after every run) | rc != 0 | INVESTIGATE at once; no run continues until explained | [Verified Fact] check exists and passed before/after S26-S31 runs (`docs/26-tevv/tevv-results.md`, `docs/31-observability/evidence/results.json` checksum_pre/post 0) |
| DM-02 | Legacy baseline store pin | sha256 + table/column lists of `data/enterprise_legacy.sqlite3` etc. vs `hub/adapters/baseline_pins.json` (read-only open, `mode=ro&immutable=1`) | pins in file (OD-09: 125 cases, seed 4100; shipped sqlite sha c254649f... per OD-02) | any difference in hash, table set or column list | INVESTIGATE; CHANGE only through class C2 if intended | [Verified Fact] pins exist; [Unknown] whether a standing command runs them outside tests |
| DM-03 | Fixture pin | `FX-BASE125.sha256` and `tests/characterization/golden/MANIFEST.sha256` verified | files in repo | any mismatch | INVESTIGATE | [Verified Fact] files exist; used by the harness |
| DM-04 | Row-count parity of the baseline | count of cases and of rows per baseline table versus the pinned set | 125 cases (OD-09) | any difference | INVESTIGATE | [Inference] derivable from the DM-02 read; [Assumption] per-table counts are not yet recorded as a baseline (GAP G-39-01) |
| DM-05 | Distribution snapshot shift | capture once, in a sandbox, per-column distributions for the fields the rules use (amount bands against the three as-found limits, status mix, site/region mix, ageing buckets at a fixed reference time) and compare later snapshots | **does not exist yet** (Unknown) | cannot be set before the first snapshot; candidate form: total-variation distance > 0.10 on any categorical field or any new/removed category | INVESTIGATE | [Unknown] GAP G-39-01; the reference-time problem is known: metrics must take `as_of` (CA-03, VL-12) or ageing drifts with the wall clock |
| DM-06 | Dataset identity | `data_origin` config must equal `synthetic` (`hub/config.py` rejects anything else before HAR-15); the 6,000-case/seed-4326 set must not appear as the baseline (OD-09) | `synthetic`, 125 cases | any other value, or a case count other than 125 in the baseline path | STOP-and-ask Dinesh (changing the dataset is a decision, not an investigation) | [Verified Fact] config guard exists |

### DD-2 Why DM-05 is only a design
[Verified Fact] OD-07 / Stage 5: `operating_costs.total_cases` is random and several time-based KPIs have no real timestamps. [Inference] A distribution snapshot of synthetic generator output measures the generator, not the world; its only legitimate use is to detect that the baseline file was replaced or regenerated. It must not be read as a signal about real customers, and must not be used to claim stability of anything in production.

### DD-3 Schema drift of the legacy stores
DM-02 covers table and column lists of the legacy stores (pinned). For the hub's own store the detector is the migration set (`DM-07` below).

| ID | Metric | How measured | Baseline | Threshold (Assumption) | Tier |
|---|---|---|---|---|---|
| DM-07 | Hub migration set and order | list `schema_migrations` rows versus the migration files (M000 coexistence, M001 access_audit forward, M002 policy rules, later increments); inserts are append-only by trigger (A-27-05) | rows present equal files present | a file without a row, a row without a file, or a changed file body for an applied migration | INVESTIGATE; CHANGE via class C1/C2 |

## Evidence References
See header. `docs/31-observability/evidence/results.json` records checksum_pre = checksum_post = 0 for the Stage 31 regression.

## Assumptions
- A-39-05 DM-05's TV-distance 0.10 is a placeholder form only; no value is meaningful before the first snapshot. Confirm: Engagement lead (Dinesh Naik).
- A-39-06 Data checks run only on sandbox copies (OD-03a); no monitor ever touches working-tree `data/`.

## Unknowns
- U-39-03 Whether any real data will ever replace the synthetic baseline (HAR-15; field classes, tenant, regime, retention are undecided, DQ-S24-xx).
- U-39-04 Time zone of the business (U-12-F06-1) which affects date-bucketed distributions.

## Unresolved Issues
- G-39-01 No distribution snapshot and no per-table row-count baseline file. Owner: Engagement lead (Dinesh Naik). Due: before any pilot or production use (no calendar date exists).

## Residual Risks
- RR-39-03 A passing hash proves the file did not change, not that it is right (OD-07 shows parts of the generator are random). Low for drift, High for any claim of meaning.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
