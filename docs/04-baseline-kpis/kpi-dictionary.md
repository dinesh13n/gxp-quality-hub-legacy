---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "kpi-dictionary.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/success-criteria.md", "docs/03-problem-value/business-requirements.md", "docs/domain-assurance.md", "docs/baseline-measurement-notes.md", "docs/02-stakeholders/decision-rights-map.md", "docs/02-stakeholders/stakeholder-conflicts.md", "data/legacy.sqlite3 (sha256 c254649f…d70aa, read-only)", "app/baseline.py", "app/legacy_logic.py"]
supersedes: "none"
---
## Summary

Complete definitions for 22 baseline KPIs (K-01..K-22), derived from Stage 3 SUC-01..SUC-11 plus the cycle-time / effort / error / rework / quality / throughput / leakage / cost / adoption scope in the Stage 4 prompt. Every KPI has formula, unit, owner, source, period, segmentation. **Owner is "Engagement lead (Dinesh Naik)" for every KPI** because no other human exists (OD-04); this is a placeholder, not a stakeholder acceptance. Where "closed"/"resolved"/the 48 h clock matters, the KPI is split into `-OPS` (D-OPS), `-EVID` (D-EVID) and `-FIN` (D-FIN) variants and **no definition is chosen** (SC-01/DR-20 unowned).

**Freeze status: FROZEN-PROVISIONAL** (v0.1) — see `kpi-baseline-signoff.md`. All values are computed on the synthetic 125-case DB (OD-02, PROVISIONAL; Q-02-04/Q-02-05 unanswered) and are "measured on synthetic baseline data (method validation only)".

Global conventions: snapshot reference time `AS_OF = 2025-12-19T07:11:00+00:00` (max timestamp in `cases`/`events`; not wall clock); all timestamps UTC ISO-8601; percentiles by linear interpolation; D-OPS = `cases.status = 'CLOSED'`.

## Findings

### A. Definitions

| KPI | Name (Stage 3 ref) | Meaning | Formula | Unit | Owner | Source (table.column) | Period / population | Segmentation | Definition class |
|---|---|---|---|---|---|---|---|---|---|
| K-01 | Unsafe action count (SUC-01) | Automated/simulated disposition, or closure without evidence and without authorised exception | count(unsafe events in window) | count | Engagement lead (Dinesh Naik) | **None exists** — no action/audit log with actor + disposition in `legacy.sqlite3` | Evaluation window of the intervention | site, actor type | Invariant (=0 required) |
| K-02 | Source attribution rate (SUC-02) | Share of sampled decisions carrying an evidence reference and a source | decisions with evidence_ref AND source / decisions sampled | % | same | `events.payload` of `STATUS_REVIEWED` (keys observed: `reviewer`,`severity`) | all STATUS_REVIEWED events | site, severity | Structural proxy only |
| K-03 | Definition transparency (SUC-03) | Share of reported figures that declare which closed/resolved definition they use | figures with definition tag / figures reported | % | same | outputs of `app/baseline.py` (6 keys) | current reporting code | report | Verified by inspection |
| K-04-OPS | Time to close, D-OPS (SUC-04) | Elapsed receipt→ops-closed | median and p90 of (closed_at − created_at) over cases with status CLOSED | hours | same | needs closure timestamp — **absent** | cohort by created month | site, severity, segment | D-OPS |
| K-04-EVID | Time to close, D-EVID (SUC-04) | Elapsed receipt→closed AND evidence+authorised approver recorded | median/p90 of (max(closed_at, evidence_at, approver_at) − created_at) | hours | same | needs evidence/approver fields — **absent** | same | same | D-EVID |
| K-04-FIN | Time to resolved, D-FIN | Elapsed receipt→"successfully resolved for cost" | **Undefined** (D-FIN is an Unknown) | hours | same | none | n/a | n/a | D-FIN |
| K-05 | Time to evidence (SUC-05) | Receipt→evidence-complete | median hours (evidence_complete_at − created_at) | hours | same | needs evidence timestamp — **absent**; proxies P-01, P-02 | same | same | D-EVID |
| K-06 | Unmatched reference rate (SUC-06) | External items whose reference matches no core case | count(ref_id NOT IN cases.id)/count(rows) | % | same | `partner_feeds.ref_id`, `policy_exceptions.ref_id` vs `cases.id` | all rows | processing_status, partner | Definition-independent |
| K-07 | Replay safety (SUC-07) | Change in queue size and totals when an already-processed item is re-delivered | queue_after − queue_before, totals_after − totals_before after replay of n processed items | count / value delta | same | Behavioural test, not a column | replay test run (sandbox) | feed kind | Invariant (=0 required) |
| K-08 | Reconciliation delay (SUC-08) | Hours from source event to record available | ingest_ts − source_ts; median, p90, % ≤ 4 h | hours, % | same | `partner_feeds.source_ts`,`ingest_ts` | all rows | processing_status, partner | Definition-independent |
| K-09-OPS | Backlog ageing & count, D-OPS (SUC-09) | Not-closed cases and their age at AS_OF | count(status<>CLOSED); median/p90 of (AS_OF − created_at) | count; days | same | `cases.status`,`created_at` | snapshot at AS_OF | site (required by BR-12), severity | D-OPS |
| K-09-EVID | Backlog, D-EVID | Cases not both closed and evidence-complete | count(cases) − count(closed AND evidence AND approver) | count | same | evidence fields **absent** | snapshot | site | D-EVID |
| K-09-FIN | Backlog, D-FIN | Undefined | — | — | same | none | — | — | D-FIN |
| K-09U | Unresolved exception rate (SUC-09) | Share of policy exceptions not resolved. Variant UE-1: outcome<>'WAIVED'; UE-2: outcome IN ('OPEN','REVIEW') | count/ count(policy_exceptions) | % | same | `policy_exceptions.outcome` | all rows | policy_code, actor | Provisional (meaning of WAIVED/BLOCKED unowned) |
| K-10 | Month-end comparability (SUC-10) | Ops month counts vs finance/cost month counts on one cut-off | months where cases created in month = operating_costs.total_cases / months compared; plus total difference | months; cases | same | `cases.created_at` vs `operating_costs.total_cases` | 2023-01..2025-12 (36) | month | Definition-dependent (cut-off unowned) |
| K-11 | Decision recorded (SUC-11) | Definition/closure-time decision has owner+date or "accepted open" record | count(DR-20, DR-21 with decision record)/2 | count of 2 | same | `docs/02-stakeholders/decision-rights-map.md` | engagement | — | Governance |
| K-12 | Handling effort per case | Labour hours per case | sum(labor_hours)/sum(total_cases) (same as `app/baseline.py` `hours_per_case`) | hours/case | same | `operating_costs` | 2023-01..2025-12 | month | Denominator = ops table, not cases table |
| K-13 | Infrastructure cost per case | Infra spend per case | sum(infrastructure_usd)/sum(total_cases) | USD/case | same | `operating_costs` | same | month | Cost proxy; D-FIN-dependent |
| K-14 | Throughput | Cases created per month | count(cases)/months with data | cases/month | same | `cases.created_at` | 2023-01..2025-12 | year, site | Definition-independent |
| K-15 | Rework (reopen) rate | Share of cases in REOPENED | count(status='REOPENED')/count(cases) | % | same | `cases.status` | snapshot | site, severity | Snapshot proxy (no history) |
| K-16 | Manual-review share (by code rule) | Share of cases the legacy rule flags for manual review | count(manual_review_required)/count | % | same | `app/legacy_logic.py` `manual_review_required` over `cases` | snapshot | site | Rule-derived |
| K-17 | Deviations closed without root cause | Integrity of closure | count(CLOSED and root_cause IS NULL)/count(CLOSED) in `deviations` | % | same | `deviations` | all (42) | classification | Quality |
| K-18 | CAPA overdue share | OVERDUE share of not-yet-verified CAPA | OVERDUE/(OVERDUE+OPEN) | % | same | `capa_actions.state` | all (21) | action_owner | Quality |
| K-19 | Batch-run rejection / failure | Rejected records over input; FAILED runs over runs | sum(rejected)/sum(input); count(FAILED)/count(runs) | % | same | `batch_runs` | 60 runs, 2021-01..2024 | partner, result | Error |
| K-20 | Upstream outage MTTR and open outages | Median resolve time; outages with no resolve time | median(resolved−began); count(resolved IS NULL) | hours; count | same | `upstream_outages` | 72 incidents, 2021-01-01..2024-04-22 | system_name | Reliability |
| K-21 | Adoption | Share of cases handled via the new capability | cases via new path/cases | % | same | none before intervention | Stage 34 | site | Not measurable pre-intervention (defined for Stage 34) |
| K-22 | Rework effort | Hours spent on avoidable rework | Σ rework hours (needs time record) | hours | same | none | — | — | Unknown (no rework time capture) |

### B. Definition-quality findings

- [Verified Fact] Every KPI with a state dependency has an explicit `-OPS/-EVID/-FIN` split; none picks a winner (`docs/03-problem-value/success-criteria.md` candidate-definition table).
- [Verified Fact] The only KPI code that exists, `app/baseline.py`, defines `open_cases` as `status != 'CLOSED'` (= D-OPS) and `hours_per_case` as `sum(labor_hours)/sum(total_cases)` from `operating_costs`, i.e. a denominator (108) that differs from the case count (125). Both are untagged (K-03).
- [Inference] Time-based KPIs (K-04, K-05) are **not computable** from the DB because `events` holds only `CASE_CREATED` and `STATUS_REVIEWED`; there is no closure/evidence/approver event. Hence "current value" is Unknown and proxies are defined in `proxy-metrics.md`.
- [Assumption] A-04-01: `operating_costs.total_cases` is intended to mean cases created in the period (confirm: Engagement lead (Dinesh Naik), Stage 5).
- [Assumption] A-04-02: threshold 4 h in K-08 is the archived target in `docs/operations-service-levels.md`, used as a reporting cut only, not a target.

## Evidence References

`docs/03-problem-value/success-criteria.md`; `docs/03-problem-value/business-requirements.md` (BR-01..BR-13); `app/baseline.py` L1-13; `app/legacy_logic.py`; DB schema read via `file:data/legacy.sqlite3?mode=ro&immutable=1` (see `baseline-evidence.md` E-02).

## Assumptions

A-04-01, A-04-02 above; A-03-12/13 carried (thresholds are placeholders; no targets set here).

## Unknowns

U-04-01 who owns each KPI in a real organisation; U-04-02 meaning of D-FIN; U-04-03 meaning of WAIVED/BLOCKED outcome for K-09U; U-04-04 whether a real source of closure/evidence timestamps exists (QMS/LIMS) — Stage 5.

## Unresolved Issues

- Q-02-04 (baseline dataset) and Q-02-05 (definitions) unanswered by Dinesh; definitions frozen provisionally. If Dinesh picks a single definition, K-04/K-09 `-OPS/-EVID` rows stay but one is designated primary through a versioned change record (v0.2).

## Residual Risks

- A KPI set with 22 owners-of-one has no independent challenge (ER-11). Several KPIs (K-01, K-04, K-05, K-07, K-22) are definitions only, with no measurable baseline.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial dictionary; frozen provisional. |
