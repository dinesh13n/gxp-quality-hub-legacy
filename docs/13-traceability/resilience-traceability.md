---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "resilience-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/operations-service-levels.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/12-specs/features/f06-scheduled-runs.md", "docs/12-specs/features/f10-coexistence-change-safety.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Resilience view: 19 requirements -> 57 acceptance criteria. Replay safety, no-silent-cap and rollback are testable in a sandbox; availability/timeliness/RTO-RPO targets are unvalidated working targets and only measurable as synthetic proxies (class C).

## Findings
### RES-1 Counts [Verified Fact: computed]
19 requirements (11 FR + 8 PNFR) -> **57 acceptance criteria (14 negative)**; class A 45 / B 5 / C 7. Business requirements: BR-05 (replay safe), BR-06 (delayed/missing/revised items visible), BR-12 (backlog ageing), BR-13 (releasable without 2025-style rollback); root causes RC-5 (silent capacity cap) and RC-6 (replay as duplicate); incident INC-2025-014.

### RES-2 Requirement -> test (resilience view)
| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |
|---|---|---|---|---|---|---|---|---|
| FR-RUN-01 | Reconcile/import runs SHALL be executable on a configured schedule and on authorised manual trigger. Whether a | R1 | AC-RUN-01..04 | 4 | 3 | AB | 16 | OD-S12-10 both modes |
| FR-RUN-02 | Every run SHALL write a run record: start/end, trigger, inputs seen, outcomes by type, errors, and whether a c | R1 | AC-INT-26; AC-OBS-02; AC-RUN-05,13 | 5 | 0 | A | 16,31 |  |
| FR-RUN-03 | No silent capacity cap SHALL exist: when work remains after a run it SHALL be reported as outstanding backlog  | R1 | AC-RUN-07..10 | 4 | 1 | A | 16 |  |
| FR-INT-01 | Each received item SHALL be stored as received (raw content, source, schema revision, receipt time) in an appe | R1 | AC-INT-01..03,29 | 4 | 2 | A | 16 |  |
| FR-INT-02 | Re-delivery of an item whose content is identical to one already processed SHALL change neither the exception  | R1 | AC-INT-04..06; AC-OBS-09 | 4 | 1 | AB | 16,31 |  |
| FR-INT-03 | A re-delivered item whose content DIFFERS from the processed one SHALL be quarantined as revised/conflicting a | R1 | AC-INT-07 | 2 | 0 | AC | 16 |  |
| FR-INT-08 | Delayed, missing or revised items SHALL be detectable and attributable to source and time without manual sprea | R2 | AC-INT-28 | 1 | 0 | A | 16 | R2 |
| FR-CO-03 | Each release SHALL have a tested rollback procedure and SHALL pass the replay-safety check (FR-INT-02) as a re | R1 | AC-CO-09,15 | 3 | 1 | A | 16 |  |
| FR-CO-01 | As-found behaviour captured in the Stage 7 characterisation baseline SHALL remain reproducible; any intended d | R1 | AC-CO-01..05,07; AC-POL-12..14,20 | 10 | 3 | AB | 16 |  |
| FR-DEC-02 | The current state of a case SHALL be reproducible from its event history, and the state of a case at any past  | R1 | AC-DEC-05..08 | 4 | 1 | A | 16 |  |
| FR-MET-05 | Backlog ageing and unresolved-exception rate SHALL be reported per site on one declared definition. | R1 | AC-MET-17 | 2 | 1 | A | 16 |  |
| PNFR-01 | Case review and reconciliation available in scheduled hours - 99.5% scheduled-hour availability | R1 measure | AC-NFR-01 | 1 | 0 | C | 28 | class C, working target |
| PNFR-02 | Overnight reconciliation completes before start of business - By 06:00 local business time, 100% of scheduled  | R1 | AC-NFR-02 | 1 | 0 | C | 28 | needs schedule (OD-S12-10) |
| PNFR-03 | Partner feed accepted promptly - Within 4 h of source event | R2 | AC-NFR-03 | 1 | 0 | C | 31 | R2 |
| PNFR-04 | Risk signals not older than tolerated age - Stale signal max 24 h | R2 | AC-NFR-04 | 1 | 0 | C | 31 | R2 |
| PNFR-05 | Service restorable from backup - RTO 8 h; RPO 24 h (older planning assumptions); restore rehearsal passes with | R1 (rehearsal) | AC-NFR-05 | 1 | 0 | C | 28 | rehearsal of hub.sqlite3 + anchor |
| PNFR-11 | Imports idempotent, contract-validated, lossless - 0 duplicate effects over replay suite; 0 silent overwrites; | R1 | AC-DEC-22; AC-INT-04; AC-NFR-11; AC-OBS-09 | 5 | 1 | AC | 16,31 |  |
| PNFR-14 | Failures/delays visible with source and time correlation - 100% of runs have run records; every R1 KPI has a c | R1 | AC-NFR-14; AC-OBS-01..03,08; AC-RUN-05,15 | 7 | 0 | A | 16,31 |  |
| PNFR-19 | Releases reversible and not causing 2025-style rollback - Rollback rehearsed; replay-safety gate passes before | R1 | AC-CO-09,15; AC-NFR-19 | 3 | 0 | A | 16,30 |  |

### RES-3 Findings
- **[Verified Fact]** The targets PNFR-01..05 (99.5% availability, 06:00 completion, 4 h feed acceptance, 24 h staleness, RTO 8 h / RPO 24 h) come from archived working targets the source calls "not measured guarantees" (`docs/operations-service-levels.md`). All five are **class C**: evidence is a sandbox measurement or rehearsal labelled synthetic; attainment of the target on a real environment cannot be shown (ACC-8). PNFR-03/04 are R2.
- **[Verified Fact]** No-silent-cap (FR-RUN-03, RC-5) is traced to the legacy behaviour characterised in Stage 7 (1000-row reconcile cap, CT-08; night-shift limits, CT-10). Both CT tests are P1 and **not acceptance-linked** [GAP-13-06].
- **[Verified Fact]** Concurrency on one SQLite file (15 s busy_timeout) is uncharacterised (CT-17, U-07-05); AC-DEC-22 covers logical sequence conflict only. A resilience claim about parallel API+bridge+reconcile cannot be made [GAP-13-15].
- **[Verified Fact]** Rollback rehearsal and replay-safety release gate (FR-CO-03 Should/R1, PNFR-19) are tested at AC-CO-09/15, AC-NFR-19; evidence belongs to Stage 30 (release) and requires a release process that does not yet exist.
- **[Verified Fact]** Restore rehearsal (PNFR-05): backup `../_data-backup-2026-10-17/` with 1,512-file SHA256SUMS exists for the *legacy* data; a rehearsal for the new `hub.sqlite3` and audit anchor is only planned (AC-NFR-05, AC-CO-09).
- **[Verified Fact]** Scheduler is disabled by default pending OD-S12-10 (is a deterministic scheduler an "automated action" under HAR-10); FR-RUN-01 tests run both modes (class B), and PNFR-02 cannot be proven until a schedule is enabled.
- **[Inference]** No chaos/failure-injection, DR (BC/DR is Stage 29) or load test is traced: no requirement asks for one. The 125-case baseline is too small for capacity conclusions; PNFR-06 target is Unknown (OPD-14).
- **[Unknown]** Site timezone for the 06:00 check (`site.timezone` not configured, U-12 register); Docker/Compose behaviour (CT-18) and Python 3.12 runtime (OD-S12-12).

## Evidence References
- `docs/09-initial-prd/nfrs.md` (PNFR-01..05, 11, 14, 19), `docs/operations-service-levels.md`, `docs/12-specs/nfr-spec.md`, `docs/07-repo-assessment/characterization-test-plan.md` (CT-08, CT-10, CT-17, CT-18), `docs/12-specs/spec-readiness.md` (OD-S12-10, -12).

## Assumptions
- A-13-11 [Assumption]: resilience targets stay Assumptions until Dinesh adopts or rejects them (OD-S12-14).

## Unknowns
- U-13-10: site timezone; real environment; concurrency behaviour (U-07-05).

## Unresolved Issues
- GAP-13-07 (class C targets) and GAP-13-15 (concurrency) are open.

## Residual Risks
- R-13-10 A passing sandbox rehearsal could be read as an RTO/RPO guarantee.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

