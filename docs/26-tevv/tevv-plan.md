---
stage: "26 — TEVV + AI Red Teaming"
artifact: "tevv-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md OD-01..OD-32", "docs/18-delivery/acceptance-test-plan.md AT-09, AT-10", "docs/18-delivery/delivery-backlog.md DW-21..DW-24", "docs/18-delivery/evaluation-rubric.md ER-1..ER-5", "docs/24-security-privacy/threat-model.md", "docs/13-traceability/evidence/tests_plan.csv", "tests/hub/regression_groups.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing in this file is an approval. The product is No-AI (OD-08): there is no model, prompt, retrieval or agent to evaluate, so "AI red teaming" here means adversarial testing of the deterministic controls, prompt-injection-style hostile input, and proof that no model or network call happens (OD-08, Stage 18 ER-1/ER-2). `zone_h.holders` ships EMPTY; a clearly labelled test-only holder exists only inside sandbox copies. No result below was produced by a human observer unless a record says so; no walkthrough is signed.**

## Summary
Stage 26 is the independent TEVV (Test, Evaluation, Verification, Validation) of the deterministic Quality Hub after the BUILD stages 20, 21, 23 and 24 merged (main at `7c60c09`). It is a VALIDATE stage: it executes, observes and records. It does not change `hub/`, legacy code, `data/`, thresholds or datasets. The plan has six parts: (1) re-run everything that exists, per runtime available; (2) add an additive, pre-declared adversarial suite (groups S26 and E26, tests/hub only); (3) mutation gates for INC-05, INC-07 and INC-08 (DW-23); (4) prepare and rehearse the three human walkthroughs (DW-22) without signing them; (5) re-score the release hypotheses RH-1..RH-7 as business-outcome proxies; (6) issue a release gate against thresholds that were declared first (`release-thresholds.md`).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TP-1 Objective and independence [Verified Fact]
Objective per the stage prompt: an objective release gate from formal TEVV across deterministic behaviour, plus red teaming. Independence: this run is a separate agent run from the build agents (Stage 18 DW-21 "not the build agent run"). It is NOT independent of the single human who is performer, approver and walkthrough subject (DLR-02, RR-DB-1, OD-24): that gap is recorded in every gate decision and is not closable inside this engagement.

### TP-2 Work items covered [Verified Fact: docs/18-delivery/delivery-backlog.md]
| Item | What | How in this stage | Done when |
|---|---|---|---|
| DW-21 | Independent TEVV re-run | full hub regression (23 groups incl. S26/E26) on the laptop, Python 3.10.12; named set TST-NFR-07/08/09/12/13 and TST-SEC-01..21; characterization CT-01..CT-16; 3.12+/3.13 evidence is NOT producible on the laptop (A-26-02) | per-group result files in `evidence/`; 0 unregistered failure |
| DW-22 | Human walkthroughs TST-REV-03/04/08 | script + record template + sandbox builder + agent rehearsal; the walkthrough itself and the signature belong to Dinesh (OD-24, DQ-10) | rehearsal done; walkthrough records stay UNSIGNED and the gate says so |
| DW-23 | Mutation gates INC-05, INC-07, INC-08 | `evidence/s26_mutation_gate.py`: hostile one-line code changes in throwaway copies, targeted test groups, H3/H5 re-run | every sampled mutant KILLED or survivor registered with a test gap |
| DW-24 | Class-B re-run protocol | the 35 class-B tests run in the decided mode where a decision exists (OD-S12-12 runtime floor, OD-S12-17 key, OD-S12-09 hold-all); the others run on the specified defaults and are listed as "default mode" | table in `tevv-results.md` |

### TP-3 Dimensions and where each is evidenced [Verified Fact for the mapping; results in tevv-results.md]
| # | Dimension (stage prompt) | Applicable? | Evidence plan |
|---|---|---|---|
| 1 | Functional correctness | yes | full regression (476 methods at main), CT-01..CT-16, TST-NFR-07/08/09/12/13, acceptance map AC to test |
| 2 | Model/RAG quality and groundedness | NO (OD-08, ER-1) | replaced by the ER-2 tripwires (N1..N5) and the S26 no-model proof; keyword-search relevance ER-4 stays "not scorable" (OPD-12, no labelled set) |
| 3 | Hallucination and abstention | NO model; deterministic analogue | "unknown stays unknown" and "refuse instead of guess": rule engine without an active rule set, null-not-comparable metrics, REVISED_CONFLICT/quarantine outcomes, S26-B04 invariance of decision fields to free text |
| 4 | Agent/tool behaviour | NO agent (Stage 22 not applicable, OD-27); excessive agency and tool abuse apply to the hub's own tool surface | S26-A02..A04: service/integration tokens, mass assignment, spoofed identity headers, Zone H attempts by every actor kind |
| 5 | Security and privacy | yes | TST-SEC-01..21, Stage 24 suite re-run, S26-A*, S26-B*, leakage sweep, mutation gates |
| 6 | Resilience | yes, fault injection only | S26-C*: read-only/locked store, corrupt config, tampered audit, concurrency, clock skew. Class-C proxies (TST-NFR-01/02/05) and DR belong to Stages 28/29 (AT-12) and are NOT re-claimed here |
| 7 | Business-outcome proxies | proxies only | RH-1..RH-7 re-scored from mechanism evidence; no value, time or cost claim (Stage 9 RH-C) |

### TP-4 Method [Verified Fact]
1. Declare thresholds, metrics and datasets first (`release-thresholds.md`, `evaluation-metrics.md`, four dataset specs, `red-team-plan.md`); commit them before any new test runs. The commit sha is recorded in `tevv-results.md`.
2. Add the S26/E26 suite (additive under `tests/hub/`; the adversarial corpus is a hash-pinned data file).
3. Execute: sandbox copies only (OD-03a); `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` before and after; one group per device call (120 to 180 s cap).
4. Mutation gates in throwaway full copies; survivors are findings, not fixed.
5. Record results as observed. A failing test is a finding routed to remediation; no test, threshold or dataset is edited to make it pass.
6. Remediation: this stage does NOT fix defects (stage prompt). `remediation-evidence.md` records what was routed where and, for every finding, whether a fix exists (none expected in this stage).
7. Gate against `release-thresholds.md` as declared.

### TP-5 Environments [Verified Fact: probed on the laptop 2026-10-24/25]
Laptop VM: Python 3.10.12, Node v22.23.4, 2 CPUs, about 2.9 GB RAM, no python3.11/3.12/3.13. Cloud workspace (orchestrator, OD-23): Python 3.13 for the hub regression, no repo copy in this agent's environment. Consequence: the 3.12+/3.13 column of AT-09 is [Unknown] for this run (A-26-02); runtime parity (ER-3 Q8) cannot be scored 2.

### TP-6 Hard constraints honoured [Verified Fact: OD log]
Never run code or tests against working-tree `data/` (OD-03/OD-03a); backup manifest rc 0 before/after; no fabricated approvals, data, stakeholders or sign-offs (OD-04); `zone_h.holders` EMPTY in shipped config (OD-17, OD-31); legacy code and `data/` byte-identical (TST-CO-05); no push (no credentials); commit identity `Claude <noreply@anthropic.com>`; default-answer authority (OD-32) covers scope and sequencing only, not risk acceptance, holders or approvals.

## Evidence References
`docs/18-delivery/acceptance-test-plan.md` (AT-09, AT-10, AT-3 matrix), `docs/18-delivery/delivery-backlog.md` DW-21..DW-24, `docs/18-delivery/evaluation-rubric.md`, `docs/24-security-privacy/{threat-model,security-test-plan,security-test-results,residual-security-risks}.md`, `docs/13-traceability/evidence/tests_plan.csv`, `tests/hub/regression_groups.json`, `docs/16-repo-validation/evidence/s16_hub_mutation_gate.py`, `docs/23-human-control/evidence/s23_mutation_gate.py`.

## Assumptions
- A-26-01 [Assumption, OD-32 default] Sequencing: declare, then build tests, then execute; walkthrough = prepare + agent rehearsal + unsigned records. Confirm: Engagement lead (Dinesh Naik).
- A-26-02 [Assumption] 3.12+/3.13 runtime evidence comes from the orchestrator's cloud regression (OD-23), not from this run. Confirm: orchestrator.
- A-26-03 [Assumption, OD-32 default] Mutation sample = 10 INC-05/07/08 mutants plus H3 and H5 re-run (12 in total); a larger sample would be Stage 27 hardening. Confirm: Engagement lead.
- A-26-04 [Assumption] The test-only Zone H holders ("holder-1", "holder-2") already used by the existing suites are acceptable inside sandbox copies for the rehearsal; they are not configuration and not people.

## Unknowns
- U-26-01 Whether the Node patch drift (CT-13) is resolved by re-baselining the golden or pinning Node (S24-DEV-04, owner: Engagement lead).
- U-26-02 Behaviour on Python 3.12+/3.13 for this commit (owner: orchestrator cloud run).
- U-26-03 Any real-user reaction to the reviewer UI (no user exists; DW-22 is the only substitute).

## Unresolved Issues
- None blocking the plan. See `tevv-release-gate.md` for the gate-level gaps.

## Residual Risks
- RR-26-01 Single human is performer, approver and subject of the walkthroughs (DLR-02): independence is not achievable here.
- RR-26-02 A killed mutant shows a test can see that class of change, not that the class is exhausted (A-S24-TP-1).
- RR-26-03 Everything runs on synthetic data and a 125-case baseline; no production behaviour is claimed.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 26). |
