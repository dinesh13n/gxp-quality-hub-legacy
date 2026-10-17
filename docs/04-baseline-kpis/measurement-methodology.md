---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "measurement-methodology.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/evidence/measure_baseline.py", "docs/baseline-measurement-notes.md", "docs/00-preflight/operating-contract/evidence-contract.md", ".fde/orchestrator-decisions.md (OD-02, OD-03a)", "app/baseline.py"]
supersedes: "none"
---
## Summary

How every KPI is measured and reproduced. Method validated on synthetic data only. Rule from `docs/baseline-measurement-notes.md`: record data window, denominator, exclusions and assumptions before comparing outcomes. Stages 34-36 MUST re-run the same script against the same population definition and compare like with like.

## Findings

### Reproduction protocol (EV-02/EV-03)

1. Environment E0 (read-only): `cd <repo root> && python3 -I docs/04-baseline-kpis/evidence/measure_baseline.py data/legacy.sqlite3 > out.json`. The script opens the DB with `file:…?mode=ro&immutable=1`; it cannot write. [Verified Fact] Run on 2026-10-17: rc=0; DB sha256 unchanged (`c254649f57e2…d70aa`); a second run was byte-identical (`cmp` OK); output sha256 `31ffa1b2b136de5a0676f612e172d190d4e23730ee1c7e3c7ebf7f41216d61ba`.
2. Cross-check (E1 sandbox, OD-03a): full repo copy in `$HOME/fde_sbx/stage4`, `python3 -m app.baseline` returned `open_cases=89`, `hours_per_case=0.603`, matching K-09-OPS (89) and K-12 (0.603). After the run, `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root: OK; `git status --porcelain` showed only `?? docs/04-baseline-kpis/`.
3. Compare after intervention by diffing JSON keys of the two outputs; DB hash and script hash must be recorded with each run (change of either is a versioned event).

### Common parameters

| Parameter | Value | Class |
|---|---|---|
| Population | 125 cases (`cases`), shipped DB per OD-02 | [Assumption] provisional; Q-02-04 open |
| Window (cases) | created 2023-01-25T23:00Z .. 2025-12-19T07:00Z (spans 36 calendar months, matching the 36 `operating_costs` periods) | [Verified Fact] |
| Window (feeds/exceptions/outages/batch runs) | 2021-01-01 .. 2024-12-27 (feeds to 2024-12-20; outages to 2024-04-22) | [Verified Fact] |
| Overlap | Case window starts 2023-01; feeds/exceptions end 2024-12; outages end 2024-04: windows only partly overlap, and 99 % of external references do not match any case | [Verified Fact] |
| Reference time | AS_OF = 2025-12-19T07:11Z, not wall clock (for reproducibility) | [Assumption] A-04-03 |
| Exclusions | None applied; no row removed (negative delays, unmatched refs kept and reported) | [Verified Fact] |
| Denominators | stated per KPI in `kpi-dictionary.md`; K-12/K-13 use operating_costs.total_cases (108), others use case count (125) | [Verified Fact] |
| Statistics | median and p90 by linear interpolation; no CI because n is small | [Verified Fact] |
| Seasonality | Not assessable: mean 3.47 cases per month, no multi-year real cycle | [Inference] |

### Per-KPI method

| KPI | Method | Reproducible now? | If not: how to obtain (owner: Engagement lead (Dinesh Naik)) |
|---|---|---|---|
| K-01 | Count unsafe events from an audit log of dispositions/closures with actor and authorisation | No (no log) | Define audit-log requirement at Stage 12/23; measure by Stage 16 test harness; production telemetry requires a real tenant (does not exist) |
| K-02 | Count STATUS_REVIEWED payloads having evidence/source keys | Yes (structural) | Real measure = manual sample audit (BR-07 verification) |
| K-03 | Inspect each reporting module's outputs for definition tags | Yes for `app/baseline.py` | Enumerate `app/server.py`, `app/operational_report.py`, `scripts/` at Stage 7 |
| K-04 | Needs `closed_at` and evidence/approver timestamps | No | Add event capture (post-intervention only; do not alter legacy flow now) or obtain QMS/LIMS audit trail via real stakeholder |
| K-05 | As K-04 | No | As K-04; proxies P-01/P-02 |
| K-06 | SQL anti-join `ref_id NOT IN (select id from cases)` | Yes | — |
| K-07 | Sandbox test: deliver an already-processed item twice, diff exception queue size and totals | No (not run; Stage 4 is measurement-only) | Stage 7 characterisation test in `$HOME/fde_sbx/` copy; existing partner replay code in `app/partner_feeds.py` |
| K-08 | `ingest_ts − source_ts` per row | Yes, with DQ caveat | Clean clock-skew rule at Stage 11; do not drop rows silently |
| K-09 | Non-CLOSED count and age at AS_OF per site | Yes (D-OPS) | D-EVID/D-FIN need evidence fields and a D-FIN definition |
| K-09U | Outcome share in `policy_exceptions` | Yes | Meaning of WAIVED/BLOCKED from owner |
| K-10 | Compare monthly `count(cases by created month)` to `operating_costs.total_cases` | Yes | Agree one cut-off with finance/ops (SC-04, DR-21) |
| K-11 | Look for decision record for DR-20/DR-21 | Yes | Dinesh records decision or "accepted open" |
| K-12/13 | Aggregate `operating_costs` | Yes | Replace estimates with time sheets/ledger (real) |
| K-14..K-20 | SQL aggregates in the script | Yes | — |
| K-21 | After deployment: cases via new path / cases | N/A now | Stage 34 |
| K-22 | Needs rework time capture | No | Time-and-motion or ticket data at Stage 5 (no real people) |

### Segmentation approach

Primary: site (6 values, required by BR-12), severity (4), segment (5), status (5), month/year. [Inference] Site cells hold 13-30 cases; severity CRITICAL has 2 cases, so any severity-level statistic is non-robust. Reported by site for K-09-OPS only.

## Evidence References

`evidence/measure_baseline.py` (sha256 cb062e1b…f60a6); `evidence/measure_baseline.output.json`; `evidence/app_baseline_sandbox_output.txt`; `docs/00-preflight/operating-contract/evidence-contract.md` EV-02/EV-03.

## Assumptions

A-04-03 AS_OF choice. A-04-04: the snapshot status in `cases` is the current status; no history exists, so cohort/trend KPIs cannot be built.

## Unknowns

U-04-05 whether other modules emit untagged figures; U-04-06 whether the 6,000-case regenerable dataset (seed 4326) gives materially different values (it would replace OD-02 if Dinesh chose it; not generated here, as generation writes `data/`).

## Unresolved Issues

- Q-02-04/05 open; if the baseline DB changes, every value must be re-measured under a new version, and a change record written.

## Residual Risks

- Script reproducibility tied to SQLite JSON1 availability and Python ≥3.10 (verified 3.10.12 only).
- Cross-check covers only 2 of 22 KPIs via application code.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial methodology. |
