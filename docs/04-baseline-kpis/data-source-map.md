---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "data-source-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (sha256 c254649f…d70aa, opened mode=ro&immutable=1)", "docs/data-dictionary.md", "docs/source-system-landscape.md", "docs/04-baseline-kpis/evidence/measure_baseline.py"]
supersedes: "none"
---
## Summary

Source system, table and query per KPI, with lineage and reliability. All sources are tables in one synthetic SQLite file; lineage to any real upstream system (EBR/MES, LIMS-QMS, PartnerGateway) is Assumption A-03 (stand-ins, `docs/00-preflight/discovery/assumptions-unknowns.md` A-03). Row counts verified 2026-10-17: cases 125, events 145, source_messages 15, operating_costs 36, partner_feeds 8,567, policy_exceptions 224, deviations 42, capa_actions 21, lab_results 125, batch_records 125, batch_runs 60, upstream_outages 72.

## Findings

| KPI | Source table(s) | Query (read-only; also in the script) | Lineage / reliability |
|---|---|---|---|
| K-01 | none | n/a | [Unknown] no action log |
| K-02 | `events` | `select payload from events where event_type='STATUS_REVIEWED'` → test keys `evidence_ref`/`source` absent in all 20 (keys: reviewer, severity) | Generated rows; Low reliability |
| K-03 | `app/baseline.py` output | inspection; keys: records, open_cases, urgent_cases, mean_amount, sites, hours_per_case | Code, High |
| K-04/05 | `cases.created_at`; events lacks CLOSED/evidence | `select event_type,count(*) from events group by 1` → CASE_CREATED 125, STATUS_REVIEWED 20 only | Gap proven |
| P-01 | `events`,`cases` | `select e.recorded_at,c.created_at from events e join cases c on c.id=e.case_id where e.event_type='STATUS_REVIEWED'` | 20 rows |
| P-02 | `source_messages`,`cases` | `… join cases c on c.id=json_extract(m.body,'$.ref')` | 15 rows, all match |
| K-06 | `partner_feeds`,`policy_exceptions`,`cases` | `select count(*),sum(ref_id not in (select id from cases)) from partner_feeds` (and policy_exceptions) | Generator residue (IO-10) |
| K-07 | `partner_feeds` (presence), code `app/partner_feeds.py` (behaviour) | `select count(*) from partner_feeds where processing_status='REPLAY'` = 67 | Behaviour untested |
| K-08 | `partner_feeds.source_ts, ingest_ts` | per-row hours difference | 26.1 % negative; Low |
| K-09-OPS | `cases` | `select site,status,created_at from cases` then age = AS_OF − created_at where status<>'CLOSED' | Snapshot; no history |
| K-09U | `policy_exceptions` | `select outcome,count(*) from policy_exceptions group by 1` | 222/224 orphan refs |
| K-10 | `cases`,`operating_costs` | `select substr(created_at,1,7),count(*) from cases group by 1` vs `select period,total_cases from operating_costs` | Two independent generators |
| K-11 | `docs/02-stakeholders/decision-rights-map.md` | rows DR-20, DR-21 | Document, High |
| K-12/13 | `operating_costs` | `select sum(labor_hours),sum(total_cases),sum(infrastructure_usd)` | Estimates |
| K-14 | `cases` | by year/month counts | — |
| K-15/16 | `cases`; `app/legacy_logic.py` | `status='REOPENED'`; `severity in ('HIGH','CRITICAL') or status in ('ESCALATED','REOPENED')` | — |
| K-17 | `deviations` | `status='CLOSED' and root_cause is null` | Synthetic nulls |
| K-18 | `capa_actions` | `state` counts | — |
| K-19 | `batch_runs` | `sum(rejected_count)/sum(input_count)`; FAILED/runs | — |
| K-20 | `upstream_outages` | `resolved−began`; `resolved is null` | — |
| K-21/22 | none | n/a | Not available |

### Linkage findings

- [Verified Fact] `cases` has no `batch_id`; `batch_records`/`deviations`/`lab_results` are not linked to `cases` by any declared key. [Inference] An id offset (case `C000000nn` ↔ batch `BT000000(nn-1)`) joins all 125 rows, but it is an undocumented convention, so case-level quality KPIs (K-17..) are kept at table level and NOT joined to cases.
- [Verified Fact] `events.CASE_CREATED.payload.status` equals `cases.status` for all 125 cases: the events table records the *current* status at creation time, not a history, so it cannot give transition times.
- [Verified Fact] `source_messages` (15 rows) all reference real cases and statuses agree with `cases.status`; `partner_feeds`/`policy_exceptions` mostly do not.

## Evidence References

`docs/data-dictionary.md`; schema dump (E-02 in `baseline-evidence.md`).

## Assumptions

Stand-in systems are not real (A-03). Case↔batch id-offset is not a business key.

## Unknowns

U-04-07 real system of record for closure, evidence and approver timestamps; U-04-08 whether any report in `data/documents`, `data/archive_documents` or `data/lake` holds closure data (not examined; out of Stage 4 scope, schedule for Stage 5/7).

## Unresolved Issues

- `data/enterprise_legacy.sqlite3` was probed read-only (`evidence/probe_enterprise_estate.py`): it is a secondary 12,500-object estate (not the OD-02 baseline) whose `state_history` has exactly one row per object (OPEN→current state at the object's own `event_at`), so it also has no closure timestamp; `evidence_events` offers an evidence-arrival lag (median 36.0 h, p90 63.0 h, n=12,500, none negative) usable only as a proxy (P-03). `data/lake/` and `data/documents` were not mined.

## Residual Risks

- A second data estate may define the same KPI differently (`docs/baseline-measurement-notes.md`: "business definitions are not guaranteed to agree").

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial source map. |
