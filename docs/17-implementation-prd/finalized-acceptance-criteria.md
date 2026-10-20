---
stage: "17 — Finalise Implementation PRD"
artifact: "finalized-acceptance-criteria.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/12-specs/acceptance-criteria.md (241 AC: AC-CO 15, AC-DEC 28, AC-GATE 22, AC-ID 17, AC-INT 29, AC-MET 21, AC-NFR 20, AC-OBS 9, AC-POL 25, AC-REV 19, AC-RUN 15, AC-SEC 21)", "docs/13-traceability/evidence/rtm.csv, tests_plan.csv", "docs/09-initial-prd/release-hypothesis.md (RH-1..RH-7)", "docs/15-modernization/modernization-summary.md (241/241 planned tests green)", "docs/16-repo-validation/{test-results,regression-results,behavior-difference-report,data-contract-results}.md", "docs/14-transformation/cutover-plan.md (CUT-1..CUT-5), transformation-gates.md (G1..G10)", ".fde/orchestrator-decisions.md (OD-22, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. "Green" means the planned test passed in a sandbox run of the shadow build; it is not acceptance by a stakeholder. No acceptance criterion is weakened here; changes are additions or wording corrections, each logged.**

## Summary
The **241 Stage 12 acceptance criteria** (95 positive, 105 negative, 41 edge) remain the acceptance basis for the 52 FRs and 20 PNFRs; every one has a planned test and all 241 planned tests are green (Stage 15 close-out; Stage 16: 396 ok, 1 skipped, 0 fail over 397 hub methods). Three qualifiers fix what "green" means: **35 class-B tests** pass only on the specified non-adopting defaults and must be re-run after the related decision; **9 class-C tests** give sandbox proxies only; **3 human walkthroughs** (TST-REV-03/04/08) stay open until Stage 26 TEVV (OD-24). This file adds **12 acceptance-criteria addenda** (FAC-01..FAC-12) for behaviour the build introduced or the Stage 16 validation found, restates **release hypotheses RH-1..RH-7** as evidence status, and defines **implementation-baseline exit criteria** that must be met before any cutover step.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FA-1 Acceptance-criteria addenda (proposed text; Stage 12 file not edited)
| ID | Requirement | Addendum criterion (Given / When / Then, abridged) | Reason | Test today | Status | Tag |
|---|---|---|---|---|---|---|
| FAC-01 | FR-INT-02/03 | Given two deliveries with the same (partner, record_kind, ref_id, source_ts), when contents are identical then NOOP_DUPLICATE; when they differ then REVISED_CONFLICT in quarantine with both versions kept | OD-18 identity key (PCH-03) | TST-INT-01..08 | Applied (decided key) | [Verified Fact] |
| FAC-02 | FR-INT-02 | Given a replay of a quarantined original, when processed then NOOP_DUPLICATE precedes validation (no second quarantine) | DEV-54 (PCH-05) | TST-INT, observation BD-02/03 | Applied | [Verified Fact] |
| FAC-03 | FR-INT-04 | Given binding `record_only`, a contract failure is recorded (`contract_missing`) and does not quarantine; given `enforce`, it quarantines; switching binding without a Zone H holder is refused | PCH-04 | TST-INT-13/14 | Applied | [Verified Fact] |
| FAC-04 | FR-POL-04 | Given a fresh store, `evaluate` without `ruleset_ref` returns `E-POL-NO-ACTIVE-RULESET`; activation without `POLICY_DECISION_RECORDED` by a holder returns `E-POL-DECISION-REQUIRED` | OD-16, DEV-35 (PCH-07) | TST-POL-*, observation | Applied | [Verified Fact] |
| FAC-05 | FR-CO-01 | golden-compare SHALL compare **observed** outputs of the built modules for every DV probe (no `declared:` new_source) | S16-D01 (PCH-26) | **fails today** (7 declared probes) | Applied as criterion; P1 work | [Verified Fact] |
| FAC-06 | FR-CO-01 | The deviation register SHALL list every known legacy-vs-hub difference: DV-07a wording, DV-09 label `MISSING_ENVELOPE_FIELD`, DV-10 (intake classification), DV-11 (DEV-29) - registered `proposed` | OD-24, PCH-35 | register check (not yet built) | Applied (registration; not approval) | [Verified Fact] |
| FAC-07 | FR-SEC-01 / PNFR-07 | Security response headers SHALL be asserted by exact value (CSP, X-Frame-Options, Referrer-Policy, nosniff, no-store) | SS-04, mutant H3 survived | none | Applied as criterion; Stage 23 | [Verified Fact] |
| FAC-08 | PNFR-08 | Given exposure approval and TLS keys in config, a non-loopback bind SHALL still be refused (current rule) | SS-08, mutant H5 survived; DEV-75 | none | Applied as criterion; Stage 23 | [Verified Fact] |
| FAC-09 | IC-7 schemas | Every hub object type written to the store SHALL validate against its (addended) Stage 12 JSON schema in an automated test | DC-02/DC-03 | Stage 16 script only (`s16_contracts.py`) | Applied as criterion; Stage 23 | [Verified Fact] |
| FAC-10 | CLI errors (all FRs with CLI) | CLI error output SHALL use the error-envelope shape `{"error": {code, message, correlation_id}}` or the spec SHALL record the CLI shape as an addendum | SS-07, S16-D12 | none | Applied as criterion (either fix) | [Verified Fact] |
| FAC-11 | NFR-RT | The characterisation harness and hub suites SHALL pass on the production runtime (Python 3.12+) against a reviewed re-baseline, and still pass on the 3.10 floor | OD-24 (PCH-36) | 3.10.12 reference green; 3.13 hub green; legacy goldens differ on 3.13 (ENV-1..6) | Applied as criterion; Stage 27 | [Verified Fact] |
| FAC-12 | PNFR-13 | Wording per PCH-31 (fixtures that exist) | DEV-89 | TST-NFR-13 green | Proposed | [Verified Fact] |

### FA-2 Per-requirement acceptance map (from `rtm.csv`; IDs unchanged)
| Req | Release | ACs (n) | AC IDs | Open decisions (class B) | Evidence classes | Status at 2c63b07 / 2f318be |
|---|---|---|---|---|---|---|
| FR-CO-01 | R1 | 10 | AC-CO-01 AC-CO-02 AC-CO-03 AC-CO-04 AC-CO-05 AC-CO-07 AC-POL-12 AC-POL-13 AC-POL-14 AC-POL-20 | OD-S12-04 | AB | green on specified defaults; re-run after decision |
| FR-CO-02 | R1 | 1 | AC-CO-08 | — | A | green |
| FR-CO-03 | R1 | 3 | AC-CO-09 AC-CO-10 AC-CO-15 | — | A | green |
| FR-CO-04 | R1 | 4 | AC-CO-11 AC-CO-12 AC-REV-07 AC-REV-17 | — | A | green |
| FR-DEC-01 | R1 | 6 | AC-DEC-01 AC-DEC-02 AC-DEC-03 AC-DEC-04 AC-DEC-22 AC-GATE-05 | OD-S12-05 | ABC | green on specified defaults; re-run after decision; class C = sandbox proxy only |
| FR-DEC-02 | R1 | 4 | AC-DEC-05 AC-DEC-06 AC-DEC-07 AC-DEC-08 | — | A | green |
| FR-DEC-03 | R1 | 3 | AC-DEC-09 AC-DEC-10 AC-DEC-11 | — | A | green |
| FR-DEC-04 | R1 | 3 | AC-DEC-12 AC-DEC-13 AC-DEC-14 | — | A | green |
| FR-DEC-05 | R1 | 7 | AC-DEC-15 AC-DEC-16 AC-DEC-17 AC-DEC-18 AC-DEC-19 AC-DEC-27 AC-DEC-28 | OD-S12-03 OD-S12-07 | B | green on specified defaults; re-run after decision |
| FR-DEC-06 | R1 | 2 | AC-DEC-20 AC-DEC-21 | OD-S12-15 | B | green on specified defaults; re-run after decision |
| FR-GATE-01 | R1 | 8 | AC-GATE-09 AC-GATE-11 AC-GATE-12 AC-GATE-13 AC-GATE-14 AC-GATE-21 AC-INT-24 AC-RUN-12 | — | A | green |
| FR-GATE-02 | R1 | 2 | AC-GATE-15 AC-GATE-16 | — | A | green |
| FR-GATE-03 | R1 | 9 | AC-DEC-17 AC-DEC-18 AC-GATE-09 AC-GATE-12 AC-OBS-06 AC-POL-02 AC-POL-18 AC-RUN-03 AC-SEC-08 | OD-S12-07 OD-S12-10 | AB | green on specified defaults; re-run after decision |
| FR-GATE-04 | R1 | 3 | AC-GATE-01 AC-GATE-02 AC-GATE-22 | OD-S12-06 | B | green on specified defaults; re-run after decision |
| FR-GATE-05 | R1 | 6 | AC-GATE-01 AC-GATE-03 AC-GATE-05 AC-GATE-06 AC-GATE-07 AC-GATE-08 | OD-S12-05 OD-S12-06 | B | green on specified defaults; re-run after decision |
| FR-GATE-06 | R1 | 4 | AC-GATE-18 AC-GATE-19 AC-GATE-20 AC-REV-08 | — | A | green |
| FR-ID-01 | R1 | 7 | AC-ID-01 AC-ID-02 AC-ID-06 AC-ID-09 AC-ID-10 AC-ID-11 AC-ID-12 | — | A | green |
| FR-ID-02 | R1 | 7 | AC-ID-02 AC-ID-03 AC-ID-04 AC-ID-05 AC-ID-06 AC-ID-07 AC-ID-08 | — | A | green |
| FR-ID-03 | R2 | 2 | AC-ID-15 AC-ID-16 | — | A | green |
| FR-ID-04 | R2 | 3 | AC-ID-13 AC-ID-14 AC-ID-17 | — | A | green |
| FR-INT-01 | R1 | 4 | AC-INT-01 AC-INT-02 AC-INT-03 AC-INT-29 | — | A | green |
| FR-INT-02 | R1 | 4 | AC-INT-04 AC-INT-05 AC-INT-06 AC-OBS-09 | OD-S12-17 | AB | green on specified defaults; re-run after decision |
| FR-INT-03 | R1 | 2 | AC-INT-07 AC-INT-08 | — | AC | green; class C = sandbox proxy only |
| FR-INT-04 | R1 | 10 | AC-INT-09 AC-INT-10 AC-INT-11 AC-INT-12 AC-INT-13 AC-INT-14 AC-INT-16 AC-INT-25 AC-INT-26 AC-INT-27 | OD-S12-11 | AB | green on specified defaults; re-run after decision |
| FR-INT-05 | R1 | 4 | AC-INT-11 AC-INT-17 AC-INT-18 AC-INT-19 | — | A | green |
| FR-INT-06 | R1 | 3 | AC-INT-15 AC-INT-20 AC-INT-21 | OD-S12-13 | AB | green on specified defaults; re-run after decision |
| FR-INT-07 | R1 | 4 | AC-GATE-13 AC-INT-22 AC-INT-23 AC-INT-24 | — | A | green |
| FR-INT-08 | R2 | 1 | AC-INT-28 | — | A | green |
| FR-MET-01 | R1 | 2 | AC-MET-01 AC-MET-02 | — | A | green |
| FR-MET-02 | R1 | 3 | AC-MET-03 AC-MET-04 AC-MET-05 | — | A | green |
| FR-MET-03 | R1 | 3 | AC-MET-06 AC-MET-07 AC-MET-08 | — | AC | green; class C = sandbox proxy only |
| FR-MET-04 | R1 | 6 | AC-INT-27 AC-MET-09 AC-MET-10 AC-MET-11 AC-MET-12 AC-MET-13 | — | A | green |
| FR-MET-05 | R1 | 2 | AC-MET-17 AC-MET-18 | — | A | green |
| FR-MET-06 | R1 | 2 | AC-MET-14 AC-MET-15 | — | A | green |
| FR-MET-07 | R2 | 1 | AC-MET-19 | — | A | green |
| FR-MET-08 | R2 | 1 | AC-MET-20 | — | A | green |
| FR-POL-01 | R1 | 6 | AC-DEC-21 AC-POL-01 AC-POL-02 AC-POL-03 AC-POL-05 AC-POL-25 | OD-S12-15 | AB | green on specified defaults; re-run after decision |
| FR-POL-02 | R1 | 4 | AC-POL-01 AC-POL-06 AC-POL-07 AC-POL-08 | — | A | green |
| FR-POL-03 | R1 | 5 | AC-GATE-08 AC-POL-03 AC-POL-09 AC-POL-10 AC-POL-25 | OD-S12-05 | AB | green on specified defaults; re-run after decision |
| FR-POL-04 | R1 | 9 | AC-CO-03 AC-POL-11 AC-POL-12 AC-POL-13 AC-POL-14 AC-POL-15 AC-POL-16 AC-POL-17 AC-POL-18 | — | A | green |
| FR-POL-05 | R2 | 1 | AC-POL-24 | — | A | green |
| FR-POL-06 | R1 | 4 | AC-POL-19 AC-POL-20 AC-POL-21 AC-REV-06 | OD-S12-04 | AB | green on specified defaults; re-run after decision |
| FR-REV-01 | R1 | 4 | AC-REV-05 AC-REV-06 AC-REV-07 AC-REV-08 | — | A | green |
| FR-REV-02 | R1 | 4 | AC-REV-01 AC-REV-02 AC-REV-03 AC-REV-04 | — | A | green |
| FR-REV-03 | R2 | 8 | AC-REV-09 AC-REV-10 AC-REV-11 AC-REV-12 AC-REV-13 AC-REV-14 AC-REV-15 AC-REV-17 | — | AC | green; class C = sandbox proxy only |
| FR-REV-04 | R2 | 1 | AC-REV-18 | — | A | green |
| FR-RUN-01 | R1 | 4 | AC-RUN-01 AC-RUN-02 AC-RUN-03 AC-RUN-04 | OD-S12-10 | AB | green on specified defaults; re-run after decision |
| FR-RUN-02 | R1 | 5 | AC-INT-26 AC-OBS-02 AC-RUN-05 AC-RUN-06 AC-RUN-13 | — | A | green |
| FR-RUN-03 | R1 | 4 | AC-RUN-07 AC-RUN-08 AC-RUN-09 AC-RUN-10 | — | A | green |
| FR-SEC-01 | R1 | 9 | AC-DEC-13 AC-ID-08 AC-SEC-01 AC-SEC-02 AC-SEC-03 AC-SEC-04 AC-SEC-05 AC-SEC-07 AC-SEC-08 | — | A | green |
| FR-SEC-02 | R1 | 10 | AC-DEC-24 AC-GATE-22 AC-SEC-03 AC-SEC-09 AC-SEC-10 AC-SEC-11 AC-SEC-12 AC-SEC-13 AC-SEC-14 AC-SEC-21 | OD-S12-06 | AB | green on specified defaults; re-run after decision |
| FR-SEC-03 | R2 | 4 | AC-ID-17 AC-REV-12 AC-SEC-19 AC-SEC-20 | — | A | green |
| PNFR-01 | R1 measure | 1 | AC-NFR-01 | — | C | green; class C = sandbox proxy only |
| PNFR-02 | R1 | 1 | AC-NFR-02 | — | C | green; class C = sandbox proxy only |
| PNFR-03 | R2 | 1 | AC-NFR-03 | — | C | green; class C = sandbox proxy only |
| PNFR-04 | R2 | 1 | AC-NFR-04 | — | C | green; class C = sandbox proxy only |
| PNFR-05 | R1 (rehearsal) | 1 | AC-NFR-05 | — | C | green; class C = sandbox proxy only |
| PNFR-06 | R1 measure | 3 | AC-NFR-06 AC-OBS-05 AC-REV-19 | — | A | green |
| PNFR-07 | R1 | 4 | AC-NFR-07 AC-SEC-01 AC-SEC-06 AC-SEC-17 | — | A | green |
| PNFR-08 | R1 | 7 | AC-INT-25 AC-NFR-08 AC-OBS-04 AC-SEC-06 AC-SEC-15 AC-SEC-16 AC-SEC-18 | OD-S12-09 | AB | green on specified defaults; re-run after decision |
| PNFR-09 | R1 | 3 | AC-NFR-09 AC-SEC-10 AC-SEC-11 | — | A | green |
| PNFR-10 | R1 (hold-all) | 3 | AC-DEC-03 AC-NFR-10 AC-SEC-18 | OD-S12-09 | AB | green on specified defaults; re-run after decision |
| PNFR-11 | R1 | 5 | AC-DEC-22 AC-DEC-23 AC-INT-04 AC-NFR-11 AC-OBS-09 | — | AC | green; class C = sandbox proxy only |
| PNFR-12 | R2 | 2 | AC-NFR-12 AC-SEC-19 | — | A | green |
| PNFR-13 | R1 | 5 | AC-DEC-25 AC-INT-22 AC-NFR-13 AC-REV-04 AC-REV-10 | — | A | green |
| PNFR-14 | R1 | 7 | AC-NFR-14 AC-OBS-01 AC-OBS-02 AC-OBS-03 AC-OBS-08 AC-RUN-05 AC-RUN-15 | — | A | green |
| PNFR-15 | R1 | 2 | AC-GATE-20 AC-NFR-15 | — | A | green |
| PNFR-16 | R1 | 3 | AC-MET-14 AC-NFR-16 AC-OBS-08 | — | A | green |
| PNFR-17 | R1 | 8 | AC-CO-13 AC-DEC-05 AC-GATE-15 AC-INT-20 AC-MET-21 AC-NFR-17 AC-POL-22 AC-REV-14 | — | A | green |
| PNFR-18 | R1 | 4 | AC-CO-11 AC-CO-12 AC-NFR-18 AC-OBS-06 | — | A | green |
| PNFR-19 | R1 | 3 | AC-CO-09 AC-CO-15 AC-NFR-19 | — | A | green |
| PNFR-20 | R1 | 3 | AC-MET-02 AC-MET-08 AC-NFR-20 | — | AC | green; class C = sandbox proxy only |

[Verified Fact] Table generated from `docs/13-traceability/evidence/rtm.csv` (script output, not hand-edited); "Status" is derived from the evidence class and the Stage 16 result that all planned tests pass. FAC-01..FAC-12 add to these sets; FR-REV-02 / FR-GATE-02 also depend on the open human walkthroughs (OD-24).

### FA-3 Release hypotheses (Stage 9 RH-1..RH-7) - evidence status
| RH | Pass criterion (Stage 9) | Evidence at 2f318be (synthetic) | Status | Tag |
|---|---|---|---|---|
| RH-1 Attributable, reconstructable decisions | events with actor/time/basis/evidence for sampled decisions; fold(events) = state | decision chains, projection mismatches 0 after backfill of 125; imported history is a proxy (PCH-12) | supported at mechanism level | [Verified Fact] |
| RH-2 Replay-safe, lossless intake | replay changes queue/totals by 0; raw = received | 67 NOOP, 0 changes; 10,983 raw items | supported on shipped data | [Verified Fact] |
| RH-3 Every figure declares its definition | 100 % tagged; mixing refused | tag/label on every figure; tags null because nothing adopted | supported (mechanism); content waits on OPD-01 | [Verified Fact] |
| RH-4 First honest baseline possible | time to close computable under >= 2 definitions | mechanism built; value `null` (no completed cycles in data) | **not yet shown** - needs data with closures | [Verified Fact] |
| RH-5 Month-end reconciles on one cut-off | single query = independent reference | 622,826.44 = `SUM(cases.amount)` reference; cut-off is a test parameter, none adopted | supported for the test cut-off | [Verified Fact] |
| RH-6 Zero unsafe action | negative suite: 0 unsafe actions | Zone H choke point, holders [], H1 killed; all negative tests green | supported in shadow | [Verified Fact] |
| RH-7 No-AI sufficient for T1/T2 | deterministic codes for all exception types; 0 model calls; no recorded shortfall | reason codes everywhere; tripwires 0; no RQ trigger | supported (synthetic; no user) | [Verified Fact] |
[Inference] None of RH-1..RH-7 says anything about value, time or cost (Stage 9 RH-C stands).

### FA-4 Implementation-baseline exit criteria (before ANY cutover step CUT-1..CUT-5)
1. FAC-05 met (observed probes) and golden-compare reports only DV rows whose preserve-or-fix decision is recorded (OD-S12-13, HAR-06) - Stage 30.
2. Harness, hub suites, No-AI check and mutation gates run in CI on the production runtime (FAC-11; RTD-01/02/14) - Stage 27.
3. Release checklist G1..G10 evaluable and green for the step (RTD-74).
4. FAC-07, FAC-08, FAC-09 tests exist and pass - Stage 23.
5. Human walkthroughs TST-REV-03/04/08 run (Stage 26, OD-24) for any step exposing the reviewer UI.
6. The step's human decisions are recorded (release-boundaries.md RB-4 per CUT step).
[Verified Fact] Stage 16 VS-3 condition 1 stands: nothing here or in Stage 16 is a cutover approval.

## Evidence References
`docs/12-specs/acceptance-criteria.md`; `docs/13-traceability/evidence/rtm.csv`; `docs/16-repo-validation/test-results.md` T-1..T-4.

## Assumptions
- A-17-FA-1 [Assumption] Class-B tests green on defaults are acceptable for the implementation baseline, provided they are re-run after each decision. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-17-FA-1 Results of class-B tests under decisions not yet taken.
- U-17-FA-2 Outcome of the human walkthroughs (Stage 26).

## Unresolved Issues
- FAC-05, FAC-07..FAC-11 have no passing test yet; FAC-12 proposed.

## Residual Risks
- RR-FA-1 241 green tests written and run by the build agent; independent re-run is Stage 26 (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
