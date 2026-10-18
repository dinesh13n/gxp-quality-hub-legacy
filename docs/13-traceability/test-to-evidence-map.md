---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "test-to-evidence-map.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/07-repo-assessment/baseline-test-results.md", "docs/13-traceability/evidence/tests_plan.csv", ".fde/stage-prompts/*.md (artifact_path)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Defines what artifact will prove each of the 241 planned tests, at which stage and folder, and how adequate that evidence is: class A 197, B 35 (decision-dependent), C 9 (sandbox proxy only). The only executed evidence today is the Stage 7 legacy baseline (15/15 unittest, goldens, 14/14 mutants). Outcome-level evidence for the 11 SUCs cannot exist until real data does.

## Findings
### T2E-1 Evidence classes and what counts as evidence [Verified Fact: definitions; Inference: adequacy]
| Class | Meaning | Tests |
|---|---|---|
| A | Executable now in a sandbox, no open decision: evidence = runner log + result JSON + hash manifest | 197 |
| B | Decision-dependent: evidence = both modes run with explicit TEST policies; the organisation's choice remains open | 35 |
| C | Sandbox/synthetic proxy only: evidence labelled "synthetic, unvalidated"; the real-world claim is not proved | 9 |
| D (outcome level) | Real operating data or stakeholder evidence required (value/KPI outcomes) | 0 tests: all 11 SUC outcomes fall here and are NOT obtainable (OD-04) |

**Evidence record contract (proposed for Stage 15/16)** [Assumption]: each executed test writes `evidence/<TST-ID>.log` plus a row in `results-<feature>.json` with: test id, AC id, git commit, dataset sha256 (must equal `c254649f...d70aa` for baseline tests), runner/interpreter versions, sandbox path, result (PASS/FAIL/ERROR/SKIP), duration, operator = agent id; the folder carries `SHA256SUMS-evidence.txt` (same convention as `docs/07-repo-assessment/evidence/SHA256SUMS-evidence.txt`). Post-run, `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` must pass (OD-03a).

### T2E-2 Evidence that exists today [Verified Fact]
- **Legacy baseline only.** `docs/07-repo-assessment/baseline-test-results.md`: 15/15 existing `unittest` tests pass on Python 3.10.12 in a sandbox (TR-01); `scripts/verify.sh` passes; goldens in `docs/07-repo-assessment/evidence/golden/*.json` regenerate byte-for-byte twice; 14/14 reference mutants killed (`evidence/analysis/golden_mutation_replay_summary.txt`). This supports FR-CO-01 / BR-11 / BR-13 as an *as-found* regression baseline.
- **Zero executed evidence for any new-module requirement.** The new Hub modules (`decision_events`, Zone H gate, rule service, intake, metrics, ...) do not exist; all 241 planned tests are NOT-RUN. No requirement in this stage is claimed as satisfied.
- Stage 12 asserted that the contracts (16 JSON Schemas, DDL, 14 examples) were validated; this stage did not re-run them (documentation-only) [Unknown until Stage 15/16].

### T2E-3 Evidence adequacy dimensions (Required Analysis 6)
- **Adequate by type [Inference]:** insert-only/immutability (database triggers + raw UPDATE/DELETE), Zone H gating (negative tests with service actors), idempotent replay, rule-table equivalence to as-found sets (goldens), static guards (no model import / egress), contract validation. These are deterministic and machine-checkable.
- **Inadequate to prove the stated claim [Verified Fact: ACC-8]:** availability 99.5 %, 06:00 completion, RTO 8 h / RPO 24 h (no environment; targets are unvalidated working targets); search ranking (3-base-sentence synthetic corpus); corrected-replay on real data (none in shipped data); event-derived time-to-close (no closure timestamps); concurrency on one SQLite file (uncharacterised, CT-17); Part 11 / GxP compliance (framing only, no claim).
- **Evidence that needs a human, not a script [Inference]:** FR-GATE-02 pack walk-through, FR-REV-04 narrative form, adoption decisions (ZH-05/06), role-holder configuration (OD-S12-05/06). Their evidence is a recorded Dinesh Naik decision, not a test log.

### T2E-4 Test -> evidence by stage
| Evidence stage | Folder (from stage prompt) | Meaning | Feature prefix | #tests | Expected evidence artifact (proposed) |
|---|---|---|---|---|---|
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | CO | 15 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-co.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | DEC | 28 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-dec.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | GATE | 22 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-gate.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | ID | 17 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-id.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | INT | 29 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-int.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | MET | 21 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-met.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | NFR | 5 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | POL | 25 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-pol.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | REV | 19 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-rev.json` + `SHA256SUMS-evidence.txt` |
| 16 | `docs/16-repo-validation/` | repo validation (functional run of the planned suite against the sandbox baseline) | RUN | 15 | `docs/16-repo-validation/evidence/<TST-ID>.log` + `results-run.json` + `SHA256SUMS-evidence.txt` |
| 25 | `docs/25-governance/` | governance (retention policy evidence) | NFR | 1 | `docs/25-governance/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 26 | `docs/26-tevv/` | TEVV (independent re-run, security/negative) | NFR | 5 | `docs/26-tevv/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 26 | `docs/26-tevv/` | TEVV (independent re-run, security/negative) | SEC | 21 | `docs/26-tevv/evidence/<TST-ID>.log` + `results-sec.json` + `SHA256SUMS-evidence.txt` |
| 27 | `docs/27-hardening/` | hardening (performance measurement) | NFR | 1 | `docs/27-hardening/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 28 | `docs/28-resilience/` | resilience (restore rehearsal, run completion) | NFR | 3 | `docs/28-resilience/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 30 | `docs/30-release/` | release (rollback rehearsal) | NFR | 1 | `docs/30-release/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 31 | `docs/31-observability/` | observability (log/metric/probe evidence) | NFR | 3 | `docs/31-observability/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |
| 31 | `docs/31-observability/` | observability (log/metric/probe evidence) | OBS | 9 | `docs/31-observability/evidence/<TST-ID>.log` + `results-obs.json` + `SHA256SUMS-evidence.txt` |
| 32 | `docs/32-finops/` | FinOps (zero-model-call tripwire) | NFR | 1 | `docs/32-finops/evidence/<TST-ID>.log` + `results-nfr.json` + `SHA256SUMS-evidence.txt` |

### T2E-5 Tests whose evidence is limited (class B and C: 44)
| Test | Class | Why evidence is limited | What the evidence can show | What it cannot show |
|---|---|---|---|---|
| TST-CO-14 | B | OD-S12-12 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-15 | B | OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-16 | B | OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-17 | B | OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-18 | B | OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-19 | B | OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-20 | B | OD-S12-15 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-21 | B | OD-S12-15 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-22 | C | ACC-8 concurrency on one SQLite file uncharacterised (CT-17) | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-DEC-26 | B | OD-S12-16 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-27 | B | OD-S12-03,OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-DEC-28 | B | OD-S12-03,OD-S12-07 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-01 | B | OD-S12-06 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-02 | B | OD-S12-06 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-03 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-04 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-05 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-06 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-07 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-08 | B | OD-S12-05 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-GATE-22 | B | OD-S12-06 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-INT-06 | B | OD-S12-17 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-INT-07 | C | ACC-8 corrected replay: none in shipped data | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-INT-12 | B | OD-S12-11 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-INT-13 | B | OD-S12-11 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-INT-14 | B | OD-S12-11 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-INT-15 | B | OD-S12-13 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-MET-08 | C | ACC-8 no real closure timestamps (OD-07) | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-NFR-01 | C | ACC-8 availability: no environment | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-NFR-02 | C | ACC-8 06:00 completion: no schedule | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-NFR-03 | C | PNFR target is an unvalidated working target (Assumption) | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-NFR-04 | C | PNFR target is an unvalidated working target (Assumption) | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-NFR-05 | C | ACC-8 RTO/RPO: unvalidated targets | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-OBS-07 | B | OD-S12-12 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-POL-19 | B | OD-S12-04 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-POL-20 | B | OD-S12-04 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-POL-21 | B | OD-S12-04 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-POL-23 | B | OD-S12-13 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-REV-15 | C | ACC-8 search quality: 3-sentence synthetic corpus | mechanism and sandbox measurement, labelled "synthetic, unvalidated" | real-world value / attainment of the stated target |
| TST-REV-16 | B | OD-S12-12 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-RUN-01 | B | OD-S12-10 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-RUN-02 | B | OD-S12-10 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-RUN-03 | B | OD-S12-10 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |
| TST-SEC-18 | B | OD-S12-09 | both modes of the configurable behaviour with explicit TEST policies | which mode the organisation chooses (decision open; accepted-open is legitimate) |

### T2E-6 PNFR evidence adequacy
| PNFR | Target (Stage 9) | Planned tests | Class mix | Evidence expected | Adequacy for the TARGET claim |
|---|---|---|---|---|---|
| PNFR-01 | 99.5% scheduled-hour availability | AC-NFR-01 | C | docs/28-resilience/ | Partial: proxy only, target is an unvalidated working target (Assumption) |
| PNFR-02 | By 06:00 local business time, 100% of scheduled nights in window | AC-NFR-02 | C | docs/28-resilience/ | Partial: proxy only, target is an unvalidated working target (Assumption) |
| PNFR-03 | Within 4 h of source event | AC-NFR-03 | C | docs/31-observability/ | Partial: proxy only, target is an unvalidated working target (Assumption) |
| PNFR-04 | Stale signal max 24 h | AC-NFR-04 | C | docs/31-observability/ | Partial: proxy only, target is an unvalidated working target (Assumption) |
| PNFR-05 | RTO 8 h; RPO 24 h (older planning assumptions); restore rehearsal pass | AC-NFR-05 | C | docs/28-resilience/ | Partial: proxy only, target is an unvalidated working target (Assumption) |
| PNFR-06 | UNKNOWN target: R1 must MEASURE p50/p95 latency on the 125-case baseli | AC-NFR-06; AC-OBS-05; AC-REV-19 | A | docs/16-repo-validation/,docs/27-hardening/,docs/31-observability/ | Measurement only: target is Unknown (OPD-14), no pass/fail possible |
| PNFR-07 | 100% of endpoints authenticated and authorised; 0 anonymous reads/writ | AC-NFR-07; AC-SEC-01,06,17 | A | docs/26-tevv/ | Adequate (mechanism, sandbox) |
| PNFR-08 | Secret scan finds 0; any non-loopback binding uses TLS and requires HA | AC-INT-25; AC-NFR-08; AC-OBS-04; AC-SEC-06,15,18 | AB | docs/16-repo-validation/,docs/26-tevv/,docs/31-observability/ | Adequate for mechanism; decision-dependent criteria need both modes (see T2E-5) |
| PNFR-09 | 100% of decision events with actor/time/basis; audit-chain verificatio | AC-NFR-09; AC-SEC-10 | A | docs/26-tevv/ | Adequate (mechanism, sandbox) |
| PNFR-10 | 0 deletions of case/evidence records while no retention policy is adop | AC-DEC-03; AC-NFR-10; AC-SEC-18 | AB | docs/16-repo-validation/,docs/25-governance/,docs/26-tevv/ | Adequate for mechanism; decision-dependent criteria need both modes (see T2E-5) |
| PNFR-11 | 0 duplicate effects over replay suite; 0 silent overwrites; 0 lost raw | AC-DEC-22; AC-INT-04; AC-NFR-11; AC-OBS-09 | AC | docs/16-repo-validation/,docs/31-observability/ | Mostly adequate; one or more criteria proxy-only (see T2E-5) |
| PNFR-12 | 100% of field classes covered by an access test | AC-NFR-12; AC-SEC-19 | A | docs/26-tevv/ | Adequate (mechanism, sandbox) |
| PNFR-13 | 0 effects on decision fields from the planted-string fixture set (86 f | AC-DEC-25; AC-INT-22; AC-NFR-13; AC-REV-04,10 | A | docs/16-repo-validation/,docs/26-tevv/ | Adequate (mechanism, sandbox) |
| PNFR-14 | 100% of runs have run records; every R1 KPI has a computed metric | AC-NFR-14; AC-OBS-01..03,08; AC-RUN-05,15 | A | docs/16-repo-validation/,docs/31-observability/ | Adequate (mechanism, sandbox) |
| PNFR-15 | 100% of rule outputs show rule trace and offer override with reason | AC-GATE-20; AC-NFR-15 | A | docs/16-repo-validation/ | Adequate (mechanism, sandbox) |
| PNFR-16 | 100% of KPIs documented; re-run gives identical value | AC-MET-14; AC-NFR-16; AC-OBS-08 | A | docs/16-repo-validation/,docs/31-observability/ | Adequate (mechanism, sandbox) |
| PNFR-17 | Identical input -> bit-identical output; characterisation goldens pass | AC-CO-13; AC-DEC-05; AC-GATE-15; AC-INT-20; AC-MET-21; AC-NFR-17; AC-POL-22; AC-REV-14 | A | docs/16-repo-validation/ | Adequate (mechanism, sandbox) |
| PNFR-18 | 0 model calls; 0 model-inference egress; Stage 32 tripwire = 0 | AC-CO-11; AC-NFR-18; AC-OBS-06 | A | docs/16-repo-validation/,docs/31-observability/,docs/32-finops/ | Adequate (mechanism, sandbox) |
| PNFR-19 | Rollback rehearsed; replay-safety gate passes before each release | AC-CO-09,15; AC-NFR-19 | A | docs/16-repo-validation/,docs/30-release/ | Adequate (mechanism, sandbox) |
| PNFR-20 | 100% of KPI outputs and reports labelled 'synthetic, unvalidated' whil | AC-MET-02,08; AC-NFR-20 | AC | docs/16-repo-validation/ | Mostly adequate; one or more criteria proxy-only (see T2E-5) |

### T2E-7 Success criteria (outcome-level) evidence
| SUC | Success criterion | Mechanism tests (ACs) | Outcome evidence needed | Available now? |
|---|---|---|---|---|
| SUC-01 | No unsafe action | 15 AC via FR-DEC-05, FR-GATE-01 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-02 | Source attribution | 9 AC via FR-DEC-01, FR-DEC-04 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-03 | Definition transparency | 8 AC via FR-MET-01, FR-POL-01 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-04 | Time to close under D-OPS and under D-EVID, reported separately | 9 AC via FR-DEC-06, FR-MET-03, FR-POL-02 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-05 | Time to evidence | 2 AC via FR-DEC-06 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-06 | Unmatched/orphan references | 5 AC via FR-INT-05, FR-MET-07 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-07 | Replay safety | 4 AC via FR-INT-02 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-08 | Reconciliation delay | 2 AC via FR-INT-08, FR-MET-07 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-09 | Backlog ageing and unresolved exception rate | 2 AC via FR-MET-05 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-10 | Month-end comparability | 6 AC via FR-MET-04 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |
| SUC-11 | Decision recorded | 6 AC via FR-POL-01 | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |

## Evidence References
- `docs/13-traceability/evidence/tests_plan.csv`, `coverage.json`.
- Stage prompts `artifact_path` (read by script): `.fde/stage-prompts/{15,16,25,26,27,28,30,31,32}_*.md`.
- `docs/07-repo-assessment/baseline-test-results.md`, `docs/07-repo-assessment/evidence/`.
- `docs/12-specs/acceptance-criteria.md` ACC-8; `docs/09-initial-prd/nfrs.md`; `docs/03-problem-value/success-criteria.md`.

## Assumptions
- A-13-06 [Assumption]: evidence folders follow the stage prompts' `artifact_path`; the sub-folder `evidence/` and the record contract in T2E-1 are proposed here. Confirm: Engagement lead (Dinesh Naik) at Stage 18.
- A-13-07 [Assumption]: classes A/B/C are computed from ACC-8 and from OD-S12 citations in the chain (AC -> BEH/SBR -> OD); an AC whose dependency is only implicit could be mis-classed A.

## Unknowns
- U-13-05: runner and tooling for the new suite (pytest vs unittest; coverage tool absent on the device, Stage 7 TQ-04). Resolution: Stage 14/15.
- U-13-06: stage numbers beyond 26 execute what, and when (Stage 28 environment for restore rehearsal; Docker unavailable).

## Unresolved Issues
- All 241 tests NOT-RUN; no evidence exists for any new-module requirement.
- 44 tests have limited evidence value by design (class B/C).
- Outcome-level SUC evidence unobtainable until real data exists (OD-04).

## Residual Risks
- R-13-05 Green sandbox results may be read as production assurance. Mitigation: every report carries "synthetic, unvalidated" (PNFR-20).
- R-13-06 Evidence produced only by the same agent that wrote the code; Stage 26 TEVV must re-run independently.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

