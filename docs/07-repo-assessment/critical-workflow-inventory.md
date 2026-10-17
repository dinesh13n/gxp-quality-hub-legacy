---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "critical-workflow-inventory.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/05-current-state/business-workflow-map.md", "docs/05-current-state/current-process-map.md", "docs/05-current-state/control-points.md", "docs/05-current-state/integration-landscape.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/00-preflight/discovery/workflow-overview.md", "app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "docs/07-repo-assessment/baseline-behaviour.md", "docs/07-repo-assessment/evidence/analysis/coverage_trace_unittest.json", "docs/07-repo-assessment/evidence/analysis/mutation_probe.log"]
supersedes: "none"
---
## Summary

Fourteen workflows (CW-01..CW-14) whose behaviour must be preserved (or consciously changed) are inventoried. "Critical" is judged on repository evidence only: workflows that (a) decide or prioritise a case/batch, (b) ingest or transform external data, (c) produce figures used for month-end or KPI reporting, or (d) provision the data on which all baselines rest. **No stakeholder has ranked business criticality** (OD-04); the ranking below is an engineering inference and the criticality labels are therefore [Assumption] to be confirmed by Engagement lead (Dinesh Naik) at Stage 8/9. Only 1 of 14 workflows (CW-12 partly) has meaningful automated coverage; 11 have **none** that would detect a behaviour change (mutation probe), and CW-14 (batch disposition) is **absent from the code**, which must itself be preserved as a boundary (no agent may simulate it, STOP-07/HAR-12).

## Findings

| ID | Workflow | Entry point / implementation | Data touched | Behaviour baseline | Existing automated coverage (line / mutation) | Criticality (engineering inference) | RCs | Characterisation plan |
|---|---|---|---|---|---|---|---|---|
| CW-01 | Case triage / prioritisation | `app/legacy_logic.priority()`; `GET /api/cases` (`app/server.py` L45-51); `app.baseline` | `cases` | BB-01, BB-02 | `legacy_logic` 85.7 % lines; 2 asserts; mutants M1-M3 survive (only `CLOSED` branch killed) | High - drives urgency used in API and metrics | RC-4, RC-3 | CT-01, CT-02, CT-03 |
| CW-02 | Case detail with manual-review flag | `GET /api/cases/<id>` (L52-59), `manual_review_required()` | `cases`, `events` | BB-01, BB-02 | `server.py` 0 %; no test asserts the flag (M10 survives) | High - the only "needs human" signal | RC-1, RC-4 | CT-03, CT-04 |
| CW-03 | Operating metrics and baseline KPIs | `GET /api/metrics`, `python -m app.baseline` | `cases`, `operating_costs` | BB-02, BB-11 | `baseline.py` 100 % lines but `test_baseline` asserts only `records==125` and `hours_per_case>0`; M12 survives | High - source of Stage 4 proxies (generator-bounded, OD-07) | RC-8 | CT-04, CT-05 |
| CW-04 | Upstream event intake: source gateway -> bridge -> `gateway_inbox` (offsets, idempotency, invalid handling) | `services/source_gateway/server.py`; `app/gateway_bridge.py` | `batch_records` (read), `gateway_inbox`, `gateway_checkpoints` | BB-03, BB-04 | bridge 61.5 %; gateway server 0 %; M9, M15 survive | High - only live integration path | RC-5, RC-6 | CT-06, CT-07 |
| CW-05 | Partner-feed reconcile (accept / reject / duplicate) | `python -m app.partner_feeds --reconcile` (`reconcile(limit=1000)`) | `partner_feeds` (mutated in place) | BB-05 | `partner_feeds.py` 21.5 %; reconcile never run; M5-M7 survive | High - decides which external records are accepted | RC-5, RC-6, RC-7 | CT-08 |
| CW-06 | Vendor file-drop import | `python -m app.historical_estate <csv>` | `vendor_file_imports`, `vendor_file_rows` | BB-06 | 0 %; M14 survives | Medium | RC-6 | CT-09 |
| CW-07 | Night-shift reconciliation | `python -m legacy_batch.shift_reconciliation --limit N` | `enterprise_legacy.sqlite3` (read) | BB-07 | 87.5 % lines via `test_enterprise_legacy_v6` (asserts only `processed`/sum of tenant counts); M8 survives | High - third approval rule (threshold 2,500-8,500) | RC-4 | CT-10 |
| CW-08 | Month-end reconciliation (Java totals; SQL report) | `legacy_java/ReconcileLegacy.java`; `sql/legacy_reports.sql` | partner CSV exports; `cases`, `events` | BB-08 | none (no Java/SQL tests) | High - finance-facing figures; known inflation 19.3 % | RC-8 | CT-11, CT-12 |
| CW-09 | Front-end approval threshold (JS) | `legacy_js/legacy_policy.js` | `contracts/decision-policies-archive.json` | BB-09 | none; M13 survives (not exercised by any test) | High - approval limit semantics (default 999,999) | RC-4, RC-3 | CT-13 |
| CW-10 | Read-only domain / partner APIs with pagination | `/api/domain/*`, `/api/partners/*` | 9 tables | BB-02 | 0 %; M11 (pagination ignored) survives | Medium | RC-7 | CT-04 |
| CW-11 | Operational correlation report | `python -m app.operational_report` | `batch_records`, `deviations`, `gateway_inbox` | BB-10 | 92.9 % lines; asserts `>0` only | Medium | RC-7 | CT-05 |
| CW-12 | Data provisioning, regeneration and readiness verification | `app.generate`, `app.partner_feeds`, `app.enterprise_legacy`, `app.historical_fixture`, `app.archived_documents`, `app.generate_documents`, `run.sh`, `scripts/*`, `app.workshop_check` | all of `data/` | BB-12 | generators 85-100 % lines, count/FK/seed-repeat asserts (valid but destructive and order-dependent, TQ-01); `workshop_check`/`offline_inventory` 0 % under unittest | High - every other baseline depends on it | RC-7 | CT-14, CT-15 |
| CW-13 | Incident status endpoint | `GET /api/incidents` (static literal) | none | BB-02 | 0 % | Low | RC-1 (doc/behaviour mismatch) | CT-04 |
| CW-14 | **Batch disposition / case decision recording** | **No implementation** (only `docs/domain-assurance.md`, `contracts/decision-policies-archive.json` rule `batch_disposition`, `domain.json`) | none | Absence: API is GET-only (POST/PUT/DELETE -> 501); no writer of `cases` except the generator | n/a | Highest business criticality (GxP) but not code | RC-1, RC-2 | CT-16 (boundary / absence test) |

### Dependencies between workflows (execution order as run today)

[Verified Fact] Every workflow is started manually (RC-5); no scheduler exists. Data flows: CW-12 (provision) -> CW-04/05/06 (intake) -> CW-01/02/03/10/11 (read) -> CW-07/08/09 (reconciliation/threshold reporting). CW-04/05/06/12 write to the same SQLite file `data/legacy.sqlite3`; CW-07 reads `enterprise_legacy.sqlite3`; CW-08 reads CSV exports and `legacy.sqlite3`.

### Preservation notes

* Where the baseline captures a **defect** (BB-07 row multiplication, BB-08 SQL inflation, BB-09 999,999 default, BB-04 schema 0.9 accepted), Stage 14 must choose per item: *preserve for parity test* or *fix under approval*; the golden file is the reference either way.
* CW-14: Stage 15 must not introduce a code path that decides or records disposition without the human approval gate (HAR-12, STOP-07); the characterisation test CT-16 pins the current absence (write verbs -> 501; no `UPDATE`/`INSERT` to `cases` outside generators).

## Evidence References

`docs/07-repo-assessment/baseline-behaviour.md` (BB-xx); coverage `evidence/analysis/coverage_trace_unittest.json`; mutants `evidence/analysis/mutation_probe.log`; code references as in the table; Stage 5 `business-workflow-map.md`, `control-points.md` (CG-01 no decision write path).

## Assumptions

- A-07-06: Criticality ratings are engineering inferences; no business owner has ranked them. Confirm: Engagement lead (Dinesh Naik), Stage 8.
- A-07-07 (carried A-07, A-05-06): disposition and scheduling happen outside the repository.

## Unknowns

- U-07-06: Which workflows are used in the organisation's real operation (all evidence is synthetic; OD-04). Resolution: none available without real stakeholders; treat all as in scope.
- U-07-07: Whether the JS threshold is consumed by any real front end (U-19).

## Unresolved Issues

- RC-3 decision gap (which approval/closure definition governs) blocks "fix vs preserve" decisions for CW-01, CW-07, CW-09 - owner: Engagement lead (Dinesh Naik), Stage 8.

## Residual Risks

- R-07-04: Workflows interact only through the shared SQLite file; concurrent runs (API + bridge + reconcile) are not characterised.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial inventory (14 workflows). |
