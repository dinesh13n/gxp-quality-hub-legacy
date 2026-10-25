---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "pattern-catalog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/adrs/ADR-001..018", "docs/14-transformation/coexistence-strategy.md", "docs/23-human-control/", "docs/26-tevv/release-thresholds.md", "docs/25-governance/", "docs/17-implementation-prd/release-boundaries.md", "docs/37-operating-model/target-operating-model.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL. No value claim (Stage 36: ROI NOT COMPUTABLE), no cutover scheduled, no risk accepted on Dinesh Naik's behalf.**

## Summary
Twelve architecture and delivery patterns used in the first use case, each with the evidence that it worked *here*, where a second use case could apply it, and the first-use-case debt that must not travel with it. A pattern is listed only if there is a cited, observed instance. "Worked here" means passed the repository's own tests in a sandbox; it is not evidence that the pattern produces value or that it works with real people.

## Findings
| ID | Pattern | Where used (evidence) | Observed result [Verified Fact] | Where a second use case could apply it [Inference] | Debt / assumption NOT to copy | Confidence |
|---|---|---|---|---|---|---|
| PT-01 | Strangler / build-beside-legacy, additive and read-only toward legacy | ADR-003; `hub/adapters/`; INC-01..09; TST-CO-05 checksum rc 0 before and after every run | Legacy and `data/` byte-identical after nine increments (PR-37) | Any use case with a legacy estate and no tolerance for behaviour change | Shadow period without cutover delivers no business value (RR-CO-1, `cutover-plan.md`); the sandbox-only evidence | Medium |
| PT-02 | Characterise first, then change | INC-01 harness; `docs/15-modernization/how-to-run-characterization-harness.md`; 14 of 15 legacy mutants survived the shipped suite (Stage 7) | Differences are visible; 9 proposed deviations registered, 0 approved | Adjacent legacy estates (AU-04, AU-05) | Goldens bound to Python 3.10.12; CT-13 Node drift; approval of DV-01..09 still open | Medium |
| PT-03 | Consequential switches ship OFF | OP-D; zone_h.holders EMPTY, disposition mode `none`, rule sets INACTIVE, scheduler OFF, contracts `record_only`, search OFF, loopback only (`release-boundaries.md`) | Nothing consequential can happen by default; verified by S26 attacks 80/80 refused | Every scale step: new site, feed or surface arrives dark and is enabled by a recorded human decision | "Off" is not "decided": each switch still needs a holder and a decision that do not exist | High |
| PT-04 | Inactive candidate rule sets + named human activation | ADR-007; OD-16 | As-found rules loaded without effect | Any rule that encodes an unowned business threshold | The three as-found rule sets; no rule owner | Medium |
| PT-05 | Approval-gated authority switch (CLI + `approval_ref`) | DW-17; OD-26, OD-31 | Works only with a recorded human approval; ships off | Making any new capability authoritative | Single approver (DQ-17); ZH-11 not adopted | Medium |
| PT-06 | Tamper-evident audit chain with insert-only ledger | ADR-005; S26 C03/C04; STG27 H01/H02 | Every tamper detected; chain verifies after concurrency | Any use case storing decisions or evidence | F-29-01; opt-in seal off (RS-03); audit growth ~81 bytes per unauthenticated request (RTR-12); hold-all retention | Medium-High |
| PT-07 | Source contract in `record_only` with a corrected natural key | OD-18, OD-28; `integration/source-contract-v1.json` | Intake in shadow; key (partner, record_kind, ref_id, source_ts) | Each additional partner feed (AU-02) | `enforce` never run; schema_version allow-list open; business_key alone is NOT an identity (OD-10) | Medium |
| PT-08 | Thresholds declared before results (TEVV) | `release-thresholds.md` TH-3; S26-DEV-06/07 disclosed | Gate computed by rule; CONDITIONAL PASS | Every scale step needs a pre-declared exit rule (this roadmap's gates) | Severity ratings are agent Inference (A-26-13); 12-mutant sample | Medium |
| PT-09 | Mutation sample to prove a control is tested | `s26_mutation_gate.py`; 13 of 13 killed after S27 | Found three surviving mutants that became findings | Before enabling any control at scale | Sample is small (RTR-13) | Medium |
| PT-10 | Zero-model-call / zero-egress tripwires | `hub/guards/`; E-groups at S26..S28 | Read 0 in every run | Keeps scaled units No-AI | Valid only while OD-08 holds | High |
| PT-11 | Sandbox-copy execution + checksum gating + "test once, orchestrator runs full regression" | OD-03a, OD-23 | Caught red groups at S24, S28, S31 that builders missed | Any shared repository with data files | Laptop disk and 180 s cap; one orchestrator | Medium |
| PT-12 | Default-answer logging: defaults recorded as ASSUMPTIONS, not approvals | OD-32 | Open items stay visible (D-27, D-28, D-31 lists) | Keeps scale decisions auditable | Risk of treating 'assumed' as 'decided' (SR-02) | Medium |

## Evidence References
Per-row. ADR files listed in `docs/10-architecture/adrs/`.

## Assumptions
- A-40-03 [Assumption] The patterns generalise to adjacent use cases; no second use case has tested that. Confirm by first adoption evidence; owner: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-03 Whether PT-01 is applicable to an adjacent use case with no legacy estate (AU-03 finance read surface).
- U-40-04 Whether the patterns survive more than one human decider (all evidence has one).

## Unresolved Issues
- PT-03 relies on holders and owners that do not exist; scaling it needs the role-holder decisions in `scale-out-backlog.md` SB-04..SB-07.

## Residual Risks
- Pattern transfer without its precondition (a holder, an owner) yields a control that looks present and is inert (SR-05).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
