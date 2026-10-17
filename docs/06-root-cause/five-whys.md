---
stage: "6 — Root-Cause Analysis"
artifact: "five-whys.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/root-cause-tree.md", "docs/06-root-cause/evidence-confidence-matrix.md", "docs/05-current-state/*", "docs/03-problem-value/problem-framing-canvas.md", "docs/correspondence/operations-vs-risk-2024.md", "app/partner_feeds.py", "app/gateway_bridge.py", "app/store.py", "sql/legacy_reports.sql", "legacy_java/ReconcileLegacy.java"]
supersedes: "none"
---
## Summary

Seven 5-Whys chains, one per symptom S2-S7 plus S1 (which terminates early in Unknown). Each "why" is tagged and cites evidence. A chain stops where the next "why" would require information outside the repository; it is **not padded to five levels** when the evidence does not exist. Chains show where a "why" is a documented claim (synthetic) rather than an observed fact.

## Findings

### FW-1. S3 "Closed" means different things at different sites

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why do sites mean different things by "closed"? | Each domain table and tool has its own status vocabulary and nothing reconciles them | [Verified Fact] | `cases` 5 states; `batch_records` REVIEW/QA_HOLD/CLOSED; `deviations` OPEN/INVESTIGATION/CLOSED; `capa_actions` OPEN/OVERDUE/VERIFIED |
| 2 | Why is there no reconciled vocabulary? | No definition of "closed/resolved/approved" is owned or recorded in the shared policy repository | [Verified Fact] (claim in synthetic doc) | `operations-vs-risk-2024.md`: "never formalized in the shared policy repository" |
| 3 | Why is it unowned? | Operations (48 h), Compliance (verifiable evidence) and Finance (no definition) each hold a different requirement and no decision right exists | [Verified Fact] (documented) | DR-20, DR-21 GAP in `decision-rights-map.md` |
| 4 | Why has nobody decided? | **Unknown**: repo shows "both requests remain active" (2024) but no escalation record, no owner | [Unknown] | `historic-decisions.md` 2024; `escalation-map.md` |
| 5 | (stops) | Further why needs a real governance study | [Unknown] | U-06-09 |

Root reached: **RC-3**. Parallel chain via the record model: closing decision not captured in system -> no write path -> **RC-1**.

### FW-2. S5 Finance and operations monthly figures disagree

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why do monthly totals disagree? | Three independent computations (Java, SQL, API) | [Verified Fact] | `ReconcileLegacy.java`, `sql/legacy_reports.sql`, `/api/metrics` |
| 2 | Why would independent computations differ? | Java: `double` sum and `catch(NumberFormatException ignored)` skips blank rows; SQL: `LEFT JOIN events` multiplies amounts of cases with 2 events (read-only re-execution: SUM 742,956.61 over 145 joined rows vs 622,826.44 over 125 cases, +19.3%); API counts rows | [Verified Fact] | re-executed SQL; Java L12; bundled CSV 200 blank of 50,000 |
| 3 | Why was each built separately? | No shared definition of the measure, period or cut-off; reports were added over time ("untuned monthly legacy reporting" comment) | [Inference] | `legacy-operations-history.md`; SQL file comment |
| 4 | Why is there no shared definition? | Finance has no agreed definition of "resolved"; ops/finance cut-offs differ | [Verified Fact] (documented claim) | `legacy-operations-history.md`; DR-20 |
| 5 | Why is that unresolved? | Same ownerless decision as FW-1 | [Unknown] | RC-3 |

Roots: **RC-8** (mechanisms), **RC-3** (definition). Note: Stage 4 K-10 is **not** used as evidence (OD-07; populations unrelated).

### FW-3. S4 Replay inflated exception queue; delayed feed forced manual reconciliation

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why did a replay inflate the queue (2025)? | Replays are a normal part of partner delivery and every replay is handled as a row to process; documented rollback | [Verified Fact] (claim) | `historic-decisions.md` 2025; `docs/partner-feed-operations.md` |
| 2 | Why is a replay costly? | The reconcile rule labels every REPLAY a DUPLICATE without content comparison, status overwritten in place; no history of what the original said | [Verified Fact] | `app/partner_feeds.py` L65-67 |
| 3 | Why does a delayed feed require manual work? | Reconcile runs only when a person starts it, at most 1,000 rows per run; no scheduler or run log | [Verified Fact] | `reconcile(limit=1000)`; grep for schedulers: none |
| 4 | Why were these designs accepted? | **Unknown**: no ADR for intake semantics; 2022 decision to reconcile manually has "original change ticket not archived" | [Unknown] | `historic-decisions.md` 2022 |
| 5 | (stops) | Cannot be answered from repository | [Unknown] | U-06-10 |

Roots: **RC-6**, **RC-5**. Caveat: INC-2025-014's "queue retried twice" has no counterpart in this repo (R-08); the chain explains the *class* of event, not that incident.

### FW-4. S2 Feed rows inconsistent with core records

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why do feed rows not match cases? | `partner_feeds.ref_id` has no key relationship to `cases.id` | [Verified Fact] | schema; SQL: 8,394 of 8,567 orphans |
| 2 | Why no relationship? | `cases` carries no batch/deviation/feed identifier; the estate has parallel identifier families (C..., BT..., deviation ids) | [Verified Fact] | `app/store.py` L19; `legacy-operations-history.md` (support asks by either id) |
| 3 | Why parallel identifier families? | Systems were added in layers (2018 spreadsheets, 2020 ingestion, ...) with no canonical key decision | [Inference] | history notes |
| 4 | (stops) | Whether a canonical key was ever intended: Unknown | [Unknown] | U-05-06 |

Root: **RC-7**. The 98% orphan figure is a generator/test residue (R-05); only the missing relationship is a finding.

### FW-5. S6 Decisions/closures cannot be attributed or reconstructed

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why can't we say who closed a case and when? | No closure/approval event or actor exists in any store | [Verified Fact] | CS-C table; `events` types = 2 |
| 2 | Why? | `cases.status` is overwritten; `version` stays 1; `CASE_CREATED.payload.status` is a copy of the current status (125/125) | [Verified Fact] | SQL re-run |
| 3 | Why is state a snapshot? | The data model was designed as a read-model of a case list; the API is GET-only and nothing in the repo writes decisions | [Inference] (design intent) / [Verified Fact] (GET-only, grep) | `app/server.py`; grep |
| 4 | Why is the decision outside the system? | **Unknown**: doc says decisions are recorded in "local systems" (step 4); no further detail | [Unknown] | `business-context.md`; U-05-02 |

Roots: **RC-1**, **RC-2**.

### FW-6. S7 Contradictory closure states possible

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Why can a batch be CLOSED with a failed lab result? | No constraint ties batch status to lab/deviation/CAPA state | [Verified Fact] (absence); counts are generator-assigned | schema; CG-04 SQL |
| 2 | Why no constraint? | Tables share no authoritative lifecycle definition and only loose FKs | [Verified Fact] | `app/store.py`; domain DDL |
| 3 | Why no lifecycle definition? | Closure rules unowned (FW-1) | [Inference] | DR-20 |

Roots: **RC-7**, **RC-3**, **RC-2** (no history to detect divergence).

### FW-7. S1 Rising exception-handling effort

| # | Why? | Answer | Tag | Evidence |
|---|---|---|---|---|
| 1 | Is effort rising? | **Unknown** - no trend data; `operating_costs` is random by construction | [Unknown] / REJECTED evidence R-01 | `app/generate.py`; OD-07 |
| 2 | If it is, why? | Candidates: duplicated manual reconciliation (RC-5/RC-6/RC-8) [Inference]; volume growth, capacity, tribal knowledge [Unknown] | - | tree |

Chain terminates at level 1: the symptom itself is unverified, so no root cause can be claimed for it. Stage 3 assumption A-03-04 remains open.

## Evidence References

Per row. Plus read-only re-execution of `sql/legacy_reports.sql` join and SQL counts on `data/legacy.sqlite3` (`mode=ro&immutable=1`).

## Assumptions

- A-06-06: Documented claims about past events (2022, 2024, 2025) are accepted as claims, not facts. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-09 Why no owner exists. U-06-10 Why intake semantics were chosen. U-06-11 Whether S1 is real.

## Unresolved Issues

- Four chains end in [Unknown] at level 4; the "human why" is outside the repository.

## Residual Risks

- Chains read as complete explanations; they are explanations of the *system as shipped*.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial 5-Whys. |
