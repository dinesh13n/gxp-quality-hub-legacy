---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "spec-to-test-map.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/12-specs/api-contracts.md", "docs/12-specs/error-handling-spec.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/13-traceability/evidence/tests_plan.csv"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Maps every spec element to a planned test: 108 behaviours and 241 acceptance criteria (= 241 planned tests), 48 API operations, 48 SBR rules and the 18 Stage 7 CT legacy-preservation tests. 108/108 behaviours and 52/52 FR have tests; the weak links are SBR (direct 2/48), API operations (named in AC/BEH 12/48) and CT-04..CT-18 (no AC). All PLANNED / NOT-RUN.

## Findings
### S2T-1 Method [Verified Fact]
Every acceptance criterion (AC) in `acceptance-criteria.md` ACC-7 becomes one planned test (`TST-<F>-<nn>`). Behaviours (BEH) and API operations are tested through the ACs that cite them; SBR rules through ACs that cite them or through their parent FR (see RTM-7). Stage 7 characterization tests CT-01..CT-18 are mapped separately (legacy-behaviour preservation). Level, fixture and class are **heuristics computed from the Given/When/Then text** [Inference] and must be confirmed by Stage 15 when tests are written. Nothing has been executed; status is PLANNED / NOT-RUN for all 241 tests.

### S2T-2 Totals by feature [Verified Fact: computed]
| Feature prefix | BEH | SBR | AC = planned tests | + | - | edge | Class A/B/C | Evidence stage(s) |
|---|---|---|---|---|---|---|---|---|
| DEC | 12 | 7 | 28 | 8 | 13 | 7 | 17/10/1 | 16 |
| GATE | 9 | 5 | 22 | 7 | 13 | 2 | 13/9/0 | 16 |
| POL | 11 | 8 | 25 | 14 | 7 | 4 | 21/4/0 | 16 |
| INT | 12 | 8 | 29 | 11 | 11 | 7 | 23/5/1 | 16 |
| ID | 8 | 3 | 17 | 5 | 9 | 3 | 17/0/0 | 16 |
| RUN | 9 | 4 | 15 | 5 | 7 | 3 | 12/3/0 | 16 |
| MET | 11 | 7 | 21 | 8 | 9 | 4 | 20/0/1 | 16 |
| REV | 8 | 0 | 19 | 8 | 7 | 4 | 17/1/1 | 16 |
| SEC | 11 | 3 | 21 | 4 | 14 | 3 | 20/1/0 | 26 |
| CO | 9 | 3 | 15 | 6 | 8 | 1 | 14/1/0 | 16 |
| OBS | 8 | 0 | 9 | 6 | 2 | 1 | 8/1/0 | 31 |
| NFR | 0 | 0 | 20 | 13 | 5 | 2 | 15/0/5 | 16,25,26,27,28,30,31,32 |
| **All** | 108 | 48 | 241 | 95 | 105 | 41 | 197/35/9 | |

Planned test levels (heuristic) [Inference]: api 16, characterization/golden 6, contract 5, database 9, nfr-measurement 10, service/unit 180, static/introspection 12, ui/manual-walkthrough 3. Fixture rules honour OD-03a/OD-09: every executable test runs in a full sandbox copy of the repo against a hash-verified copy of the 125-case / seed-4100 baseline (`data/legacy.sqlite3` sha256 `c254649f...d70aa`), never against the working tree.

### S2T-3 Untested specs [Verified Fact: computed]
- **Behaviours:** 108 of 108 have >= 1 AC. None untested.
- **Acceptance-criteria quality:** vague-term scan (appropriate, reasonable, fast, ...) over all Then-clauses flags **0** criteria [Verified Fact]; 3 criteria use a UI walk-through level and are manual.
- **API operations:** 12 of 48 are cited by name in an AC or behaviour; the remaining 36 are reached only through their parent FR's criteria. Every operation has at least one FR with >= 1 AC, so none is untraceable, but **an operation-level contract test (one per op, driven from `contracts/openapi.yaml`) is not yet planned** [GAP-13-04].
- **SBR rules:** 2 of 48 cited by an AC directly; 45 only via parent FR [GAP-13-03]. The 7 [PARAM] rules (SBR-DEC-03, SBR-GATE-03, SBR-INT-01, SBR-INT-07, SBR-POL-04, SBR-POL-06, SBR-RUN-04) have mechanism-only content because they depend on open decisions.
- **Error codes:** 55 of 82 error codes defined in `error-handling-spec.md` are asserted by an AC; **27 are not** (E-AUTH-BAD-CREDENTIALS, E-CO-EGRESS-ATTEMPT, E-CO-UNAPPROVED-DEVIATION, E-DEC-CASE-NOT-FOUND, E-DEC-FIELD-TOO-LONG, E-GATE-UNKNOWN-ACTION, ...) [GAP-13-12].
- **Contracts:** 14 example documents + `invalid-cases.json` exist in `docs/12-specs/contracts/examples/` and 16 JSON Schemas in `contracts/schemas/`; they are fixtures for contract tests (5 ACs are at contract level). Whether examples validate was claimed by Stage 12 (not re-run here: documentation-only stage) [Unknown until Stage 15/16 executes them].

### S2T-4 Planned test per behaviour (108)
| BEH | Requirement(s) named by the behaviour | ACs (planned tests `TST-`) | #AC |
|---|---|---|---|
| BEH-CO-01 | FR-CO-01 | AC-CO-01..03 | 3 |
| BEH-CO-02 | FR-CO-01 | AC-CO-01 | 1 |
| BEH-CO-03 | FR-CO-01 | AC-CO-04 | 2 |
| BEH-CO-04 | FR-CO-01 | AC-CO-06 | 2 |
| BEH-CO-05 | FR-CO-02 | AC-CO-08 | 1 |
| BEH-CO-06 | FR-CO-03, PNFR-19 | AC-CO-09 | 2 |
| BEH-CO-07 | FR-CO-04, PNFR-18 | AC-CO-11 | 2 |
| BEH-CO-08 | PNFR-17 | AC-CO-13 | 1 |
| BEH-CO-09 | **none** (OD-S12-12) | AC-CO-14 | 1 |
| BEH-DEC-01 | FR-DEC-01 | AC-DEC-01..04 | 4 |
| BEH-DEC-02 | FR-DEC-01, FR-DEC-02 | AC-DEC-05,07 | 2 |
| BEH-DEC-03 | FR-DEC-02, PNFR-17 | AC-DEC-05 | 1 |
| BEH-DEC-04 | FR-DEC-02 | AC-DEC-06,08 | 2 |
| BEH-DEC-05 | FR-DEC-03 | AC-DEC-09..11 | 3 |
| BEH-DEC-06 | FR-DEC-04, FR-SEC-01 | AC-DEC-12..14 | 3 |
| BEH-DEC-07 | FR-DEC-05, FR-GATE-03 | AC-DEC-15..19,27 | 7 |
| BEH-DEC-08 | FR-DEC-06, FR-POL-02 | AC-DEC-20 | 2 |
| BEH-DEC-09 | FR-DEC-01, PNFR-11 | AC-DEC-22 | 2 |
| BEH-DEC-10 | FR-DEC-01, FR-POL-01 | AC-DEC-26 | 1 |
| BEH-DEC-11 | FR-DEC-01, FR-SEC-02 | AC-DEC-24; AC-SEC-14 | 2 |
| BEH-DEC-12 | FR-INT-07, PNFR-13 | AC-DEC-25 | 1 |
| BEH-GATE-01 | FR-GATE-01, FR-GATE-03 | AC-GATE-09,12,21 | 4 |
| BEH-GATE-02 | FR-GATE-01, FR-INT-07 | AC-GATE-11,13 | 3 |
| BEH-GATE-03 | FR-GATE-02 | AC-GATE-15 | 2 |
| BEH-GATE-04 | FR-GATE-02, FR-GATE-03 | AC-GATE-17 | 1 |
| BEH-GATE-05 | FR-GATE-04 | AC-GATE-01,22 | 3 |
| BEH-GATE-06 | FR-DEC-01, FR-GATE-05 | AC-GATE-03..08 | 6 |
| BEH-GATE-07 | FR-GATE-03, FR-SEC-02 | AC-GATE-09 | 1 |
| BEH-GATE-08 | FR-GATE-06, PNFR-15 | AC-GATE-18..20 | 3 |
| BEH-GATE-09 | FR-GATE-04, FR-GATE-05 | AC-GATE-01 | 1 |
| BEH-ID-01 | FR-ID-01 | AC-ID-01,09..11 | 5 |
| BEH-ID-02 | FR-ID-02 | AC-ID-03..05 | 3 |
| BEH-ID-03 | FR-ID-02 | AC-ID-02 | 2 |
| BEH-ID-04 | FR-ID-01, FR-ID-02 | AC-ID-06..10 | 5 |
| BEH-ID-05 | FR-ID-01 | AC-ID-12 | 1 |
| BEH-ID-06 | FR-ID-04 | AC-ID-13,17 | 3 |
| BEH-ID-07 | FR-ID-03 | AC-ID-15 | 2 |
| BEH-ID-08 | FR-ID-03 | AC-ID-15 | 1 |
| BEH-INT-01 | FR-INT-01, PNFR-11 | AC-INT-01..03,29 | 4 |
| BEH-INT-02 | FR-INT-02, FR-INT-03 | AC-INT-05..07 | 3 |
| BEH-INT-03 | FR-INT-02 | AC-INT-04 | 2 |
| BEH-INT-04 | FR-INT-03 | AC-INT-07 | 2 |
| BEH-INT-05 | FR-INT-04, FR-INT-06 | AC-INT-09..11,15 | 5 |
| BEH-INT-06 | FR-INT-04 | AC-INT-12..14 | 3 |
| BEH-INT-07 | FR-INT-06, PNFR-17 | AC-INT-20 | 2 |
| BEH-INT-08 | FR-ID-02, FR-INT-05 | AC-INT-17..19 | 3 |
| BEH-INT-09 | FR-INT-07, PNFR-13 | AC-INT-22..24 | 3 |
| BEH-INT-10 | FR-INT-01 | AC-INT-29 | 1 |
| BEH-INT-11 | FR-INT-04, FR-INT-06 | AC-INT-25..27 | 3 |
| BEH-INT-12 | FR-INT-08 | AC-INT-28 | 1 |
| BEH-MET-01 | FR-MET-01, FR-MET-06 | AC-MET-01,15 | 2 |
| BEH-MET-02 | FR-MET-01, FR-MET-06, PNFR-20 | AC-MET-02 | 1 |
| BEH-MET-03 | FR-MET-02 | AC-MET-03..05 | 3 |
| BEH-MET-04 | FR-DEC-06, FR-MET-03 | AC-MET-06..08 | 3 |
| BEH-MET-05 | FR-MET-04 | AC-MET-09..11,13 | 4 |
| BEH-MET-06 | FR-MET-04 | AC-MET-12 | 1 |
| BEH-MET-07 | FR-MET-06, PNFR-16 | AC-MET-14 | 1 |
| BEH-MET-08 | FR-MET-05 | AC-MET-17 | 2 |
| BEH-MET-09 | FR-MET-04 | AC-MET-16 | 1 |
| BEH-MET-10 | FR-MET-07 | AC-MET-19 | 1 |
| BEH-MET-11 | FR-MET-08 | AC-MET-20 | 1 |
| BEH-OBS-01 | PNFR-14 | AC-OBS-01 | 1 |
| BEH-OBS-02 | FR-RUN-02, PNFR-14 | AC-OBS-02 | 2 |
| BEH-OBS-03 | FR-GATE-04 | AC-OBS-07 | 1 |
| BEH-OBS-04 | PNFR-06 | AC-OBS-05 | 1 |
| BEH-OBS-05 | PNFR-14, PNFR-16 | AC-OBS-08 | 1 |
| BEH-OBS-06 | FR-GATE-03, PNFR-18 | AC-OBS-06 | 1 |
| BEH-OBS-07 | PNFR-10 | AC-NFR-10 | 1 |
| BEH-OBS-08 | **none** (ADR-016) | AC-OBS-02 | 1 |
| BEH-POL-01 | FR-POL-01 | AC-POL-01,25 | 2 |
| BEH-POL-02 | FR-POL-01, FR-POL-02 | AC-POL-01,06 | 2 |
| BEH-POL-03 | FR-GATE-03, FR-POL-01 | AC-POL-02..05 | 4 |
| BEH-POL-04 | FR-DEC-06, FR-MET-03, FR-POL-02 | AC-POL-06..08 | 3 |
| BEH-POL-05 | FR-POL-03, FR-SEC-02 | AC-POL-09 | 2 |
| BEH-POL-06 | FR-POL-04, FR-REV-01, PNFR-17 | AC-POL-12,22 | 2 |
| BEH-POL-07 | FR-CO-01, FR-POL-04 | AC-POL-11..14 | 4 |
| BEH-POL-08 | FR-GATE-03, FR-POL-04 | AC-POL-16..18 | 3 |
| BEH-POL-09 | FR-CO-01, FR-POL-06 | AC-POL-19..21 | 3 |
| BEH-POL-10 | FR-POL-05 | AC-POL-24 | 1 |
| BEH-POL-11 | FR-POL-04, PNFR-17 | AC-POL-23 | 1 |
| BEH-REV-01 | FR-REV-02 | AC-REV-01..04 | 4 |
| BEH-REV-02 | FR-REV-01, PNFR-15 | AC-REV-05..08 | 4 |
| BEH-REV-03 | FR-REV-03 | AC-REV-09..11 | 3 |
| BEH-REV-04 | FR-REV-03, FR-SEC-03, PNFR-13 | AC-REV-12..14 | 3 |
| BEH-REV-05 | FR-CO-04, FR-REV-03, PNFR-18 | AC-REV-10,17 | 2 |
| BEH-REV-06 | FR-REV-03 | AC-REV-16 | 1 |
| BEH-REV-07 | FR-REV-04 | AC-REV-18 | 1 |
| BEH-REV-08 | PNFR-06 | AC-REV-19 | 1 |
| BEH-RUN-01 | FR-RUN-01, FR-SEC-01 | AC-RUN-04 | 1 |
| BEH-RUN-02 | FR-GATE-01, FR-RUN-01 | AC-RUN-01..03 | 3 |
| BEH-RUN-03 | FR-RUN-02, PNFR-14 | AC-RUN-05 | 1 |
| BEH-RUN-04 | FR-RUN-02 | AC-RUN-06 | 1 |
| BEH-RUN-05 | FR-RUN-03 | AC-RUN-08..10,14 | 4 |
| BEH-RUN-06 | FR-RUN-02, PNFR-11 | AC-RUN-11 | 1 |
| BEH-RUN-07 | FR-RUN-03, PNFR-11 | AC-RUN-07 | 1 |
| BEH-RUN-08 | FR-RUN-01, PNFR-14 | AC-RUN-15 | 1 |
| BEH-RUN-09 | PNFR-02 | AC-NFR-02 | 1 |
| BEH-SEC-01 | FR-SEC-01, PNFR-07 | AC-SEC-01 | 2 |
| BEH-SEC-02 | FR-SEC-01, PNFR-07 | AC-SEC-04..07 | 4 |
| BEH-SEC-03 | FR-GATE-03, FR-SEC-01 | AC-SEC-08 | 1 |
| BEH-SEC-04 | FR-SEC-01 | AC-SEC-03 | 1 |
| BEH-SEC-05 | FR-SEC-02, PNFR-09 | AC-SEC-09,13 | 3 |
| BEH-SEC-06 | FR-SEC-02, PNFR-09 | AC-SEC-10..12 | 3 |
| BEH-SEC-07 | PNFR-08 | AC-OBS-04; AC-SEC-15,18 | 3 |
| BEH-SEC-08 | PNFR-08 | AC-SEC-16 | 1 |
| BEH-SEC-09 | PNFR-07, PNFR-13 | AC-SEC-17 | 1 |
| BEH-SEC-10 | FR-SEC-03, PNFR-12 | AC-SEC-19 | 2 |
| BEH-SEC-11 | PNFR-10 | AC-SEC-18 | 1 |

### S2T-5 Planned test per acceptance criterion (241)
Test ID = `TST-` + AC suffix. "Class" A/B/C as in RTM-4. Evidence stage: 16 functional validation, 26 TEVV, 31 observability, 28 resilience, 25 governance, 27 hardening, 30 release, 32 FinOps.

| Planned test | AC | Kind | Level (heuristic) | Fixture | Requirement / rule / behaviour | Author stage | Evidence stage | Class | Status |
|---|---|---|---|---|---|---|---|---|---|
| TST-CO-01 | AC-CO-01 | positive | characterization/golden | FX-BASE125 | FR-CO-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-02 | AC-CO-02 | negative | characterization/golden | FX-UNIT-SYNTHETIC | FR-CO-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-03 | AC-CO-03 | positive | characterization/golden | FX-TESTPOLICY | FR-CO-01, FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-04 | AC-CO-04 | negative | service/unit | FX-BASE125 | FR-CO-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-05 | AC-CO-05 | negative | service/unit | FX-BASE125; FX-FRESHINSTALL | FR-CO-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-06 | AC-CO-06 | negative | service/unit | FX-UNIT-SYNTHETIC |  | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-07 | AC-CO-07 | positive | nfr-measurement | FX-SANDBOX-COPY | FR-CO-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-08 | AC-CO-08 | negative | api | FX-UNIT-SYNTHETIC | FR-CO-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-09 | AC-CO-09 | positive | nfr-measurement | FX-SYNTHETIC-FEED; FX-SANDBOX-COPY | FR-CO-03, PNFR-19 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-10 | AC-CO-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-CO-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-11 | AC-CO-11 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-CO-04, PNFR-18 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-12 | AC-CO-12 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-CO-04, PNFR-18 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-13 | AC-CO-13 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-CO-14 | AC-CO-14 | edge | database | FX-UNIT-SYNTHETIC |  | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-CO-15 | AC-CO-15 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-CO-03, PNFR-19 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-01 | AC-DEC-01 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-01, BEH-DEC-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-02 | AC-DEC-02 | negative | database | FX-UNIT-SYNTHETIC | FR-DEC-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-03 | AC-DEC-03 | negative | database | FX-UNIT-SYNTHETIC | FR-DEC-01, PNFR-10 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-04 | AC-DEC-04 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-DEC-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-05 | AC-DEC-05 | positive | service/unit | FX-BASE125 | FR-DEC-02, PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-06 | AC-DEC-06 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-07 | AC-DEC-07 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-08 | AC-DEC-08 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-09 | AC-DEC-09 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-10 | AC-DEC-10 | positive | service/unit | FX-FRESHINSTALL | FR-DEC-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-11 | AC-DEC-11 | edge | service/unit | FX-BASE125 | FR-DEC-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-12 | AC-DEC-12 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-13 | AC-DEC-13 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-04, FR-SEC-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-14 | AC-DEC-14 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-15 | AC-DEC-15 | negative | service/unit | FX-TESTPOLICY | FR-DEC-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-16 | AC-DEC-16 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-17 | AC-DEC-17 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-05, FR-GATE-03 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-18 | AC-DEC-18 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-05, FR-GATE-03 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-19 | AC-DEC-19 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-20 | AC-DEC-20 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-21 | AC-DEC-21 | negative | service/unit | FX-TESTPOLICY | FR-DEC-06, FR-POL-01 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-22 | AC-DEC-22 | edge | api | FX-UNIT-SYNTHETIC | FR-DEC-01, PNFR-11 | 15 | 16 | C | PLANNED / NOT-RUN |
| TST-DEC-23 | AC-DEC-23 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-11 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-24 | AC-DEC-24 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-02, BEH-DEC-11 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-25 | AC-DEC-25 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-13, BEH-DEC-12 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-DEC-26 | AC-DEC-26 | edge | service/unit | FX-UNIT-SYNTHETIC | BEH-DEC-10 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-27 | AC-DEC-27 | edge | service/unit | FX-TESTPOLICY; FX-FRESHINSTALL | FR-DEC-05, SBR-DEC-03 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-DEC-28 | AC-DEC-28 | edge | service/unit | FX-FRESHINSTALL | FR-DEC-05, SBR-DEC-03 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-01 | AC-GATE-01 | positive | service/unit | FX-FRESHINSTALL | FR-GATE-04, FR-GATE-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-02 | AC-GATE-02 | negative | service/unit | FX-FRESHINSTALL | FR-GATE-04 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-03 | AC-GATE-03 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-04 | AC-GATE-04 | negative | service/unit | FX-FRESHINSTALL | BEH-GATE-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-05 | AC-GATE-05 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-DEC-01, FR-GATE-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-06 | AC-GATE-06 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-07 | AC-GATE-07 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-05 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-08 | AC-GATE-08 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-05, FR-POL-03 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-GATE-09 | AC-GATE-09 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-01, FR-GATE-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-10 | AC-GATE-10 | negative | static/introspection | FX-UNIT-SYNTHETIC | BEH-GATE-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-11 | AC-GATE-11 | negative | static/introspection | FX-SYNTHETIC-FEED | FR-GATE-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-12 | AC-GATE-12 | negative | database | FX-UNIT-SYNTHETIC | FR-GATE-01, FR-GATE-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-13 | AC-GATE-13 | negative | service/unit | FX-SYNTHETIC-FEED | FR-GATE-01, FR-INT-07 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-14 | AC-GATE-14 | negative | contract | FX-UNIT-SYNTHETIC | FR-GATE-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-15 | AC-GATE-15 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-02, PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-16 | AC-GATE-16 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-17 | AC-GATE-17 | edge | service/unit | FX-UNIT-SYNTHETIC | BEH-GATE-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-18 | AC-GATE-18 | positive | api | FX-UNIT-SYNTHETIC | FR-GATE-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-19 | AC-GATE-19 | negative | service/unit | FX-FRESHINSTALL | FR-GATE-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-20 | AC-GATE-20 | positive | api | FX-UNIT-SYNTHETIC | FR-GATE-06, PNFR-15 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-21 | AC-GATE-21 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-GATE-22 | AC-GATE-22 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-04, FR-SEC-02 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-ID-01 | AC-ID-01 | positive | service/unit | FX-BASE125 | FR-ID-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-02 | AC-ID-02 | positive | service/unit | FX-SYNTHETIC-FEED | FR-ID-01, FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-03 | AC-ID-03 | negative | service/unit | FX-SYNTHETIC-FEED | FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-04 | AC-ID-04 | negative | service/unit | FX-SYNTHETIC-FEED | FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-05 | AC-ID-05 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-06 | AC-ID-06 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-ID-01, FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-07 | AC-ID-07 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-ID-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-08 | AC-ID-08 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-ID-02, FR-SEC-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-09 | AC-ID-09 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-ID-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-10 | AC-ID-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-ID-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-11 | AC-ID-11 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-ID-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-12 | AC-ID-12 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-ID-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-13 | AC-ID-13 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-ID-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-14 | AC-ID-14 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-ID-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-15 | AC-ID-15 | positive | service/unit | FX-FRESHINSTALL | FR-ID-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-16 | AC-ID-16 | negative | service/unit | FX-TESTPOLICY; FX-FRESHINSTALL | FR-ID-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-ID-17 | AC-ID-17 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-ID-04, FR-SEC-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-01 | AC-INT-01 | positive | service/unit | FX-SYNTHETIC-FEED | FR-INT-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-02 | AC-INT-02 | negative | api | FX-SYNTHETIC-FEED | FR-INT-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-03 | AC-INT-03 | negative | service/unit | FX-BASE125; FX-SYNTHETIC-FEED | FR-INT-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-04 | AC-INT-04 | positive | service/unit | FX-SYNTHETIC-FEED | FR-INT-02, PNFR-11 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-05 | AC-INT-05 | positive | service/unit | FX-BASE125 | FR-INT-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-06 | AC-INT-06 | negative | service/unit | FX-BASE125 | FR-INT-02, SBR-INT-01 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-INT-07 | AC-INT-07 | positive | service/unit | FX-SYNTHETIC-FEED | FR-INT-03 | 15 | 16 | C | PLANNED / NOT-RUN |
| TST-INT-08 | AC-INT-08 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-INT-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-09 | AC-INT-09 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-INT-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-10 | AC-INT-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-INT-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-11 | AC-INT-11 | positive | service/unit | FX-BASE125 | FR-INT-04, FR-INT-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-12 | AC-INT-12 | edge | contract | FX-BASE125; FX-SYNTHETIC-FEED | FR-INT-04, BEH-INT-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-INT-13 | AC-INT-13 | edge | contract | FX-SYNTHETIC-FEED | FR-INT-04, BEH-INT-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-INT-14 | AC-INT-14 | positive | contract | FX-BASE125; FX-SYNTHETIC-FEED | FR-INT-04 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-INT-15 | AC-INT-15 | edge | service/unit | FX-BASE125 | FR-INT-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-INT-16 | AC-INT-16 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-INT-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-17 | AC-INT-17 | positive | service/unit | FX-SYNTHETIC-FEED | FR-INT-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-18 | AC-INT-18 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-INT-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-19 | AC-INT-19 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-INT-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-20 | AC-INT-20 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-INT-06, PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-21 | AC-INT-21 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-INT-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-22 | AC-INT-22 | negative | service/unit | FX-BASE125; FX-PLANTED; FX-SYNTHETIC-FEED | FR-INT-07, PNFR-13 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-23 | AC-INT-23 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-INT-07 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-24 | AC-INT-24 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-01, FR-INT-07 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-25 | AC-INT-25 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-INT-04, PNFR-08 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-26 | AC-INT-26 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-INT-04, FR-RUN-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-27 | AC-INT-27 | negative | service/unit | FX-SYNTHETIC-FEED | FR-INT-04, FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-28 | AC-INT-28 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-INT-08 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-INT-29 | AC-INT-29 | positive | service/unit | FX-BASE125; FX-SYNTHETIC-FEED | FR-INT-01, BEH-INT-10 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-01 | AC-MET-01 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-MET-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-02 | AC-MET-02 | positive | api | FX-TESTPOLICY; FX-SYNTHETIC-FEED | FR-MET-01, PNFR-20 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-03 | AC-MET-03 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-MET-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-04 | AC-MET-04 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-MET-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-05 | AC-MET-05 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-MET-02, BR-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-06 | AC-MET-06 | positive | service/unit | FX-TESTPOLICY | FR-MET-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-07 | AC-MET-07 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-MET-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-08 | AC-MET-08 | edge | service/unit | FX-BASE125; FX-TESTPOLICY | FR-MET-03, PNFR-20 | 15 | 16 | C | PLANNED / NOT-RUN |
| TST-MET-09 | AC-MET-09 | positive | service/unit | FX-BASE125; FX-PLANTED | FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-10 | AC-MET-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-11 | AC-MET-11 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-12 | AC-MET-12 | negative | api | FX-UNIT-SYNTHETIC | FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-13 | AC-MET-13 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-MET-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-14 | AC-MET-14 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-MET-06, PNFR-16 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-15 | AC-MET-15 | negative | nfr-measurement | FX-UNIT-SYNTHETIC | FR-MET-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-16 | AC-MET-16 | negative | service/unit | FX-UNIT-SYNTHETIC | BEH-MET-09 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-17 | AC-MET-17 | positive | service/unit | FX-BASE125 | FR-MET-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-18 | AC-MET-18 | negative | service/unit | FX-TESTPOLICY | FR-MET-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-19 | AC-MET-19 | positive | service/unit | FX-SYNTHETIC-FEED | FR-MET-07 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-20 | AC-MET-20 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-MET-08 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-MET-21 | AC-MET-21 | positive | api | FX-UNIT-SYNTHETIC | PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-NFR-01 | AC-NFR-01 | positive | nfr-measurement | FX-UNIT-SYNTHETIC | PNFR-01 | 15 | 28 | C | PLANNED / NOT-RUN |
| TST-NFR-02 | AC-NFR-02 | edge | service/unit | FX-TESTPOLICY | PNFR-02 | 15 | 28 | C | PLANNED / NOT-RUN |
| TST-NFR-03 | AC-NFR-03 | edge | service/unit | FX-UNIT-SYNTHETIC | PNFR-03 | 15 | 31 | C | PLANNED / NOT-RUN |
| TST-NFR-04 | AC-NFR-04 | positive | service/unit | FX-FRESHINSTALL | PNFR-04 | 15 | 31 | C | PLANNED / NOT-RUN |
| TST-NFR-05 | AC-NFR-05 | positive | nfr-measurement | FX-SANDBOX-COPY | PNFR-05 | 15 | 28 | C | PLANNED / NOT-RUN |
| TST-NFR-06 | AC-NFR-06 | positive | nfr-measurement | FX-BASE125 | PNFR-06 | 15 | 27 | A | PLANNED / NOT-RUN |
| TST-NFR-07 | AC-NFR-07 | negative | static/introspection | FX-UNIT-SYNTHETIC | PNFR-07 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-NFR-08 | AC-NFR-08 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-08 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-NFR-09 | AC-NFR-09 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-09 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-NFR-10 | AC-NFR-10 | negative | service/unit | FX-SYNTHETIC-FEED | PNFR-10 | 15 | 25 | A | PLANNED / NOT-RUN |
| TST-NFR-11 | AC-NFR-11 | positive | service/unit | FX-SYNTHETIC-FEED | PNFR-11 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-NFR-12 | AC-NFR-12 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-12 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-NFR-13 | AC-NFR-13 | negative | service/unit | FX-PLANTED; FX-SYNTHETIC-FEED | PNFR-13 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-NFR-14 | AC-NFR-14 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-14 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-NFR-15 | AC-NFR-15 | positive | api | FX-UNIT-SYNTHETIC | PNFR-15 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-NFR-16 | AC-NFR-16 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-16 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-NFR-17 | AC-NFR-17 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-NFR-18 | AC-NFR-18 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-18 | 15 | 32 | A | PLANNED / NOT-RUN |
| TST-NFR-19 | AC-NFR-19 | positive | nfr-measurement | FX-SYNTHETIC-FEED; FX-SANDBOX-COPY | PNFR-19 | 15 | 30 | A | PLANNED / NOT-RUN |
| TST-NFR-20 | AC-NFR-20 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-20 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-OBS-01 | AC-OBS-01 | positive | service/unit | FX-UNIT-SYNTHETIC | PNFR-14, BEH-OBS-01 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-02 | AC-OBS-02 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-02, PNFR-14 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-03 | AC-OBS-03 | edge | service/unit | FX-UNIT-SYNTHETIC | PNFR-14 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-04 | AC-OBS-04 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-08, BEH-SEC-07 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-05 | AC-OBS-05 | positive | nfr-measurement | FX-BASE125 | PNFR-06 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-06 | AC-OBS-06 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-03, PNFR-18 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-07 | AC-OBS-07 | positive | database | FX-UNIT-SYNTHETIC |  | 15 | 31 | B | PLANNED / NOT-RUN |
| TST-OBS-08 | AC-OBS-08 | positive | service/unit | FX-BASE125 | PNFR-14, PNFR-16 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-OBS-09 | AC-OBS-09 | positive | service/unit | FX-SYNTHETIC-FEED | FR-INT-02, PNFR-11 | 15 | 31 | A | PLANNED / NOT-RUN |
| TST-POL-01 | AC-POL-01 | positive | service/unit | FX-TESTPOLICY; FX-FRESHINSTALL | FR-POL-01, FR-POL-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-02 | AC-POL-02 | negative | service/unit | FX-FRESHINSTALL | FR-GATE-03, FR-POL-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-03 | AC-POL-03 | positive | service/unit | FX-TESTPOLICY | FR-POL-01, FR-POL-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-04 | AC-POL-04 | negative | nfr-measurement | FX-UNIT-SYNTHETIC | BEH-POL-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-05 | AC-POL-05 | positive | service/unit | FX-TESTPOLICY | FR-POL-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-06 | AC-POL-06 | positive | service/unit | FX-TESTPOLICY | FR-POL-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-07 | AC-POL-07 | negative | service/unit | FX-TESTPOLICY | FR-POL-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-08 | AC-POL-08 | edge | service/unit | FX-TESTPOLICY | FR-POL-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-09 | AC-POL-09 | negative | service/unit | FX-TESTPOLICY; FX-FRESHINSTALL | FR-POL-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-10 | AC-POL-10 | positive | service/unit | FX-TESTPOLICY | FR-POL-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-11 | AC-POL-11 | positive | service/unit | FX-BASE125; FX-TESTPOLICY | FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-12 | AC-POL-12 | positive | characterization/golden | FX-UNIT-SYNTHETIC | FR-CO-01, FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-13 | AC-POL-13 | positive | characterization/golden | FX-UNIT-SYNTHETIC | FR-CO-01, FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-14 | AC-POL-14 | edge | characterization/golden | FX-UNIT-SYNTHETIC | FR-CO-01, FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-15 | AC-POL-15 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-16 | AC-POL-16 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-17 | AC-POL-17 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-18 | AC-POL-18 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-03, FR-POL-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-19 | AC-POL-19 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-POL-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-POL-20 | AC-POL-20 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-CO-01, FR-POL-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-POL-21 | AC-POL-21 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-POL-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-POL-22 | AC-POL-22 | positive | service/unit | FX-TESTPOLICY | PNFR-17, BEH-POL-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-23 | AC-POL-23 | negative | service/unit | FX-UNIT-SYNTHETIC | BEH-POL-11 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-POL-24 | AC-POL-24 | positive | service/unit | FX-BASE125 | FR-POL-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-POL-25 | AC-POL-25 | negative | service/unit | FX-TESTPOLICY | FR-POL-01, FR-POL-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-01 | AC-REV-01 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-REV-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-02 | AC-REV-02 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-REV-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-03 | AC-REV-03 | edge | ui/manual-walkthrough | FX-BASE125; FX-SYNTHETIC-FEED | FR-REV-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-04 | AC-REV-04 | negative | ui/manual-walkthrough | FX-UNIT-SYNTHETIC | FR-REV-02, PNFR-13 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-05 | AC-REV-05 | positive | api | FX-TESTPOLICY | FR-REV-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-06 | AC-REV-06 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-POL-06, FR-REV-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-07 | AC-REV-07 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-CO-04, FR-REV-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-08 | AC-REV-08 | positive | ui/manual-walkthrough | FX-UNIT-SYNTHETIC | FR-GATE-06, FR-REV-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-09 | AC-REV-09 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-REV-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-10 | AC-REV-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-REV-03, PNFR-13 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-11 | AC-REV-11 | negative | database | FX-UNIT-SYNTHETIC | FR-REV-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-12 | AC-REV-12 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-REV-03, FR-SEC-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-13 | AC-REV-13 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-REV-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-14 | AC-REV-14 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-REV-03, PNFR-17 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-15 | AC-REV-15 | edge | service/unit | FX-BASE125 | FR-REV-03 | 15 | 16 | C | PLANNED / NOT-RUN |
| TST-REV-16 | AC-REV-16 | edge | service/unit | FX-UNIT-SYNTHETIC | BEH-REV-06 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-REV-17 | AC-REV-17 | negative | contract | FX-UNIT-SYNTHETIC | FR-CO-04, FR-REV-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-18 | AC-REV-18 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-REV-04 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-REV-19 | AC-REV-19 | positive | nfr-measurement | FX-BASE125 | PNFR-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-01 | AC-RUN-01 | positive | database | FX-TESTPOLICY | FR-RUN-01 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-RUN-02 | AC-RUN-02 | negative | database | FX-FRESHINSTALL | FR-RUN-01, BEH-RUN-02 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-RUN-03 | AC-RUN-03 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-03, FR-RUN-01 | 15 | 16 | B | PLANNED / NOT-RUN |
| TST-RUN-04 | AC-RUN-04 | negative | api | FX-UNIT-SYNTHETIC | FR-RUN-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-05 | AC-RUN-05 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-02, PNFR-14 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-06 | AC-RUN-06 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-07 | AC-RUN-07 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-03, BEH-RUN-07 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-08 | AC-RUN-08 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-09 | AC-RUN-09 | positive | service/unit | FX-FRESHINSTALL | FR-RUN-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-10 | AC-RUN-10 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-RUN-03 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-11 | AC-RUN-11 | negative | service/unit | FX-UNIT-SYNTHETIC | BEH-RUN-06 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-12 | AC-RUN-12 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-GATE-01 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-13 | AC-RUN-13 | edge | service/unit | FX-FRESHINSTALL; FX-SYNTHETIC-FEED | FR-RUN-02 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-14 | AC-RUN-14 | negative | service/unit | FX-UNIT-SYNTHETIC | BEH-RUN-05 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-RUN-15 | AC-RUN-15 | edge | service/unit | FX-UNIT-SYNTHETIC | PNFR-14 | 15 | 16 | A | PLANNED / NOT-RUN |
| TST-SEC-01 | AC-SEC-01 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-SEC-01, PNFR-07 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-02 | AC-SEC-02 | negative | api | FX-UNIT-SYNTHETIC | FR-SEC-01 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-03 | AC-SEC-03 | negative | api | FX-UNIT-SYNTHETIC | FR-SEC-01, FR-SEC-02 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-04 | AC-SEC-04 | negative | service/unit | FX-FRESHINSTALL | FR-SEC-01 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-05 | AC-SEC-05 | edge | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-01 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-06 | AC-SEC-06 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-07, PNFR-08 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-07 | AC-SEC-07 | edge | api | FX-UNIT-SYNTHETIC | FR-SEC-01 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-08 | AC-SEC-08 | negative | api | FX-UNIT-SYNTHETIC | FR-GATE-03, FR-SEC-01 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-09 | AC-SEC-09 | positive | service/unit | FX-TESTPOLICY | FR-SEC-02 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-10 | AC-SEC-10 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-02, PNFR-09 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-11 | AC-SEC-11 | negative | static/introspection | FX-UNIT-SYNTHETIC | FR-SEC-02, PNFR-09 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-12 | AC-SEC-12 | edge | static/introspection | FX-UNIT-SYNTHETIC | FR-SEC-02 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-13 | AC-SEC-13 | negative | database | FX-UNIT-SYNTHETIC | FR-SEC-02 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-14 | AC-SEC-14 | negative | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-02, BEH-DEC-11 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-15 | AC-SEC-15 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-08 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-16 | AC-SEC-16 | negative | service/unit | FX-UNIT-SYNTHETIC | PNFR-08 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-17 | AC-SEC-17 | negative | api | FX-UNIT-SYNTHETIC | PNFR-07 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-18 | AC-SEC-18 | negative | static/introspection | FX-UNIT-SYNTHETIC | PNFR-08, PNFR-10 | 15 | 26 | B | PLANNED / NOT-RUN |
| TST-SEC-19 | AC-SEC-19 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-03, PNFR-12 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-20 | AC-SEC-20 | negative | service/unit | FX-FRESHINSTALL | FR-SEC-03 | 15 | 26 | A | PLANNED / NOT-RUN |
| TST-SEC-21 | AC-SEC-21 | positive | service/unit | FX-UNIT-SYNTHETIC | FR-SEC-02 | 15 | 26 | A | PLANNED / NOT-RUN |

### S2T-6 API operation -> test path (48)
| Op | Route | Release | Requirement(s) | Cited by AC | Cited by BEH | Test path | Level of link |
|---|---|---|---|---|---|---|---|
| OP-DEC-01 | POST `/api/v2/cases/{case_id}/transitions` | R1 | FR-DEC-01, FR-DEC-03, FR-DEC-05 | - | - | FR ACs: AC-DEC-01..04,09..11,15..19,22,27; AC-GATE-05 | via parent FR only |
| OP-DEC-02 | GET `/api/v2/cases/{case_id}/events` | R1 | FR-DEC-01, FR-DEC-02 | - | - | FR ACs: AC-DEC-01..08,22; AC-GATE-05 | via parent FR only |
| OP-DEC-03 | GET `/api/v2/cases/{case_id}/state` | R1 | FR-DEC-02 | - | - | FR ACs: AC-DEC-05..08 | via parent FR only |
| OP-DEC-04 | GET `/api/v2/events/{event_id}` | R1 | FR-DEC-04 | AC-DEC-12, AC-DEC-13 | BEH-DEC-06 | AC-DEC-12 | direct (AC names op) |
| OP-DEC-05 | POST `/api/v2/cases/{case_id}/facts` | R1 | FR-DEC-06 | - | - | FR ACs: AC-DEC-20 | via parent FR only |
| OP-DEC-06 | POST `/api/v2/cases/{case_id}/evidence` | R1 | FR-DEC-04, FR-DEC-05 | - | - | FR ACs: AC-DEC-12..19,27 | via parent FR only |
| OP-GATE-01 | GET `/api/v2/cases/{case_id}/evidence-pack` | R1 | FR-GATE-02 | - | BEH-GATE-03 | AC-GATE-15 | via behaviour |
| OP-GATE-02 | POST `/api/v2/zone-h/actions` | R1 | FR-GATE-01, FR-GATE-03, FR-GATE-04, FR-GATE-05 | - | - | FR ACs: AC-DEC-17; AC-GATE-01..03,05..09,11..14,21; AC-INT-24; AC-OB | via parent FR only |
| OP-GATE-03 | GET `/api/v2/gate/status` | R1 | FR-GATE-04, FR-GATE-05 | - | BEH-GATE-09 | AC-GATE-01 | via behaviour |
| OP-GATE-04 | POST `/api/v2/flags/{flag_id}/overrides` | R1 | FR-GATE-06 | - | BEH-GATE-08 | AC-GATE-18..20 | via behaviour |
| OP-ID-01 | GET `/api/v2/crosswalk/lookup` | R1 | FR-ID-01 | - | BEH-ID-05 | AC-ID-12 | via behaviour |
| OP-ID-02 | POST `/api/v2/crosswalk/links` | R1 | FR-ID-01, FR-ID-02 | AC-ID-06, AC-ID-08 | BEH-ID-04 | AC-ID-06,08 | direct (AC names op) |
| OP-ID-03 | POST `/api/v2/crosswalk/links/{link_id}/retract` | R1 | FR-ID-01 | - | - | FR ACs: AC-ID-01,06,09..12 | via parent FR only |
| OP-ID-04 | GET `/api/v2/crosswalk/view` | R2 | FR-ID-04 | - | BEH-ID-06 | AC-ID-13,17 | via behaviour |
| OP-ID-05 | GET `/api/v2/crosswalk/findings` | R2 | FR-ID-03 | - | - | FR ACs: AC-ID-15 | via parent FR only |
| OP-INT-01 | POST `/api/v2/intake/items` | R1 | FR-INT-01, FR-INT-02, FR-INT-04 | - | - | FR ACs: AC-INT-01..06,09..14,16,25..27,29; AC-OBS-09 | via parent FR only |
| OP-INT-02 | GET `/api/v2/intake/items/{raw_id}` | R1 | FR-INT-01, FR-INT-06 | - | - | FR ACs: AC-INT-01..03,15,20,29 | via parent FR only |
| OP-INT-03 | POST `/api/v2/intake/conflicts/{raw_id}/resolve` | R1 | FR-INT-03 | - | - | FR ACs: AC-INT-07 | via parent FR only |
| OP-INT-04 | GET `/api/v2/intake/sources/{source}/delays` | R2 | FR-INT-08 | - | - | FR ACs: AC-INT-28 | via parent FR only |
| OP-MET-01 | GET `/api/v2/metrics/time-to-close` | R1 | FR-MET-03 | - | - | FR ACs: AC-MET-06..08 | via parent FR only |
| OP-MET-02 | GET `/api/v2/metrics/month-end-total` | R1 | FR-MET-04 | - | - | FR ACs: AC-INT-27; AC-MET-09..13 | via parent FR only |
| OP-MET-03 | GET `/api/v2/metrics/backlog` | R1 | FR-MET-05 | - | - | FR ACs: AC-MET-17 | via parent FR only |
| OP-MET-04 | GET `/api/v2/metrics/values/{value_id}/reproduce | R1 | FR-MET-06 | - | - | FR ACs: AC-MET-14 | via parent FR only |
| OP-MET-05 | GET `/api/v2/metrics/case-cost` | R2 | FR-MET-08 | AC-MET-20 | BEH-MET-11 | AC-MET-20 | direct (AC names op) |
| OP-MET-06 | GET `/api/v2/metrics/source-quality` | R2 | FR-MET-07 | - | - | FR ACs: AC-MET-19 | via parent FR only |
| OP-MET-07 | GET `/api/v2/metrics/registry` | R1 | FR-MET-01, FR-MET-06 | - | - | FR ACs: AC-MET-01,14 | via parent FR only |
| OP-MET-08 | POST `/api/v2/metrics/combine` | R1 | FR-MET-02 | - | - | FR ACs: AC-MET-03..05 | via parent FR only |
| OP-POL-01 | GET `/api/v2/policies` | R1 | FR-POL-01 | - | - | FR ACs: AC-DEC-21; AC-POL-01..03,05,25 | via parent FR only |
| OP-POL-02 | POST `/api/v2/policies` | R1 | FR-POL-01, FR-POL-02, FR-POL-03 | - | - | FR ACs: AC-DEC-21; AC-GATE-08; AC-POL-01..03,05..10,25 | via parent FR only |
| OP-POL-03 | GET `/api/v2/policies/{policy_id}/versions/{vers | R1 | FR-POL-01, FR-POL-03 | - | - | FR ACs: AC-DEC-21; AC-GATE-08; AC-POL-01..03,05,09,25 | via parent FR only |
| OP-POL-04 | GET `/api/v2/rulesets` | R1 | FR-POL-04 | - | - | FR ACs: AC-CO-03; AC-POL-11..18 | via parent FR only |
| OP-POL-05 | GET `/api/v2/rulesets/{ruleset_id}/{version}` | R1 | FR-POL-04 | - | - | FR ACs: AC-CO-03; AC-POL-11..18 | via parent FR only |
| OP-POL-06 | POST `/api/v2/rules/evaluate` | R1 | FR-POL-04, FR-POL-06 | - | - | FR ACs: AC-CO-03; AC-POL-11..21; AC-REV-06 | via parent FR only |
| OP-POL-07 | GET `/api/v2/rules/divergence` | R2 | FR-POL-05 | - | - | FR ACs: AC-POL-24 | via parent FR only |
| OP-POL-08 | GET `/api/v2/cases/{case_id}/clocks` | R1 | FR-DEC-06, FR-POL-02 | - | - | FR ACs: AC-DEC-20; AC-POL-01,06..08 | via parent FR only |
| OP-REV-01 | GET `/api/v2/queues/exceptions` | R1 | FR-REV-02 | - | BEH-REV-01 | AC-REV-01..04 | via behaviour |
| OP-REV-02 | GET `/api/v2/cases/{case_id}/rule-trace` | R1 | FR-REV-01 | - | BEH-REV-02 | AC-REV-05..08 | via behaviour |
| OP-REV-03 | GET `/api/v2/search` | R2 | FR-REV-03 | - | BEH-REV-03, BEH-REV-06 | AC-REV-09..11,16 | via behaviour |
| OP-REV-04 | POST `/api/v2/drafts` | R2 | FR-REV-04 | - | BEH-REV-07 | AC-REV-18 | via behaviour |
| OP-RUN-01 | POST `/api/v2/runs` | R1 | FR-RUN-01, FR-RUN-02, FR-RUN-03 | - | - | FR ACs: AC-INT-26; AC-OBS-02; AC-RUN-01..10,13 | via parent FR only |
| OP-RUN-02 | GET `/api/v2/runs` | R1 | FR-RUN-02 | - | - | FR ACs: AC-INT-26; AC-OBS-02; AC-RUN-05,13 | via parent FR only |
| OP-RUN-03 | GET `/api/v2/runs/{run_id}` | R1 | FR-RUN-02 | - | - | FR ACs: AC-INT-26; AC-OBS-02; AC-RUN-05,13 | via parent FR only |
| OP-SEC-01 | POST `/api/v2/auth/login` | R1 | FR-SEC-01 | - | - | FR ACs: AC-DEC-13; AC-ID-08; AC-SEC-01..05,07 | via parent FR only |
| OP-SEC-02 | POST `/api/v2/auth/logout` | R1 | FR-SEC-01 | - | - | FR ACs: AC-DEC-13; AC-ID-08; AC-SEC-01..05,07 | via parent FR only |
| OP-SEC-03 | GET `/api/v2/audit/records` | R1 | FR-SEC-02 | - | - | FR ACs: AC-DEC-24; AC-GATE-22; AC-SEC-03,09..14,21 | via parent FR only |
| OP-SEC-04 | POST `/api/v2/audit/verify` | R1 | FR-SEC-02 | - | - | FR ACs: AC-DEC-24; AC-GATE-22; AC-SEC-03,09..14,21 | via parent FR only |
| OP-SEC-05 | POST `/api/v2/auth/reauth` | R1 | FR-GATE-03 | - | - | FR ACs: AC-DEC-17; AC-GATE-09,12; AC-OBS-06; AC-POL-02,18; AC-RUN-03 | via parent FR only |
| OP-SYS-01 | GET `/healthz` | R1 | FR-SEC-01 | - | - | FR ACs: AC-DEC-13; AC-ID-08; AC-SEC-01..05,07 | via parent FR only |

### S2T-7 Legacy behaviour preservation (Stage 7 CT-01..CT-18) [Verified Fact: plan; Unknown: suite]
| CT | Workflow | What it pins | Pri | Covered today (Stage 7) | Spec mentions | Explicit AC | Linked FR | Planned status |
|---|---|---|---|---|---|---|---|---|
| CT-01 | CW-01 | `priority()` truth table, 120 combinations (statuses x severities x {0,1,50000,5 | P1 | partially (2 asserts) | 7 doc(s) | AC-CO-03 | FR-CO-01, FR-POL-04 | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-02 | CW-01 | priority of all 125 shipped cases via the API (id, priority) and distribution ar | P1 | no | 2 doc(s) (range only) | AC-CO-03 | FR-CO-01, FR-POL-04 | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-03 | CW-01/02 | `manual_review_required()` truth table (20) and flag in `/api/cases/<id>` for CR | P1 | no | 4 doc(s) | AC-CO-03 | FR-CO-01, FR-POL-04 | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-04 | CW-02/10/13 | all HTTP responses of BB-02: status, content-type, body (or sha256), pagination  | P1 | no | 2 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-05 | CW-03/11 | `app.baseline` and `app.operational_report` outputs on shipped DB (and, as a sec | P1 | no (asserts `==125`, `>0`) | 1 doc(s) (range only) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-06 | CW-04 | source gateway: all 16 responses incl. failure modes, `0.9` schema cadence, mess | P1 | no | 3 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-07 | CW-04 | bridge: ingest sequence, checkpoint, idempotency, invalid handling (unknown key, | P1 | partially (valid + `bad`) | 3 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-08 | CW-05 | reconcile: 4 outcome rules, 1000-row cap, ordering, 10-run sequence, final statu | P1 | no | 3 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-09 | CW-06 | file import: first/second import, blank-amount storage, digest key | P2 | no | 3 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-10 | CW-07 | night shift: `processed`/`flagged_count`/`by_tenant` for limits 50, 100, 500, 12 | P1 | partially | 2 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-11 | CW-08 | Java totals/skips on tiny + bundled CSV, usage rc 2; cross-check against `decima | P1 | no | 4 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-12 | CW-08 | SQL report 1 rows and the 742,956.61 vs 622,826.44 discrepancy; report 2 rows | P1 | no | 1 doc(s) (range only) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-13 | CW-09 | JS threshold table (32 pairs), tolerance cases (26250/26250.01/negative/null/"ab | P1 | no | 4 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-14 | CW-12 | regeneration equivalence: `generate 125/4100`, `enterprise_legacy`, `historical_ | P2 | partially (counts only) | 1 doc(s) (range only) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-15 | CW-12 | readiness scripts: `workshop_check`, `offline_inventory`, `rehearse_local` outpu | P2 | no | 1 doc(s) (range only) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-16 | CW-14 | boundary/absence: POST/PUT/DELETE -> 501 on all routes; no module other than gen | P1 | no | 5 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-17 | cross | concurrency smoke: API + bridge + reconcile concurrently on one SQLite file - ch | P3 | no | 6 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |
| CT-18 | cross | docker/compose smoke (E2 tier) | P3 | no | 2 doc(s) | - | - | plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT |

Findings: only CT-01..CT-03 are linked by an explicit AC (AC-CO-03); `FR-GATE-01` cites CT-16 and `FR-POL-04` cites CT-01 in the PRD verification column. BEH-CO-01 / AC-CO-01 describe a `hub golden-compare` harness over CT-01..CT-16 but **CT-04..CT-18 have no AC that asserts them individually** [GAP-13-06]. CT-17 (concurrency) and CT-18 (docker) are P3 with no golden (Unknown U-07-05, Docker unavailable); CT-11 (Java) needs a JDK absent on the device (ACC-8).

## Evidence References
- `docs/12-specs/acceptance-criteria.md` (ACC-4..ACC-8), `docs/12-specs/features/*.md`, `docs/12-specs/api-contracts.md` (API-2, API-3), `docs/12-specs/error-handling-spec.md`, `docs/12-specs/contracts/`.
- `docs/07-repo-assessment/characterization-test-plan.md`, `baseline-test-results.md` (15/15 existing unittest tests pass in a sandbox, TR-01), `evidence/analysis/golden_mutation_replay_summary.txt`.
- `docs/13-traceability/evidence/tests_plan.csv`, `coverage.json`.

## Assumptions
- A-13-04 [Assumption]: AC-per-test 1:1 mapping; unit/service level is the default where no stronger keyword appears.
- A-13-05 [Assumption]: Stage 15 builds the tests on a BUILD branch (WB-04); Stage 16 runs them; Stage 26 re-runs independently. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-13-03: whether the Stage 12 example JSON files validate against their schemas (claimed in Stage 12, not re-executed here).
- U-13-04: CT-17 concurrency behaviour (U-07-05), Docker/3.12 behaviour (U-07-04).

## Unresolved Issues
- Operation-level contract tests are not explicit (GAP-13-04); SBR-level tags absent (GAP-13-03); CT-04..CT-18 not acceptance-linked (GAP-13-06); 27 error codes unasserted (GAP-13-12).

## Residual Risks
- R-13-03 Heuristic test levels may mis-classify (e.g. a criterion needing a running API marked service/unit); impact is planning only.
- R-13-04 Class A means "executable without an open decision", not "will pass".

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

