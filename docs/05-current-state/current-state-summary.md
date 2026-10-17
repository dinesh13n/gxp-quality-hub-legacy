---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "current-state-summary.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/05-current-state/current-process-map.md", "docs/05-current-state/business-workflow-map.md", "docs/05-current-state/system-landscape.md", "docs/05-current-state/integration-landscape.md", "docs/05-current-state/brownfield-inventory.md", "docs/05-current-state/manual-handoffs.md", "docs/05-current-state/process-bottlenecks.md", "docs/05-current-state/control-points.md", "docs/05-current-state/dependency-hotspots.md", "docs/04-baseline-kpis/kpi-baseline-signoff.md", "docs/04-baseline-kpis/proxy-metrics.md", "docs/04-baseline-kpis/kpi-dictionary.md", "docs/04-baseline-kpis/measurement-methodology.md", "app/generate.py", "app/enterprise_legacy.py", "services/source_gateway/server.py", "data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)", "data/lake/bundled (read-only)", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Current state in one paragraph.** The "process" is a five-step documented workflow (external messages → integration → operations review → local decision → monthly measures) whose steps 1, 2, 3 and 5 are represented by ~850 lines of Python/Java/JavaScript/SQL running against local SQLite files, started by hand, with no scheduler, no authentication, no audit trail and no write path for decisions. Step 4 - the human decision, including the GxP-significant `batch_disposition` - and the people who perform steps 3-4 are invisible in the repository (only documentation and a policy-archive JSON mention them). Three implementations of the approval/priority rule disagree. All quantitative "process" data is produced by generators, so wait times and counts describe the generator, not an organisation. Stage 5 therefore delivers a **code-and-data-level map plus an explicit list of what only stakeholders can supply**.

**Stage gate: CONDITIONAL PASS** (see CS-F). Stage 4's carried items A-04-01, A-04-03, A-04-05 and the closure/evidence timestamp question are investigated in CS-B..CS-D.

## Findings

### CS-A. Key current-state findings (ranked)

| # | Finding | Where detailed | Confidence | Class |
|---|---|---|---|---|
| 1 | Decision recording and batch disposition have no implementation; human approval gate is only documented | `current-process-map.md` P-A; `control-points.md` CG-01 | High | [Verified Fact] (absence by grep/schema) |
| 2 | No audit trail: status is a snapshot, `version` never changes, creation event copies the current status, no reopen/close events | `control-points.md` CG-02 | High | [Verified Fact] |
| 3 | Three divergent approval/priority rules; policy archive roles change 2025 but are unused at runtime | `business-workflow-map.md` D-03/05/06/07, BW-B | High | [Verified Fact] |
| 4 | Every batch is human-started; reconcile capped at 1,000 rows/run vs 8,567 backlog; failures drop or overwrite evidence silently | `integration-landscape.md`; `process-bottlenecks.md` BN-01 | High | [Verified Fact] |
| 5 | Wait-time proxies from Stage 4 are generator-bounded, not evidence of delay; real flow times are unmeasurable | `process-bottlenecks.md` PB-A | High | [Verified Fact] |
| 6 | No cross-record consistency: contradictory closure states across cases/batches/deviations/CAPA/lab results are permitted | `control-points.md` CG-04 | Medium (synthetic) | [Verified Fact] |
| 7 | `cases` is unlinked to batch/deviation/CAPA records; `partner_feeds` references mostly non-existent cases (8,394 of 8,567) | `business-workflow-map.md` BW-C | High | [Verified Fact] |
| 8 | Documentation conflicts with behaviour: runbook "does not mutate", `/api/incidents` hard-coded, INC-2025-014's "queue retried twice" has no counterpart | `current-process-map.md` P-D; `integration-landscape.md` IN-03 | High | [Verified Fact] |

### CS-B. Stage 4 open items - disposition

| Item | Stage 4 statement | Stage 5 repo investigation | Disposition | Class |
|---|---|---|---|---|
| **A-04-01** | `operating_costs.total_cases` = cases created in the period | `app/generate.py` (last loop): `n = max(1, count//36 + randrange(-min(count//100,50), +…))` for each of 36 months; `labor_hours = n × U(0.35,0.90)`; `infrastructure_usd = 70 + 0.07 n`. For 125 cases `count//36 = 3`, ±1 → n ∈ {2,3,4} (observed min 2, max 4, sum 108; labor/case 0.353-0.878; infra residual 0). **`n` is drawn independently of the `cases` rows**; no code or doc links the two. No document defines the column. | **Assumption NOT supported by evidence; refuted as a derivation** ("created in period" cannot be derived because totals are independent draws). Intended business meaning remains **Unknown**. Consequence: K-10 (125 vs 108) and cost-per-case (K-12/K-13) compare two unrelated populations; carry as a defect of the dataset, not a finding about the business. | [Verified Fact] (generator logic); intent [Unknown] |
| **A-04-03** | AS_OF = dataset max timestamp 2025-12-19T07:11Z is an acceptable snapshot | No code or doc defines a snapshot/"as of" time; `baseline.py` has no time dimension; the generator's latest possible case date is 2023-01-01 + 1,100 days = 2026-01-05, so 2025-12-19 is simply the largest random draw (max of `events.recorded_at` and `source_messages.received_at`). Wall-clock "now" (2026-10-17) would add ~10 months to every open-case age. | **Remains an Assumption**, now with evidence that the value is an artefact, not a process-defined cut. Acceptable only for reproducibility; any age/overdue KPI (K-09, BN-06) must be labelled "age at generator horizon". Owner to confirm: Engagement lead (Dinesh Naik). | [Verified Fact] (artefact); acceptance [Assumption] |
| **A-04-05** | `STATUS_REVIEWED`/`reviewer:"operations"` is an operations-side review | The string is a literal in `app/generate.py` (`json.dumps({'reviewer':'operations','severity':severity})`); generated with probability 0.17 per case; only one reviewer value exists; **no code in the repo writes `STATUS_REVIEWED`** other than the generator; no reviewer identity, role model or login. `docs/business-context.md` step 3 ("Operations users review and prioritize work") is the only corroboration. | **Remains an Assumption (label-level only).** It is consistent with documented step 3 but not evidence of a performed review by a named role. Do not use P-01 as a measure of operations response time. | [Verified Fact] (origin); meaning [Assumption] |

### CS-C. Is there any real source of closure / evidence timestamps? (Stage 4 question for Stage 5)

**Answer: No. No store in the repository holds a real closure, approval, verification or evidence-completion timestamp.** Search covered every table and file below.

| Store | What looks like a timestamp | Why it is not a closure/evidence time | Evidence |
|---|---|---|---|
| `cases` | `created_at` only | No `closed_at`/`updated_at`; `status` snapshot; `version`=1 for all | `app/store.py` DDL; SQL |
| `events` | `CASE_CREATED` (125), `STATUS_REVIEWED` (20) | No close/reopen/approve type; `CASE_CREATED.payload.status` = current status for 125/125 (copy) | SQL; `app/generate.py` |
| `source_messages` | `received_at` (15) | Source's claimed `status`, no approver; timestamps = event time of generator | SQL; P-02 |
| `operating_costs` | `period` | Monthly totals independent of cases (A-04-01) | generator |
| `deviations`, `capa_actions`, `lab_results`, `batch_records` | `opened_at`, `due_at`, `measured_at`, none for close/verify | No `closed_at`, `verified_at`, `completed_at` | SQL schema |
| `sop_versions` | `effective_at`/`retired_at` | Document lifecycle, all dated 2023-01-01..13 | SQL |
| `partner_feeds` | `source_ts`, `ingest_ts` | Arrival, not closure; 26% have `source_ts > ingest_ts` by design (offsets −1440…+10080 min) | `app/partner_feeds.py` L33 |
| `upstream_outages` | `began`, `resolved` | Infrastructure outage, not case closure; 8 unresolved | SQL |
| Gateway events | `occurred_at`, `published_at` | Formula (`2025-03-…` by offset), including a `qa_disposition` type with no consumer | `services/source_gateway/server.py` |
| `data/enterprise_legacy.sqlite3` `state_history` | `at_utc` | **12,500 rows = one per object, `from_state='OPEN'`, `to_state` = current status, `at_utc` = creation time**; not a transition history (0 distinct transitions per object) | SQL; `app/enterprise_legacy.py` L40 |
| same: `evidence_events` | `event_time`, `arrival_time` | `arrival = t + ((i*3) % 72) h`; deterministic | `app/enterprise_legacy.py` L43 |
| same: `workflow_tasks` | `due_at` | = creation + 14 days for every task; no completion time | L47 |
| same: `access_audit` | `recorded_at` | only `read` actions (generator index bug), no `approve` | L50 |
| `data/lake/*` events, ledger, docs | `event_time`, `posted_date`, `date` | `outcome` states ACTIVE/PENDING/FAILED/REVERSED/ESCALATED/REOPENED (no CLOSED), 92 impossible dates; documents `status` draft/approved with no time | JSONL parse |
| Files `data/archive_documents/*`, `operations/incidents/INC-2025-014.md` | email Date headers; incident times 03:15/04:00 UTC | Only **one** human-authored time pair exists: INC-2025-014 (2025-11-18 03:15 → 04:00 UTC manual reconciliation), a single anecdote | files |

**Consequence:** K-04 (time to close), K-05 (time to evidence) and the Stage 34 post-intervention comparison cannot be measured from this repository. Earliest sources: (1) stakeholder-provided system extracts with status-change timestamps (none promised: OD-04), (2) new event capture built in a later build stage. Until then Stage 4's proxies stay explicitly "PROXY, generator-bounded" (`process-bottlenecks.md` PB-A).

### CS-D. Documented vs observed - consolidated

| # | Documented | Observed | Where |
|---|---|---|---|
| 1 | Five-step workflow, step 4 "decisions recorded in local systems" | Step 4 absent from code | P-A |
| 2 | "API process does not mutate core records" (runbook) | True for cases; DDL on partner routes and at startup | DO-01 |
| 3 | `/api/incidents` suggests incident tracking | Single hard-coded `INC-2019-0082` | DO-02 |
| 4 | Header: priority logic "used by both API and month-end reports" | Used only by `app/server.py` and `app/baseline.py` | BW D-03 |
| 5 | Policy archive gives approval roles per year | Not enforced anywhere; JS defaults to 999,999 | D-05/D-07 |
| 6 | INC-2025-014: "queue retried twice" | No queue or retry code exists | IN-03 |
| 7 | `okstatus: released` in `domain.json` | No such value in any data | DO-03 |
| 8 | Partner replays are "operationally common" | All replays → DUPLICATE regardless of content | IN-01 |
| 9 | Business measure "batch quality cases reviewed" | Not computed | WF-09 |
| 10 | History notes name "Pharma" service with approvals since 2018 | Current service has no approval function | SD-02 |

### CS-E. Where stakeholder evidence is needed (all with OD-04: none available)

Decision step and approver (U-05-02), closure definition (BN-03), manual reconciliation practice (A-05-08), real timing/volume data (U-05-03, U-05-18), real-world control environment (U-05-20). Without them Stage 6 can analyse structure and control gaps, not causes of delay.

### CS-F. Completion Gate evaluation (honest)

| Gate condition | Status | Basis |
|---|---|---|
| End-to-end process and system landscape mapped with evidence | **Met, with limit** | Steps 1,2,3,5 mapped to code; step 4 explicitly marked Unknown. Landscape in `system-landscape.md`, `integration-landscape.md`, `brownfield-inventory.md`. |
| Bottlenecks, control gaps, dependency hotspots identified | **Met** | 11 bottlenecks, 12 control gaps, 10 hotspots, each with evidence/impact/risk/confidence |
| Documented vs observed differences recorded | **Met** | CS-D (10 items) plus per-artifact tables |
| All required artifacts exist | **Met** | 10 of 10 under `docs/05-current-state/` with the required header and section skeleton |
| Critical gaps resolved or explicitly documented | **Met (documented)** | Unknowns U-05-01..U-05-23 with owner |
| Evidence supports the conclusion | **Met for code/data-level conclusion; not for real-world process conclusions** | Process behaviour in practice is [Unknown] |

**Gate = CONDITIONAL PASS.** No blocking condition: the missing human-process evidence is a known, accepted constraint (OD-04) and does not prevent root-cause analysis of structure. Non-blocking gaps (owner for all: Engagement lead (Dinesh Naik); target = before the Stage 6 gate, no calendar date set - Dinesh to assign):

| Gap | Risk if left open | Resolving stage |
|---|---|---|
| Decision step / disposition owner and tool unknown | Stage 6 treats the core step as a black box; interventions may bypass a real gate | 6 (ruling or stakeholder evidence), 8 |
| Real timing/volume unavailable | Bottleneck ranking based on structure only | 6, 34 (instrumentation) |
| A-04-01 / A-04-03 / A-04-05 remain Assumption or refuted | K-10, K-12/13, K-09, P-01 must carry caveats | 6 (confirm), 4 addendum if Dinesh wants KPI sheet amended |
| Authoritative approval rule undecided | Later design cannot pick a rule | 6/7 |
| Closure/"resolved"/48 h definitions unowned | KPI K-04/K-05 undefined | 6, 8 |

## Evidence References

All nine sibling artifacts in `docs/05-current-state/`; `app/generate.py`; `app/enterprise_legacy.py` L36-51; `services/source_gateway/server.py`; `docs/04-baseline-kpis/*`; read-only SQL (`mode=ro&immutable=1`) on `data/legacy.sqlite3` and `data/enterprise_legacy.sqlite3`; Python parse of `data/lake/bundled`. No application code was executed in this stage; backup checksum verification `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` returned OK after the queries.

## Assumptions

A-05-01..A-05-12 as listed in the sibling artifacts. Plus A-04-01 (not supported), A-04-03 and A-04-05 (open, see CS-B). Owner for all: Engagement lead (Dinesh Naik).

## Unknowns

U-05-01..U-05-23 across sibling artifacts; the most consequential: U-05-02 (where disposition is recorded), U-05-03/U-05-18 (real timings), U-05-05 (authoritative rule).

## Unresolved Issues

- Stage 4 KPI sheet still cites A-04-01 as "cases created in month" and K-10 as a business signal; it should be annotated by Dinesh or a Stage 4 addendum (Stage 5 is read-only and did not edit it).
- Proxies P-01/P-03/P-04 need a "generator-bounded" caveat wherever they are quoted.

## Residual Risks

- Process conclusions may be mistaken for observed organisational behaviour; every claim here is code/data-level on synthetic input.
- Self-approval (one human) persists; Stage 5 findings are not independently reviewed.
- Feeds forward: Stage 6 (root-cause on structural causes: BN-01..BN-11, CG-01..CG-12), Stage 7 (hotspots DH-01..DH-10; characterisation tests for duplicated rules), Stage 14 (manual handoffs MH-01..MH-13 as automation/removal candidates, subject to the unknown external gate).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
