---
stage: "12 — Spec-Driven Design"
artifact: "acceptance-criteria.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/features/*.md", "docs/12-specs/observability-spec.md", "docs/12-specs/nfr-spec.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Consolidated acceptance criteria: 241 Given/When/Then criteria (95 positive, 105 negative, 41 edge) across 10 feature specs, observability and NFRs; computed coverage of all 52 FRs, 20 PNFRs and 108 behaviours; honest list of criteria that cannot be fully verified today.

## Findings
### ACC-1 Conventions
- Format: **Given / When / Then**, one criterion per row, ID `AC-<FEATURE>-nn`; `Implements` lists the FR-/PNFR-/BR-/SBR-/BEH- IDs the criterion verifies. The feature files (`features/*.md`), `observability-spec.md` and `nfr-spec.md` are the **source**; this file is a generated consolidation so Stage 13 can build the traceability matrix from one table. If the two ever differ, the source file wins and this file is regenerated.
- Kind: **positive** (expected behaviour), **negative** (refusal/abuse/forbidden), **edge** (boundary, conflict, missing data).
- Execution rule (OD-03a): every executable criterion runs only in a full repository copy outside the working tree against a copy of `data/`; the baseline manifest is verified afterwards (AC-CO-07). Fixtures use explicitly configured **test policies**, never an adopted real one (FF-3).
- A criterion is *verifiable now* when it needs no open decision; criteria that depend on a decision test **both modes** and are marked in spec-readiness.md.

### ACC-2 Counts
| Feature | Prefix | Total | Positive | Negative | Edge |
|---|---|---|---|---|---|
| F01 | DEC | 28 | 8 | 13 | 7 |
| F02 | GATE | 22 | 7 | 13 | 2 |
| F03 | POL | 25 | 14 | 7 | 4 |
| F04 | INT | 29 | 11 | 11 | 7 |
| F05 | ID | 17 | 5 | 9 | 3 |
| F06 | RUN | 15 | 5 | 7 | 3 |
| F07 | MET | 21 | 8 | 9 | 4 |
| F08 | REV | 19 | 8 | 7 | 4 |
| F09 | SEC | 21 | 4 | 14 | 3 |
| F10 | CO | 15 | 6 | 8 | 1 |
| OBS | OBS | 9 | 6 | 2 | 1 |
| NFR | NFR | 20 | 13 | 5 | 2 |
| **All** | | **241** | **95** | **105** | **41** |

### ACC-3 Requirement coverage check [Verified Fact: computed by script from the tables below]
- 52 of 52 functional requirements have >= 1 criterion; 20 of 20 PNFRs have >= 1 criterion; 108 of 108 behaviours (BEH-) map to >= 1 criterion; 0 duplicate AC IDs; every AC referenced in the behaviour map exists.
- Negative-test weight: 105 of 241 criteria are negative (forbidden-path) tests, reflecting the safety-first nature of the PRD.

### ACC-4 FR -> acceptance criteria (for Stage 13)
| FR | MoSCoW | Release | Acceptance criteria |
|---|---|---|---|
| FR-DEC-01 | Must | R1 | AC-DEC-01, AC-DEC-02, AC-DEC-03, AC-DEC-04, AC-DEC-22, AC-GATE-05 |
| FR-DEC-02 | Must | R1 | AC-DEC-05, AC-DEC-06, AC-DEC-07, AC-DEC-08 |
| FR-DEC-03 | Must | R1 | AC-DEC-09, AC-DEC-10, AC-DEC-11 |
| FR-DEC-04 | Must | R1 | AC-DEC-12, AC-DEC-13, AC-DEC-14 |
| FR-DEC-05 | Must | R1 | AC-DEC-15, AC-DEC-16, AC-DEC-17, AC-DEC-18, AC-DEC-19, AC-DEC-27, AC-DEC-28 |
| FR-DEC-06 | Must | R1 | AC-DEC-20, AC-DEC-21 |
| FR-GATE-01 | Must | R1 | AC-GATE-09, AC-GATE-11, AC-GATE-12, AC-GATE-13, AC-GATE-14, AC-GATE-21, AC-INT-24, AC-RUN-12 |
| FR-GATE-02 | Must | R1 | AC-GATE-15, AC-GATE-16 |
| FR-GATE-03 | Must | R1 | AC-DEC-17, AC-DEC-18, AC-GATE-09, AC-GATE-12, AC-POL-02, AC-POL-18, AC-RUN-03, AC-SEC-08, AC-OBS-06 |
| FR-GATE-04 | Must | R1 | AC-GATE-01, AC-GATE-02, AC-GATE-22 |
| FR-GATE-05 | Must | R1 | AC-GATE-01, AC-GATE-03, AC-GATE-05, AC-GATE-06, AC-GATE-07, AC-GATE-08 |
| FR-GATE-06 | Must | R1 | AC-GATE-18, AC-GATE-19, AC-GATE-20, AC-REV-08 |
| FR-POL-01 | Must | R1 | AC-DEC-21, AC-POL-01, AC-POL-02, AC-POL-03, AC-POL-05, AC-POL-25 |
| FR-POL-02 | Must | R1 | AC-POL-01, AC-POL-06, AC-POL-07, AC-POL-08 |
| FR-POL-03 | Must | R1 | AC-GATE-08, AC-POL-03, AC-POL-09, AC-POL-10, AC-POL-25 |
| FR-POL-04 | Must | R1 | AC-POL-11, AC-POL-12, AC-POL-13, AC-POL-14, AC-POL-15, AC-POL-16, AC-POL-17, AC-POL-18, AC-CO-03 |
| FR-POL-05 | Should | R2 | AC-POL-24 |
| FR-POL-06 | Must | R1 | AC-POL-19, AC-POL-20, AC-POL-21, AC-REV-06 |
| FR-INT-01 | Must | R1 | AC-INT-01, AC-INT-02, AC-INT-03, AC-INT-29 |
| FR-INT-02 | Must | R1 | AC-INT-04, AC-INT-05, AC-INT-06, AC-OBS-09 |
| FR-INT-03 | Must | R1 | AC-INT-07, AC-INT-08 |
| FR-INT-04 | Must | R1 | AC-INT-09, AC-INT-10, AC-INT-11, AC-INT-12, AC-INT-13, AC-INT-14, AC-INT-16, AC-INT-25, AC-INT-26, AC-INT-27 |
| FR-INT-05 | Must | R1 | AC-INT-11, AC-INT-17, AC-INT-18, AC-INT-19 |
| FR-INT-06 | Must | R1 | AC-INT-15, AC-INT-20, AC-INT-21 |
| FR-INT-07 | Must | R1 | AC-GATE-13, AC-INT-22, AC-INT-23, AC-INT-24 |
| FR-INT-08 | Should | R2 | AC-INT-28 |
| FR-ID-01 | Must | R1 | AC-ID-01, AC-ID-02, AC-ID-06, AC-ID-09, AC-ID-10, AC-ID-11, AC-ID-12 |
| FR-ID-02 | Must | R1 | AC-ID-02, AC-ID-03, AC-ID-04, AC-ID-05, AC-ID-06, AC-ID-07, AC-ID-08 |
| FR-ID-03 | Should | R2 | AC-ID-15, AC-ID-16 |
| FR-ID-04 | Should | R2 | AC-ID-13, AC-ID-14, AC-ID-17 |
| FR-RUN-01 | Must | R1 | AC-RUN-01, AC-RUN-02, AC-RUN-03, AC-RUN-04 |
| FR-RUN-02 | Must | R1 | AC-INT-26, AC-RUN-05, AC-RUN-06, AC-RUN-13, AC-OBS-02 |
| FR-RUN-03 | Must | R1 | AC-RUN-07, AC-RUN-08, AC-RUN-09, AC-RUN-10 |
| FR-MET-01 | Must | R1 | AC-MET-01, AC-MET-02 |
| FR-MET-02 | Must | R1 | AC-MET-03, AC-MET-04, AC-MET-05 |
| FR-MET-03 | Must | R1 | AC-MET-06, AC-MET-07, AC-MET-08 |
| FR-MET-04 | Must | R1 | AC-INT-27, AC-MET-09, AC-MET-10, AC-MET-11, AC-MET-12, AC-MET-13 |
| FR-MET-05 | Should | R1 | AC-MET-17, AC-MET-18 |
| FR-MET-06 | Must | R1 | AC-MET-14, AC-MET-15 |
| FR-MET-07 | Should | R2 | AC-MET-19 |
| FR-MET-08 | Could | R2 | AC-MET-20 |
| FR-REV-01 | Should | R1 | AC-REV-05, AC-REV-06, AC-REV-07, AC-REV-08 |
| FR-REV-02 | Must | R1 | AC-REV-01, AC-REV-02, AC-REV-03, AC-REV-04 |
| FR-REV-03 | Should | R2 | AC-REV-09, AC-REV-10, AC-REV-11, AC-REV-12, AC-REV-13, AC-REV-14, AC-REV-15, AC-REV-17 |
| FR-REV-04 | Could | R2 | AC-REV-18 |
| FR-SEC-01 | Must | R1 | AC-DEC-13, AC-ID-08, AC-SEC-01, AC-SEC-02, AC-SEC-03, AC-SEC-04, AC-SEC-05, AC-SEC-07, AC-SEC-08 |
| FR-SEC-02 | Must | R1 | AC-DEC-24, AC-GATE-22, AC-SEC-03, AC-SEC-09, AC-SEC-10, AC-SEC-11, AC-SEC-12, AC-SEC-13, AC-SEC-14, AC-SEC-21 |
| FR-SEC-03 | Should | R2 | AC-ID-17, AC-REV-12, AC-SEC-19, AC-SEC-20 |
| FR-CO-01 | Must | R1 | AC-POL-12, AC-POL-13, AC-POL-14, AC-POL-20, AC-CO-01, AC-CO-02, AC-CO-03, AC-CO-04, AC-CO-05, AC-CO-07 |
| FR-CO-02 | Must | R1 | AC-CO-08 |
| FR-CO-03 | Should | R1 | AC-CO-09, AC-CO-10, AC-CO-15 |
| FR-CO-04 | Must | R1 | AC-REV-07, AC-REV-17, AC-CO-11, AC-CO-12 |

### ACC-5 PNFR -> acceptance criteria
| PNFR | Acceptance criteria |
|---|---|
| PNFR-01 | AC-NFR-01 |
| PNFR-02 | AC-NFR-02 |
| PNFR-03 | AC-NFR-03 |
| PNFR-04 | AC-NFR-04 |
| PNFR-05 | AC-NFR-05 |
| PNFR-06 | AC-REV-19, AC-OBS-05, AC-NFR-06 |
| PNFR-07 | AC-SEC-01, AC-SEC-06, AC-SEC-17, AC-NFR-07 |
| PNFR-08 | AC-INT-25, AC-SEC-06, AC-SEC-15, AC-SEC-16, AC-SEC-18, AC-OBS-04, AC-NFR-08 |
| PNFR-09 | AC-SEC-10, AC-SEC-11, AC-NFR-09 |
| PNFR-10 | AC-DEC-03, AC-SEC-18, AC-NFR-10 |
| PNFR-11 | AC-DEC-22, AC-DEC-23, AC-INT-04, AC-OBS-09, AC-NFR-11 |
| PNFR-12 | AC-SEC-19, AC-NFR-12 |
| PNFR-13 | AC-DEC-25, AC-INT-22, AC-REV-04, AC-REV-10, AC-NFR-13 |
| PNFR-14 | AC-RUN-05, AC-RUN-15, AC-OBS-01, AC-OBS-02, AC-OBS-03, AC-OBS-08, AC-NFR-14 |
| PNFR-15 | AC-GATE-20, AC-NFR-15 |
| PNFR-16 | AC-MET-14, AC-OBS-08, AC-NFR-16 |
| PNFR-17 | AC-DEC-05, AC-GATE-15, AC-POL-22, AC-INT-20, AC-MET-21, AC-REV-14, AC-CO-13, AC-NFR-17 |
| PNFR-18 | AC-CO-11, AC-CO-12, AC-OBS-06, AC-NFR-18 |
| PNFR-19 | AC-CO-09, AC-CO-15, AC-NFR-19 |
| PNFR-20 | AC-MET-02, AC-MET-08, AC-NFR-20 |

### ACC-6 Behaviour -> acceptance criteria
| Behaviour | Acceptance criteria |
|---|---|
| BEH-DEC-01 | AC-DEC-01, AC-DEC-02, AC-DEC-03, AC-DEC-04 |
| BEH-DEC-02 | AC-DEC-05, AC-DEC-07 |
| BEH-DEC-03 | AC-DEC-05 |
| BEH-DEC-04 | AC-DEC-06, AC-DEC-08 |
| BEH-DEC-05 | AC-DEC-09, AC-DEC-10, AC-DEC-11 |
| BEH-DEC-06 | AC-DEC-12, AC-DEC-13, AC-DEC-14 |
| BEH-DEC-07 | AC-DEC-15, AC-DEC-16, AC-DEC-17, AC-DEC-18, AC-DEC-19, AC-DEC-27, AC-DEC-28 |
| BEH-DEC-08 | AC-DEC-20, AC-DEC-21 |
| BEH-DEC-09 | AC-DEC-22, AC-DEC-23 |
| BEH-DEC-10 | AC-DEC-26 |
| BEH-DEC-11 | AC-DEC-24 |
| BEH-DEC-12 | AC-DEC-25 |
| BEH-GATE-01 | AC-GATE-09, AC-GATE-10, AC-GATE-12, AC-GATE-21 |
| BEH-GATE-02 | AC-GATE-11, AC-GATE-13, AC-GATE-14 |
| BEH-GATE-03 | AC-GATE-15, AC-GATE-16 |
| BEH-GATE-04 | AC-GATE-17 |
| BEH-GATE-05 | AC-GATE-01, AC-GATE-02, AC-GATE-22 |
| BEH-GATE-06 | AC-GATE-03, AC-GATE-04, AC-GATE-05, AC-GATE-06, AC-GATE-07, AC-GATE-08 |
| BEH-GATE-07 | AC-GATE-09 |
| BEH-GATE-08 | AC-GATE-18, AC-GATE-19, AC-GATE-20 |
| BEH-GATE-09 | AC-GATE-01 |
| BEH-POL-01 | AC-POL-01, AC-POL-25 |
| BEH-POL-02 | AC-POL-01, AC-POL-06 |
| BEH-POL-03 | AC-POL-02, AC-POL-03, AC-POL-04, AC-POL-05 |
| BEH-POL-04 | AC-POL-06, AC-POL-07, AC-POL-08 |
| BEH-POL-05 | AC-POL-09, AC-POL-10 |
| BEH-POL-06 | AC-POL-12, AC-POL-22 |
| BEH-POL-07 | AC-POL-11, AC-POL-12, AC-POL-13, AC-POL-14 |
| BEH-POL-08 | AC-POL-16, AC-POL-17, AC-POL-18 |
| BEH-POL-09 | AC-POL-19, AC-POL-20, AC-POL-21 |
| BEH-POL-10 | AC-POL-24 |
| BEH-POL-11 | AC-POL-23 |
| BEH-INT-01 | AC-INT-01, AC-INT-02, AC-INT-03, AC-INT-29 |
| BEH-INT-02 | AC-INT-05, AC-INT-06, AC-INT-07 |
| BEH-INT-03 | AC-INT-04, AC-INT-05 |
| BEH-INT-04 | AC-INT-07, AC-INT-08 |
| BEH-INT-05 | AC-INT-09, AC-INT-10, AC-INT-11, AC-INT-15, AC-INT-16 |
| BEH-INT-06 | AC-INT-12, AC-INT-13, AC-INT-14 |
| BEH-INT-07 | AC-INT-20, AC-INT-21 |
| BEH-INT-08 | AC-INT-17, AC-INT-18, AC-INT-19 |
| BEH-INT-09 | AC-INT-22, AC-INT-23, AC-INT-24 |
| BEH-INT-10 | AC-INT-29 |
| BEH-INT-11 | AC-INT-25, AC-INT-26, AC-INT-27 |
| BEH-INT-12 | AC-INT-28 |
| BEH-ID-01 | AC-ID-01, AC-ID-02, AC-ID-09, AC-ID-10, AC-ID-11 |
| BEH-ID-02 | AC-ID-03, AC-ID-04, AC-ID-05 |
| BEH-ID-03 | AC-ID-02, AC-ID-03 |
| BEH-ID-04 | AC-ID-06, AC-ID-07, AC-ID-08, AC-ID-09, AC-ID-10 |
| BEH-ID-05 | AC-ID-12 |
| BEH-ID-06 | AC-ID-13, AC-ID-14, AC-ID-17 |
| BEH-ID-07 | AC-ID-15, AC-ID-16 |
| BEH-ID-08 | AC-ID-15 |
| BEH-RUN-01 | AC-RUN-04 |
| BEH-RUN-02 | AC-RUN-01, AC-RUN-02, AC-RUN-03 |
| BEH-RUN-03 | AC-RUN-05 |
| BEH-RUN-04 | AC-RUN-06 |
| BEH-RUN-05 | AC-RUN-08, AC-RUN-09, AC-RUN-10, AC-RUN-14 |
| BEH-RUN-06 | AC-RUN-11 |
| BEH-RUN-07 | AC-RUN-07 |
| BEH-RUN-08 | AC-RUN-15 |
| BEH-RUN-09 | AC-NFR-02 |
| BEH-MET-01 | AC-MET-01, AC-MET-15 |
| BEH-MET-02 | AC-MET-02 |
| BEH-MET-03 | AC-MET-03, AC-MET-04, AC-MET-05 |
| BEH-MET-04 | AC-MET-06, AC-MET-07, AC-MET-08 |
| BEH-MET-05 | AC-MET-09, AC-MET-10, AC-MET-11, AC-MET-13 |
| BEH-MET-06 | AC-MET-12 |
| BEH-MET-07 | AC-MET-14 |
| BEH-MET-08 | AC-MET-17, AC-MET-18 |
| BEH-MET-09 | AC-MET-16 |
| BEH-MET-10 | AC-MET-19 |
| BEH-MET-11 | AC-MET-20 |
| BEH-REV-01 | AC-REV-01, AC-REV-02, AC-REV-03, AC-REV-04 |
| BEH-REV-02 | AC-REV-05, AC-REV-06, AC-REV-07, AC-REV-08 |
| BEH-REV-03 | AC-REV-09, AC-REV-10, AC-REV-11 |
| BEH-REV-04 | AC-REV-12, AC-REV-13, AC-REV-14 |
| BEH-REV-05 | AC-REV-10, AC-REV-17 |
| BEH-REV-06 | AC-REV-16 |
| BEH-REV-07 | AC-REV-18 |
| BEH-REV-08 | AC-REV-19 |
| BEH-SEC-01 | AC-SEC-01, AC-SEC-02 |
| BEH-SEC-02 | AC-SEC-04, AC-SEC-05, AC-SEC-06, AC-SEC-07 |
| BEH-SEC-03 | AC-SEC-08 |
| BEH-SEC-04 | AC-SEC-03 |
| BEH-SEC-05 | AC-SEC-09, AC-SEC-13, AC-SEC-14 |
| BEH-SEC-06 | AC-SEC-10, AC-SEC-11, AC-SEC-12 |
| BEH-SEC-07 | AC-SEC-15, AC-SEC-18 |
| BEH-SEC-08 | AC-SEC-16 |
| BEH-SEC-09 | AC-SEC-17 |
| BEH-SEC-10 | AC-SEC-19, AC-SEC-20 |
| BEH-SEC-11 | AC-SEC-18 |
| BEH-CO-01 | AC-CO-01, AC-CO-02, AC-CO-03 |
| BEH-CO-02 | AC-CO-01 |
| BEH-CO-03 | AC-CO-04, AC-CO-05 |
| BEH-CO-04 | AC-CO-06, AC-CO-07 |
| BEH-CO-05 | AC-CO-08 |
| BEH-CO-06 | AC-CO-09, AC-CO-10 |
| BEH-CO-07 | AC-CO-11, AC-CO-12 |
| BEH-CO-08 | AC-CO-13 |
| BEH-CO-09 | AC-CO-14 |
| BEH-OBS-01 | AC-OBS-01 |
| BEH-OBS-02 | AC-OBS-02, AC-OBS-03 |
| BEH-OBS-03 | AC-OBS-07 |
| BEH-OBS-04 | AC-OBS-05 |
| BEH-OBS-05 | AC-OBS-08 |
| BEH-OBS-06 | AC-OBS-06 |
| BEH-OBS-07 | AC-NFR-10 |
| BEH-OBS-08 | AC-OBS-02 |

### ACC-7 Full register (241 criteria)
| ID | Given | When | Then | Implements | Kind | Source file |
|---|---|---|---|---|---|---|
| AC-DEC-01 | a case with N=5 successful transitions | the events for the case are listed | exactly 5 state events plus the creation event exist with seq 1..6 gapless and no row was modified (row hashes unchanged between reads) | FR-DEC-01, BEH-DEC-01 | positive | f01-decision-evidence-record.md |
| AC-DEC-02 | an existing event | a raw `UPDATE decision_events SET basis='x'` is executed on the database | the statement fails with E-DEC-IMMUTABLE and the row is unchanged | FR-DEC-01 | negative | f01-decision-evidence-record.md |
| AC-DEC-03 | an existing event | a raw `DELETE FROM decision_events` is executed | the statement fails with E-DEC-IMMUTABLE | FR-DEC-01, PNFR-10 | negative | f01-decision-evidence-record.md |
| AC-DEC-04 | the service interface | its public methods are enumerated by a test | no method named or behaving as update/delete of an event exists | FR-DEC-01 | negative | f01-decision-evidence-record.md |
| AC-DEC-05 | 125 imported legacy cases and any later transitions | `verify-projection` runs | folded state equals `case_state` for 100% of cases (0 mismatches) | FR-DEC-02, PNFR-17 | positive | f01-decision-evidence-record.md |
| AC-DEC-06 | a case with events at t1<t2<t3 and states A,B,C | `state?as_of=` t2 and t2+epsilon | returns B for both; `as_of` just before t1 returns E-DEC-NOT-YET-EXISTS | FR-DEC-02 | edge | f01-decision-evidence-record.md |
| AC-DEC-07 | a case creation | the CASE_CREATED event is read after the case later moves to CLOSED | its `to_state` is the creation state and `from_state` is null | FR-DEC-02 | positive | f01-decision-evidence-record.md |
| AC-DEC-08 | a client supplies `occurred_at` in the future or earlier than the previous event | the transition is posted | request refused with E-DEC-TIME-ORDER and nothing is stored | FR-DEC-02 | negative | f01-decision-evidence-record.md |
| AC-DEC-09 | a case in CLOSED | a transition to REOPENED is posted with event_type STATUS_CHANGE | refused E-DEC-REOPEN-EXPLICIT | FR-DEC-03 | negative | f01-decision-evidence-record.md |
| AC-DEC-10 | a case in CLOSED | a REOPEN event with non-empty basis is posted | accepted, state REOPENED, cycle incremented from 1 to 2 | FR-DEC-03 | positive | f01-decision-evidence-record.md |
| AC-DEC-11 | the full event store after any test run | invariant query counts cases in REOPENED state lacking a REOPEN event, excluding legacy-imported cases carrying the `LEGACY_UNEVIDENCED_REOPEN` marker | count = 0, and the 8 marked legacy cases are listed separately (not hidden) | FR-DEC-03 | edge | f01-decision-evidence-record.md |
| AC-DEC-12 | a decision event with two evidence refs, one resolvable and one dangling | OP-DEC-04 is called by a reviewer | response contains the event, the resolved evidence with source, and the dangling one flagged `unresolvable` | FR-DEC-04 | edge | f01-decision-evidence-record.md |
| AC-DEC-13 | evidence with access level restricted and a caller without access | OP-DEC-04 is called | that evidence appears as `{ev_id, access: denied}` with no body or source text | FR-DEC-04, FR-SEC-01 | negative | f01-decision-evidence-record.md |
| AC-DEC-14 | a sample of 20 decision events | each is audited | 100% have evidence and source retrievable or an explicit exception marker | FR-DEC-04 | positive | f01-decision-evidence-record.md |
| AC-DEC-15 | a closing-state policy including CLOSED and a case with no evidence | a transition to CLOSED without exception is posted | refused E-DEC-EVIDENCE-REQUIRED | FR-DEC-05 | negative | f01-decision-evidence-record.md |
| AC-DEC-16 | the same case with one resolvable evidence ref (content irrelevant) | the transition is posted | accepted; no sufficiency judgement is made or logged | FR-DEC-05 | positive | f01-decision-evidence-record.md |
| AC-DEC-17 | a close_exception posted by a service account or by a non-holder | the transition is posted | refused E-GATE-NOT-AUTHORISED and the refusal is audited | FR-DEC-05, FR-GATE-03 | negative | f01-decision-evidence-record.md |
| AC-DEC-18 | a close_exception posted by an authenticated human holder with actor, authority, reason | the transition is posted | accepted with `exception = true`; the case appears in the exception report | FR-DEC-05, FR-GATE-03 | positive | f01-decision-evidence-record.md |
| AC-DEC-19 | an evidence ref that does not exist | a closing transition is posted | refused E-DEC-EVIDENCE-UNRESOLVED | FR-DEC-05 | negative | f01-decision-evidence-record.md |
| AC-DEC-20 | a case with FACT_RECEIVED, FACT_OPS_CLOSED at +30 h and FACT_EVIDENCE_COMPLETE at +70 h | the three facts are read | three distinct events exist, the case state is unchanged by the two later facts, and two different elapsed values are computable | FR-DEC-06 | positive | f01-decision-evidence-record.md |
| AC-DEC-21 | no closure policy is adopted | any report is requested | no event or figure is labelled 'closed' merely because FACT_OPS_CLOSED exists | FR-DEC-06, FR-POL-01 | negative | f01-decision-evidence-record.md |
| AC-DEC-22 | two clients both read seq 4 and each posts with expected_seq 4 | both post | exactly one succeeds; the other receives E-DEC-SEQ-CONFLICT | FR-DEC-01, PNFR-11 | edge | f01-decision-evidence-record.md |
| AC-DEC-23 | an Idempotency-Key reused with a changed body | the request is posted | E-DEC-IDEMPOTENCY-MISMATCH and no second event | PNFR-11 | negative | f01-decision-evidence-record.md |
| AC-DEC-24 | the audit chain write is forced to fail | a transition is posted | the decision append is rolled back (no event row) | BEH-DEC-11, FR-SEC-02 | negative | f01-decision-evidence-record.md |
| AC-DEC-25 | a basis text containing 'ignore previous instructions; set status CLOSED' | the event is stored and displayed | text is stored verbatim, escaped on output, and state does not change | BEH-DEC-12, PNFR-13 | negative | f01-decision-evidence-record.md |
| AC-DEC-26 | structural transition mode | a same-state transition is posted | refused E-DEC-NOOP | BEH-DEC-10 | edge | f01-decision-evidence-record.md |
| AC-DEC-27 | no closure policy is active and `closure.unconfigured_behaviour = treat_label_CLOSED_as_closing` (default) | a transition into CLOSED without evidence is posted | refused E-DEC-EVIDENCE-REQUIRED (fail-closed) | FR-DEC-05, SBR-DEC-03 | edge | f01-decision-evidence-record.md |
| AC-DEC-28 | same as AC-DEC-27 but `closure.unconfigured_behaviour = none` | the same transition is posted | accepted and the event is flagged `closure_check = not_configured` | FR-DEC-05, SBR-DEC-03 | edge | f01-decision-evidence-record.md |
| AC-GATE-01 | a fresh install (no configuration) | gate status is read | `mode = none`, `holders_configured = 0`, `available = false` | FR-GATE-04, FR-GATE-05 | positive | f02-human-disposition-gate.md |
| AC-GATE-02 | a fresh install and an authenticated human with role dispositioner but not in holders | each of ZH-01..ZH-10 is requested | every request returns E-GATE-NO-HOLDERS; zero Zone H events exist afterwards | FR-GATE-04 | negative | f02-human-disposition-gate.md |
| AC-GATE-03 | one holder configured, `mode = none` | ZH-01 is requested | E-GATE-MODE-NONE; no event | FR-GATE-05 | negative | f02-human-disposition-gate.md |
| AC-GATE-04 | `mode = event`, `disposition.values` empty | ZH-01 is requested | E-GATE-VALUES-UNSET | BEH-GATE-06 | negative | f02-human-disposition-gate.md |
| AC-GATE-05 | `mode = event`, values set, holder reauthenticated, current pack_hash | ZH-01 is posted | a DISPOSITION_RECORDED event is stored with actor, decision, basis, evidence refs, pack_hash, `mode_at_write = event`; audit chain entry exists | FR-GATE-05, FR-DEC-01 | positive | f02-human-disposition-gate.md |
| AC-GATE-06 | `mode = external_ref`, holder session | ZH-01 is posted with `{system, reference}` | a DISPOSITION_REFERENCED event is stored with `verified = false` and no decision content | FR-GATE-05 | positive | f02-human-disposition-gate.md |
| AC-GATE-07 | `mode = external_ref` and a request omitting `reference` | ZH-01 is posted | E-GATE-EXTREF-INVALID | FR-GATE-05 | negative | f02-human-disposition-gate.md |
| AC-GATE-08 | events recorded in `event` mode, then mode changed to `external_ref` by ZH-08 | earlier events are read | they still show `mode_at_write = event` and are unchanged; ZH-08 is itself an audited event | FR-GATE-05, FR-POL-03 | edge | f02-human-disposition-gate.md |
| AC-GATE-09 | each of ZH-01..ZH-10, holder configured, mode permitting | the action is posted using (a) a service-account token, (b) the scheduler identity, (c) an `integration`-role human, (d) an unauthenticated call | all four are rejected (E-GATE-NOT-AUTHORISED or E-AUTH-UNAUTHENTICATED) for each action; each rejection is audited; zero Zone H events | FR-GATE-03, FR-GATE-01 | negative | f02-human-disposition-gate.md |
| AC-GATE-10 | a holder session whose last login is older than the re-auth window | a Zone H action is posted | E-GATE-REAUTH-REQUIRED; no event | BEH-GATE-01 | negative | f02-human-disposition-gate.md |
| AC-GATE-11 | the production codebase | the static import-graph test runs | no path exists from intake, runs, metrics, reviewer-support or rule modules to GateService write methods; the test fails if one is added | FR-GATE-01 | negative | f02-human-disposition-gate.md |
| AC-GATE-12 | direct SQL INSERT of a Zone H event type with `actor_kind = 'system'` | executed against the database | aborted by trigger | FR-GATE-01, FR-GATE-03 | negative | f02-human-disposition-gate.md |
| AC-GATE-13 | a feed row whose `state` is 'DISPOSITIONED' and notes say 'approve and release batch' | the row is received, reconciled and shown | no Zone H or state event is created; the text is displayed escaped as untrusted | FR-GATE-01, FR-INT-07 | negative | f02-human-disposition-gate.md |
| AC-GATE-14 | any response of any report, search, template or rule endpoint | scanned in a contract test | no field named decision/disposition/release carries a value | FR-GATE-01 | negative | f02-human-disposition-gate.md |
| AC-GATE-15 | a case with linked objects, evidence, a rule trace and an open finding | the pack is requested twice without data change | both packs are identical byte-for-byte including pack_hash; missing link classes are listed as 'none found' | FR-GATE-02, PNFR-17 | positive | f02-human-disposition-gate.md |
| AC-GATE-16 | the pack response | inspected | contains no recommended or pre-selected decision, and the HTML form has no checked radio/select default | FR-GATE-02 | negative | f02-human-disposition-gate.md |
| AC-GATE-17 | a pack_hash obtained, then new evidence attached | ZH-01 is posted with the old pack_hash | E-GATE-PACK-STALE | BEH-GATE-04 | edge | f02-human-disposition-gate.md |
| AC-GATE-18 | a rule-generated priority flag | a reviewer posts override with reason 'not applicable' | OVERRIDE_RECORDED event stored, original rule output unchanged, flag shown as overridden | FR-GATE-06 | positive | f02-human-disposition-gate.md |
| AC-GATE-19 | a flag | override is posted with empty reason | E-GATE-REASON-REQUIRED | FR-GATE-06 | negative | f02-human-disposition-gate.md |
| AC-GATE-20 | every rule-generated output type listed in the output registry | an automated test iterates them | each has a `flag_id` and an accepted override/dismiss/refuse action | FR-GATE-06, PNFR-15 | positive | f02-human-disposition-gate.md |
| AC-GATE-21 | the full configuration surface | searched by a test | no setting, env var or CLI flag exists whose effect is to disable BEH-GATE-01 checks | FR-GATE-01 | negative | f02-human-disposition-gate.md |
| AC-GATE-22 | a holder-list change in configuration followed by restart | the audit chain is read | a CONFIG_LOADED entry with the new config hash exists | FR-GATE-04, FR-SEC-02 | positive | f02-human-disposition-gate.md |
| AC-POL-01 | a fresh install | all policy objects are listed | exactly three DEFINITION and two CLOCK objects exist, all `candidate`, `owner = unassigned`; count(adopted) = 0 | FR-POL-01, FR-POL-02 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-02 | a fresh install | a service-actor token requests adoption of D-OPS | rejected E-GATE-NOT-AUTHORISED and audited; status still candidate | FR-POL-01, FR-GATE-03 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-03 | a holder session | D-OPS is adopted with effective_from and authority_ref | new version status adopted, POLICY_ADOPTED event with old/new value and authority_ref stored | FR-POL-01, FR-POL-03 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-04 | D-OPS adopted for 2026 | a second adoption with overlapping window for the same tag is posted | E-POL-OVERLAP | BEH-POL-03 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-05 | a holder session | 'accepted-open' is recorded for D-FIN with reason | status accepted-open, dated event exists; a report shows the definition as accepted-open, not as adopted | FR-POL-01 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-06 | clocks C-OPS and C-EVID are candidates and two cases exist | elapsed time is requested | elapsed under both clocks is returned side by side; `verdict = not_available_no_adopted_policy`; no pass/fail anywhere | FR-POL-02 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-07 | a CLOCK created with `calendar_basis = business_calendar` and no `calendar_ref` | it is saved | E-POL-CLOCK-CALENDAR-REQUIRED | FR-POL-02 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-08 | a CLOCK adopted with duration 48 | elapsed 47.9 h and 48.1 h cases are evaluated | verdicts within / not within, boundary rule 'elapsed <= duration' is stated in the response | FR-POL-02 | edge | f03-policy-definitions-rule-service.md |
| AC-POL-09 | any policy edit or rule-row edit | it is executed with empty authority_ref | E-POL-AUTHORITY-REQUIRED; nothing stored | FR-POL-03 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-10 | a threshold edit by a holder | the policy_events are read | one event with who, when, old value, new value, authority_ref; a service actor attempting the same edit is rejected and logged | FR-POL-03 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-11 | the loader run against the shipped repo | rule sets are listed | `as-found-python`, `as-found-js`, `as-found-batch` exist with `origin = as-found`, `read_only = true`; an edit attempt returns E-POL-READONLY-SET | FR-POL-04 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-12 | `as-found-python` and the 120-row truth table of Stage 7 (`batch_golden.priority_truth_table`) | each row is evaluated with explicit ruleset_ref | all 120 outcomes equal the golden (byte-equal JSON of outcomes) | FR-POL-04, FR-CO-01 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-13 | `as-found-python` and the 20-row manual-review table | evaluated | all 20 equal golden, including CLOSED+HIGH = true | FR-POL-04, FR-CO-01 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-14 | `as-found-js` and the 32 (region, year) pairs plus tolerance cases 26250 and 26250.01 | evaluated | thresholds and allow/deny equal golden (26250 allowed, 26250.01 denied for APAC 2026 limit 25000 x 1.05) | FR-POL-04, FR-CO-01 | edge | f03-policy-definitions-rule-service.md |
| AC-POL-15 | `as-found-batch` and a fixed row set of (status, value, threshold) cases | evaluated | flags equal the row-level predicate; a test shows the rule service does not multiply rows | FR-POL-04 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-16 | no active ruleset for PRIORITY | evaluate is called without ruleset_ref | E-POL-NO-ACTIVE-RULESET | FR-POL-04 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-17 | no active ruleset | evaluate is called with explicit `as-found-python` | outcome returned with `authoritative = false` | FR-POL-04 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-18 | a holder sets `active_ruleset[PRIORITY] = as-found-python` | the pointer is read and the change audited | pointer set, RULESET_ACTIVATED event exists; a service actor attempt is rejected | FR-POL-04, FR-GATE-03 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-19 | `as-found-js`, region 'MARS', year 2026 | evaluated | limit 999999 returned with `defaulted = true`, reason NO_MATCH_REGION_YEAR; the same marker appears in the API response, pack and trace text | FR-POL-06 | edge | f03-policy-definitions-rule-service.md |
| AC-POL-20 | `as-found-python` with status 'WEIRD' | evaluated | outcome `queue` (as-found) with `defaulted = true`, reason UNKNOWN_INPUT_VALUE | FR-POL-06, FR-CO-01 | edge | f03-policy-definitions-rule-service.md |
| AC-POL-21 | a known status and severity (LOW, OPEN) falling to the final queue row | evaluated | outcome `queue`, `defaulted = false` | FR-POL-06 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-22 | the same (ruleset version, inputs) evaluated 1000 times in two processes | outputs compared | bit-identical JSON; evaluation function performs no I/O (verified by a test that runs it with file, network and clock access patched to raise) | PNFR-17, BEH-POL-06 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-23 | amount 'abc', null or NaN | evaluate is called | E-POL-INPUT-INVALID; no outcome | BEH-POL-11 | negative | f03-policy-definitions-rule-service.md |
| AC-POL-24 | R2: the 125 shipped cases and the three sets | the divergence report runs | lists cases where `amount_over_limit` differs, with traces; the count is recorded; no state change and no 'correct' set named | FR-POL-05 | positive | f03-policy-definitions-rule-service.md |
| AC-POL-25 | every policy version row | an UPDATE is attempted | rejected (immutability) | FR-POL-01, FR-POL-03 | negative | f03-policy-definitions-rule-service.md |
| AC-INT-01 | a fixture of 100 valid items | the intake job runs twice | raw_intake has 200 rows (each delivery stored), original 100 raw rows are byte-unchanged, intake_outcome holds both runs' outcomes | FR-INT-01 | positive | f04-safe-intake-exceptions.md |
| AC-INT-02 | any raw_intake row | UPDATE or DELETE is attempted | rejected E-INT-RAW-IMMUTABLE | FR-INT-01 | negative | f04-safe-intake-exceptions.md |
| AC-INT-03 | the code base | searched in a test | no statement updates a status column of an intake table and the legacy `partner_feeds` is opened only `mode=ro` | FR-INT-01 | negative | f04-safe-intake-exceptions.md |
| AC-INT-04 | 100 processed items and a queue snapshot | the same 100 are re-delivered | queue size, queue ages, per-reason counts and all totals are identical before and after; 100 `NOOP_DUPLICATE` outcomes exist with `counts_toward_totals = false` | FR-INT-02, PNFR-11 | positive | f04-safe-intake-exceptions.md |
| AC-INT-05 | the 134 shipped rows forming 67 natural-key pairs | ingested | 67 pairs are classified one original + one `NOOP_DUPLICATE` (67/67), none quarantined | FR-INT-02 | positive | f04-safe-intake-exceptions.md |
| AC-INT-06 | the shipped rows sharing a business_key but different natural keys | ingested | none is classified duplicate or revised-conflict because of the shared business_key | FR-INT-02, SBR-INT-01 | negative | f04-safe-intake-exceptions.md |
| AC-INT-07 | a synthetic corrected-replay fixture (same identity_key, changed `quantity`) | ingested | outcome QUARANTINED `REVISED_CONFLICT`, queue revision_review, both versions retrievable and linked, not marked duplicate | FR-INT-03 | positive | f04-safe-intake-exceptions.md |
| AC-INT-08 | a quarantined conflict | a reviewer resolves `accept_revision` with a reason | resolution event stored, no case state changes; a resolution without reason gives E-INT-RESOLUTION-REASON-REQUIRED | FR-INT-03 | edge | f04-safe-intake-exceptions.md |
| AC-INT-09 | the 224 `unsupported` rows | ingested | 224 outcomes with `UNSUPPORTED_REVISION` in queue quarantine_invalid; quarantine rows = 224; raw rows = 224 | FR-INT-04, DQ-02 | positive | f04-safe-intake-exceptions.md |
| AC-INT-10 | items with invalid JSON, missing envelope field, unknown record_kind and missing payload field | ingested | each lands in quarantine with INVALID_JSON, MISSING_ENVELOPE_FIELD, UNKNOWN_RECORD_KIND, MISSING_PAYLOAD_FIELD; counts of reasons equal counts of quarantine rows | FR-INT-04 | negative | f04-safe-intake-exceptions.md |
| AC-INT-11 | the 210 shipped rows without `business_key` | ingested | 210 outcomes with NO_BUSINESS_KEY, queue unmatched, none linked | FR-INT-04, FR-INT-05, DQ-01 | positive | f04-safe-intake-exceptions.md |
| AC-INT-12 | binding for partner_feed = `record_only` (default) | the shipped 8,567 rows are ingested | every outcome carries `contract_check = fail` (8,567), none is quarantined by contract alone | FR-INT-04, BEH-INT-06 | edge | f04-safe-intake-exceptions.md |
| AC-INT-13 | binding for partner_feed = `enforce` | same input | 8,567 CONTRACT_VIOLATION quarantine outcomes (100%) and no item is dropped | FR-INT-04, BEH-INT-06 | edge | f04-safe-intake-exceptions.md |
| AC-INT-14 | binding for `external-feed` source_messages = `enforce` | the 15 shipped messages are ingested | 15 `contract_check = pass`, 0 quarantined | FR-INT-04, FND-INT-3 | positive | f04-safe-intake-exceptions.md |
| AC-INT-15 | a quantity of -4.942 | validated | flag NEGATIVE_VALUE, queue flagged_value, value kept verbatim (legacy rejected it: recorded as OD-S12-13 difference) | FR-INT-06, DQ-10 | edge | f04-safe-intake-exceptions.md |
| AC-INT-16 | units 'pct' and 'percent', currency 'XXX' and 'usd' | validated | `pct` -> UNKNOWN_UNIT; `percent` clean; 'XXX' and 'usd' -> UNKNOWN_CURRENCY; raw values preserved | FR-INT-04 | edge | f04-safe-intake-exceptions.md |
| AC-INT-17 | a feed `ref_id` equal to exactly one `cases.id` | matched | one crosswalk link with creator rule and key_used | FR-INT-05 | positive | f04-safe-intake-exceptions.md |
| AC-INT-18 | a `ref_id` equal to no case | matched | UNMATCHED_REF in queue unmatched, no link | FR-INT-05 | negative | f04-safe-intake-exceptions.md |
| AC-INT-19 | a `ref_id` equal to two entities under the configured keys | matched | AMBIGUOUS_MATCH with both candidates listed, no link created, item not shown as matched | FR-INT-05 | negative | f04-safe-intake-exceptions.md |
| AC-INT-20 | 1,000 randomly ordered fixture items (fixed seed) classified twice, in different orders | outputs compared | identical primary_reason, all_reasons and queue per item | FR-INT-06, PNFR-17 | positive | f04-safe-intake-exceptions.md |
| AC-INT-21 | an item failing three checks | classified | one primary reason by SBR-INT-03 precedence, `all_reasons` has all three, exactly one queue | FR-INT-06 | edge | f04-safe-intake-exceptions.md |
| AC-INT-22 | the 86 shipped feed rows with instruction-like notes plus the 22 document bodies and 44 regex-hit fixtures | processed end to end | zero events, status changes, priority/queue changes, approvals or dispositions result from any of them (compare full store before/after except raw/outcome rows) | FR-INT-07, PNFR-13 | negative | f04-safe-intake-exceptions.md |
| AC-INT-23 | code that tries to pass an `Untrusted` value into a decision parameter | the type check and runtime guard run | static check fails the build; runtime raises E-INT-UNTRUSTED-USE | FR-INT-07 | negative | f04-safe-intake-exceptions.md |
| AC-INT-24 | payload `state = 'DISPOSITIONED'` | ingested | stored as `source_state`; case state unchanged; no gate event | FR-INT-07, FR-GATE-01 | negative | f04-safe-intake-exceptions.md |
| AC-INT-25 | the gateway URL `file:///etc/passwd` or `ftp://x` | configured | refused E-INT-URL-SCHEME-REFUSED, no read | FR-INT-04, PNFR-08 | negative | f04-safe-intake-exceptions.md |
| AC-INT-26 | an unreachable gateway | the job runs | retries up to `gateway.retries`, then run record shows error SOURCE_UNREACHABLE; no item outcome fabricated | FR-INT-04, FR-RUN-02 | edge | f04-safe-intake-exceptions.md |
| AC-INT-27 | a vendor CSV with a blank amount and a negative amount | imported | blank -> UNPARSABLE_AMOUNT quarantined (not skipped), negative -> NEGATIVE_VALUE; totals use Decimal | FR-INT-04, FR-MET-04 | negative | f04-safe-intake-exceptions.md |
| AC-INT-28 | R2: a source with late items | the delay report runs | items listed per source with delay and no manual step; future `source_ts` flagged | FR-INT-08 | positive | f04-safe-intake-exceptions.md |
| AC-INT-29 | the backfill of the 8,567 legacy rows run twice | row counts compared | raw_intake count equals 8,567 after run 1 and run 2 adds 0 new content (idempotent by hash) while legacy file checksum is unchanged | FR-INT-01, BEH-INT-10 | positive | f04-safe-intake-exceptions.md |
| AC-ID-01 | the shipped legacy data after rule matching | links of LT-01 and LT-02 are counted | 42 deviation->batch and 21 capa->deviation links exist, each with key_used, creator_kind = rule, created_at | FR-ID-01 | positive | f05-identity-crosswalk.md |
| AC-ID-02 | the 173 feed rows whose ref_id equals a case id | matched | 173 LT-04 links; 8,394 feed items remain unlinked | FR-ID-01, FR-ID-02 | positive | f05-identity-crosswalk.md |
| AC-ID-03 | an orphan fixture (feed ref_id 'C99999999') | the matcher runs 3 times with other data added | the item stays unlinked after every run | FR-ID-02 | negative | f05-identity-crosswalk.md |
| AC-ID-04 | feed ref_id 'c00000001' (case differs) and 'C0000000 1' | matched | no link is created (no case-folding/fuzzy); outcome UNMATCHED_REF | FR-ID-02 | negative | f05-identity-crosswalk.md |
| AC-ID-05 | the crosswalk module source | static check runs | no import of difflib/fuzzy/levenshtein/similarity libraries | FR-ID-02 | negative | f05-identity-crosswalk.md |
| AC-ID-06 | a reviewer links case C00000001 to batch BT00000000 with reason | OP-ID-02 is called | link stored (creator_kind human) and LINK_CREATED_HUMAN event exists with actor, time, reason | FR-ID-02, FR-ID-01 | positive | f05-identity-crosswalk.md |
| AC-ID-07 | the same request without reason | called | E-ID-REASON-REQUIRED | FR-ID-02 | negative | f05-identity-crosswalk.md |
| AC-ID-08 | a service account calls OP-ID-02 | called | rejected E-AUTH-FORBIDDEN and audited | FR-ID-02, FR-SEC-01 | negative | f05-identity-crosswalk.md |
| AC-ID-09 | an existing active link | the same link is posted again | E-ID-LINK-EXISTS | FR-ID-01 | negative | f05-identity-crosswalk.md |
| AC-ID-10 | a link between an unregistered type pair | posted | E-ID-PAIR-NOT-REGISTERED | FR-ID-01 | negative | f05-identity-crosswalk.md |
| AC-ID-11 | a link retracted with reason | the current set and history are read | link no longer active, original and LINK_RETRACTED event both present | FR-ID-01 | edge | f05-identity-crosswalk.md |
| AC-ID-12 | an id string that matches two registered patterns | lookup without id_type | E-ID-AMBIGUOUS-TYPE with candidate types, no data returned | FR-ID-01 | edge | f05-identity-crosswalk.md |
| AC-ID-13 | R2: batch BT00000000 with a deviation and CAPA | lookup by batch id, by deviation id and by capa id with view | the same linked set (3 entities) is returned each time | FR-ID-04 | positive | f05-identity-crosswalk.md |
| AC-ID-14 | R2: a view that exceeds the size cap | requested | `truncated = true` with total count, no silent cut | FR-ID-04 | edge | f05-identity-crosswalk.md |
| AC-ID-15 | R2: a configured test CONSISTENCY rule (case state X while linked batch qa_status Y) and a seeded contradictory fixture | the check runs twice | exactly one open finding, zero state changes anywhere (store diff empty except finding rows) | FR-ID-03 | positive | f05-identity-crosswalk.md |
| AC-ID-16 | R2: fresh install, no adopted CONSISTENCY policy | the check runs | zero findings and a statement 'no consistency policy adopted' | FR-ID-03 | negative | f05-identity-crosswalk.md |
| AC-ID-17 | a caller lacking access to restricted documents | joined view requested | restricted linked documents appear as `{access: denied}` and are not counted in totals revealed to the caller | FR-ID-04, FR-SEC-03 | negative | f05-identity-crosswalk.md |
| AC-RUN-01 | schedule enabled for a non-Zone-H job via ZH-09 | the scheduled trigger fires at the configured time in a test clock | a run starts, a run record exists with trigger = scheduled | FR-RUN-01 | positive | f06-scheduled-runs.md |
| AC-RUN-02 | fresh install (schedule disabled) | a scheduled trigger is attempted | E-RUN-SCHEDULE-DISABLED and a run record with outcome refused | FR-RUN-01, BEH-RUN-02 | negative | f06-scheduled-runs.md |
| AC-RUN-03 | schedule disabled | a service actor attempts ZH-09 | rejected E-GATE-NOT-AUTHORISED; schedule remains disabled | FR-RUN-01, FR-GATE-03 | negative | f06-scheduled-runs.md |
| AC-RUN-04 | an authenticated reviewer (no manual-run role) | POST /runs | E-AUTH-FORBIDDEN; with role quality_lead the run starts | FR-RUN-01 | negative | f06-scheduled-runs.md |
| AC-RUN-05 | 10 runs of mixed jobs | run records are listed | 100% of runs have a record with all fields of BEH-RUN-03 populated | FR-RUN-02, PNFR-14 | positive | f06-scheduled-runs.md |
| AC-RUN-06 | a run processing 500 items | totals compared | outcomes_by_type sums to 500 and equals the count of outcome rows with that run_id | FR-RUN-02 | positive | f06-scheduled-runs.md |
| AC-RUN-07 | a run killed mid-way (process terminated) | the next run is started | RUN_ABANDONED is written for the old run, the new run resumes, and the final store equals an uninterrupted run (row-set equality on outcomes) | FR-RUN-03, BEH-RUN-07 | edge | f06-scheduled-runs.md |
| AC-RUN-08 | a seeded backlog of 2,500 eligible items and batch_size 1,000 | three consecutive runs | run 1 reports limit_reached = true, backlog_remaining = 1,500; run 2 backlog 500; run 3 backlog 0, limit_reached false; every item processed exactly once | FR-RUN-03 | positive | f06-scheduled-runs.md |
| AC-RUN-09 | the same backlog with `--until-empty` | one run | backlog_remaining 0 at end, one record | FR-RUN-03 | positive | f06-scheduled-runs.md |
| AC-RUN-10 | the source code and config | searched by a test | no hard-coded row cap (e.g. LIMIT 1000) exists outside configuration; the cap used is printed in the run record | FR-RUN-03 | negative | f06-scheduled-runs.md |
| AC-RUN-11 | two simultaneous starts of the same job | started | exactly one runs; the other gets E-RUN-ALREADY-RUNNING | BEH-RUN-06 | negative | f06-scheduled-runs.md |
| AC-RUN-12 | any job code path | an import-graph test runs | no job module can reach GateService write methods; a job forced to call it fails with E-GATE-NOT-AUTHORISED and the run is RUN_FAILED | FR-GATE-01 | negative | f06-scheduled-runs.md |
| AC-RUN-13 | an unreachable source | the intake job runs | RUN_FINISHED with errors[] = SOURCE_UNREACHABLE, outcomes_by_type empty, no fabricated items | FR-RUN-02 | edge | f06-scheduled-runs.md |
| AC-RUN-14 | a corrupt checkpoint value | the job starts | E-RUN-CHECKPOINT-INVALID, run refused, no data change | BEH-RUN-05 | negative | f06-scheduled-runs.md |
| AC-RUN-15 | schedule enabled, expected 02:00 run absent | the missing-run detector runs | the absent run is listed; with schedule disabled it reports 'schedule disabled' | PNFR-14 | edge | f06-scheduled-runs.md |
| AC-MET-01 | the metric registry | enumerated by a test | every metric of category time/money involving closed, resolved, approved, cost or handling time has a non-null tag; registering one without a tag fails E-MET-TAG-REQUIRED | FR-MET-01 | negative | f07-metrics-definition-tags.md |
| AC-MET-02 | any rendered report/API/CSV figure of those categories | inspected (100%) | tag, policy version, status (candidate/adopted/accepted-open) and the label 'synthetic, unvalidated' appear | FR-MET-01, PNFR-20 | positive | f07-metrics-definition-tags.md |
| AC-MET-03 | one figure tagged D-OPS and one D-EVID | `combine(sum)` and `compare` are called | both raise E-MET-TAG-MIX | FR-MET-02 | negative | f07-metrics-definition-tags.md |
| AC-MET-04 | the same two figures | `side_by_side` is used | rendered in separate labelled columns with no derived cross-column value and the 'not comparable' note | FR-MET-02 | positive | f07-metrics-definition-tags.md |
| AC-MET-05 | D-OPS improves and D-EVID worsens between two periods | the trend report is generated | flag FAIL-02-conflict is present and no single 'improved' headline is produced | FR-MET-02, BR-01 | edge | f07-metrics-definition-tags.md |
| AC-MET-06 | a fixture with 10 completed cycles under clock C-OPS and 8 under C-EVID | the time-to-close report runs | two separate series, each with n, median, p90 per stated method, plus open_count; no pooled series | FR-MET-03 | positive | f07-metrics-definition-tags.md |
| AC-MET-07 | fixture durations [1,2,3,4,100] and [1,2,3,4] | median and p90 computed | median 3 and 2.5; p90 nearest-rank 100 and 4 | FR-MET-03 | edge | f07-metrics-definition-tags.md |
| AC-MET-08 | the 125 shipped cases (events: CASE_CREATED only for most) | time-to-close is requested for event-derived clocks | `value: null`, reason `no_completed_cycles`, n = 0 (K-04/K-05 remain unmeasurable per OD-07); no zero or invented value | FR-MET-03, PNFR-20 | edge | f07-metrics-definition-tags.md |
| AC-MET-09 | the shipped 125 cases | `month_end_total` is called with an explicit cutoff after all case dates and source = cases.amount | result 622,826.44 exactly (Decimal), `n = 125`; the legacy 742,956.61 is not produced | FR-MET-04 | positive | f07-metrics-definition-tags.md |
| AC-MET-10 | the same call without cutoff or denominator | called | E-MET-CUTOFF-REQUIRED | FR-MET-04 | negative | f07-metrics-definition-tags.md |
| AC-MET-11 | a cases fixture where two cases have 2 events and 1 event respectively | totals computed | each case amount counted once (no fan-out); an equivalent join-based query on the same fixture inflates and the test asserts they differ | FR-MET-04 | negative | f07-metrics-definition-tags.md |
| AC-MET-12 | a text-amount fixture with 1 blank, 1 'abc', 1 negative among 100 rows | totals computed | default call raises E-MET-UNPARSABLE-INPUT naming 2 rows; with allow_partial the result is flagged partial with 2 errors; negative value is summed as-is and flagged NEGATIVE_VALUE | FR-MET-04 | negative | f07-metrics-definition-tags.md |
| AC-MET-13 | float sums 0.1+0.2 style fixture | totals computed | exact decimal result 0.30 (no binary rounding drift) | FR-MET-04 | edge | f07-metrics-definition-tags.md |
| AC-MET-14 | a metric computed and stored | `reproduce` runs after unrelated data are added | equal value (inputs_hash restricts the inputs); if a code change alters it, E-MET-NOT-REPRODUCIBLE is reported | FR-MET-06, PNFR-16 | positive | f07-metrics-definition-tags.md |
| AC-MET-15 | all registered KPIs | documentation is generated | 100% have window, denominator, exclusions and tag; a KPI missing one fails the build | FR-MET-06 | negative | f07-metrics-definition-tags.md |
| AC-MET-16 | `operating_costs.total_cases` offered as 'cases created' | a metric is configured with it | E-MET-SOURCE-REFUSED | BEH-MET-09 | negative | f07-metrics-definition-tags.md |
| AC-MET-17 | tag D-OPS declared, as_of 2025-12-19 | backlog by site is produced | per-site backlog counts and bucket counts; total backlog under D-OPS = cases whose state is not CLOSED at as_of (89 of 125 per Stage 4 K-09-OPS, if the fixture is the baseline); table has one tag | FR-MET-05 | positive | f07-metrics-definition-tags.md |
| AC-MET-18 | backlog requested without a definition tag | requested | E-MET-DEFINITION-REQUIRED | FR-MET-05 | negative | f07-metrics-definition-tags.md |
| AC-MET-19 | R2: intake and run records for two sources | per-source metrics run | unmatched rate and delay distribution per source are produced and reproducible | FR-MET-07 | positive | f07-metrics-definition-tags.md |
| AC-MET-20 | R2: OP-MET-05 requested | called | E-MET-NOT-AVAILABLE | FR-MET-08 | negative | f07-metrics-definition-tags.md |
| AC-MET-21 | any metric endpoint | called twice with identical parameters | byte-identical JSON (apart from `computed_at`, excluded from the comparison) | PNFR-17 | positive | f07-metrics-definition-tags.md |
| AC-REV-01 | a fixture with 5 quarantined, 3 unmatched, 2 ambiguous and 4 NOOP_DUPLICATE items | the queue view is requested | 10 items listed (duplicates excluded), each with primary reason, queue, source, receipt_time and age | FR-REV-02 | positive | f08-reviewer-support.md |
| AC-REV-02 | the full store | a test compares queue rows to all items whose current outcome has a queue | 100% appear, none twice | FR-REV-02 | positive | f08-reviewer-support.md |
| AC-REV-03 | the shipped feed backlog (224 unsupported, 210 no key, 8,394 unmatched... overlapping) | the view is paged with limit 500 | the page size is clamped to 100 and `next` works; totals are reported | FR-REV-02 | edge | f08-reviewer-support.md |
| AC-REV-04 | an item whose notes contain `<script>alert(1)</script>` | the queue page is rendered | the text appears escaped, with the untrusted marker, and no script executes (response contains `&lt;script&gt;`) | FR-REV-02, PNFR-13 | negative | f08-reviewer-support.md |
| AC-REV-05 | a stored trace of as-found-python for status CLOSED | the explanation is generated twice | identical text naming rule set, row id, input values and outcome 'archive' | FR-REV-01 | positive | f08-reviewer-support.md |
| AC-REV-06 | a defaulted result (region MARS) | the explanation is shown | includes the 'defaulted: NO_MATCH_REGION_YEAR' marker and the retained as-found value | FR-REV-01, FR-POL-06 | positive | f08-reviewer-support.md |
| AC-REV-07 | the explanation module source | scanned | no network, model client or random call is imported/used | FR-REV-01, FR-CO-04 | negative | f08-reviewer-support.md |
| AC-REV-08 | any explanation | the page is inspected | the override/dismiss/refuse control is present | FR-REV-01, FR-GATE-06 | positive | f08-reviewer-support.md |
| AC-REV-09 | R2: `ref:C00000001` | search is run | documents whose `reference` equals the case id are returned (30 documents in total reference a case across the corpus; the case's own count per fixture) | FR-REV-03 | positive | f08-reviewer-support.md |
| AC-REV-10 | R2: query `"ignore previous"` | search is run | the 22-document injection set is found as ordinary matches, labelled untrusted; no other behaviour changes | FR-REV-03, PNFR-13 | negative | f08-reviewer-support.md |
| AC-REV-11 | R2: query `foo OR NOT bar* NEAR(x y) col:evil` | search is run | tokens are treated literally or E-REV-QUERY-INVALID for unknown field `col`; no FTS syntax error leaks; no SQL fragment executes | FR-REV-03 | negative | f08-reviewer-support.md |
| AC-REV-12 | R2: a caller without access to restricted documents (328) | search for a term present in restricted and open docs | restricted hits absent and not counted; counts equal the permitted subset | FR-REV-03, FR-SEC-03 | negative | f08-reviewer-support.md |
| AC-REV-13 | R2: ja-JP text | search with a substring query | trigram index returns the matching documents; es/de text with diacritics matches without diacritics | FR-REV-03 | edge | f08-reviewer-support.md |
| AC-REV-14 | R2: two identical-score hits | search twice | same order (effective_at desc, doc_id) | FR-REV-03, PNFR-17 | positive | f08-reviewer-support.md |
| AC-REV-15 | R2: labelled question set of >= 50 queries (proposal OPD-12) | top-5 recall measured | recall is reported as a baseline number, no threshold enforced; on the shipped corpus the test notes that ranking quality cannot be assessed (3 base sentences) | FR-REV-03 | edge | f08-reviewer-support.md |
| AC-REV-16 | R2: FTS5 disabled in the test runtime | the product starts | `search.engine = fallback`, identical result order for the AC-REV-09 and AC-REV-14 fixtures | BEH-REV-06 | edge | f08-reviewer-support.md |
| AC-REV-17 | R2: any search response | scanned in a contract test | contains no field named answer/summary/recommendation | FR-REV-03, FR-CO-04 | negative | f08-reviewer-support.md |
| AC-REV-18 | R2: template feature enabled | a draft is created | no field is pre-filled; no Zone H action is reachable from the template | FR-REV-04 | negative | f08-reviewer-support.md |
| AC-REV-19 | the queue and search endpoints under the 125-case baseline | 200 calls are made | p50 and p95 latencies are recorded in a report (no pass/fail threshold; PNFR-06 measure-only) | PNFR-06 | positive | f08-reviewer-support.md |
| AC-SEC-01 | every registered route (enumerated by test) | called without credentials | 401 for all except `/healthz` and `/auth/login`; `/healthz` returns no case data | FR-SEC-01, PNFR-07 | negative | f09-access-audit-protection.md |
| AC-SEC-02 | a route registered without a permission declaration | the route-registry test runs | the test fails (deny by default) | FR-SEC-01 | negative | f09-access-audit-protection.md |
| AC-SEC-03 | roles reviewer, finance_read, integration | each calls an operation outside its matrix row | 403 E-AUTH-FORBIDDEN and an audit record with outcome denied | FR-SEC-01, FR-SEC-02 | negative | f09-access-audit-protection.md |
| AC-SEC-04 | a fresh install | the user table is read | zero users exist; no default credentials; login with any password fails | FR-SEC-01 | negative | f09-access-audit-protection.md |
| AC-SEC-05 | a user with 5 consecutive bad logins | a 6th login with the correct password is tried within 15 min | E-AUTH-LOCKED; after 15 min login succeeds | FR-SEC-01 | edge | f09-access-audit-protection.md |
| AC-SEC-06 | the credential store | inspected | password hashes are PBKDF2 with per-user salt; session tokens are stored only as SHA-256; no plaintext secret anywhere | PNFR-07, PNFR-08 | negative | f09-access-audit-protection.md |
| AC-SEC-07 | an idle session beyond 30 min or older than 8 h | used | 401 E-AUTH-SESSION-EXPIRED | FR-SEC-01 | edge | f09-access-audit-protection.md |
| AC-SEC-08 | a service token | used on interactive login or a Zone H / human-link route | login refused; Zone H and human-link refused and audited | FR-GATE-03, FR-SEC-01 | negative | f09-access-audit-protection.md |
| AC-SEC-09 | a decision event, a policy change, a Zone H attempt, an authz failure, a login failure | each is performed | one audit record per action with the BEH-SEC-05 fields, chain linked | FR-SEC-02 | positive | f09-access-audit-protection.md |
| AC-SEC-10 | a chain of 1,000 audit records and an anchor | `verify-audit` runs | `ok` | FR-SEC-02, PNFR-09 | positive | f09-access-audit-protection.md |
| AC-SEC-11 | the same chain with (a) one record's `details` edited, (b) one record deleted, (c) two records swapped, (d) the last 50 records deleted after an anchor at seq 1,000 | `verify-audit` runs for each | (a)-(c) report the first broken seq and kind; (d) reports head mismatch against the anchor | FR-SEC-02, PNFR-09 | negative | f09-access-audit-protection.md |
| AC-SEC-12 | records deleted after the last anchor | `verify-audit` runs | not detected - the test documents the limitation (residual risk R-SEC-1) | FR-SEC-02 | edge | f09-access-audit-protection.md |
| AC-SEC-13 | the audit table | UPDATE/DELETE attempted | rejected by trigger | FR-SEC-02 | negative | f09-access-audit-protection.md |
| AC-SEC-14 | the audit write forced to fail | any change is attempted | change rolled back, E-SEC-AUDIT-WRITE-FAILED | FR-SEC-02, BEH-DEC-11 | negative | f09-access-audit-protection.md |
| AC-SEC-15 | a login failure followed by the audit read | the record is inspected | no password or token appears in `details` or logs | PNFR-08 | negative | f09-access-audit-protection.md |
| AC-SEC-16 | start-up with `bind = 0.0.0.0` and no exposure approval | the server starts | refused E-SEC-EXPOSURE-NOT-APPROVED; with approval but no TLS settings also refused | PNFR-08 | negative | f09-access-audit-protection.md |
| AC-SEC-17 | a state-changing form post without CSRF token / a JSON write without the custom header | posted | E-SEC-CSRF, no change | PNFR-07 | negative | f09-access-audit-protection.md |
| AC-SEC-18 | the code base | secret scan and deletion-path grep run | 0 secret findings; no DELETE statements on retained tables | PNFR-08, PNFR-10 | negative | f09-access-audit-protection.md |
| AC-SEC-19 | R2: one fixture record per field class and each role | read through the API | handling matches metadata-model M3/M4 (finance masked account_id, restricted denied, missing access_level treated restricted); 100% of field classes covered | FR-SEC-03, PNFR-12 | positive | f09-access-audit-protection.md |
| AC-SEC-20 | R2: a C3 read or export without reason | requested | E-SEC-REASON-REQUIRED; with reason it succeeds and the reason is audited (non-empty) | FR-SEC-03 | negative | f09-access-audit-protection.md |
| AC-SEC-21 | holder list changed and process restarted | audit chain read | CONFIG_LOADED record with config hash (also AC-GATE-22) | FR-SEC-02 | positive | f09-access-audit-protection.md |
| AC-CO-01 | all deviation_register rows `proposed` | `golden-compare` runs on the 125-case baseline (sandbox copy) | every difference from DV-01..DV-09 is listed as UNAPPROVED and the exit code is non-zero; with matching approved rows the exit code is 0 | FR-CO-01 | positive | f10-coexistence-change-safety.md |
| AC-CO-02 | a change that alters an unlisted golden (e.g. priority of one case) | the harness runs | reports UNAPPROVED for that golden and fails | FR-CO-01 | negative | f10-coexistence-change-safety.md |
| AC-CO-03 | the Stage 7 goldens CT-01..CT-03 | run through `as-found-*` rule sets | zero differences (cross-reference AC-POL-12..14) | FR-CO-01, FR-POL-04 | positive | f10-coexistence-change-safety.md |
| AC-CO-04 | the new code | a test opens each legacy DB path | only via `mode=ro`; a write attempt raises E-CO-LEGACY-WRITE-REFUSED | FR-CO-01 | negative | f10-coexistence-change-safety.md |
| AC-CO-05 | the repo after an R1 build | `git diff` on legacy source paths | empty | FR-CO-01, ADR-003 | negative | f10-coexistence-change-safety.md |
| AC-CO-06 | a working data directory inside the original repo root | the harness starts | E-CO-NOT-SANDBOX, no run | OD-03a | negative | f10-coexistence-change-safety.md |
| AC-CO-07 | a sandbox run completes | `sha256sum -c --quiet` on the backup manifest is executed from the repo root | exit 0 (all 1,512 files match) | OD-03a, FR-CO-01 | positive | f10-coexistence-change-safety.md |
| AC-CO-08 | the coexistence inventory | read | CO-WF-01 present with owner 'Unknown'; no API route or job named update/retire/disable for it exists | FR-CO-02 | negative | f10-coexistence-change-safety.md |
| AC-CO-09 | a rollback rehearsal in the sandbox | executed from the written procedure | store restored, checksum matches, audit chain verifies, replay-safety suite passes | FR-CO-03, PNFR-19 | positive | f10-coexistence-change-safety.md |
| AC-CO-10 | the release checklist | a release is attempted with G2 failing | release record cannot be marked ready | FR-CO-03 | negative | f10-coexistence-change-safety.md |
| AC-CO-11 | a dependency `openai` added to the project | CI deny-list check runs | build fails E-CO-DENYLIST-IMPORT | FR-CO-04, PNFR-18 | negative | f10-coexistence-change-safety.md |
| AC-CO-12 | the process runs the full acceptance suite with `socket.connect` patched to record attempts | the suite finishes | zero non-loopback connection attempts; `model_calls_total = 0` | FR-CO-04, PNFR-18 | negative | f10-coexistence-change-safety.md |
| AC-CO-13 | core functions run under PYTHONHASHSEED 0/1/random, TZ UTC/Asia/Kolkata/America/Los_Angeles, locale C/en_IN | outputs hashed | all hashes equal; no `random` import in core modules | PNFR-17 | positive | f10-coexistence-change-safety.md |
| AC-CO-14 | a runtime older than the floor (Python 3.9) | the product starts | E-CO-RUNTIME-UNSUPPORTED; on 3.10.12 / SQLite 3.37.2 it starts and prints versions | OD-S12-12 | edge | f10-coexistence-change-safety.md |
| AC-CO-15 | G1-G10 | the pre-release checklist is generated | every gate has a recorded pass/fail with evidence path; any fail blocks | FR-CO-03, PNFR-19 | positive | f10-coexistence-change-safety.md |
| AC-OBS-01 | any API call | it completes | one log line with correlation_id, op_id, outcome, duration_ms; the same correlation id appears in the audit record (for writes) and in any error envelope | PNFR-14, BEH-OBS-01 | positive | observability-spec.md |
| AC-OBS-02 | 10 job runs | `hub report health` runs | every run is listed; a seeded killed run appears as abandoned | FR-RUN-02, PNFR-14 | positive | observability-spec.md |
| AC-OBS-03 | schedule enabled, one expected run absent | the detector runs | `run_missed_total` = 1 and the run is listed | PNFR-14 | edge | observability-spec.md |
| AC-OBS-04 | logs produced by the full acceptance suite (including failed logins and injection fixtures) | scanned for passwords, tokens, hashes, raw notes text | 0 matches | PNFR-08, BEH-SEC-07 | negative | observability-spec.md |
| AC-OBS-05 | the 125-case baseline fixture | `hub report latency` runs 200 calls per key operation | p50 and p95 per operation are printed; no pass/fail | PNFR-06 | positive | observability-spec.md |
| AC-OBS-06 | the acceptance suite | finishes | `model_calls_total = 0`, `egress_attempts_total = 0`, `zone_h_service_actor_accepted = 0` | PNFR-18, FR-GATE-03 | negative | observability-spec.md |
| AC-OBS-07 | start-up | selfcheck runs | prints Python, SQLite, FTS5 status, config hash, gate status | OD-S12-12 | positive | observability-spec.md |
| AC-OBS-08 | the KPI registry on the shipped baseline | kpi-coverage runs | lists each R1 KPI with a value or a stated reason (e.g. `no_completed_cycles`) | PNFR-14, PNFR-16 | positive | observability-spec.md |
| AC-OBS-09 | a duplicate replay of 100 items | metrics are read | `intake_noop_duplicate_total` +100 and queue depths unchanged | FR-INT-02, PNFR-11 | positive | observability-spec.md |
| AC-NFR-01 | a probe log for a simulated 30-day window with known 216 down minutes in 43,200 | availability is computed | 99.50% is reported with method and the label 'against an unvalidated working target'; no claim is made about real availability | PNFR-01 | positive | nfr-spec.md |
| AC-NFR-02 | schedule enabled in a sandbox test with a fixed clock and 30 simulated nights | scheduled runs complete | `run_finished_before_0600_local` reported per night; share reported; production timeliness is stated as unproven | PNFR-02 | edge | nfr-spec.md |
| AC-NFR-03 | R2: items with delays 1 h, 3.9 h, 4.1 h, and a future `source_ts` | the delay report runs | share within 4 h = 2 of 3 non-future items (66.7%); the future item is flagged and excluded from the share | PNFR-03 | edge | nfr-spec.md |
| AC-NFR-04 | R2: a source whose newest accepted item is 25 h old | the freshness report runs | source listed as older than 24 h with age | PNFR-04 | positive | nfr-spec.md |
| AC-NFR-05 | a pre-release backup | restore is rehearsed in a sandbox from the written procedure | store restored, SHA-256 matches, `verify-audit` ok, `verify-projection` 0 mismatches; elapsed restore time recorded and compared (labelled) with 8 h | PNFR-05 | positive | nfr-spec.md |
| AC-NFR-06 | the 125-case baseline fixture | latency is measured | p50/p95 recorded for queue, rule-trace, evidence-pack, state; no threshold | PNFR-06 | positive | nfr-spec.md |
| AC-NFR-07 | the route registry | enumerated | 100% of routes authenticated and authorised; 0 anonymous reads/writes of case data in test | PNFR-07 | negative | nfr-spec.md |
| AC-NFR-08 | the code base and start-up configs | secret scan and start-up tests run | 0 secrets; non-loopback without approval+TLS refused | PNFR-08 | negative | nfr-spec.md |
| AC-NFR-09 | 100% of decision events in a test run | audited | each has actor/time/basis, chain verifies, deliberate tamper detected | PNFR-09 | positive | nfr-spec.md |
| AC-NFR-10 | the full acceptance run | table row counts before and after | 0 deletions of case, evidence, event, audit, intake rows | PNFR-10 | negative | nfr-spec.md |
| AC-NFR-11 | the replay suite (AC-INT-04/05/29) | run | 0 duplicate effects, 0 silent overwrites, raw count = received count | PNFR-11 | positive | nfr-spec.md |
| AC-NFR-12 | R2: one fixture per field class | access tests run | 100% field classes covered | PNFR-12 | positive | nfr-spec.md |
| AC-NFR-13 | planted-string fixtures: 86 feed rows, 22 document bodies, 44 regex-hit strings | processed | 0 effects on any decision field | PNFR-13 | negative | nfr-spec.md |
| AC-NFR-14 | a run history and the KPI registry | health and coverage reports run | 100% of runs have records; every R1 KPI has a value or a stated reason | PNFR-14 | positive | nfr-spec.md |
| AC-NFR-15 | the rule-output registry | iterated | 100% show trace and offer override with reason | PNFR-15 | positive | nfr-spec.md |
| AC-NFR-16 | all KPIs | documentation and reproduce tests run | 100% documented; identical value on re-run | PNFR-16 | positive | nfr-spec.md |
| AC-NFR-17 | core paths run across hash seeds, time zones, locales | outputs compared | bit-identical | PNFR-17 | positive | nfr-spec.md |
| AC-NFR-18 | the full suite | dependency, import and socket checks run | 0 model calls, 0 egress, deny-list clean | PNFR-18 | negative | nfr-spec.md |
| AC-NFR-19 | a release candidate | rollback rehearsal and replay gate run | both pass before ready status | PNFR-19 | positive | nfr-spec.md |
| AC-NFR-20 | all KPI outputs and reports generated while data are synthetic | scanned | 100% carry 'synthetic, unvalidated' | PNFR-20 | positive | nfr-spec.md |

### ACC-8 Criteria that cannot be fully verified today (honest limits) [Unknown / Assumption]
| Limit | Why | Handling |
|---|---|---|
| Real-world availability, 06:00 completion, RTO/RPO attainment | no environment, no schedule, targets are unvalidated working targets | measured in sandbox and reported with label (AC-NFR-01/02/05) |
| Search ranking quality | synthetic corpus has 3 base sentences | recall baseline reported only (AC-REV-15) |
| Corrected-replay handling on real data | none in shipped data (FND-INT-1) | synthetic fixture (AC-INT-07) |
| Event-derived time-to-close values | no real closure timestamps (OD-07) | null with reason (AC-MET-08) |
| Concurrency on one SQLite file | CT-17 uncharacterised | AC-DEC-22 covers logical conflict only |
| Part 11 / GxP compliance | framing only (DR-29) | no compliance claim |
| Cross-language goldens (Java CT-11) | JDK absent on the device | deferred to CI with JDK; documented in Stage 14 |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-ACC-1 The coverage check proves each ID is referenced by a criterion, not that the criterion is sufficient; Stage 13/14 test design and Stage 26 TEVV judge sufficiency.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-ACC-1 Mutation-kill power of the future suite (shipped suite kills 1 of 15 mutants).

## Unresolved Issues
- Criteria parameterised on open decisions are executed with test policies only; final values await Dinesh's decisions.

## Residual Risks
- Generated table can drift from source files; regenerate at any spec change (script is outside the repo: $HOME/fde_sbx/s12/collect_ac.py).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
