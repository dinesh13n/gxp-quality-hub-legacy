---
stage: "12 — Spec-Driven Design"
artifact: "spec-readiness.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/*", "docs/09-initial-prd/open-product-decisions.md", "docs/10-architecture/architecture-decision-summary.md", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Readiness assessment: CONDITIONAL PASS. 19 open decisions registered with modes/defaults/blocked actions, 10 material findings (incl. wrong identity key in Stage 11 DC-03, contract-scope evidence, runtime conflict, FR split 43/9), consistency check against 18 ADRs and Stage 11 contracts (3 divergences recorded), consolidated assumption and unknown registers, and the completion-gate evaluation.

## Findings
### RD-1 Verdict
**Gate status: CONDITIONAL PASS.** All ten features, thirteen required artifacts and the machine-checkable contracts exist; every FR (52), every PNFR (20) and every behaviour (108) has at least one Given/When/Then criterion (241 in total); every unresolved decision is registered below, is expressed as configurable policy with an explicit default and **both modes specified and tested where a mode choice exists**, and is marked as blocking only the work that depends on it. No blocking condition prevents Stage 13 (traceability). Conditions are non-blocking for Stage 13 but block specific later actions (RD-4). Nothing in this document is an approval; approval is Dinesh Naik's (HAR-11).

### RD-2 Readiness per feature
| Feature | Buildable now (Stage 15) | Parameterised on open decisions | Blocked until decision | Status |
|---|---|---|---|---|
| F01 Decision & Evidence Record | event store, fold, as-of, reopen, evidence refs, facts, concurrency, audit hook | closing set (OD-S12-03), sufficiency (07), fact recorder (15), transition table (16), case creation path (19) | use of any closing policy as 'adopted' | READY WITH PARAMETERS |
| F02 Human Disposition Gate | gate service, holder check, pack, overrides, all three modes, triggers, tests | mode and values (05), holders (06) | any pilot use of Zone H (needs 05 and 06) | READY WITH PARAMETERS |
| F03 Policy & Rule Service | policy objects, rule engine, three as-found sets, defaulted marker, active pointer | definitions (01), clock (02), rule authority and default (04) | adopting any policy / activating any rule set; changing a rule value | READY WITH PARAMETERS |
| F04 Safe Intake | raw/outcome store, hash/identity, validation, reason codes, quarantine, matching | identity key (17), contract scope (11) | `enforce` on any source | READY WITH PARAMETERS |
| F05 Identity Crosswalk | link store, exact-key matcher, human links, lookup | consistency rules (R2) | shipping any adopted CONSISTENCY rule | READY |
| F06 Scheduled Runs | CLI/HTTP jobs, run records, checkpoints, lock | schedule (10) | enabling the schedule | READY WITH PARAMETERS |
| F07 Metrics | registry, tags, mixing refusal, percentiles, exact totals, reproduce | cut-off/denominator (08), definitions (01), clock (02) | any KPI target or pass/fail verdict | READY WITH PARAMETERS |
| F08 Reviewer Support | exception queue, rule trace; R2 search/template | runtime FTS5 (12) | search ranking claims | READY (R1); R2 conditional |
| F09 Access, Audit, Protection | authenticator, RBAC, audit chain, CSRF, loopback | anchor location (18), user administration (06) | exposure beyond loopback | READY WITH PARAMETERS |
| F10 Coexistence & Change Safety | golden harness, register, gates, rollback, No-AI checks | preserve-vs-fix (13), runtime (12) | cut-over of any DV-xx item | READY WITH PARAMETERS |

### RD-3 Open-decision register (all owned by Engagement lead (Dinesh Naik); "due" is stage-relative because no calendar dates exist)
| ID | Decision needed | Source | Specs affected | Modes / defaults specified | Resolving stage / due | Blocks |
|---|---|---|---|---|---|---|
| OD-S12-01 | Definition of closed / resolved / approved (D-OPS, D-EVID, D-FIN or other) | OPD-01, OPD-03, Q-02-05 | F01, F03, F07; BR-02 | candidates only; accepted-open recordable; no adopted value | before any KPI target (Stage 34) and before Stage 13 adoption claims | KPI targets, pass/fail verdicts |
| OD-S12-02 | Meaning of '48 h' (start, stop, duration, calendar) | OPD-02 | F03, F07 | CLOCK objects, 2 candidates, verdict only if adopted | before Stage 13 / Stage 34 | SLA verdicts |
| OD-S12-03 | Closing-state set when no closure policy is active | new (BEH-DEC-07) | F01 (AC-DEC-27/28) | `treat_label_CLOSED_as_closing` (default) or `none` | before Stage 15 build of F01 | semantics of closure check |
| OD-S12-04 | Approval/priority-rule authority; active rule set; default 999,999; fix vs preserve | OPD-04, RC-4 | F03, F10 | three as-found sets read-only; no active set; default preserved and marked | before Stage 14/15 code change | any rule change |
| OD-S12-05 | Where batch disposition is recorded (this system / external reference / none) | OPD-05, ADR-006 | F02 | `none` (default), `event`, `external_ref` all specified and tested | before pilot use (Stage 15+) | Zone H pilot |
| OD-S12-06 | Who holds the dispositioner role; who administers users | OPD-06 | F02, F09 | holders `[]`; offline `hub user` | before pilot use | Zone H pilot |
| OD-S12-07 | Evidence sufficiency criteria and exception rule | OPD-07 | F01 | structural presence only | before Stage 13 | judging evidence |
| OD-S12-08 | Month-end cut-off, denominator, cost data source | OPD-08 | F07 | required parameters; no hidden default; cost = E-MET-NOT-AVAILABLE | Stage 13/34 | month-end KPIs |
| OD-S12-09 | Retention policy | OPD-09 | F09, all | hold-all, no delete paths | Stage 25 | any deletion/archival |
| OD-S12-10 | Is a deterministic scheduler an 'automated action' (HAR-10)? | OPD-11 | F06 | disabled (default) / enabled for non-Zone-H jobs via ZH-09 | before Stage 15 | enabling schedule, PNFR-02 proof |
| OD-S12-11 | Scope of `integration/source-contract-v1.json` (evidence: source_messages 15/15 conform, partner_feeds 0/8,567, gateway 0/1) | new; Stage 11 DQ-04 refined | F04 | `record_only` (default) / `enforce` per source; amend-contract option noted | before Stage 14 test design | enforcing FR-INT-04 literally on partner feeds |
| OD-S12-12 | Target runtime: ADR-018 says Python 3.12; `pyproject.toml` says >= 3.10; device 3.10.12 / SQLite 3.37.2; FTS5 availability on target unknown | ADR-018, ADR-012 | F08, F10, NF-A1 | floor 3.10/3.37 with FTS5 optional and fallback | before Stage 15 | use of 3.11+ features |
| OD-S12-13 | Preserve-vs-fix for DV-01..DV-09 | R-07-02, HAR-06 | F10 | all proposed, none approved | before Stage 14 (migration plan) / Stage 15 | cut-over of each item |
| OD-S12-14 | Approval of Initial PRD, R1/R2 split (43/9), NFR targets, ADRs | OPD-13, HAR-11 | all | specs DRAFT | before Stage 17 | treating specs as approved |
| OD-S12-15 | Who records FACT_OPS_CLOSED / FACT_EVIDENCE_COMPLETE (human only, or may a rule derive them) | new (BEH-DEC-08) | F01, F07 | human roles reviewer/quality_lead/compliance | before Stage 15 | automatic fact derivation |
| OD-S12-16 | Legal transition table between case states | new (BEH-DEC-10) | F01 | `structural` default / strict table | before Stage 15 | enforcement of any workflow order |
| OD-S12-17 | Item identity key for re-delivery (replace DC-03 `feed_id/business_key`) | FND-INT-1/2 | F04, Stage 11 DC-03 | natural key (partner, record_kind, ref_id, source_ts) | before Stage 14; Stage 11 v0.2 addendum | revision-conflict semantics |
| OD-S12-18 | Audit anchor location in a real deployment | ADR-005 | F09 | file outside DB dir (config) | before Stage 24/27 | external tamper-evidence claim |
| OD-S12-19 | How new cases enter the system (creation path/workflow) | new; none in repo or PRD | F01, API | R1 = legacy backfill only; no creation endpoint | before Stage 15 | creation of non-legacy cases |
Carried unchanged from Stage 9: OPD-10 buy-vs-build (ADR-017 not evaluated), OPD-12 search question set, OPD-14 performance target, OPD-15 parallel-workflow owner, OPD-16 synthetic vs real organisation.

### RD-4 Blocked actions (the guardrail: 'mark ambiguous items as open and block them')
| Blocked action | Until | How the spec enforces the block |
|---|---|---|
| Using Zone H in any pilot | OD-S12-05 and OD-S12-06 | holders empty, mode none, E-GATE-NO-HOLDERS / E-GATE-MODE-NONE |
| Adopting a definition, clock, rule set or closure policy | OD-S12-01/02/04 | nothing ships adopted; adoption is ZH-05/06 |
| Enabling a schedule | OD-S12-10 | schedule disabled; ZH-09 |
| Enforcing the source contract on a feed | OD-S12-11 | `record_only` default |
| Changing any legacy-golden behaviour | OD-S12-13 and HAR-06 | deviation register `proposed`; golden gate fails |
| Producing KPI targets or pass/fail verdicts | OD-S12-01/02/08 | verdict `not_available_no_adopted_policy`, cut-off required |
| Any deletion/archival | OD-S12-09 | no delete paths |
| Exposure beyond loopback | HAR-05, Stage 23-25 | start-up refusal |

### RD-5 Findings (material) [each: evidence, impact, risk, confidence, unresolved question]
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved |
|---|---|---|---|---|---|---|
| RF-1 | [Verified Fact] `business_key` is not an item identity: 2,386 of 2,407 multi-row business-key groups carry different payloads; the 67 REPLAY rows are content-identical to a sibling with the same natural key (67/67); no corrected-replay exists. | read-only queries on `data/legacy.sqlite3` (F04 FND-INT-1/2) | Stage 11 DC-03 wording would quarantine thousands of legitimate events | High if unnoticed | High | OD-S12-17 |
| RF-2 | [Verified Fact] The declared source contract is met by `source_messages` (15/15) but not by `partner_feeds` (0/8,567) or `gateway_inbox` (0/1). Stage 11 'not met by any feed' is accurate for the feeds only. | F04 FND-INT-3 | FR-INT-04 cannot be literally enforced on partner feeds without 100% quarantine | Medium | High | OD-S12-11 |
| RF-3 | [Verified Fact] ADR-018 specifies Python 3.12 but `pyproject.toml` requires >= 3.10 with no dependencies and the device runs 3.10.12. | pyproject.toml; Stage 11 RT-01 | New code may use 3.11+ features that fail on the device | Low-Medium | High | OD-S12-12 |
| RF-4 | [Verified Fact] The Stage 9 register has 43 R1 and 9 R2 FRs (40 Must, 3 Should in R1; 7 Should, 2 Could in R2), not 41/11 as quoted in the stage brief. | functional-requirements.md FF-1 | Traceability counts must use 43/9 | Low | High | OD-S12-14 |
| RF-5 | [Verified Fact] Observed unit, currency and object_type vocabularies close the 'enumerate at Stage 12' item in DC-02; all 8,567 payloads conform to the new payload schema. | F04 FND-INT-4; schema-specifications SC-4 | schemas can be frozen as v0.1 | Low | High | none |
| RF-6 | [Verified Fact] Only deviation->batch and capa->deviation (and lab_result->batch) have explicit keys; no key links a case to a batch, deviation or CAPA, so those links are human-only (LT-06). | F05-1 (42/42, 21/21, 0 of 125) | Cross-object consistency (FR-ID-03) will find little until humans link | Medium | High | none |
| RF-7 | [Inference] The single Zone H choke point plus DB trigger plus import-graph test make the human gate testable from three independent angles (AC-GATE-09/11/12). | F02 | Strongest control for the highest-risk RC-1 | Low | Medium (design, not built) | none |
| RF-8 | [Verified Fact] A reference value for the fan-out-free total exists: `SUM(cases.amount)` = 622,826.44 over 125 cases (Decimal), matching Stage 7 BB-08; the legacy SQL gives 742,956.61. | F07; read-only query | Regression oracle for FR-MET-04 | Low | High | none |
| RF-9 | [Inference] Most event-derived KPIs return null on the shipped baseline (no real closure timestamps); the spec forbids rendering null as 0. | OD-07; AC-MET-08 | KPI coverage report will show gaps by design | Low | High | Q-02-04/05 |
| RF-10 | [Assumption] Spec-chosen conventions (step-up re-auth 300 s, lockout 5/15/15, PBKDF2 >= 600k, percentile method, query limits, paging clamp) have no organisational source. | A-12-* register | Could be mistaken for client policy | Low | Medium | Stage 24 to confirm |

### RD-6 Analysis dimensions (required by the stage prompt)
| Dimension | Assessment | Evidence |
|---|---|---|
| Completeness | Every FR/PNFR covered; 10 features; 48 API ops; 15 decision events; 16 JSON Schemas; DDL tested; known gaps listed (RD-3) | acceptance-criteria ACC-3; system-spec SYS-9 |
| Unambiguity | Decision-dependent text uses explicit parameters and modes; conventions labelled Assumption; 19 open decisions registered | RD-3; A-12-* register |
| Testability | 241 Given/When/Then criteria, 44% negative; 7 limits on verifiability stated; machine-checkable schemas with 13 valid / 17 invalid examples; OpenAPI 3.0.3 parses | acceptance-criteria ACC-8; schema-specifications SC-1 |
| Consistency with ADRs and data contracts | see RD-7; two deliberate divergences recorded (DC-03 identity key; ADR-018 runtime) | RD-7 |
| Error and edge-case coverage | 82 error codes all defined; 12 edge/failure modes; edge tests 41 | error-handling-spec ER-3/ER-4 |
| Security and observability | 15 control objectives, permission matrix over all ops, 10 abuse cases; 23 metrics incl. zero-tripwires; log prohibition list | security-spec; observability-spec |

### RD-7 Consistency with ADRs and Stage 11 contracts
| Source | Result | Note |
|---|---|---|
| ADR-001 modular monolith | consistent | components C1-C11 reused |
| ADR-002 No-AI enforcement | consistent | BEH-CO-07, BEH-INT-09, AC-CO-11/12 |
| ADR-003 coexistence | consistent | read-only adapters, deviation register, no dual-write |
| ADR-004 event store | consistent | insert-only triggers, projection rebuild; added per-case hash chain |
| ADR-005 audit chain | consistent | anchor outside DB; tail truncation residual risk added |
| ADR-006 gate modes | consistent | none/event/external_ref; default none; added `disposition.values` and pack_hash (proposals) |
| ADR-007 policy/rule | consistent | no adopted default; three named sets |
| ADR-008 intake | **one divergence** | identity key replaced (OD-S12-17); contract validation made per-source binding (OD-S12-11) |
| ADR-009 crosswalk | consistent | exact key only |
| ADR-010 runs | consistent | schedule disabled by default |
| ADR-011 metrics | consistent | tags, decimal, no fan-out |
| ADR-012 search | consistent | FTS5 R2, fallback |
| ADR-013 authn/authz | consistent | six roles, PBKDF2, deny by default |
| ADR-014 API/UI | consistent | stdlib HTTP, CSRF, escaping |
| ADR-015 topology | consistent | loopback, single host |
| ADR-016 observability | consistent | logs, run records, metrics tables |
| ADR-017 buy vs build | not evaluated | still OPD-10 |
| ADR-018 runtime | **one divergence** | Python floor 3.10 per pyproject (OD-S12-12) |
| DC-01, DC-02, DC-04..DC-16 | consistent | DC-02 unit set closed (RF-5); DC-10 actor_kind kept; DC-12/13/15/16 realised in DDL |
| DC-03 re-delivery rule | **amended proposal** | natural key (RF-1); Stage 11 not edited |
| DQ-01..DQ-24 | realised | reason codes, invariants, tags |

### RD-8 Completion Gate evaluation
| Gate condition | Result | Evidence |
|---|---|---|
| Every feature has a spec with testable acceptance criteria | Met | 10 feature files; 241 criteria |
| No material ambiguity left unmarked | Met (with residual risk) | RD-3 register + A-12/U-12 registers below; residual: conventions in RF-10 |
| Consistent with ADRs and data contracts | Met with two recorded divergences | RD-7 |
| All required artifacts exist at the paths above | Met | 13 required artifacts + `features/` (10) + `contracts/` |
| Critical gaps resolved or explicitly documented | Met | RD-3/RD-4 |
| Evidence supports the stage conclusion | Met | evidence references per artifact; read-only queries cited |
**Result: CONDITIONAL PASS.** Non-blocking conditions C1-C4 (owner Engagement lead (Dinesh Naik)): C1 decide or accept-open OD-S12-03, 11, 12, 15, 16, 17, 19 before Stage 15 (due: before Stage 15 build begins; risk if late: rework of F01/F04 schema); C2 decide OD-S12-05/06 before any Zone H pilot (risk: gate unusable); C3 record preserve-vs-fix for DV-01..DV-09 before Stage 15 (risk: pinning known-wrong numbers or breaking goldens); C4 approve (or amend) the PRD, ADRs and NFR targets (OD-S12-14) before Stage 17 (risk: specs treated as agreed policy).

### RD-9 Consolidated assumption register (38)
| ID | Assumption (abridged) | Where |
|---|---|---|
| A-12-01 | Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik). | acceptance-criteria.md |
| A-12-02 | The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04). | acceptance-criteria.md |
| A-12-ACC-1 | The coverage check proves each ID is referenced by a criterion, not that the criterion is sufficient; Stage 13/14 test design and Stage 26 TEVV judge sufficiency. | acceptance-criteria.md |
| A-12-API-1 | Port 8081, ULID-like ids and the 128-char idempotency key limit are conventions chosen here. | api-contracts.md |
| A-12-API-2 | The case-creation entry path is not specified: R1 brings cases in by backfill (CASE_IMPORTED); a creation operation is not defined because no workflow exists in the repo or PRD (OD-S12-19). | api-contracts.md |
| A-12-BR-1 | SBR-POL-08 inclusive boundary and SBR-MET-03 percentile method are conventions chosen for testability; the owner may change them as policy. | business-rules.md |
| A-12-ER-1 | HTTP code choices (423 for configuration-locked states, 501 for not-in-release) are conventions. | error-handling-spec.md |
| A-12-EV-1 | In-process synchronous consumers are sufficient at 125 cases; any broker is deferred (ADR-004 trigger conditions). | event-contracts.md |
| A-12-F01-1 | For imported legacy cases `cases.created_at` is an acceptable proxy for receipt time (no real receipt timestamp exists; OD-07). Confirm: Engagement lead (Dinesh Naik). | features/f01-decision-evidence-record.md |
| A-12-F01-2 | Role tags closing_label/reopened on legacy labels CLOSED/REOPENED are a spec convenience, not a definition of 'closed' (OD-S12-01). | features/f01-decision-evidence-record.md |
| A-12-F02-1 | Step-up re-authentication with a 300 s window and pack_hash acknowledgement are spec proposals, not PRD requirements. Confirm: Engagement lead (Dinesh Naik). | features/f02-human-disposition-gate.md |
| A-12-F02-2 | Single dispositioner role covers all Zone H actions; separate adoption authority is an option under OPD-06. | features/f02-human-disposition-gate.md |
| A-12-F03-1 | The normalised output key `amount_over_limit` is a spec convenience for divergence reporting only; it does not assert that the three rules are meant to agree. Confirm: Engagement lead (Dinesh Naik). | features/f03-policy-definitions-rule-service.md |
| A-12-F03-2 | Domain lists for UNKNOWN_INPUT_VALUE (status vocabulary, severity LOW/MEDIUM/HIGH/CRITICAL, regions AMER/APAC/EMEA in cases) are taken from the shipped data; real domains are unknown. | features/f03-policy-definitions-rule-service.md |
| A-12-F04-1 | Legacy `ingest_ts` is an acceptable proxy for receipt_time in backfill. Confirm: Engagement lead (Dinesh Naik). | features/f04-safe-intake-exceptions.md |
| A-12-F04-2 | Closed unit and currency sets are the observed sets (synthetic); real sets unknown. | features/f04-safe-intake-exceptions.md |
| A-12-F04-3 | Natural key (partner, record_kind, ref_id, source_ts) is the right item identity; supported only by the 67 replay pairs (OD-S12-17). | features/f04-safe-intake-exceptions.md |
| A-12-F05-1 | LT-03 (lab_result->batch) resolves for all rows; counts not re-verified in this stage. Confirm at Stage 14. | features/f05-identity-crosswalk.md |
| A-12-F05-2 | Depth cap 4 / size cap 500 for the joined view are spec proposals. | features/f05-identity-crosswalk.md |
| A-12-F06-1 | Default heartbeat staleness (15 min) and the role set for manual trigger are spec proposals. | features/f06-scheduled-runs.md |
| A-12-F07-1 | Median/p90 methods (mean-of-middle; nearest-rank) are spec choices; no owner defined a method. Confirm: Engagement lead (Dinesh Naik). | features/f07-metrics-definition-tags.md |
| A-12-F07-2 | 'Unresolved-exception rate' is defined here as open exception-queue items / all exception-queue items per matched-case site; the PRD gives no formula. | features/f07-metrics-definition-tags.md |
| A-12-F07-3 | Age buckets copied from the Stage 4 sheet (<=90, 91-365, 366-730, >730). | features/f07-metrics-definition-tags.md |
| A-12-F08-1 | Query grammar, length limits (200 chars/12 terms) and page clamp (100, mirroring the legacy API clamp) are spec choices. | features/f08-reviewer-support.md |
| A-12-F08-2 | Mapping of document access_level values to roles (A-11-09) is unconfirmed; deny by default when unmapped. | features/f08-reviewer-support.md |
| A-12-F09-1 | PBKDF2 iterations (>= 600,000), lockout (5/15/15), session timeouts (30 min idle, 8 h absolute), password length 12, CSP and body limit are spec proposals; no organisational policy exists. Confirm in Stage 24. | features/f09-access-audit-protection.md |
| A-12-F09-2 | Role set derived from documentary personas (A-09-06). | features/f09-access-audit-protection.md |
| A-12-F10-1 | DV-01..DV-09 are the complete set of intended deviations known at Stage 12; Stage 14/15 may add more. Each needs HAR-06 approval. | features/f10-coexistence-change-safety.md |
| A-12-F10-2 | Deny-list contents are heuristic (ADR-002). | features/f10-coexistence-change-safety.md |
| A-12-IF-1 | Rule sets are transcribed as data (not imported from legacy modules) so rule 3 holds; equality is proven by goldens CT-01..03, CT-13. | interface-contracts.md |
| A-12-IF-2 | Exit codes and env var names are proposals. | interface-contracts.md |
| A-12-NFR-1 | The capacity envelope is a set of test fixtures, not a commitment; real volumes are unknown (OD-04). | nfr-spec.md |
| A-12-OBS-1 | Latency percentiles computed from stored samples are adequate at 125 cases. | observability-spec.md |
| A-12-SCH-1 | Closed unit/currency/object_type sets are the synthetic observed sets; real feeds may differ (flag-class codes, not rejection). | schema-specifications.md |
| A-12-SCH-2 | `actor_kind` for service principals in decision events is `system`, preserving DC-10's three-value enum. | schema-specifications.md |
| A-12-SEC-1 | Role capabilities are derived from documentary personas, not observed users (A-09-06). | security-spec.md |
| A-12-SEC-2 | Control parameter values (timeouts, lockout) are proposals for Stage 24 to confirm. | security-spec.md |
| A-12-SYS-1 | The R1/R2 split (43/9) is the Stage 9 proposal (A-09-02). The orchestrator brief quoted 41/11; the Stage 9 register parses to 43 R1 and 9 R2 (40 Must + 3 Should in R1; 7 Should + 2 Could in R2). The register is used. | system-spec.md |

### RD-10 Consolidated unknown register (38)
| ID | Unknown (abridged) | Where |
|---|---|---|
| U-12-01 | Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik). | acceptance-criteria.md |
| U-12-ACC-1 | Mutation-kill power of the future suite (shipped suite kills 1 of 15 mutants). | acceptance-criteria.md |
| U-12-API-1 | Consumers of the legacy API are unknown (TD register), so v2 cannot be validated against real clients. | api-contracts.md |
| U-12-BR-1 | Real business rules for closure, approval and evidence sufficiency do not exist in the repo (RC-3, RC-4). | business-rules.md |
| U-12-ER-1 | Real lock-contention behaviour under concurrent writers (CT-17) is Unknown. | error-handling-spec.md |
| U-12-EV-1 | Whether any downstream system needs outbound events (none identified; Teams integration is a separate memory-listed plan, not in the PRD). | event-contracts.md |
| U-12-F01-1 | Who records FACT_OPS_CLOSED / FACT_EVIDENCE_COMPLETE in real operation (human vs rule) - OD-S12-15. | features/f01-decision-evidence-record.md |
| U-12-F01-2 | Legal transition table between case states - none exists in repo (OD-S12-16). | features/f01-decision-evidence-record.md |
| U-12-F02-1 | Where the real decision of record lives (OPD-05). | features/f02-human-disposition-gate.md |
| U-12-F02-2 | Allowed disposition values (`disposition.values`) - none in repo; contracts archive names only rule `batch_disposition` and approval roles. | features/f02-human-disposition-gate.md |
| U-12-F02-3 | Whether four-eyes/dual control is required - not stated anywhere. | features/f02-human-disposition-gate.md |
| U-12-F03-1 | Which of the three rules (if any) is correct (OPD-04). | features/f03-policy-definitions-rule-service.md |
| U-12-F03-2 | Business calendar for 'business_calendar' clocks - none exists. | features/f03-policy-definitions-rule-service.md |
| U-12-F03-3 | Whether 48 h is the right duration (OPD-02). | features/f03-policy-definitions-rule-service.md |
| U-12-F04-1 | Whether real partners ever send corrected replays (none in shipped data). | features/f04-safe-intake-exceptions.md |
| U-12-F04-2 | Human capacity for quarantine queues (volume unknown). | features/f04-safe-intake-exceptions.md |
| U-12-F04-3 | Intended scope of source-contract-v1.json (OD-S12-11). | features/f04-safe-intake-exceptions.md |
| U-12-F05-1 | Whether a real key between cases and batch/deviation/CAPA exists in the source systems (none in repo). | features/f05-identity-crosswalk.md |
| U-12-F05-2 | Identifier patterns for deviation and CAPA ids not enumerated here. | features/f05-identity-crosswalk.md |
| U-12-F06-1 | Production schedule, time zone and business calendar (none in repo). | features/f06-scheduled-runs.md |
| U-12-F06-2 | Real data volumes per run (OD-04). | features/f06-scheduled-runs.md |
| U-12-F07-1 | Month-end cut-off and denominator (OPD-08). | features/f07-metrics-definition-tags.md |
| U-12-F07-2 | Cost input and owner (OPD-08); no benefit is quantified here. | features/f07-metrics-definition-tags.md |
| U-12-F08-1 | Whether any user wants document search at all (U-S01) and whether the real corpus defeats keyword search (RQ-1..RQ-3). | features/f08-reviewer-support.md |
| U-12-F08-2 | Latency target (OPD-14). | features/f08-reviewer-support.md |
| U-12-F09-1 | Identity provider / SSO (none exists). | features/f09-access-audit-protection.md |
| U-12-F09-2 | Audit anchor location for any real deployment (ADR-005). | features/f09-access-audit-protection.md |
| U-12-F09-3 | Who administers users and holder lists (OD-S12-06). | features/f09-access-audit-protection.md |
| U-12-F10-1 | Owner and nature of the parallel workflow for older customers (OPD-15). | features/f10-coexistence-change-safety.md |
| U-12-F10-2 | Whether the mutation-kill gate required by ADR-003 (R-1) can be met before cut-over. | features/f10-coexistence-change-safety.md |
| U-12-IF-1 | Java/JDK availability for CT-11 cross-language goldens in CI (Docker/JDK absent on the device per Stage 7). | interface-contracts.md |
| U-12-NFR-1 | Real availability needs, business calendar and time zone, latency expectations (OPD-14), 'risk signal' definition for PNFR-04. | nfr-spec.md |
| U-12-OBS-1 | Log retention and monitoring platform (none exists; Stage 31). | observability-spec.md |
| U-12-OBS-2 | Site time zone for the 06:00 completion metric. | observability-spec.md |
| U-12-SCH-1 | Whether the target store will be SQLite (ADR-004 option B) or PostgreSQL; the DDL is SQLite-dialect and the schemas are store-neutral. | schema-specifications.md |
| U-12-SEC-1 | Real identity provider and user population. | security-spec.md |
| U-12-SEC-2 | Whether real data would add direct identifiers (X-2). | security-spec.md |
| U-12-SYS-1 | Target deployment host, scheduler and operator roles are unknown. | system-spec.md |

### RD-11 Recommended next action
Proceed to **Stage 13** (requirements -> specs -> tests -> evidence traceability) using `acceptance-criteria.md` ACC-4/5/6 as the join tables, and raise a **Stage 11 v0.2 addendum** for DC-03 (identity key) and the DQ-04 scope note. Ask Dinesh for the C1-C4 decisions in one batch.

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-RD-1 'Due' dates are stage-relative because the engagement has no calendar; Dinesh Naik is the only human.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-RD-1 Whether Dinesh will decide or record 'accepted open' for the listed items; accepted-open is a legitimate outcome (BR-02, SUC-11).

## Unresolved Issues
- See RD-3 (19 decisions) and conditions C1-C4 in RD-8.

## Residual Risks
- Reader may treat CONDITIONAL PASS as approval of the PRD/ADRs; it is not (OD-S12-14).
- Conventions chosen for testability (RF-10) may be cited as policy.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
