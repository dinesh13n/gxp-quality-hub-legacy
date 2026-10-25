---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "as-built-architecture.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["hub/", "docs/10-architecture/adrs/", "docs/10-architecture/architecture-decision-summary.md", "docs/16-repo-validation/architecture-conformance-report.md", "docs/17-implementation-prd/implementation-prd.md", "docs/20-application/application-readiness.md", "docs/28-reliability/resilience-readiness.md", "docs/31-observability/observability-validation.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
The as-built architecture is a stdlib-only modular monolith in shadow beside untouched legacy, loopback-only, with every consequential switch OFF and several mechanisms (resilience, observability, release evaluator, CI) built but not wired or not installed. There is no deployed environment.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AB-AR-1 System shape [Verified Fact]
A **modular monolith** `hub/` (stdlib-only Python, no third-party dependency) built **beside** the untouched legacy estate (`legacy_batch/`, `legacy_java/`, `legacy_js/`, `app/`, `services/`, `data/`). Counted by me at main 08add05: **204 Python files / 17,247 lines under `hub/`** (Stage 16 recorded 163 files / 13,994 lines; the difference is Stages 20-31, see AB-2). Tests live in `tests/hub/` and `tests/characterization/`. Legacy code and data are read through adapters AD-01..AD-08 and never written (E-CO-LEGACY-WRITE-REFUSED).

### AB-AR-2 Packages [Verified Fact: `ls hub`]
`adapters admin control coexistence core crosswalk decision gate golden guards intake metrics obs ops policy r2 release resilience review runs search security store web` plus `cli.py config.py runtime.py __main__.py`. Mapping to capabilities: `final-capability-map.md`.

### AB-AR-3 Stores and migrations [Verified Fact: implementation-prd IC-4]
One hub SQLite file; insert-only tables with triggers (Stage 27 added insert-only triggers on `schema_migrations`, A-27-05). Migrations M000..M007 apply by per-package runners with **seven version tables** (a deviation from the Stage 14 single-runner plan, S16-D03). Forward-only, backup-before-migrate; rollback = backup restore. FTS5 virtual tables are derived objects built by the corpus loader.

### AB-AR-4 What is built but NOT wired [Verified Fact]
- `hub/resilience` (GuardedGateway, BoundedLoopbackServer, budget) is not wired into `gateway-pull` or `hub web serve` (S28; D-28-01/02).
- `hub/obs` metrics persistence/alerts are not wired; only 4 of 21 declared log events are emitted; six specified metrics are not exported (Stage 31; D-31-01/02/06/09).
- `hub/release` go/no-go evaluator exists; evaluating it returns NO-GO; it gates nothing.
- Schedule flag exists; ZH-09 only; OFF.
- CI file `ci/hub-hardening.yml` exists in the repo but is NOT installed under `.github/` (HAR-07, D-27-03).

### AB-AR-5 Deployment topology [Verified Fact / Inference]
[Verified Fact] ADR-015 topology: loopback-only HTTP (`127.0.0.1`); non-loopback bind is refused even with an approval in config (PCH-45); no TLS. [Verified Fact] No production host exists (AP-OPS-01 OPEN); the only environment is the reference laptop (Python 3.10.12 / SQLite 3.37.2) plus the orchestrator's cloud workspace (Python 3.13, provider Unknown, PA-18) used for the full hub regression. [Verified Fact] Legacy `Dockerfile`/`compose.yaml` are unchanged (frozen path; `0.0.0.0` bind in legacy compose is RP-11). [Inference] There is no deployed architecture; this is a development/shadow topology.

### AB-AR-6 Coexistence pattern (ADR-003) [Verified Fact]
Shadow/additive: legacy remains the system of record and authority for all outputs. The hub reads a snapshot (`FX-BASE125`, sha256 `c254649f…d70aa`, 125 cases, seed 4100, OD-02/OD-09) and writes only to its own store. Authority switch per capability exists (BX-01) but ships OFF and requires `approval_ref` (OD-26, OD-31).

### AB-AR-7 ADR status [Verified Fact]
All 18 ADR files `docs/10-architecture/adrs/ADR-001..018` carry front-matter `status: "DRAFT"` (the Stage 10 summary calls them PROPOSED); none carries ACCEPTED. OD-25 accepted the implementation baseline as a whole, not per ADR. This resolves Stage 42 U-42-01: no per-ADR acceptance exists. Conformance (Stage 16 AC-1): ADR-014 and ADR-016 partial, ADR-017 not assessable, ADR-018 superseded for production by OD-24.

### AB-AR-8 Structural debt, then and now
| Item (Stage 16/17) | State at main 08add05 | Evidence | Tag |
|---|---|---|---|
| 16 package cycles; domain imports `hub.web` | Stage 20 reduced (10 to 6, 6 to 4); Stage 27 reports all ten package import cycles removed | application-readiness DW-06; production-readiness-checklist; OD-34 | [Verified Fact] (as reported) |
| Three copies of the Zone H check | One holder rule (Stage 20 DW-06) | application-readiness RD-1 | [Verified Fact] |
| Seven migration runners / version tables | Unchanged | IC-4 | [Verified Fact] |
| Two server entry points (`hub.web serve`, `hub.r2 serve`) | Unchanged; choice before exposure open | PCH-21 | [Verified Fact] |
| 10 functions over complexity 15 | 9 remain | OD-34 | [Verified Fact] |
| Resilience wired? | No | OD-35 | [Verified Fact] |

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-04 [Assumption] Code line/file counts are those of main 08add05 as I counted; Stage 16 figures differ because of later stages.
- A-43-05 [Assumption] 'All ten cycles removed' (Stage 27) is taken from the Stage 27 document; I did not re-run the static check.

## Unknowns
- U-43-04 Whether cycle count and complexity figures are unchanged after Stage 31 merges (no re-run).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
