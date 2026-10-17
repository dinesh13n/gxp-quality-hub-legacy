---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "current-process-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/legacy-operations-history.md", "docs/historic-decisions.md", "docs/correspondence/operations-vs-risk-2024.md", "operations/runbook.md", "operations/incidents/INC-2025-014.md", "app/server.py", "app/legacy_logic.py", "app/generate.py", "app/gateway_bridge.py", "app/partner_feeds.py", "app/historical_estate.py", "legacy_batch/shift_reconciliation.py", "docs/03-problem-value/user-journeys.md", "docs/00-preflight/discovery/workflow-overview.md", "data/legacy.sqlite3 (read-only)"]
supersedes: "none"
---
## Summary

End-to-end current process, reconstructed only from evidence. **Documented process** = the 5-step workflow in `docs/business-context.md` ("Existing workflow"). **Observed process** = what code, schema and data actually support. Result: steps 1, 2, 3 and 5 are visible in code as automated or read-only mechanisms; **step 4 (decision recording) and the human actors performing steps 3-4 are not observable anywhere in the repository** [Verified Fact, absence by grep and schema inspection]. No interviews, shadowing, tickets, SOPs or production logs exist (OD-04). Actors below are therefore *documented roles*, not observed people. Nothing in this file names a person or invents an owner.

## Findings

### P-A. Documented vs observed process (step-level)

| Step | Documented (source) | Observed in repo | Gap | Class |
|---|---|---|---|---|
| 1 External sources produce case messages | `docs/business-context.md` step 1 | Simulated: `services/source_gateway/server.py` synthesises events from `batch_records`; `source_messages` and `partner_feeds` are generator output (`app/generate.py`, `app/partner_feeds.py`) | No real upstream; the process start is synthetic | [Verified Fact] |
| 2 Integration reconciles/imports | step 2; `docs/legacy-operations-history.md` ("replays ... operationally common", "several reconciliations remain manual") | Four mechanisms: gateway pull (`app/gateway_bridge.py`), partner-feed reconcile (`app/partner_feeds.py` `reconcile()`), CSV file drop (`app/historical_estate.py`), source-message adapter (`app/integration.py`). Reconcile classifies rows by 4 rules and overwrites `processing_status` in place | Manual reconciliation (2022 decision, INC-2025-014) has no tooling or record in repo | [Verified Fact] (code) / [Unknown] (manual practice) |
| 3 Operations review and prioritise | step 3 | `priority()` and `manual_review_required()` in `app/legacy_logic.py`, exposed read-only by `GET /api/cases`, `/api/cases/<id>` (`app/server.py`). On the shipped DB: 2 open cases `urgent`, 17 `review`, 25 open cases flagged manual-review | The *human* review is not recorded by any code; the only trace is 20 synthetic `STATUS_REVIEWED` events whose writer is the generator (`app/generate.py`, literal `'reviewer':'operations'`) | [Verified Fact] |
| 4 Case decisions recorded in "local systems" | step 4; `contracts/decision-policies-archive.json` rule `batch_disposition` (approval role `operations_lead` in 2022 versions) | **No code path writes a decision.** API is GET-only; no CLI mutates `cases.status`; `batch_disposition` appears only in docs and policy JSON | The core GxP decision and its approval gate are outside the repository | [Verified Fact] (absence) |
| 5 Monthly operating measures reviewed | step 5 | `GET /api/metrics`, `python -m app.baseline`, `sql/legacy_reports.sql`, `legacy_java/ReconcileLegacy.java` | Business measure "batch quality cases reviewed" (`domain.json`) not computed by any code; finance/ops cut-offs differ per `legacy-operations-history.md` | [Verified Fact] |

### P-B. Reconstructed end-to-end flow (swim-lane, evidence-tagged)

```
Lane: External sources (simulated)   MES/LIMS/QMS events -----> gateway :8090 /api/events      [Verified Fact]
                                     partner feeds (5 partners) -> partner_feeds rows (NEW/RETRY/REPLAY)   [Verified Fact]
                                     vendor CSV -----------------> vendor_file_rows            [Verified Fact]
Lane: Integration (batch/CLI)        gateway_bridge pull -> gateway_inbox (drop unknown business_key)  [Verified Fact]
                                     partner_feeds --reconcile -> ACCEPTED/REJECTED/DUPLICATE (overwrite)  [Verified Fact]
                                     [manual spreadsheet reconciliation when totals diverge]  [documented only: INC-2025-014]
Lane: Core store                     legacy.sqlite3 (cases, events, domain tables, feeds)       [Verified Fact]
Lane: Legacy API (read-only)         /api/cases + priority(), /api/metrics, /api/domain/*, /api/partners/*  [Verified Fact]
Lane: Operations users (documented)  review & prioritise ............ (no system trace)         [Unknown]
Lane: Authorised human (documented)  batch_disposition decision ..... (no system trace)         [Unknown]
Lane: Local systems (documented)     decision recorded ............... (not in repo)           [Unknown]
Lane: Monthly measures               /api/metrics, baseline.py, SQL, Java, night-shift job       [Verified Fact]
Lane: Finance / Risk (documented)    cut-off disputes; evidence requirement                     [Verified Fact] that docs say so
```

### P-C. Actors (documented roles only)

| Actor | Source | Evidence of activity in repo | Class |
|---|---|---|---|
| Quality operations lead | `docs/business-context.md` stakeholders | none beyond documentation | [Unknown] activity |
| Enterprise application owner | same | none | [Unknown] |
| Finance partner | same; `operations-vs-risk-2024.md` | none | [Unknown] |
| Risk and security partner | same | none | [Unknown] |
| Integration lead | same | none; INC-2025-014 says follow-up owner unknown | [Unknown] |
| Team labels `MANUFACTURING/QC/QA/REGULATORY/SUPPLY` | `operational_objects.owner_team`, `workflow_tasks.queue` in `data/enterprise_legacy.sqlite3` | Generator-assigned (`app/enterprise_legacy.py` `DOMAIN['teams'][i%5]`) | [Verified Fact] synthetic |
| Exception actors `system/operator/manager/qa` | `policy_exceptions.actor` (62/62/52/48 rows) | Generator-assigned | [Verified Fact] synthetic |

### P-D. Process facts that conflict with documentation

| ID | Documented claim | Observed | Class |
|---|---|---|---|
| DO-01 | `operations/runbook.md`: "API process does not mutate core records" | True for case data (GET-only), but `GET /api/partners/<table>` calls `partner_feeds.init()` (`app/server.py`; `app/partner_feeds.py` L11-19), executing `CREATE TABLE/INDEX IF NOT EXISTS`, and startup calls `setup()` (DDL). Schema-writing side effects on read paths. | [Verified Fact] |
| DO-02 | `/api/incidents` implies incident tracking | Returns one hard-coded incident `INC-2019-0082` built from `domain.json` `legacy_incident`; the real documented incident is INC-2025-014 (markdown only) | [Verified Fact] |
| DO-03 | `domain.json` `okstatus: released` | No data value `released` in any store | [Verified Fact] |
| DO-04 | Five-step workflow is linear | Replays/duplicates/outages create loops (REPLAY rows, RETRY, rollbacks in `historic-decisions.md` 2025) that the doc does not show | [Inference] |

## Evidence References

`docs/business-context.md` L19-27; `app/server.py`; `app/legacy_logic.py`; `app/generate.py` (events loop); `app/partner_feeds.py` L11-71; `docs/00-preflight/discovery/workflow-overview.md` WF-01..WF-11; read-only SQL on `data/legacy.sqlite3` (priority counts: open & urgent 2, open & review 17, open & manual-review 25 of 89 non-closed).

## Assumptions

- A-05-01: The documented 5-step workflow is the intended process; its human steps happen outside the repository (extends 0A A-07). Confirm: Engagement lead (Dinesh Naik) — resolving stage: 6/8 (needs stakeholder evidence or an explicit "no stakeholders" ruling).
- A-05-02: Roles listed in `docs/business-context.md` are the only recognised actors; no org chart exists. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-01 Who performs steps 3-4, with what tools and in what order. U-05-02 Where `batch_disposition` is recorded and by whom (carries 0A U-17). U-05-03 Volume, frequency and duration of each step. U-05-04 Whether manual reconciliation is still the 2026 practice (carries 0A U-11). Resolution route for all: stakeholder interview or explicit engagement-lead ruling (OD-04); until then analysis stays at code/data level.

## Unresolved Issues

- Process cannot be traced end-to-end because the decision step is outside the repo; Stage 6 root-cause work must treat step 4 as a black box.

## Residual Risks

- Risk of treating `business-context.md` as the real process (the prompt forbids this). Mitigation: every row above tags documented vs observed.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
