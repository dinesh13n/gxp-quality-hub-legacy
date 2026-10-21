---
stage: "25 — Governance + Compliance + Assurance"
artifact: "risk-acceptance-register.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md (OD-12, OD-14..OD-29)", "docs/18-delivery/delivery-risk-register.md", "docs/17-implementation-prd/{invalidated-assumptions,finalized-nfrs,release-boundaries}.md", "docs/16-repo-validation/{repo-quality-gate,remaining-debt-register,security-scan-summary}.md", "docs/10-architecture/architecture-risk-register.md", "docs/13-traceability/coverage-gap-register.md", "docs/02-stakeholders/stakeholder-conflicts.md", "hub/security/audit.py", "docs/25-governance/{compliance-control-matrix,governance-readiness}.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Only the Engagement lead (Dinesh Naik) can accept a risk (AP-7, TP-14). This stage accepts NOTHING. Part A lists acceptances that Dinesh already recorded in the OD log (quoted, not re-decided). Part B lists risks this stage proposes for his decision; their status is PROPOSED, not accepted. Likelihood / impact ratings are the agent's qualitative judgement (Inference), not measured.**

## Summary
Part A records **11 acceptances already made by Dinesh** (RA-01..RA-11, each with the OD entry). Part B proposes **12 risks for his decision** (RP-01..RP-12), each with the treatment this stage recommends, the compensating control that exists today, and a review trigger. Defaults when he does not answer: 'accepted open' with the compensating control kept, never silent acceptance. No risk in either part has an expiry date because no calendar exists; review triggers are stage-relative.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RR-A Acceptances already recorded by the Engagement lead (Verified Fact: OD entries)
| ID | Risk / deviation accepted | Recorded as | Conditions stated | Review trigger | Tag |
|---|---|---|---|---|---|
| RA-01 | Stage 16 CONDITIONAL PASS and its conditions (no cutover, exposure, activation or scheduler may cite it) | OD-24 (1) | carried to Stages 24 / 26 / 30 | Stage 26, Stage 30 | [Verified Fact] |
| RA-02 | Production runtime Python 3.12+ while code keeps the 3.10 floor (goldens remain 3.10.12-specific) | OD-24 (2) | CI on both (FAC-11) | Stage 27 | [Verified Fact] |
| RA-03 | Manual reviewer walkthroughs TST-REV-03/04/08 stay open (automated stand-ins) | OD-24 (3) | until Stage 26 TEVV | Stage 26 | [Verified Fact] |
| RA-04 | Stage 17 implementation baseline (PCH-47 / DQ-01); FR-REV-04 templates Could / R2; PNFR-13 reworded to existing fixtures (PCH-31); Stage 12 addendum IC-1..IC-8 as v0.2 content (DQ-03 / HAR-13) | OD-25 | — | Stage 26 | [Verified Fact] |
| RA-05 | Delivery plan including DW-17 (approval-gated authority switch; built at Stage 23; ships off); CLI errors keep current shape, documented as addendum | OD-26 | DW-17 only with a recorded human approval | Stage 23 merge | [Verified Fact] |
| RA-06 | S20-DEV-01..08, incl. DEV-01 (plain golden-compare marks module probes not run; exit 6 unchanged) and DEV-05 (non-add edits list reset per build stage); package cycles (4+6) and 10 functions over complexity 15 as debt | OD-27 | debt until Stage 27 | Stage 27 | [Verified Fact] |
| RA-07 | Source-contract `record_only` everywhere (per-source contracts at Stage 23); gateway retry bounded; `schema_version` 0.9 accepted with the allowed list open; late deliveries need a manual catch-up run; outside consumers of the 13 outputs Unknown | OD-28 | — | Stage 23, Stage 30 | [Verified Fact] |
| RA-08 | Exit-code clashes (2 and 9) documented in Stage 12 v0.2, numbers kept; FAC-13 policy withdrawal (ZH-10) approved as built | OD-29 | — | Stage 27 (CI scripts) | [Verified Fact] |
| RA-09 | Open product decisions OPD-01..03 (closed / resolved / approved, 48 h clock), OPD-04..06, OPD-11, retention, Zone H holders stay 'accepted open' | OD-22 | build ships safe defaults | per decision | [Verified Fact] |
| RA-10 | Test-once and cloud-regression split (laptop 3.10.12 for goldens; cloud 3.13 for the full hub regression); independent doc stages in parallel | OD-23 | checksum-gated copies | Stage 27 | [Verified Fact] |
| RA-11 | Rule sets ship inactive; `zone_h.holders` stays empty until Dinesh names real holders; DV/DEV preserve-or-fix open until Stage 30; baseline dataset 125 cases seed 4100 | OD-16, OD-17, OD-09 | activation needs a recorded human decision | Stage 30 | [Verified Fact] |

### RR-B Risks proposed for the Engagement lead's decision (NOT accepted)
Ratings: L = Low, M = Medium, H = High (agent judgement). Owner of the decision: **Engagement lead (Dinesh Naik)**.

| ID | Risk | Source | Likelihood / impact | Compensating control today | Recommended treatment | Review trigger |
|---|---|---|---|---|---|---|
| RP-01 | Single approver, no separation of duties for GxP-relevant changes; self-review of walkthroughs | GD-05, DR-10, DQ-17, ES-09; OD-24 | M / H | decisions logged in OD file; mutation gates; Stage 26 as a separate agent invocation (procedural independence only, A-18-OM-2) | Accept with condition: no CUT step, activation or exposure proceeds on a single-approver record without a note of this risk (DQ-17 default); revisit if a second human appears | before any CUT step; Stage 37 |
| RP-02 | Part 11 / GMP data integrity treated as framing only; reader may over-read "tamper-evident" as compliance | GD-11, A-08, DR-29, GAP-13-22, PR-14 | M / M | label on every artifact; PNFR-09 wording "framing, not Part 11"; this stage's no-claim rule | Accept framing-only with the rule "no 'compliant' / 'validated' wording" until Dinesh declares otherwise; qualified review if binding | Q-02-06 answer; OPD-16 |
| RP-03 | Audit anchor is an unsigned local file; tail records appended after the last anchor can be removed undetected; a compromised host can rewrite chain and anchor | RTD-29; R-SEC-1 (`hub/security/audit.py` docstring); ADR-005 residual | L (shadow, loopback) / H (if used as evidence) | `verify-audit`; anchor every N records and at end of run; tamper tests | Accept for shadow use; decide anchor location / strength at Stage 24 (OD-S12-18, DQ-09) | Stage 24; before any CUT-1 |
| RP-04 | No retention policy: hold-all; unbounded growth; no authority to dispose | OD-S12-09, OPD-09, RTD-30, OD-15 | M / M | insert-only triggers; no delete paths; checksum backup | Accept hold-all as interim; adopt `evidence-retention-policy.md` classes as a proposal only after Dinesh names periods | Stage 25 answer; Stage 37 |
| RP-05 | No CI gate: No-AI guard, release checklist and mutation gates are manual | RTD-01/02/14; RR-AI-1; PNFR-19 | M / M | orchestrator runs full regression before each merge (OD-23) | Accept until Stage 27 with the orchestrator's pre-merge run recorded in each OD entry | Stage 27 |
| RP-06 | Security-hardening gaps: header values and non-loopback bind refusal untested (H3, H5 survive); no TLS; unvalidated control values | SS-04, SS-06, SS-08; FAC-07/08 | L (loopback) / M | loopback bind, peer filter (H4 killed), CSRF (H2 killed) | Accept for loopback shadow; close via DW-14 / DW-15 / DW-19 before any exposure | Stage 23, Stage 24 |
| RP-07 | Privacy regime not assessed (DPDP / GDPR named); field classes are proposals | U-11-17, RTD-83, PNFR-12 | L (synthetic data only) / H (if real data) | `data_origin` = synthetic; STOP-04 on real data | Accept for synthetic scope; qualified review before any real data (HAR-15) | any move to real data |
| RP-08 | 11 behaviour deviations unapproved; golden-compare red by design; cutover cannot start | DV-01..DV-11; OD-S12-13 | H (blocks value) / M | register, exit 6, release checklist G1 | Keep 'accepted open'; decide per DV row at Stage 30 | Stage 30 |
| RP-09 | No Zone H holder: the human-gate is unexercised end to end; synthetic holder only in tests | OD-S12-06; A-10-07 | H (blocks pilot) / L (safe by default) | default refusal of all ZH actions | Keep 'accepted open'; if a test holder is wanted, record it as a test configuration, not an authorisation | Stage 30 |
| RP-10 | Stage 25 mapped controls before Stage 23 / 24 merged; DW-17 and security values may change the picture | `delivery-backlog.md` DW-13..DW-19 | M / M | v0.1 labels PLANNED controls as no evidence | Re-issue Stage 25 artifacts as v0.2 after Stage 23 and 24 merge (reconciliation list in `governance-readiness.md` GR-3) | Stage 23 and 24 merge |
| RP-11 | Legacy estate keeps its control gaps (no audit trail, no enforced disposition gate, weak hash, `0.0.0.0` bind in compose) while legacy runs | SS-05, CG-01..CG-05 (`control-points.md`) | H / M | legacy unchanged by decision (CG-4); hub in shadow | Accept as out of engagement scope; retire at cutover (Stage 30/41) | Stage 30, Stage 41 |
| RP-12 | Definitions of closed / resolved / approved and the 48 h clock have no owner; any KPI verdict rests on an unadopted definition | OPD-01..03, DR-20, DR-21 | H / M | verdicts return `not_available_no_adopted_policy` | Already 'accepted open' (RA-09); keep, do not allow a KPI claim without an adopted definition | Stage 34 |

### RR-C Acceptance procedure (proposed, not adopted)
1. Requester (agent) states the risk, evidence, compensating control and review trigger in the register.
2. Dinesh answers in his own message or via AskUserQuestion; the orchestrator appends an OD entry "Risk RP-nn accepted / accepted open / rejected" with conditions (HAR-11, TP-14).
3. The register row changes status only after that entry exists (EV-07, EO-4). No agent may mark a row ACCEPTED.
4. A review trigger firing re-opens the row; a CONDITIONAL PASS carrying a row to a later stage names that stage.

## Evidence References
OD entries cited per row; `delivery-risk-register.md` DLR-01..; `architecture-risk-register.md`; `remaining-debt-register.md`.

## Assumptions
- A-25-RR-1 [Assumption] An AskUserQuestion answer recorded by the orchestrator in the OD log is an acceptable form of risk acceptance (as practised since OD-08). Confirm: Engagement lead (Dinesh Naik).
- A-25-RR-2 [Assumption] No expiry dates are needed while no calendar exists (U-17-RB-2).

## Unknowns
- U-25-RR-1 Whether a real risk-acceptance authority (SH-06) would require a different form or a higher level.
- U-25-RR-2 Quantified likelihood or impact for any risk (no telemetry, OD-04).

## Unresolved Issues
- RP-01..RP-12 awaiting Dinesh's answer; default is 'accepted open' with the compensating control kept.

## Residual Risks
- RR-RA-1 Accepting many risks at once could be rubber-stamping (0B residual): recommend answering RP-01, RP-02, RP-04 first (decisions needed at Stage 25), the rest at their review triggers.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
