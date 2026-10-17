---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "baseline-evidence.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/evidence/*", "data/legacy.sqlite3", "data/enterprise_legacy.sqlite3", "../_data-backup-2026-10-17/SHA256SUMS.txt"]
supersedes: "none"
---
## Summary

Raw evidence index for Stage 4 (EV-01..EV-08 classes from `docs/00-preflight/operating-contract/evidence-contract.md`). Every number in the other seven artifacts traces to one of the items below. Command environment: E0 (read-only, `mode=ro&immutable=1`) unless marked E1 (sandbox copy under `$HOME/fde_sbx/stage4`).

## Findings

| ID | Evidence | Class | Command / path | Result |
|---|---|---|---|---|
| E-01 | Baseline DB identity | EV-04 | `sha256sum data/legacy.sqlite3` (before and after all measurement) | `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa` both times; matches OD-02 |
| E-02 | Schema and row counts | EV-03 | `python3 -I` + `sqlite3.connect('file:data/legacy.sqlite3?mode=ro&immutable=1')` over `sqlite_master` | 19 tables; cases 125, events 145, source_messages 15, operating_costs 36, partner_feeds 8,567, policy_exceptions 224, deviations 42, capa_actions 21, lab_results 125, batch_records 125, batch_runs 60, upstream_outages 72, materials 30, sop_versions 45, reference_versions 180, vendor_file_rows 2,400, gateway_inbox 1, vendor_file_imports 1, gateway_checkpoints 0 |
| E-03 | Status distribution | EV-03 | `select status,count(*) from cases group by 1` | CLOSED 36, ESCALATED 9, OPEN 42, REOPENED 8, UNDER_REVIEW 30 |
| E-04 | Event types | EV-03 | `select event_type,count(*) from events group by 1` | CASE_CREATED 125, STATUS_REVIEWED 20 (payload keys: reviewer, severity) |
| E-05 | Full KPI computation | EV-02/03 | `python3 -I docs/04-baseline-kpis/evidence/measure_baseline.py data/legacy.sqlite3` | rc=0; output `evidence/measure_baseline.output.json` sha256 `31ffa1b2b136de5a0676f612e172d190d4e23730ee1c7e3c7ebf7f41216d61ba`; script sha256 `cb062e1bae216db47abd909f8923ee9284fa619f2743ba86ae8d3849d53f60a6`; second run byte-identical |
| E-06 | Application cross-check | EV-02 (E1) | `python3 -m app.baseline` in `$HOME/fde_sbx/stage4` (Python 3.10.12) | records 125, open_cases 89, urgent_cases 2, mean_amount 4982.61, sites 6, hours_per_case 0.603 (`evidence/app_baseline_sandbox_output.txt`) |
| E-07 | Code of existing KPI logic | EV-01 | `app/baseline.py` L1-13; `app/legacy_logic.py` (`priority`, `manual_review_required`) | `open_cases = status != 'CLOSED'`; `hours_per_case = Σlabor_hours/Σtotal_cases` |
| E-08 | Enterprise estate probe | EV-03 | `python3 -I evidence/probe_enterprise_estate.py data/enterprise_legacy.sqlite3` | sha256 of DB `210f4baf…b4c0b` unchanged; output sha256 `a6288205…df50`; 12,500 objects, 1 history row per object |
| E-09 | Stage 3 criteria | EV-06 | `docs/03-problem-value/success-criteria.md` SUC-01..11, FAIL-01..06 | Source of KPI list |
| E-10 | Definition gap | EV-06 | `docs/02-stakeholders/decision-rights-map.md` L40-41 (DR-20, DR-21); `stakeholder-conflicts.md` SC-01 | No decider |
| E-11 | Open questions | EV-06 | `docs/02-stakeholders/operating-contract-confirmations.md` L33, L73-74 | GD-02 OPEN (blocks Stage 4), Q-02-04, Q-02-05 unanswered |
| E-12 | Integrity after run | EV-04/05 | from repo root: `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` ; `git status --porcelain` | exit 0 (no output, all 1,512 files OK); only `?? docs/04-baseline-kpis/` |

### Reference results (excerpt, verified in E-05)

K-06: 8,394/8,567 and 222/224 · K-08: median 0.02 h, p90 168 h, 75.24 % ≤ 4 h, 2,234 negative · K-09-OPS: 89/125, median 565.05 d, p90 974.15 d · K-10: 8/36 months equal, 125 vs 108 · K-12: 0.603 h · K-15: 8/125 · K-16: 29/125 · K-17: 8/12 · K-18: 6/13 · K-19: 3.25 %, 19/60 · K-20: median 2.30 h, 8/72 open.

## Evidence References

This file is the index. Files in `docs/04-baseline-kpis/evidence/`: `measure_baseline.py`, `measure_baseline.output.json`, `app_baseline_sandbox_output.txt`, `probe_enterprise_estate.py`, `probe_enterprise_estate.output.json`.

## Assumptions

Sandbox copy was byte-equivalent to the working tree at the time of copy (copied with `cp -r` after measurement; not hash-compared file by file).

## Unknowns

None additional.

## Unresolved Issues

- E-12 final integrity check must be repeated by the orchestrator before commit (see sign-off).

## Residual Risks

- `data/` is git-ignored, so the DB hash is the only anchor; the backup SHA256SUMS is outside the repo.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial evidence index. |
