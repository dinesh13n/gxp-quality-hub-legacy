---
stage: "9 — Initial PRD / Product Intent"
artifact: "release-hypothesis.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/08-ai-qualification/intervention-hypothesis.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

R1 (the MVP) must prove **seven testable hypotheses**, mostly structural, because no baseline exists and no benefit can honestly be asserted (OD-07, IH-2: "P-NOAI produces the first measurable baseline rather than an improvement over an existing one"). R1 is **not** expected to prove time saved, cost saved or ROI; that is deferred to real baselines (Stage 34/36). All tests run on the shipped 125-case dataset (seed 4100, OD-09) in a sandbox copy.

## Findings
### RH-A Release hypothesis statement [Assumption]
> If the product (1) records every decision as an append-only, attributable event behind an unbypassable human gate, (2) takes intake non-destructively and idempotently with quarantine, (3) carries definitions, clocks and rules as owner-tagged configurable policy with no adopted default, and (4) reports every figure under a declared definition on one cut-off, then reviewers, finance, operations and compliance can look at the *same* case record and the *same* numbers, and a first measurable baseline exists - without any AI and without removing the human approval step. (Adapted from IH-1 and V0.)

### RH-B Hypotheses, pass criteria and falsifiers
| ID | Hypothesis | Pass criterion (provisional) | Success criteria / requirements | Fail criterion | Falsifier / note |
|---|---|---|---|---|---|
| RH-1 | Decisions become attributable and reconstructable | R1 produces, for 100% of sampled decisions in sandbox fixtures, an event with actor, time, basis, evidence ref and source; any case's state at a past time is reconstructable | SUC-02; FR-DEC-01..04 | Any sampled decision lacks evidence/source, or fold(events) != stored state | FH-1: real decisions already recorded externally -> shrink to mirror mode |
| RH-2 | Intake is replay-safe and lossless | Replaying the full intake set (incl. 67 REPLAY rows) changes queue and totals by 0; corrected replay lands in quarantine; raw count = received count | SUC-07; FR-INT-01..04; FAIL-04 | Any change in queue/totals on identical replay; any discarded item | - |
| RH-3 | Every figure declares its definition | 100% of closed/resolved/approved/cost figures carry a definition tag; attempt to mix tags is refused | SUC-03; FR-MET-01/02; FAIL-02 | Any untagged figure; any silent combination | - |
| RH-4 | The first honest baseline becomes possible | With receipt/ops-closed/evidence-complete timestamps recorded, time-to-close is computable under >=2 candidate definitions on the same population (K-04/K-05 move from unmeasurable to measurable) | SUC-04, SUC-05; FR-DEC-06, FR-MET-03; OD-07 | Still unmeasurable after R1 | Result is 'measurable', NOT 'improved' |
| RH-5 | Month-end totals reconcile on one cut-off | Totals from the single query equal an independent reference on the shipped data (resolving the 19.3% fan-out); ops and finance views use the same configured cut-off | SUC-10; FR-MET-04; RC-8 | Residual difference > 0 on agreed cut-off | Requires a configured test cut-off (OPD-08) |
| RH-6 | Zero unsafe action; human gate intact | Unsafe action count = 0 across the negative-test suite (service actors rejected for Zone H, no closure without evidence/exception, no inbound string alters a decision) | SUC-01; FR-GATE-01..06; FR-DEC-05; PNFR-13; FAIL-01 | Any unsafe action | Immediate stop (STOP-07) |
| RH-7 | No-AI is sufficient for the reviewer touchpoints | T1 (rule-trace) and T2 (reason-coded quarantine) cover 100% of the shipped exception types with deterministic output; zero model calls (tripwire); no stakeholder-recorded shortfall | FR-REV-01, FR-INT-06, FR-CO-04; OD-08; RQ-1..RQ-3 | A recorded shortfall meeting an RQ trigger | Re-open Stage 8 for that element only |

### RH-C What R1 deliberately does NOT claim
- [Verified Fact] No effort, cost or time-saving effect (S1 unmeasurable; no real data).
- [Verified Fact] No claim that 48 h, any definition or any rule is correct (RC-3/RC-4 are decisions).
- [Verified Fact] No claim about the real organisation (Stage 6 scope statement).

### RH-D Kill / reframe conditions [Inference]
- FAIL-06 (effect negligible after real baselining) and FH-1 (decisions already recorded elsewhere) are tracked; either triggers reframing at Stage 34 rather than continued build.
- RH-6 failure stops work (HAR-14 to proceed).

## Evidence References
`docs/08-ai-qualification/intervention-hypothesis.md` IH-1..IH-3; `docs/03-problem-value/success-criteria.md`; `docs/03-problem-value/value-hypothesis.md`.

## Assumptions
- A-09-01 Stage 3 BR/NFR/SUC items stand as *candidate* requirements; no stakeholder has accepted them (synthetic, unvalidated). Confirm: Engagement lead (Dinesh Naik).
- A-09-02 The R1 (MVP) / R2 (later) split is an agent proposal. Confirm: Engagement lead (Dinesh Naik).
- A-09-03 For FR-DEC-05 the structural presence of an evidence reference (not its sufficiency) is an acceptable default closure check; sufficiency is policy (OPD-07). Confirm: Engagement lead (Dinesh Naik).
- A-09-04 NFR numeric targets are archived working targets, not measured guarantees (`docs/operations-service-levels.md`). Confirm: Engagement lead (Dinesh Naik).
- A-09-05 Content statistics from the synthetic data (fixed-key feeds, short stubs) represent real content structure well enough for a No-AI product (A-08-14).
- A-09-06 The user roles in FR-SEC-01 are derived from documentary personas PER-01..PER-08, not observed users.

## Unknowns
- U-09-01 Definitions of closed/resolved/approved and the 48 h clock (OPD-01, OPD-02) - accepted open (Q-02-05 unanswered).
- U-09-02 Owner of approval-rule conflicts (OPD-04) and where batch disposition is recorded (OPD-05).
- U-09-03 Real volumes, timings, labour and cost (no production telemetry; OD-04). No benefit is quantified in this PRD.
- U-09-04 Whether any user wants natural-language document Q&A (U-S01); whether the real corpus would defeat keyword search (RQ-1..RQ-3).
- U-09-05 Retention policy (OPD-09); performance targets (OPD-14); owner of the parallel legacy-customer workflow (OPD-15).

## Unresolved Issues
- Pass criteria are provisional (A-03-12: thresholds are placeholders); RH-5 needs a test cut-off (OPD-08).

## Residual Risks
- A hypothesis set about structure is easy to satisfy and says little about value; value proof waits for real data.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
