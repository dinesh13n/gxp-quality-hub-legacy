---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "acceptance-test-plan.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/13-traceability/evidence/tests_plan.csv (241 planned tests; execute_stage, fixture, evidence_class columns, counted by script in Stage 18)", "docs/13-traceability/evidence/rtm.csv", "docs/17-implementation-prd/finalized-acceptance-criteria.md (FAC-01..FAC-12, FA-2, FA-4)", "docs/16-repo-validation/{test-results,regression-results,security-scan-summary}.md", "docs/16-repo-validation/evidence/{s16_observe.py,s16_contracts.py,s16_hub_mutation_gate.py,hub-mutation.json}", "tests/hub/ (72 files; 397 test methods by grep at 40b2762)", "tests/characterization/ (CT harness, goldens, mutants.json)", ".fde/orchestrator-decisions.md (OD-21, OD-23, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Test data are synthetic fixtures only (OD-09: FX-BASE125 = shipped 125 cases, seed 4100). No real data, user or environment exists. Results described as "expected" here do not exist yet.**

## Summary
Acceptance for the remaining delivery is organised in **14 acceptance suites (AT-01..AT-14)**. They re-use the 241 Stage 12/13 tests (IDs unchanged), add tests for the Stage 17 addenda FAC-05..FAC-11 and the proposed FAC-13, add tests for new scope DW-17, and schedule the 45 tests whose evidence stage is after Stage 16 (Stage 25: 1, 26: 26, 27: 1, 28: 3, 30: 1, 31: 12, 32: 1). Three runtimes are used: laptop Python 3.10.12 (reference for goldens), cloud 3.13 (full hub regression, OD-23), and CI Python 3.12+ (production target, OD-24; does not exist yet - DW-26).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AT-1 Test datasets and fixtures
| Fixture | Content | Planned tests using it | Provenance / control | Tag |
|---|---|---|---|---|
| FX-BASE125 | copy of `data/legacy.sqlite3` (125 cases, seed 4100, sha256 `c254649f…d70aa`) + lake copy | 26 | hash-gated; sandbox copy only (OD-03a, OD-09) | [Verified Fact] |
| FX-UNIT-SYNTHETIC | in-memory / temp DB built by tests | 158 | test-generated | [Verified Fact] |
| FX-SYNTHETIC-FEED | synthetic intake items | 27 | test-generated | [Verified Fact] |
| FX-TESTPOLICY | test policies / rule sets (never adopted in product) | 24 | test-generated | [Verified Fact] |
| FX-FRESHINSTALL | empty hub store, shipped defaults | 19 | test-generated | [Verified Fact] |
| FX-SANDBOX-COPY | full repo copy outside working tree | 4 | OD-03a | [Verified Fact] |
| FX-PLANTED | planted-string fixtures (86 / 22 / 44) | 3 | G9 | [Verified Fact] |
| Stage 7 goldens | `docs/07-repo-assessment/evidence/golden/{api,batch,lib}_golden_run1.json` | CT-01..CT-16 | frozen; re-baseline only by reviewed `--update-golden` (CT-H4) | [Verified Fact] |
| 3.12+ golden set (to create) | versioned new files, Stage 7 files untouched | CT-01..CT-16 on 3.12+ | DQ-07 approval | [Assumption] |
| Labelled search question set | does not exist (OPD-12) | none; FR-REV-03 quality unassessable | DQ-16 | [Unknown] |
[Verified Fact] Counts by script over `tests_plan.csv` (a test may cite more than one fixture).

### AT-2 Acceptance suites
| Suite | Scope | Tests | Work items | Stage | Runtime(s) | Pass criterion | Evidence path | Tag |
|---|---|---|---|---|---|---|---|---|
| AT-01 Regression baseline | full hub suite + harness | 397 hub methods (396 ok / 1 skipped at 2c63b07); CT-01..CT-16; TST-CO-03 included | DW-02, DW-03 | every build stage | cloud 3.13; laptop 3.10.12 | 0 fail; method count = discovered count; D5 = 0 | `docs/<stage>/evidence/` regression log | [Verified Fact] Stage 16 counts |
| AT-02 Observed comparison | golden-compare on built modules | TST-CO-01, TST-CO-02 + new FAC-05 test; register test FAC-06 | DW-04, DW-05 | 20 | laptop 3.10.12 | no `declared:` source; DV-01..DV-11 matched as D4; exit 6 while unapproved | `docs/20-application/evidence/` | [Verified Fact] FAC-05/06 |
| AT-03 Structural safety | Zone H single check, imports, cycles | TST-GATE-01..22, TST-SEC-01..21; mutant H1 | DW-06 | 20 | cloud + laptop | green; H1 KILLED; import report | `docs/20-application/evidence/` | [Inference] |
| AT-04 R1 gap closure | withdrawal, trace producer, CLI errors | AC-POL-09/10 + FAC-13 (proposed); AC-REV-05..08; AC-GATE-18..20; FAC-10 | DW-07..DW-09 | 20 | cloud + laptop | green | `docs/20-application/evidence/` | [Inference] |
| AT-05 Integration evidence | contracts, adapters, legacy paths | TST-INT-09..16; TST-CO-04, TST-CO-05 | DW-10..DW-12 | 21 | laptop 3.10.12 | report reproducible; 0 legacy writes | `docs/21-integration/evidence/` | [Verified Fact] |
| AT-06 Control boundaries & security tests | header values, bind refusal, schemas, authority switch, error registry | new tests FAC-07, FAC-08, FAC-09 (16 schemas), DW-17 (both modes), registry diff | DW-13..DW-17 | 23 | cloud + laptop | all green; mutants H3, H5 KILLED | `docs/23-human-control/evidence/` | [Verified Fact] SS-04/SS-08 |
| AT-07 Security values | TST-SEC-01..21 after value decisions; RETAINED_TABLES | 21 + new | DW-19 | 24 | cloud + laptop | green; scan rc 0 | `docs/24-security-privacy/evidence/` | [Verified Fact] |
| AT-08 Governance | TST-NFR-10 | 1 | DW-20 | 25 | laptop | green | `docs/25-governance/` | [Verified Fact] stage 25 |
| AT-09 Independent TEVV | Stage-26 set: TST-NFR-07/08/09/12/13, TST-SEC-01..21 (TST-SEC-18 class B); full re-run; mutation INC-05/07/08 | 26 + 397 + mutants | DW-21, DW-23 | 26 | 3.10.12, 3.13, 3.12+ when available | 0 fail or registered; mutants KILLED or registered | `docs/26-tevv/evidence/` | [Verified Fact] |
| AT-10 Human walkthroughs | TST-REV-03 (edge), TST-REV-04 (negative), TST-REV-08 (positive) | 3 | DW-22 | 26 | laptop loopback | AC-REV-03/04/08 observed by the Engagement lead (Dinesh Naik); record signed | `docs/26-tevv/` | [Verified Fact] OD-24 |
| AT-11 CI / runtime | suites in CI on 3.12+ and 3.10; reviewed goldens; FTS5; TST-NFR-06 | all + CT on both | DW-25..DW-31 | 27 | CI 3.12+, 3.10 | FAC-11 met | CI run log in `docs/27-hardening/evidence/` | [Verified Fact] FAC-11 |
| AT-12 Resilience & continuity | TST-NFR-01, -02, -05 (class C), CT-17; tabletop | 3 + CT-17 | DW-32, DW-33 | 28-29 | laptop sandbox | labelled sandbox proxies; tabletop record | `docs/28-resilience/`, `docs/29-incident-bcdr/` | [Verified Fact] class C |
| AT-13 Release readiness per CUT step | G1..G10; TST-NFR-19; TST-CO-10, TST-CO-15; step-specific re-runs (RB-4); L3 rehearsal | per step | DW-34..DW-41 | 30 | 3.12+ CI + laptop | DoD-C met or step recorded "not run" | `docs/30-release/evidence/` | [Verified Fact] |
| AT-14 Observability & FinOps | TST-NFR-03/04 (C), TST-NFR-14, TST-OBS-01..09 (TST-OBS-07 class B); TST-NFR-18 | 12 + 1 | DW-42, DW-43 | 31, 32 | laptop / CI | green; `model_calls_total = 0` | `docs/31-observability/`, `docs/32-finops/` | [Verified Fact] |

### AT-3 Class-B re-run matrix (DW-24)
[Verified Fact] 35 class-B tests depend on: OD-S12-03, -04, -05, -06, -07, -09, -10, -11, -12, -13, -15, -17 (per `rtm.csv` / FA-2). When a decision is recorded (DoD-Q), the linked tests re-run in the decided mode within the next build increment; a failure creates a rework item, never a silent test change. OD-S12-17 (decided, OD-18) and OD-S12-12 (decided, OD-24) tests already run in the decided mode for the key; the 3.12+ part of OD-S12-12 is covered by AT-11.

### AT-4 What acceptance cannot show (limits)
| Limit | Evidence | Consequence | Tag |
|---|---|---|---|
| 9 class-C tests (TST-DEC-22, TST-INT-07, TST-MET-08, TST-NFR-01..05, TST-REV-15) give sandbox proxies only | tests_plan.csv | no production performance / volume claim | [Verified Fact] |
| No completed closure cycles in FX-BASE125 | K-04/K-05 null; RH-4 not shown | time-to-close acceptance cannot be shown on baseline data | [Verified Fact] |
| No labelled search set | OPD-12 | FR-REV-03 quality unassessed | [Verified Fact] |
| Walkthrough performer = approver | OD-24; single human | no independent user acceptance | [Verified Fact] |

### AT-5 AI evaluation datasets
Not applicable: the product is No-AI (OD-08). The only AI-related acceptance is the absence control (TST-CO-11, TST-CO-12, TST-NFR-18). See `evaluation-rubric.md`. [Verified Fact]

## Evidence References
`docs/13-traceability/evidence/tests_plan.csv`; `docs/17-implementation-prd/finalized-acceptance-criteria.md`; `docs/16-repo-validation/evidence/`.

## Assumptions
- A-18-AT-1 [Assumption] New test IDs for FAC-05..FAC-13 and DW-17 are allocated by the build agent in the TST-<area>-NN pattern continuing existing numbering, never reusing an ID. Confirm at Stage 23 addendum (DQ-03).
- A-18-AT-2 [Assumption] A 3.12+ interpreter will be available to CI (GitHub-hosted runner); none exists on the laptop (Stage 14 E-4).

## Unknowns
- U-18-AT-1 Whether the legacy estate (Node / JDK / SQLite-dependent float sums) can be re-baselined deterministically on 3.12+ (ENV-1..6).

## Unresolved Issues
- FAC-05, FAC-07..FAC-11 have no passing test yet; FAC-12 and FAC-13 are proposals.

## Residual Risks
- RR-AT-1 All tests are authored by the build agent; Stage 26 independence is procedural only (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
