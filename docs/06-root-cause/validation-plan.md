---
stage: "6 — Root-Cause Analysis"
artifact: "validation-plan.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/causal-hypotheses.md", "docs/06-root-cause/evidence-confidence-matrix.md", ".fde/orchestrator-decisions.md (OD-03a, OD-04, OD-07)", "docs/00-preflight/operating-contract/", "app/*", "sql/legacy_reports.sql", "data/legacy.sqlite3 (read-only, immutable)"]
supersedes: "none"
---
## Summary

How each hypothesis is (or would be) validated, what was executed in this stage, and what remains. Two classes of validation: **V-repo** (executable now with read-only inspection of the repository; done in Stage 6) and **V-field** (requires stakeholders or telemetry; unavailable under OD-04). Methods obey OD-03/OD-03a: only read-only SQLite (`mode=ro&immutable=1`), static reading and grep were used; **no application code was executed**; the backup manifest check (`sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt`) returned OK after the queries. Any later method that runs application code must use a full sandbox copy (`$HOME/fde_sbx/<name>/`).

## Findings

### VP-A. Validation register

| ID | Hyp | Method | Pass criterion | Falsifier | Executed? | Result | Class |
|---|---|---|---|---|---|---|---|
| V-01 | H-01 | Exhaustive grep over `.py .js .java .sql .sh` for writes to `cases`/status/decision; inspect GET-only API; read `domain-assurance.md` L4 | No write path for decision/closure/disposition anywhere | Any code that records an actor+decision | Yes | Only `INSERT INTO cases` at `app/generate.py:37`; no UPDATE; PASS | [Verified Fact] |
| V-02 | H-02 | SQL: `min/max(version)`; `CASE_CREATED.payload.status = cases.status` count; event type histogram; grep for version increments | version constant; creation payload equals current status; no reopen/close events; no increment code | Any version >1, any transition event type | Yes | version 1/1 (125 rows); status copy 125/125; types CASE_CREATED 125, STATUS_REVIEWED 20; PASS | [Verified Fact] |
| V-03 | H-03, H-04 | Triangulate 4 repo sources: correspondence, business-context L19, decision-rights DR-20/21/23, status-vocabulary count in code; look for any decision record in `docs/decisions/` | Conflict documented AND no decision record AND vocabularies diverge | A policy record that defines and owns the terms | Yes | No record found; PASS (documentary only) | [Verified Fact] (docs) |
| V-04 | H-05 | Read three rule sources; importer grep for `legacy_logic`; check shipped data for the amount branch | Three copies, no shared import | A shared module used by all | Yes | Confirmed; side finding: 0 of 125 cases > 50,000 so the amount branch of `priority()` never fires on shipped data | [Verified Fact] |
| V-05 | H-06 | Grep scheduler tokens (crontab, apscheduler, celery, schedule(, systemd, cron:, schedule:); read `reconcile(limit=1000)`; SQL backlog count; check `batch_runs` insert in reconcile | No scheduler; cap present; backlog 8,567 | Scheduler config or run logging | Yes | None found; cap L60-63; NEW 8,000 + RETRY 500 + REPLAY 67; PASS | [Verified Fact] |
| V-06 | H-07 | Read `partner_feeds.py` L60-71, `gateway_bridge.py` L13-34, `integration.py`, Java catch | Overwrite, drop, content-blind replay, no contract enforcement | Content comparison, quarantine, history table | Yes | PASS | [Verified Fact] |
| V-07 | H-08 | Schema inspection (`app/store.py` L19, domain DDL); SQL orphan count | No linking column/FK between cases and batch/deviation/feed | Link column or FK | Yes | PASS for schema; orphan rate not admissible as behaviour (R-05) | [Verified Fact] |
| V-08 | H-09 | Re-execute the join from `sql/legacy_reports.sql` read-only and compare with a direct SUM; read Java parse loop | SUM(join) != SUM(base) | Equal sums | Yes | 742,956.61 (145 rows) vs 622,826.44 (125) = +19.3%; Java silent skip present; PASS | [Verified Fact] |
| V-09 | H-10 | Stakeholder walk-through: where closure evidence lives and how it is referenced | A named evidence location per case type | Evidence demonstrably in a linked store | **No** (no stakeholder) | - | [Unknown] |
| V-10 | H-11 | Structured interview about manual reconciliation (who, how often, written procedure) | Procedure known to <=1 person / unwritten | Written, shared procedure | **No** | - | [Unknown] |
| V-11 | H-12 | Obtain headcount/roster/workload by role | Demand exceeds capacity in measured period | Spare capacity | **No** | - | [Unknown] |
| V-12 | H-13 | Real monthly case counts / feed volumes (>=12 periods) | Positive trend correlating with effort | Flat or negative | **No** | - | [Unknown] |
| V-13 | H-14 | In a sandbox copy (`$HOME/fde_sbx/<name>/`, OD-03a): concurrent reconcile + API writes, observe lock errors | Lock errors/timeouts under realistic concurrency | None observed | **No** (code execution; deferred to a later stage) | - | [Inference] |
| V-14 | H-15 | Pattern scan for instruction-like strings (done Stage 0A IO-15, Stage 5 CG-08) | Strings present in decision-adjacent fields | None present | Prior stages | 86 feed rows etc.; PASS (presence) | [Verified Fact] |
| V-15 | H-16 | Read `app/server.py` for auth; read `access_audit` shape | No authN/Z | Auth middleware | Yes (static) | PASS (presence) | [Verified Fact] |

### VP-B. Counter-hypothesis checks run (disconfirmation attempts)

| Attempt | Outcome |
|---|---|
| Search for any other writer to `cases`/`events` (e.g. in Java, JS, SQL, shell) to disconfirm H-01/H-02 | None; only generator |
| Search for a scheduler in Compose, CI workflow, scripts to disconfirm H-06 | None (`restart: "no"` for bridge per Stage 5 IL-01) |
| Check whether SQL join inflation is an artefact of `count(DISTINCT)` use | Report counts DISTINCT cases correctly but still sums an un-deduplicated amount; inflation real on this dataset |
| Check whether stage-4 proxies (P-01, P-03, P-04, K-10) can serve as evidence | No; generator-bounded (R-02..R-04, OD-07) |

### VP-C. Field validation needed (cannot be done by this engagement)

| Need | Unblocks | Owner | Resolving stage |
|---|---|---|---|
| Decision on RC-3 terms (closed/resolved/approved, 48 h clock, evidence sufficiency) or explicit "accepted open" | H-03/H-04 real-world status; Stage 8 option design | Engagement lead (Dinesh Naik) | before Stage 8 |
| Statement of where the decision-of-record and closure evidence live (or ruling that they are out of scope) | H-01 org-level, H-10 | Engagement lead (Dinesh Naik) | before Stage 8 |
| Real status-change timestamps / volume series | S1, H-12, H-13, K-04/K-05 | Engagement lead (Dinesh Naik); instrumentation in a later build stage | Stage 34 re-baseline |
| Sandbox contention test (V-13) | H-14 | Engagement lead (Dinesh Naik) | Stage 7 or later |

## Evidence References

Commands run read-only against the working tree: grep patterns listed above; Python `sqlite3` with `file:data/legacy.sqlite3?mode=ro&immutable=1`; `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` (OK). Operating contract constraints: `docs/00-preflight/operating-contract/`, OD-03a.

## Assumptions

- A-06-08: Static reading of code is an acceptable validation method for "this mechanism exists"; it is not validation of runtime behaviour. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-14 Runtime behaviour of the reconcile and bridge paths under real data (not executed).

## Unresolved Issues

- V-09..V-13 cannot be executed; no due date can be committed because no stakeholder exists (OD-04). Owner and resolving stage stated above; Dinesh to assign dates.

## Residual Risks

- Validation by reading code can miss behaviour set by environment/config outside the repo (e.g. external schedulers).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial validation plan with V-repo executed. |
