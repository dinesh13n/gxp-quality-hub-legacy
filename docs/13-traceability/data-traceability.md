---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "data-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/12-specs/schema-specifications.md", "docs/12-specs/event-contracts.md", "docs/12-specs/contracts/", "docs/11-data-context/data-contracts.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Data view: 26 requirements -> 100 acceptance criteria (38 negative); 15 schemas and 15 events traced; replay/changed-content and month-end paths are the weak spots; all evidence is synthetic.

## Findings
### DAT-1 Counts [Verified Fact: computed]
26 requirements in the data view (20 FR + 6 PNFR) -> **100 acceptance criteria (38 negative)**; class A 87 / B 10 / C 3. 15 schemas (SCH-), 15 decision events (EV-), 16 JSON Schema files, DDL `contracts/ddl/hub-schema-v0.1.sql`, 14 valid examples + `invalid-cases.json`.

### DAT-2 Requirement -> test (data view)
| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |
|---|---|---|---|---|---|---|---|---|
| FR-ID-01 | The system SHALL maintain an explicit crosswalk linking case, batch, deviation, CAPA and feed reference, each  | R1 | AC-ID-01,06,09..12 | 7 | 2 | A | 16 |  |
| FR-ID-02 | Orphans SHALL remain orphans: no link SHALL be created by guessing or similarity. A human MAY create a link; t | R1 | AC-ID-02..08 | 7 | 5 | A | 16 |  |
| FR-ID-03 | The system SHALL surface, as findings and without auto-correction, cross-object state combinations that a conf | R2 | AC-ID-15 | 2 | 1 | A | 16 |  |
| FR-ID-04 | A read-only joined view SHALL let an investigator see all linked objects for any identifier (touchpoint T5, de | R2 | AC-ID-13,17 | 3 | 1 | A | 16 |  |
| FR-INT-01 | Each received item SHALL be stored as received (raw content, source, schema revision, receipt time) in an appe | R1 | AC-INT-01..03,29 | 4 | 2 | A | 16 |  |
| FR-INT-02 | Re-delivery of an item whose content is identical to one already processed SHALL change neither the exception  | R1 | AC-INT-04..06; AC-OBS-09 | 4 | 1 | AB | 16,31 |  |
| FR-INT-03 | A re-delivered item whose content DIFFERS from the processed one SHALL be quarantined as revised/conflicting a | R1 | AC-INT-07 | 2 | 0 | AC | 16 | no negative AC; synthetic fixture |
| FR-INT-04 | Each item SHALL be validated against the declared source contract (integration/source-contract-v1.json) and su | R1 | AC-INT-09..14,16,25..27 | 10 | 3 | AB | 16 | OD-S12-11 both modes |
| FR-INT-05 | Each external item SHALL be matched to exactly one core case or flagged unmatched before reaching a reviewer q | R1 | AC-INT-11,17..19 | 4 | 2 | A | 16 |  |
| FR-INT-06 | Every exception SHALL carry an enumerated reason code and queue; classification SHALL be rule-based and determ | R1 | AC-INT-15,20 | 3 | 0 | AB | 16 |  |
| FR-INT-07 | Inbound text (feed notes, document bodies, emails) SHALL be treated strictly as data: no inbound string SHALL  | R1 | AC-GATE-13; AC-INT-22..24 | 4 | 4 | A | 16 |  |
| FR-INT-08 | Delayed, missing or revised items SHALL be detectable and attributable to source and time without manual sprea | R2 | AC-INT-28 | 1 | 0 | A | 16 |  |
| FR-DEC-01 | Every case decision or state change SHALL be stored as a new immutable event carrying actor, timestamp, from-s | R1 | AC-DEC-01..04,22; AC-GATE-05 | 6 | 3 | ABC | 16 |  |
| FR-DEC-02 | The current state of a case SHALL be reproducible from its event history, and the state of a case at any past  | R1 | AC-DEC-05..08 | 4 | 1 | A | 16 |  |
| FR-DEC-03 | A reopen SHALL produce an explicit reopen event; a case SHALL NOT enter a reopened state without one. | R1 | AC-DEC-09..11 | 3 | 1 | A | 16 |  |
| FR-DEC-04 | Each decision event SHALL be retrievable together with the evidence relied on and its source, on request, by a | R1 | AC-DEC-12..14 | 3 | 1 | A | 16 |  |
| FR-DEC-06 | The system SHALL record, as separate timestamped facts, (a) receipt of the case, (b) operations-closed, and (c | R1 | AC-DEC-20 | 2 | 1 | B | 16 |  |
| FR-MET-04 | Month-end totals SHALL be computed by one documented query/function on one configured cut-off and denominator, | R1 | AC-INT-27; AC-MET-09..13 | 6 | 4 | A | 16 | OD-S12-08 |
| FR-MET-06 | Each KPI SHALL document its window, denominator and exclusions, and SHALL be reproducible from them; every KPI | R1 | AC-MET-14 | 2 | 1 | A | 16 |  |
| FR-CO-01 | As-found behaviour captured in the Stage 7 characterisation baseline SHALL remain reproducible; any intended d | R1 | AC-CO-01..05,07; AC-POL-12..14,20 | 10 | 3 | AB | 16 |  |
| PNFR-10 | Retention follows a policy once decided - 0 deletions of case/evidence records while no retention policy is ad | R1 (hold-all) | AC-DEC-03; AC-NFR-10; AC-SEC-18 | 3 | 3 | AB | 16,25,26 | OD-S12-09 hold-all |
| PNFR-11 | Imports idempotent, contract-validated, lossless - 0 duplicate effects over replay suite; 0 silent overwrites; | R1 | AC-DEC-22; AC-INT-04; AC-NFR-11; AC-OBS-09 | 5 | 1 | AC | 16,31 |  |
| PNFR-12 | Sensitive fields handled per data-use constraints - 100% of field classes covered by an access test | R2 | AC-NFR-12; AC-SEC-19 | 2 | 0 | A | 26 |  |
| PNFR-16 | KPIs reproducible from documented window, denominator, exclusions - 100% of KPIs documented; re-run gives iden | R1 | AC-MET-14; AC-NFR-16; AC-OBS-08 | 3 | 0 | A | 16,31 |  |
| PNFR-17 | Core decision, rule, intake and metric paths reproducible - Identical input -> bit-identical output; character | R1 | AC-CO-13; AC-DEC-05; AC-GATE-15; AC-INT-20; AC-MET-21; AC-NFR-17; AC-POL-22; AC-REV-14 | 8 | 0 | A | 16 |  |
| PNFR-20 | Outputs from synthetic data are labelled - 100% of KPI outputs and reports labelled 'synthetic, unvalidated' w | R1 | AC-MET-02,08; AC-NFR-20 | 3 | 0 | AC | 16 |  |

### DAT-3 Schema -> requirement -> test
| Schema | Table / shape | Requirement(s) | Planned tests (via requirement) | Contract file |
|---|---|---|---|---|
| SCH-AUDIT | `audit_log` | FR-SEC-02 | AC-DEC-24; AC-GATE-22; AC-SEC-03,09..14,21 | `schemas/audit-record.schema.json` (exists) |
| SCH-CASE-STATE | `case_state` (projection) | FR-DEC-02 | AC-DEC-05..08 | no file (derived or DDL-only) |
| SCH-CROSSWALK | `crosswalk_link`, `crosswalk_link_event` | FR-ID-01, FR-ID-02 | AC-ID-01..12 | `schemas/crosswalk-link.schema.json` (exists) |
| SCH-DEC-EVENT | `decision_events` | FR-DEC-01 | AC-DEC-01..04,22; AC-GATE-05 | `schemas/decision-event.schema.json` (exists) |
| SCH-ERROR | error envelope | **none** (cross-cutting) | - | `schemas/error-envelope.schema.json` (exists) |
| SCH-EVIDENCE | `evidence_record` | FR-DEC-04 | AC-DEC-12..14 | `schemas/evidence-record.schema.json` (exists) |
| SCH-GATE-CONFIG | configuration file | FR-GATE-04, FR-RUN-01 | AC-GATE-01,22; AC-RUN-01..04 | `schemas/hub-config.schema.json` (exists) |
| SCH-INTAKE-OUTCOME | `intake_outcome`, view `intake_current` | FR-INT-02 | AC-INT-04..06; AC-OBS-09 | `schemas/intake-outcome.schema.json` (exists) |
| SCH-METRIC-DEF | `metric_definition` | FR-MET-01, FR-MET-06 | AC-MET-01,14 | `schemas/metric-definition.schema.json` (exists) |
| SCH-METRIC-VALUE | `metric_value` | FR-MET-01, PNFR-20 | AC-MET-01,08; AC-NFR-20 | `schemas/metric-value.schema.json` (exists) |
| SCH-POLICY | `policy_object`, `policy_events` | FR-POL-01 | AC-DEC-21; AC-POL-01..03,05,25 | `schemas/policy-object.schema.json` (exists) |
| SCH-RAW-INTAKE | `raw_intake` | FR-INT-01 | AC-INT-01..03,29 | `schemas/raw-intake.schema.json` (exists) |
| SCH-REASON | reason-code catalogue (SC-3) | FR-INT-06 | AC-INT-15,20 | no file (derived or DDL-only) |
| SCH-RULE-SET | `rule_set`, `rule_row`, `active_ruleset` | FR-POL-04, FR-POL-06 | AC-CO-03; AC-POL-11..21; AC-REV-06 | no file (derived or DDL-only) |
| SCH-RUN-RECORD | `run_event` (+ derived record) | FR-RUN-02, FR-RUN-03 | AC-INT-26; AC-OBS-02; AC-RUN-05..10,13 | `schemas/run-record.schema.json` (exists) |

### DAT-4 Event -> requirement -> test
| Event | Name | Requirement(s) | Planned tests |
|---|---|---|---|
| EV-DEC-01 | CASE_CREATED | FR-DEC-02 | AC-DEC-05..08 |
| EV-DEC-02 | CASE_IMPORTED | FR-CO-01, FR-DEC-02 | AC-CO-01..05,07; AC-DEC-05..08; AC-POL-12..14,20 |
| EV-DEC-03 | STATUS_CHANGE | FR-DEC-01, FR-DEC-05 | AC-DEC-01..04,15..19,22,27; AC-GATE-05 |
| EV-DEC-04 | REOPEN | FR-DEC-03 | AC-DEC-09..11 |
| EV-DEC-05 | EVIDENCE_ATTACHED | FR-DEC-04 | AC-DEC-12..14 |
| EV-DEC-06 | FACT_RECEIVED | FR-DEC-06 | AC-DEC-20 |
| EV-DEC-07 | FACT_OPS_CLOSED | FR-DEC-06 | AC-DEC-20 |
| EV-DEC-08 | FACT_EVIDENCE_COMPLETE | FR-DEC-06 | AC-DEC-20 |
| EV-DEC-09 | CLOSE_EXCEPTION | FR-DEC-05, FR-GATE-03 | AC-DEC-15..19,27; AC-GATE-09,12; AC-OBS-06; AC-POL-02,18; AC-RUN-03; AC-SEC-08 |
| EV-DEC-10 | DISPOSITION_RECORDED | FR-GATE-05 | AC-GATE-01,03,05..08 |
| EV-DEC-11 | DISPOSITION_REFERENCED | FR-GATE-05 | AC-GATE-01,03,05..08 |
| EV-DEC-12 | QA_RELEASE_RECORDED | FR-GATE-03 | AC-DEC-17; AC-GATE-09,12; AC-OBS-06; AC-POL-02,18; AC-RUN-03; AC-SEC-08 |
| EV-DEC-13 | ESIGNATURE_RECORDED | FR-GATE-03 | AC-DEC-17; AC-GATE-09,12; AC-OBS-06; AC-POL-02,18; AC-RUN-03; AC-SEC-08 |
| EV-DEC-14 | OVERRIDE_RECORDED | FR-GATE-06 | AC-GATE-18..20; AC-REV-08 |
| EV-DEC-15 | CORRECTION | FR-DEC-01 | AC-DEC-01..04,22; AC-GATE-05 |

### DAT-5 Findings
- **[Verified Fact]** Every schema and event except `SCH-ERROR` traces to an FR/PNFR. `SCH-ERROR` (error envelope) is a cross-cutting convention justified by API conventions, not a requirement [GAP-13-05].
- **[Verified Fact]** Replay/idempotency (FR-INT-02, BR-05, PNFR-11) is the highest-value data requirement (2025 rollback, INC-2025-014). It has ACs for identical re-delivery; the *changed-content* path (FR-INT-03 REVISED_CONFLICT) has **no negative AC** and its corrected-replay fixture cannot come from shipped data (none exists, FND-INT-1) so it is class C (synthetic fixture) [GAP-13-11].
- **[Verified Fact]** Stage 11 DC-03 identity key is wrong (business_key is not an item identity; 2,386 of 2,407 multi-row groups differ) - OD-10(a). Specs use the natural key (partner, record_kind, ref_id, source_ts) (OD-S12-17); tests built on DC-03 would be wrong. Stage 11 v0.2 addendum is pending (owner: Engagement lead (Dinesh Naik)).
- **[Verified Fact]** Source contract: `source_messages` 15/15 conform, `partner_feeds` 0/8,567, `gateway_inbox` 0/1 (RF-2). The per-source `record_only` vs `enforce` choice (OD-S12-11) is open, so FR-INT-04 tests must run both modes (class B).
- **[Verified Fact]** Month-end totals (FR-MET-04, BR-10): the legacy SQL report 742,956.61 vs true 622,826.44 (+19.3%) (DV-01) is a golden (CT-12) that is not acceptance-linked [GAP-13-06]; cut-off/denominator/cost source are open (OD-S12-08).
- **[Verified Fact]** Retention (PNFR-10) is hold-all: tests assert 0 deletions; no deletion/archival path exists to test (OD-S12-09).
- **[Inference]** All data-quality evidence runs on the 125-case, seed-4100 baseline (OD-09) and synthetic feeds; no real data exists (OD-04). Results are labelled "synthetic, unvalidated" (PNFR-20).
- **[Unknown]** Case creation path (OD-S12-19): R1 is backfill only, so data-creation requirements for non-legacy cases cannot be traced or tested.

## Evidence References
- `docs/12-specs/schema-specifications.md`, `event-contracts.md`, `contracts/schemas/`, `contracts/ddl/`, `docs/11-data-context/data-contracts.md`, `docs/12-specs/spec-readiness.md` (RF-1, RF-2), `docs/07-repo-assessment/characterization-test-plan.md` (CT-05, CT-07, CT-08, CT-12).

## Assumptions
- A-13-09 [Assumption]: natural key (partner, record_kind, ref_id, source_ts) is the item identity (supported only by 67 replay pairs, A-12-F04-3).

## Unknowns
- U-13-08: item identity on real data; corrected-replay behaviour; cost data source.

## Unresolved Issues
- Stage 11 DC-03 addendum pending (OD-10a); OD-S12-08/09/11/17/19 open.

## Residual Risks
- R-13-08 Tests pinned to an unconfirmed identity key may need rewriting if OD-S12-17 is decided differently.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

