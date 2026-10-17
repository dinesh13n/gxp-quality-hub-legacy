---
stage: "6 — Root-Cause Analysis"
artifact: "evidence-confidence-matrix.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/causal-hypotheses.md", "app/store.py", "app/generate.py", "app/legacy_logic.py", "app/server.py", "app/partner_feeds.py", "app/gateway_bridge.py", "app/enterprise_legacy.py", "legacy_js/legacy_policy.js", "legacy_java/ReconcileLegacy.java", "sql/legacy_reports.sql", "contracts/decision-policies-archive.json", "docs/domain-assurance.md", "docs/02-stakeholders/decision-rights-map.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/05-current-state/*", "data/legacy.sqlite3 (read-only, immutable)"]
supersedes: "none"
---
## Summary

For each live hypothesis: supporting evidence, **contradictory evidence considered**, confidence, validation method and validation status. Confidence rule used: **High** = directly observed in code/schema/SQL and reproducible; **Medium** = observed but resting on a synthetic document or a generator-shaped number; **Low** = inference or single anecdote. Confidence here concerns *the existence of the structural condition*; none of it speaks to business size (no telemetry; OD-04). Evidence ceiling for every row: repository + synthetic data.

## Findings

### EM-A. Matrix

| Hyp | Supporting evidence | Contradictory / limiting evidence considered | Confidence | Validation method | Status |
|---|---|---|---|---|---|
| H-01 No decision write path | Grep of all `.py/.js/.java/.sql/.sh`: the only `INSERT INTO cases` is `app/generate.py:37`; no `UPDATE cases`; API is GET-only (`app/server.py`); `docs/domain-assurance.md` L4 requires a human gate; `docs/business-context.md` step 4 says "recorded in local systems"; DR-22 holder GAP | The decision may be made and recorded in an external "local system" outside the repo (that is exactly what the doc says) - so absence in this repo is not absence in the organisation. Policy archive lists approver roles (data exists) | High (absence in repo) / Unknown (in org) | V-01 exhaustive grep + schema inspection | PASSED (repo-level) |
| H-02 Mutable snapshot, no history | `cases.version` min=max=1 over 125 rows and no code increments it (grep); `events` has only `CASE_CREATED` 125 and `STATUS_REVIEWED` 20; `CASE_CREATED.payload.status` equals current `cases.status` for 125/125; 8 REOPENED cases, 0 reopen events | Enterprise DB `state_history` exists, but is 1 row per object with `to_state` = current status (not a transition log); a real client system outside the repo may keep history | High | V-02 SQL + grep | PASSED |
| H-03 No owned definition of closed/resolved/approved | `operations-vs-risk-2024.md` ("Finance has not agreed what counts as a successfully resolved case... never formalized"); DR-20, DR-23 = GAP; five status vocabularies in code (`cases`, `batch_records.qa_status`, `deviations.status`, `capa_actions.state`, enterprise); `business-context.md` L19 | The document is synthetic and from 2024; U-03-03: conflict may be resolved since. No second source independent of the synthetic corpus. Dinesh is the only human and could simply decide (A-03-16) | Medium | V-03 document triangulation (4 repo sources) + code vocabulary count | PASSED (documentary); real-world status Unknown |
| H-04 No decider for speed vs evidence | DR-21 GAP ("both requests remain active", `historic-decisions.md` 2024); no decision record in `docs/decisions/` resolving it (`open-governance-decisions.md`) | Same synthetic-source limit; a decider may exist in the real client | Medium | V-03 | PASSED (documentary) |
| H-05 Three rule copies | `app/legacy_logic.py` `priority()` (amount>50,000; severity/status); `legacy_js/legacy_policy.js` (regional limit x1.05, default 999,999); `legacy_batch/shift_reconciliation.py` (threshold 2,500-8,500 after region LEFT JOIN); importers of `legacy_logic` only `app/server.py`, `app/baseline.py`, test; header comment claims month-end use | The three rules answer slightly different questions (priority vs within-limit vs follow-up flag), so "disagreement" is partly a naming issue; no authoritative rule declared (U-05-05). Baseline data: 0 of 125 cases exceed 50,000 so the amount branch never fires in the shipped DB | High (code) | V-04 code reading + importer grep; BW-B cell values are [Inference] (not executed) | PASSED for existence of 3 copies; outcome divergence on real input Inference |
| H-06 Manual, capped, unscheduled, no run record | Grep for cron/schedule/celery/systemd tokens outside `data/`: none; `reconcile(limit=1000)` at `app/partner_feeds.py` L60-63 with `LIMIT ?`; shipped backlog NEW 8,000 + RETRY 500 + REPLAY 67 = 8,567 (SQL re-run) -> 9 runs; `reconcile()` has no INSERT into `batch_runs` | The client may schedule these jobs externally (A-05-06). The backlog size is a generator parameter (default 8,500 feeds), not an observed operational backlog. Limit is a default argument and could be raised by the operator | High (mechanism) / Low (delay impact) | V-05 grep + code + SQL | PASSED (mechanism) |
| H-07 Destructive, content-blind intake | `partner_feeds.py` L65-67: REPLAY -> DUPLICATE without content comparison; status overwritten in place; `gateway_bridge.py` L17-23: invalid events counted, not persisted; `gateway_checkpoints` 0 rows; `integration/source-contract-v1.json` not enforced by `app/integration.py`; Java `catch(NumberFormatException ignored)` | The documented 2025 replay incident is consistent but cannot be tied to this code (R-08); frequency of corrected replays Unknown | High (mechanism) / Low (frequency) | V-06 code reading | PASSED (mechanism) |
| H-08 No shared identity / referential model | `cases` DDL (`app/store.py` L19) has no batch/deviation/CAPA column; `partner_feeds.ref_id` no FK; contradictory states present in data (CG-04: 25 of 33 CLOSED batches carry OOS/PENDING/INVALID lab result; 10 CLOSED deviations on non-closed batches) | The CG-04 counts are random generator assignments (cannot be read as client behaviour); orphan rate 8,394/8,567 re-confirmed but is generator/test residue (R-05). What is verified is **absence of constraints**, not that users produced the contradictions | High (schema) / Low (behaviour) | V-07 schema inspection + SQL | PASSED (schema) |
| H-09 Independent month-end computations | `sql/legacy_reports.sql`: `LEFT JOIN events ... sum(c.amount)`; **re-executed read-only: 145 joined rows, SUM 742,956.61 vs true 622,826.44 over 125 cases (+19.3%)**; Java `Double.parseDouble` with silent catch; API counts | Reproducing inflation proves a method defect on this dataset; size depends on events-per-case (20 of 125 have 2 events, generator). K-10 (8 of 36 months agree) is unusable (R-04). Whether finance actually uses the SQL report is Unknown | High (mechanism: join inflation) / Low (organisational impact) | V-08 read-only SQL reproduction + code reading | PASSED (mechanism) |
| H-10 Closure evidence not linked to case | `cases` has no evidence reference; `document_links` only in enterprise DB (one per object); 30 of 36 CLOSED cases have no `STATUS_REVIEWED` event | Evidence may live in external ECM (U-05-20); enterprise DB does link documents to objects, so some link model exists in the estate | Low-Medium | V-09 stakeholder walk-through (not available) | NOT PASSABLE (repo-only) -> SUPPORTED |
| H-11 Tribal knowledge | 2022 decision and 2025 note each one sentence; no owner, no procedure (MH-02, DH-10) | Brevity of a note is not evidence of dependence on one person | Low | V-10 interview | UNTESTED |
| H-12 Capacity shortfall | None in repo (no headcount, no roster) | None to weigh; absence of data | Low | V-11 staffing data | UNTESTED |
| H-13 Volume growth | None valid (R-01, R-10 rejected) | `operating_costs` random by construction | Low | V-12 real volume series | UNTESTED |
| H-14 SQLite contention | `busy_timeout=15000`, `timeout=15` in `app/store.py`; DDL on read routes | No lock failure observed anywhere; single-user synthetic setting | Low | V-13 load test in sandbox (later stage) | UNTESTED |
| H-15 Untrusted text in data | Instruction-like strings in 86 feed rows, notes, lake events (0A IO-15; CG-08) | No AI component reads these fields today, so no present harm; treated as data in this engagement | High (presence) | V-14 pattern scan (done in Stage 0A/5) | PASSED (presence); not a symptom cause |
| H-16 No authN/Z | `app/server.py` has no auth; `access_audit` 4,167 rows all `read` (but generator bug R-09) | The synthetic estate is local-only; production may sit behind a gateway | High (presence) | V-15 code reading | PASSED (presence); not a symptom cause |

### EM-B. Confidence summary

| Band | Hypotheses |
|---|---|
| High (structural, code/schema/SQL) | H-01, H-02, H-05, H-06 (mechanism), H-07 (mechanism), H-08 (schema), H-09 (mechanism) |
| Medium (rests on synthetic document) | H-03, H-04 |
| Low-Medium / Low | H-10, H-11, H-12, H-13, H-14 |
| Presence-only (latent risk) | H-15, H-16 |

### EM-C. Correlation-vs-causation checks applied

| Pair observed together | Why not treated as causal |
|---|---|
| 83% of CLOSED cases lack a review event (CG-03) -> "premature closure" | Review events are generated with p=0.17 independent of status; shows absence of a *rule*, not a behaviour |
| 71% of cases not CLOSED -> "backlog caused by slow review" | Status drawn independently of date and of events (PB-00c); stock is a weight, not a flow |
| 25/33 CLOSED batches with bad lab result -> "closure bypasses QA" | Random assignment in generator; supports H-08 (constraint absent) only |
| Replay incident (2025) and content-blind REPLAY rule | Temporal/thematic coincidence; the incident's mechanism cannot be mapped to this code (R-08) |
| K-10 monthly totals differ -> "reports disagree because of method" | Populations unrelated (OD-07); method defect (H-09) shown by direct SQL reproduction, not by K-10 |

## Evidence References

All paths in `evidence_sources`. New read-only reproductions in this stage: SQL join inflation (145 rows / 742,956.61 vs 125 / 622,826.44); `cases.version` 1/1; `CASE_CREATED` status copy 125/125; `partner_feeds` orphans 8,394/8,567; `processing_status` NEW 8,000, RETRY 500, REPLAY 67; 0 of 125 cases above 50,000. Queries via `file:data/legacy.sqlite3?mode=ro&immutable=1`; backup checksum verification returned OK afterwards. No application code executed.

## Assumptions

- A-06-03: Confidence reflects existence of a condition in the shipped repo, not prevalence in a real organisation. Confirm: Engagement lead (Dinesh Naik).
- A-06-04: Generator-shaped numbers (orphan rate, CG-04 counts, 83% no-review) are admissible only as proof that constraints are absent. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-04 Whether finance or ops consume `legacy_reports.sql` output. U-06-05 Whether history/audit exists in an external system of record. U-06-06 Real prevalence of every symptom.

## Unresolved Issues

- No row can reach "confirmed in the organisation" without stakeholder evidence; that limitation is structural to this engagement.

## Residual Risks

- Over-reading High confidence as business significance; mitigated by the Confidence definition above and the scope statement in `confirmed-root-causes.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial matrix. |
