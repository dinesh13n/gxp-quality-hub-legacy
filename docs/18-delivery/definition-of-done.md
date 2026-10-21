---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "definition-of-done.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/14-transformation/transformation-gates.md (TG-2 CG-1..CG-11, TG-4 D0..D5)", "docs/17-implementation-prd/finalized-acceptance-criteria.md (FA-2 class A/B/C, FA-4 exit criteria)", "docs/12-specs/features/f10-coexistence-change-safety.md (G1..G10, BEH-CO-06)", "docs/14-transformation/feature-flag-plan.md FF-2", ".fde/orchestrator-decisions.md (OD-03a, OD-04, OD-13, OD-16, OD-21, OD-23)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. "Done" in this file means "the stated evidence exists at the stated path and was checked". It never means approved by the organisation, delivered to users, or cut over.**

## Summary
Six levels of Definition of Done: **DoD-W** (code work item), **DoD-D** (document / evidence-only work item), **DoD-Q** (human decision item), **DoD-I** (delivery increment), **DoD-C** (cutover step) and **DoD-S** (stage). Each level lists mandatory conditions and the evidence that proves them. A universal rule applies to all: **no item is done without its evidence in `evidence-checklist.md`, and a missing or failing piece of evidence keeps the item open** (stage prompt guardrail). Class-B tests count as done only in the mode they ran in; class-C tests give sandbox proxies only.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DoD-W Code work item (BUILD stages)
1. Branch `stage-NN-<slug>`; PR opened by the orchestrator; squash-merged only after checks (OD-01, OD-13). [Verified Fact]
2. New or changed behaviour has tests linked to AC / FAC / TST IDs; IDs not renumbered. [Verified Fact] Stage 13 SUM-5
3. Build agent ran its own new tests in a sandbox copy (`~/fde_sbx/<x>`), each device call < 180 s, sandbox deleted after (OD-03a, OD-16, OD-21, OD-23). [Verified Fact]
4. Orchestrator full hub regression green once before merge (cloud 3.13 workspace, OD-23); characterization harness CT-01..CT-16 green on the laptop 3.10.12 (CG-2). [Verified Fact]
5. golden-compare D5 = 0 (CG-9); D4 rows listed against the CUT step they block. [Verified Fact] TG-4
6. Class-B tests pass in both flag modes where the item introduces or touches a decision flag (FF-2 rule 2). [Verified Fact]
7. No-AI guard and egress tripwires green (CG-7, TST-CO-11/12); no new dependency (HAR-08). [Verified Fact]
8. Legacy paths and `data/` unchanged; `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after (CG-4, CG-5). [Verified Fact]
9. Shipped defaults stay safe (no adoption, activation, exposure, schedule, authority) unless the item carries a recorded decision with approval_ref (FF-2 rule 1/3). [Verified Fact]
10. Rollback described in the PR (L1 / L2 / L3) (CG-10). [Verified Fact]
11. Evidence files written under the stage folder with a SHA256SUMS entry; artifact headers per spine convention. [Inference]
12. Debt found during the item is registered (RTD / stage debt ID), not silently fixed or ignored. [Inference]

### DoD-D Document / evidence-only work item
1. Spine header (stage, artifact, version v0.1, date, author_agent claude-fde-agent, status, evidence_sources, supersedes) and the eight sections. [Verified Fact] stage prompts
2. Every finding tagged Verified Fact / Inference / Assumption / Unknown; synthetic figures labelled "synthetic, unvalidated". [Verified Fact] OD-04
3. Every claim cites a path, test, log, schema or OD entry; no invented person, date, cost or approval. [Verified Fact] OD-04
4. Earlier-stage artifacts not edited; corrections recorded as addenda in the current stage folder. [Verified Fact] OD-07, OD-10
5. Any execution was sandbox-only with checksum verification. [Verified Fact] OD-03a

### DoD-Q Human decision item
1. Answer recorded by the Engagement lead (Dinesh Naik) in `.fde/orchestrator-decisions.md` (OD-nn) with date, or recorded explicitly as "accepted open" with its default. [Verified Fact] OD-22 practice
2. Where the decision changes a flag or DV row: non-empty `approval_ref` in config / register, audited (CONFIG_CHANGED / POLICY_DECISION_RECORDED). [Verified Fact] FF-2
3. Linked class-B tests re-run in the decided mode (DW-24) and results recorded. [Verified Fact] A-17-FA-1
4. An agent may never record the decision itself or treat its own recommendation as approval (SH-02; HAR-11). [Verified Fact]

### DoD-I Delivery increment (DI-01..DI-12)
1. All its work items meet DoD-W / DoD-D; its entry decisions meet DoD-Q or are accepted open with the safe default. [Inference]
2. Increment exit evidence in `increment-plan.md` IN-2 exists. [Inference]
3. Common gate CG-1..CG-11 recorded (IN-5). [Verified Fact]
4. Stage gate artifact records outcome PASS / CONDITIONAL PASS / BLOCKED with reasons. [Verified Fact]

### DoD-C Cutover step (CUT-1..CUT-5, Stage 30)
1. FA-4 items 1-6 met for the step (observed probes; CI on production runtime; G1..G10 green; FAC-07/08/09; walkthroughs if reviewer UI exposed; step decisions recorded). [Verified Fact] FA-4
2. Every DV used by the step is `approved` with approval_ref (HAR-06); D5 = 0, D4 = 0 for that step. [Verified Fact] CO-2
3. Approval-gated authority switch exists and the L3 flip back to `shadow` was rehearsed (DW-17). [Verified Fact] `hub/config.py` refuses today
4. Consumer re-point target identified, or the step is recorded as "cannot run - consumer Unknown" (U-14-01). [Verified Fact] CF-1
5. Backup of hub store + anchor checksummed; legacy backup manifest verified (STOP-01). [Verified Fact] CO-2 step 2
6. Go / no-go recorded by the Engagement lead (Dinesh Naik). A step not run because a decision is accepted open is a valid, recorded outcome - it is NOT done. [Verified Fact]

### DoD-S Stage
All required artifacts exist at the stage path; gate outcome recorded; open items carry owner, stage-relative due point and risk; commit made by the orchestrator. [Verified Fact] stage prompts / OD-01

### DoD-X What never counts as done
- A test green only on a non-adopting default, cited as acceptance of the decided behaviour (class B). [Verified Fact]
- A class-C sandbox proxy cited as a production measurement. [Verified Fact]
- An agent self-assessment cited as human approval; a CONDITIONAL PASS cited as cutover approval (VS-3 condition 1). [Verified Fact]
- A golden-compare result that relies on `declared:` values (FAC-05). [Verified Fact]

## Evidence References
`docs/14-transformation/transformation-gates.md`; `docs/17-implementation-prd/finalized-acceptance-criteria.md`; OD log.

## Assumptions
- A-18-DD-1 [Assumption] Cloud regression on 3.13 (OD-23) remains acceptable evidence until CI on 3.12+ exists (DW-26). Confirm: Engagement lead (Dinesh Naik) (OD-23 approved the split).

## Unknowns
- None specific.

## Unresolved Issues
- DoD-C item 3 cannot be met until DW-17 is built.

## Residual Risks
- RR-DD-1 DoD relies on one human for every DoD-Q; no second-person check (DR-10 open) (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
