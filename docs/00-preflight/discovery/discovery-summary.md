---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "discovery-summary.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/00-preflight/discovery/*.md", "git status --porcelain", "sha256sum -c (pre-inspection checksums)", "isolated-copy execution logs"]
supersedes: "none"
---
## Summary

**Stage 0A gate: CONDITIONAL PASS.**

`gxp-quality-hub-legacy` is a small, self-described **synthetic legacy training simulator** for Pharma batch quality review, deviation and CAPA processing (Python 3 stdlib + SQLite; optional Java and Node consumers). It has a read-only JSON API (:8080), a simulated upstream source gateway (:8090), an ingestion bridge, partner-feed staging/reconciliation, a CSV file-drop import, a night-shift batch over a separate enterprise DB, and month-end reconciliation scripts. There are no AI/LLM calls, no authentication, no telemetry and no deployment evidence beyond Docker/Compose/CI descriptors. Git history has only 2 commits (both 2026-10-17), so activity and ownership cannot be inferred from VCS.

The single most important discovery: **the shipped primary database is not the documented baseline**. `data/legacy.sqlite3` holds 125 cases (README promises 6,000) — the residue of the repo's own test suite, which writes to the real DB because `app/store.py` resolves `LEGACY_DB` at import time. This was reproduced in an isolated copy (6,000 → 125 cases after one `unittest` run). Every documented preflight (`PRELOADED_DATA.md`, `DATA_READINESS.md`, `scripts/verify.sh`, CI) runs those tests.

## Findings

### One-page orientation

| Dimension | Orientation (details in artifact) |
|---|---|
| Topology | Single repo, 548 tracked files (421 archive docs); ~45 logic/config files; data DBs git-ignored → `repository-overview.md` |
| Technology | Python ≥3.10 stdlib only (Docker/CI 3.12), SQLite, Java 17+ (1 class), Node 18+ (1 script), SQL (1 file, unreferenced); no deps, no lock files → `technology-inventory.md` |
| Architecture | Shared-SQLite integration hub; GET-only `http.server` API; second HTTP simulator; one-shot bridge; CLIs/batches → `high-level-architecture.md` |
| Integrations | Offset-pull HTTP (gateway→bridge), in-place partner staging, CSV file-drop, raw `source_messages`; third parties only as data values → `integration-overview.md` |
| Data | 6 SQLite DBs + JSON/JSONL/CSV/EML/HTML corpora; deliberate quality defects; synthetic PII indicators; ≥286 embedded instruction-like strings → `data-flow-overview.md` |
| Workflows | Intake, feed reconciliation, triage/priority, monthly measures exist; **batch disposition (human approval) not implemented**; 3 divergent threshold rules → `workflow-overview.md` |
| Tests | 15 unittest tests green; characterisation-only; destructive to default DB → `test-overview.md` |
| Security / observability | No authn/z/TLS; no secrets; stderr access log only; gateway logs disabled; no metrics/tracing/alerts → `security-observability-overview.md` |
| Operational status | No evidence any component is in production; Compose not executed; CI never evidenced as run [Unknown] |

### Top findings (classified)

1. [Verified Fact] Shipped `legacy.sqlite3` = 125 cases / 125 batches (test fixture), with 8,394 orphan `partner_feeds` refs and 222 orphan `policy_exceptions` — `data-flow-overview.md` DF-01/DF-03, `integration-overview.md` IO-10.
2. [Verified Fact, reproduced] Test suite overwrites the real DB (import-time `LEGACY_DB` resolution) — `test-overview.md` TO-03.
3. [Verified Fact] Approval/priority logic implemented three times with different thresholds; GxP `batch_disposition` gate only in docs/policy data — `workflow-overview.md` WF-05/WF-06.
4. [Verified Fact] No authentication/authorisation/audit mechanism; tenant and `access_level` fields unenforced — `security-observability-overview.md` SO-01/02/09.
5. [Verified Fact] Untrusted instruction-like content embedded throughout feeds/documents/events (treated strictly as data in this stage) — DF-08.
6. [Verified Fact] Zero AI/model calls today (input to Stage 0C: current model-call workload = 0; data volumes: 6,000-case documented tier, 50k/100k bundled lake, 1,200 + 420 + 960 documents).

### Areas requiring deeper assessment in Stage 7

| # | Area | Why | Source finding |
|---|---|---|---|
| S7-01 | Test isolation & behaviour baseline (characterisation of API, reconcile, bridge, batch outputs on an agreed dataset) | Tests destructive and thin | TO-01, TO-03, TO-07 |
| S7-02 | Decision-rule divergence (Python / JS / policy_register / policy archive roles & effective dates) | Inconsistent outcomes | WF-06 |
| S7-03 | Shared-DB coupling, import-time config, DDL on GET, dynamic SQL table names | Change-safety | HA-02–HA-04 |
| S7-04 | Ingestion semantics: dropped events, no retry, in-place status mutation, replay handling, schema versions | Reliability / auditability | IO-01–IO-03, IO-12 |
| S7-05 | Night-shift join row multiplication (500 rows → 118 objects) and Java/SQL float & cut-off behaviour | Reconciliation correctness | WF-07, WF-08 |
| S7-06 | Compose runtime behaviour (DB copy divergence, fresh-clone empty DB) | Runtime correctness | HA-05, HA-06 |
| S7-07 | Data-quality rule inventory (units, nulls, negative values, invalid dates, overlapping validity, multilingual text) | KPI and reconciliation definitions | DF-05, DF-09 |
| S7-08 | Security & audit-trail gaps vs Part 11 concepts; untrusted-content handling | Compliance framing / safety | SO-*, DF-08 |
| S7-09 | Observability baseline (logs, health depth, SLO measurability) | Operability | SO-12–SO-17 |
| S7-10 | Runtime currency and build reproducibility (Python 3.10 EOL, unpinned image/CI, Java/Node build) | Supportability | TI-01, TI-04, TI-07 |

### Completion Gate self-check

| Gate condition | Met? | Evidence |
|---|---|---|
| Orientation sufficient to conduct engagement qualification (Stage 1) | Yes | 12 artifacts cover all 8 analysis dimensions; system purpose, workflows, stakeholders-by-role, risks and data volumes established |
| No transformation recommendation made | Yes | Risk register lists containment/investigation actions only; no technology/AI/architecture recommendations |
| Every material statement classified and cited | Yes | Findings tables carry class tags and path/line or command evidence |
| No file outside `docs/00-preflight/discovery/` changed | Yes | `git status --porcelain` shows only `?? docs/00-preflight/`; SHA-256 of all 6 git-ignored SQLite DBs unchanged (`sha256sum -c` OK); no `__pycache__`/`.class` created in repo; all execution done in a disposable copy outside the repo |
| All required artifacts exist at the paths | Yes | 12 files in `docs/00-preflight/discovery/` |
| Critical gaps resolved or explicitly documented | **Documented, not resolved** | Baseline dataset identity (A-02/U-13), original snapshot (U-14), all stakeholder confirmations — owner Engagement lead (Dinesh Naik) |
| Evidence supports the stage conclusion | Yes | Reproduction run + read-only queries |

**Gate decision: CONDITIONAL PASS.** No blocking gap for Stage 0B. Non-blocking gaps with owner and due point:

| Condition | Owner | Due | Risk if unmet |
|---|---|---|---|
| C-1 Decide which dataset is the authoritative "before" baseline (shipped 125-case DB vs documented 6,000-case seed 4326) — A-02/U-13 | Engagement lead (Dinesh Naik) | Before Stage 4 starts (decide by Stage 1) | Invalid before/after KPI comparison (R-03) |
| C-2 Locate original archive / snapshot `data/` with checksums outside the working tree — U-14 | Engagement lead (Dinesh Naik) | Before any command that runs tests (Stage 0B boundary) | Irrecoverable baseline loss (R-01, R-02) |
| C-3 Stage 0B to codify "never run tests/preflights against the working-tree `data/`" | Engagement lead (Dinesh Naik) | Stage 0B | R-01 |
| C-4 Stakeholder confirmations for all assumptions A-01…A-08 | Engagement lead (Dinesh Naik) | Per resolving stage in `assumptions-unknowns.md` | Mis-framed qualification |

## Evidence References

- Artifacts: `repository-overview.md`, `system-landscape.md`, `technology-inventory.md`, `high-level-architecture.md`, `integration-overview.md`, `data-flow-overview.md`, `workflow-overview.md`, `test-overview.md`, `security-observability-overview.md`, `assumptions-unknowns.md`, `initial-risk-register.md` (this folder).
- Pre-inspection checksums: `legacy.sqlite3` c254649f57e2…d70aa; `enterprise_legacy.sqlite3` 210f4bafd858…4c0b (re-verified unchanged at end of stage).
- Execution evidence (disposable copy outside repo): `unittest` 15/15 OK; `smoke.py` pass; `offline_inventory.py` ready; `app.baseline` (shipped DB) records 125 / open 89 / urgent 2 / hours_per_case 0.603; (regenerated 6,000, seed 4326) records 6000 / open 4251 / urgent 159 / mean_amount 4403.0 / hours_per_case 0.601.

## Assumptions

A-01 … A-08 — see `assumptions-unknowns.md`.

## Unknowns

U-01 … U-24 — see `assumptions-unknowns.md`; U-13 is blocking for Stage 4 only.

## Unresolved Issues

- Conditions C-1 … C-4 above.
- No real stakeholders, approvals or business metrics are available; none have been invented.

## Residual Risks

R-01 … R-15 — see `initial-risk-register.md`.

**Recommended next action:** proceed to Stage 0B (Provisional Operating Contract & Engineering Boundaries), carrying conditions C-2 and C-3 as inputs.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
