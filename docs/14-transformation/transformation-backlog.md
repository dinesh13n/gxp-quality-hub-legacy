---
stage: "14 — Transformation / Migration Plan"
artifact: "transformation-backlog.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/repo-transformation-readiness.md (R-1..R-12, heat map)", "docs/07-repo-assessment/characterization-test-plan.md (CT-H1..H7, CT-01..CT-18)", "docs/07-repo-assessment/critical-workflow-inventory.md (CW-01..CW-14)", "docs/10-architecture/component-model.md (C1..C11)", "docs/10-architecture/architecture-decision-summary.md (ADR-001..018, all PROPOSED)", "docs/12-specs/spec-readiness.md (RD-3 OD-S12-01..19, RD-4)", "docs/12-specs/features/f10-coexistence-change-safety.md (DV-01..09, G1..G10, BEH-CO-01..09)", "docs/13-traceability/traceability-summary.md (C1..C5)", "docs/13-traceability/evidence/tests_plan.csv, rtm.csv", "docs/14-transformation/evidence/increment-test-map.csv", "docs/00-preflight/operating-contract/ (HAR-01..16, WB-01..11, STOP-01..12)", ".fde/orchestrator-decisions.md (OD-03a, OD-07..OD-10)", "pyproject.toml", "app/, tests/ (listing only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: a plan, not an approval. Nothing in this stage changes code or data; execution is Stage 15 (HAR-11: only Engagement lead (Dinesh Naik) approves).**

The transformation is **not** a rewrite of the legacy estate. Per ADR-001/ADR-003 (PROPOSED) a No-AI modular monolith (`hub/`, own `hub.sqlite3`) is built **beside** the untouched legacy code; legacy sources stay byte-identical through R1 (BEH-CO-03, AC-CO-05). The backlog therefore has three kinds of item: (1) **safety prerequisites** that make change observable (harness, hermetic fixtures, guards), (2) **net-new capability modules** C1..C11 built in shadow, and (3) **cutover items** that need explicit preserve-vs-fix decisions (DV-01..09) and belong to Stage 30, not Stage 15. 23 backlog items (TB-01..TB-23) are grouped into **9 Stage-15 increments (INC-01..INC-09)** plus 5 cutover steps (CUT-1..CUT-5). All 241 Stage 13 planned tests are assigned to an increment by script (`evidence/increment-test-map.csv`).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### TB-0 Derivation (target-vs-current gaps)
| Gap | Current state (evidence) | Target (evidence) | Tag |
|---|---|---|---|
| G-A No executable regression net | Goldens exist only as JSON captures (`docs/07-repo-assessment/evidence/golden/{api,batch,lib}_golden_run1.json`); shipped suite kills 1/15 mutants (TD-02, TQ-05); tests overwrite the default DB (TQ-01, WB-F2) | Executable CT-01..CT-16 + mutation gate (CT-H1..H7) | [Verified Fact] |
| G-B Repo-relative writers | ≥5 modules write `data/` paths regardless of `LEGACY_DB` (WB-F1; OD-03a) | Every run in a full copy outside the repo; harness sandbox guard (BEH-CO-04) | [Verified Fact] |
| G-C No decision record / audit trail | CW-14 "no implementation"; all routes reject writes with 501 (CT-16) | C2 audit chain + C3 append-only decision events (ADR-004/005) | [Verified Fact] |
| G-D Rules scattered, inconsistent | Python `app/legacy_logic.py`, JS `legacy_js/legacy_policy.js`, SQL `sql/`, Java `legacy_java/` (CW-01, CW-08, CW-09) | One rule service with versioned as-found sets (C4, ADR-007) | [Verified Fact] |
| G-E Destructive intake | `app/partner_feeds.reconcile` overwrites `processing_status` in place (DV-07); invalid gateway events dropped (DV-09) | Append-only intake + quarantine (C6, ADR-008) | [Verified Fact] |
| G-F Wrong-but-pinned figures | SQL month-end 742,956.61 vs 622,826.44 (DV-01); night-shift fan-out (DV-08) | Definition-tagged metrics, no fan-out (C9, ADR-011) | [Verified Fact] |
| G-G No identity links | no crosswalk table (RC-7) | C7 explicit crosswalk | [Verified Fact] |
| G-H No authn/authz, no human gate | no auth in `app/server.py`; disposition absent | C2 RBAC, C5 Zone H gate default blocked (ADR-006/013) | [Verified Fact] |

### TB-1 Backlog
Size: S ≤ ~1 day of review, M ≤ ~3, L > 3 (relative reviewability, [Assumption] no calendar exists). Test IDs: Stage 13 `tests_plan.csv`; counts from `evidence/increment-test-map-summary.txt`.

| ID | Item | Kind | Component / ADR | Behaviour change to legacy? | Increment | Size | Decisions it depends on | Tag |
|---|---|---|---|---|---|---|---|---|
| TB-01 | Hermetic fixture FX-BASE125: copy `data/legacy.sqlite3` (sha256 c254649f…d70aa, OD-09) into a temp full-repo copy per test class, hash-verified (CT-H1) | prerequisite | C11 / ADR-003 | None | INC-01 | M | none (OD-09 decided) | [Inference] |
| TB-02 | Subprocess-per-scenario runner: each CT scenario runs the **unmodified** legacy code in a child process whose cwd is the sandbox copy, so import-time `app.store` binding (WB-F2) and repo-relative writers (WB-F1) only touch the copy | prerequisite | C11 | None | INC-01 | M | harness approach HD-1 (recommended: subprocess, no legacy refactor) | [Inference] |
| TB-03 | Port the Stage 7 capture scripts (`evidence/scripts/capture_{api,batch,lib}.py`) into `tests/characterization/` with normalisation CT-H3, reviewed golden update CT-H4, goldens copied from `docs/07-repo-assessment/evidence/golden/` | prerequisite | C11 | None | INC-01 | M | none | [Inference] |
| TB-04 | Executable CT-01..CT-16 (P1/P2) + CT-H6 mutation gate M1..M15 (`mutation_probe.sh`) in sandbox | prerequisite | C11 | None | INC-01 | M | none | [Inference] |
| TB-05 | AC links for CT-04..CT-16 (Stage 13 condition C3) recorded as test metadata `ac_links` | prerequisite | — | None | INC-01 | S | none | [Verified Fact] C3 requires it before first legacy change |
| TB-06 | `hub/` package skeleton, runtime self-check (floor Python 3.10 / SQLite 3.37, BEH-CO-09), sandbox guard E-CO-NOT-SANDBOX (BEH-CO-04) | foundation | C11, ADR-018 | None | INC-02 | S | OD-S12-12 (default floor 3.10) | [Inference] |
| TB-07 | No-AI structural guard: import/dependency deny-list + egress test (BEH-CO-07, G5) | foundation | ADR-002 (OD-08 approved) | None | INC-02 | S | none | [Verified Fact] OD-08 |
| TB-08 | Read-only legacy adapters (`mode=ro`), deviation register (DV-01..09 `proposed`), `hub golden-compare` (BEH-CO-01..03) | foundation | C11, ADR-003 | None | INC-02 | M | none to build; OD-S12-13 to approve any DV | [Inference] |
| TB-09 | `hub.sqlite3` forward-only migration runner + schema v1 (DDL from `docs/12-specs/contracts/ddl`), backup-before-migrate | foundation | ADR-004 | None (new file) | INC-03 | M | OD-S12-09 (default hold-all) | [Inference] |
| TB-10 | C2 Access & Audit: users/roles (offline `hub user`), audit hash chain, `verify-audit`, anchor file via config | module | C2, ADR-005/013 | None | INC-03 | M | OD-S12-18 (default config path), OD-S12-06 only for holders | [Inference] |
| TB-11 | Backup/restore rehearsal tooling (BEH-CO-06, G7) | foundation | ADR-015 | None | INC-03 | S | none | [Inference] |
| TB-12 | C4 Policy & Rule service: as-found rule sets (Python/JS/SQL thresholds) imported read-only; no active set; DV-06 `defaulted` marker | module | C4, ADR-007 | None (legacy files untouched) | INC-04 | M | OD-S12-04 (default: no active set) | [Inference] |
| TB-13 | C3 Decision Record: append-only events, projection, as-of, closure check (both closure modes) | module | C3, ADR-004 | None | INC-05 | L | OD-S12-03/-07/-15/-16 (defaults allow build; class-B tests run both modes) | [Inference] |
| TB-14 | C7 Crosswalk + R1 legacy backfill (read-only import of 125 cases with provenance; OD-S12-19 default "legacy backfill only") | module + data | C7, ADR-009 | None | INC-05 | M | OD-S12-19 | [Inference] |
| TB-15 | C6 Intake in shadow over sandbox copies of feeds: raw store, content-hash idempotency, natural key (partner, record_kind, ref_id, source_ts), quarantine | module | C6, ADR-008 | None (legacy reconcile untouched) | INC-06 | L | OD-S12-17, OD-S12-11 (default record_only) | [Inference] |
| TB-16 | C8 Runs (CLI jobs, run records, checkpoints; schedule disabled) | module | C8, ADR-010 | None | INC-07 | M | OD-S12-10 (default disabled) | [Inference] |
| TB-17 | C9 Metrics (definition tags, exact decimals, no fan-out; verdict `not_available_no_adopted_policy`) | module | C9, ADR-011 | None | INC-07 | M | OD-S12-01/-02/-08 (no adopted values needed to build) | [Inference] |
| TB-18 | C1 HTTP layer + minimal pages, loopback-only (ADR-014/015) | module | C1 | None (new process, new port) | INC-08 | M | none to build | [Inference] |
| TB-19 | C10 Reviewer exception queue + rule-trace views (R1 part) | module | C10, ADR-012 | None | INC-08 | M | none | [Inference] |
| TB-20 | C5 Disposition gate in mode `none`, holders `[]` (E-GATE-MODE-NONE / E-GATE-NO-HOLDERS) — never simulates a real disposition (HAR-12) | module | C5, ADR-006 | None | INC-08 | M | OD-S12-05/-06 only to *use*, not to build | [Inference] |
| TB-21 | R2: FTS5 reviewer search + templates (FTS5 availability on target Unknown) | module | C10, ADR-012 | None | INC-09 (after R1 release; outside Stage 15 R1 scope) | M | OD-S12-12, OD-S12-14 R1/R2 split | [Inference] |
| TB-22 | Correct legacy documentation that is unsafe to follow (TD-04, R-12; e.g. AD-09 quick start runs destructive tests) | docs fix | — | None (docs only) | INC-01 (docs part, optional) | S | WB-03 branch write | [Verified Fact] R-12 |
| TB-23 | Cutover per capability: make a hub output authoritative / retire a legacy output (DV approvals, HAR-06) | cutover | ADR-003 | **Yes** (consumer-visible) | CUT-1..CUT-5 (Stage 30) | — | OD-S12-13 per DV, OD-S12-14, OPD-15 owner of CO-WF-01 | [Inference] |

### TB-2 Explicitly NOT in the backlog (preserved / unchanged) [Verified Fact: paths exist; Inference: decision to keep]
See `coexistence-strategy.md` CS-2 for the full unchanged-component list. In short: `app/*.py`, `legacy_batch/`, `legacy_java/`, `legacy_js/`, `sql/`, `contracts/`, `integration/`, `services/`, `scripts/`, `ops/`, existing `tests/test_*.py`, `data/` (all 1,512 files), `Dockerfile`, `compose.yaml`, `environments/`, `pyproject.toml`, `run.sh`, `domain.json` are **not modified in Stage 15 R1**. Refactoring legacy code (e.g. making `app.store` injectable) is **rejected for R1** in favour of the subprocess harness (HD-1) because it would itself be a behaviour risk under HAR-06.

### TB-3 Harness design decision HD-1 (Stage 7 open question "subprocess-per-test vs refactor-for-injection")
| Option | Legacy change? | Reversibility | Risk | Verdict |
|---|---|---|---|---|
| A. Refactor `app/store.py` to resolve `LEGACY_DB` lazily | Yes (11 importers, heat map "High ripple") | Revert PR | Changes the very code being characterised before a net exists | Rejected for INC-01 |
| B. Subprocess per scenario in a full repo copy (OD-03a) | No | Delete test tree | Slower; needs process mgmt (CT-H2) | **Recommended (PROPOSED)** |
| C. `importlib.reload` in-process | No | — | Module globals leak across tests; Stage 7 TQ-01 shows ordering effects | Rejected |
Recommendation recorded as PROPOSED; Dinesh may override (Stage 15 entry checklist E-1).

## Evidence References
- `docs/07-repo-assessment/characterization-test-plan.md` L19-58 (CT-H, CT-01..18); `repo-transformation-readiness.md` (heat map, go/no-go).
- `docs/10-architecture/component-model.md` L21-31 (C1..C11); `adrs/ADR-001`, `ADR-003`, `ADR-004`, `ADR-018`.
- `docs/12-specs/spec-readiness.md` RD-3 L37-55, RD-4 L58-69; `features/f10-coexistence-change-safety.md` F10-2..F10-6.
- `docs/13-traceability/evidence/tests_plan.csv` (241 rows), `rtm.csv` (release column); `docs/14-transformation/evidence/increment-test-map.csv` + `increment_map.py` + `increment-test-map-summary.txt` (generated this stage from those CSVs only).
- Device facts (this stage): Python 3.10.12, SQLite 3.37.2, `java` and `node` present, **no python3.11/3.12 interpreter** on the device.

## Assumptions
- A-14-01 [Assumption] New top-level package `hub/` is a WB-04-class path (branch-only write, merge after review). WB-04 lists existing code folders only. Confirm: Engagement lead (Dinesh Naik) — Stage 15 entry checklist E-2.
- A-14-02 [Assumption] Sizes are relative review effort, not calendar estimates (no calendar exists; A-12-RD-1).
- A-14-03 [Assumption] Stage 7 A-07-18 (adding `tests/characterization/` on a BUILD branch) holds. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-01 Downstream consumers of legacy outputs (SQL report, Java totals, JS threshold) — Unknown (heat map "consumers unknown"); resolved only by a real owner (Stage 30 / OPD-15).
- U-14-02 Whether 3.12 will be the production runtime (OD-S12-12).

## Unresolved Issues
- 19 OD-S12 decisions, DV-01..09, OPD-05, OPD-13 remain open; handled as gates in `transformation-gates.md` and the Stage 15 entry checklist.

## Residual Risks
- RR-TB-1 Backlog sized on DRAFT specs; if Dinesh changes specs at Stage 17 (OD-S12-14) INC-03..INC-08 may need rework (mitigated by harness-first ordering, which is spec-independent).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial backlog (Stage 14). |
