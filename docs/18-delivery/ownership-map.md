---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "ownership-map.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/02-stakeholders/{stakeholder-map,decision-rights-map,approval-authority-map}.md (SH-01..SH-15, DR-01..DR-31)", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md (HAR-01..HAR-16)", ".fde/orchestrator-decisions.md (OD-01, OD-04, OD-12, OD-13, OD-23, OD-24)", "docs/17-implementation-prd/implementation-prd.md IP-7", "docs/18-delivery/delivery-backlog.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. No person other than the engagement lead exists (OD-04). Owners below are the engagement lead or agent roles; client roles are named only as they appear in repo documents and are unfilled. No owner is invented.**

## Summary
Every work item DW-01..DW-50 and decision DQ-01..DQ-19 has one accountable owner. **All human accountability sits with the Engagement lead (Dinesh Naik)**, the only evidenced decision-maker (SH-01; DR-01/DR-02). Execution is by three agent roles (all `claude-fde-agent`, no decision rights, SH-02): **Build agent** (BUILD-stage code and tests), **Stage agent** (DESIGN / VALIDATE / OPERATE stage documents and executions) and **Orchestrator** (merges, full regression, OD log, CI). Client roles SH-03..SH-15 would be consulted on many items, but no holder exists; each is recorded as a GAP and carried to Stage 37 (DR-30).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OM-1 Roles
| Role | Holder | Rights | Source | Tag |
|---|---|---|---|---|
| Engagement lead (A for every item; R for decisions and walkthroughs) | Dinesh Naik (SH-01) | approves HAR-01..HAR-16, decides OD / OD-S12 / OPD items, go / no-go | OD-01, OD-04, OD-12, OD-22, OD-24; A-0B-06 (wider authority provisional) | [Verified Fact] for recorded decisions; [Assumption] beyond |
| Orchestrator | claude-fde-agent | opens / merges PRs after checks (OD-13), runs full regression (OD-23), records OD entries, owns CI wiring execution | OD-13, OD-23 | [Verified Fact] |
| Build agent | claude-fde-agent per BUILD stage | writes code / tests on `stage-NN-*` branches; runs only its own new tests (OD-23) | OD-01, OD-23 | [Verified Fact] |
| Stage agent | claude-fde-agent per DESIGN / VALIDATE / OPERATE stage | writes its stage folder; executes in sandbox only | OD-03a | [Verified Fact] |
| Independent verifier | **GAP** - Stage 26 is run by a separate agent invocation, but no independent human exists | — | PR-10; RR-FA-1 | [Inference] |

### OM-2 Ownership by work item (R / A; C = consulted role, holder Unknown)
| Work items | R | A | C (unfilled roles, Stage 2) | Tag |
|---|---|---|---|---|
| DW-01 | Stage 19 agent | Engagement lead (Dinesh Naik) | — | [Verified Fact] OD-08 |
| DW-02, DW-03 | Orchestrator / Build agent | Engagement lead (Dinesh Naik) | — | [Inference] |
| DW-04, DW-05, DW-35 | Build agent | Engagement lead (Dinesh Naik) (HAR-06 for any approval) | SH-09 compliance, SH-04 application owner | [Verified Fact] HAR-06 |
| DW-06, DW-07, DW-08, DW-09 | Build agent | Engagement lead (Dinesh Naik) | SH-03 quality ops lead (FR-POL-01, FR-REV-01) | [Inference] |
| DW-10, DW-11, DW-12 | Build agent | Engagement lead (Dinesh Naik) | SH-07 integration lead, SH-14 source owners, SH-08 legacy technical owner | [Verified Fact] roles; holders [Unknown] |
| DW-13..DW-18 | Build agent / Stage 23 agent | Engagement lead (Dinesh Naik) (HAR-13 for DW-13) | SH-06 risk & security partner | [Verified Fact] |
| DW-19 | Build agent | Engagement lead (Dinesh Naik) | SH-06 | [Verified Fact] |
| DW-20 | Stage 25 agent | Engagement lead (Dinesh Naik) | SH-09, SH-11, SH-15 | [Verified Fact] |
| DW-21, DW-23 | Stage 26 agent | Engagement lead (Dinesh Naik) | — | [Verified Fact] |
| DW-22 | **Engagement lead (Dinesh Naik) performs** | Engagement lead (Dinesh Naik) | SH-13 reviewers (would be the real users) | [Verified Fact] OD-24; independence GAP |
| DW-24 | Build agent | Engagement lead (Dinesh Naik) | — | [Inference] |
| DW-25..DW-31 | Orchestrator / Build agent | Engagement lead (Dinesh Naik) (CI change, golden update) | SH-04 | [Verified Fact] |
| DW-32, DW-33 | Stage 28 / 29 agents | Engagement lead (Dinesh Naik) | SH-04, SH-10 operations | [Inference] |
| DW-34, DW-36..DW-41 | Stage 30 agent / Build agent | Engagement lead (Dinesh Naik) (go / no-go per step, HAR-11) | SH-03, SH-05 finance (CUT-4), SH-09, SH-15 (Zone H use) | [Verified Fact] RB-4 |
| DW-42 | Stage 31 agent | Engagement lead (Dinesh Naik) | SH-04 | [Inference] |
| DW-43..DW-50 | Stage agents | Engagement lead (Dinesh Naik) | per stage | [Inference] |
| DQ-01..DQ-19 | Engagement lead (Dinesh Naik) | Engagement lead (Dinesh Naik) | as in the source decision | [Verified Fact] IP-7 |

### OM-3 Ownership gaps carried (not filled)
| Gap | Affects | Source | Resolution point | Tag |
|---|---|---|---|---|
| Zone H holders (batch disposition, policy adoption, rule activation) | DW-07 use, DW-36, DW-37, DW-40 | DR-22, OD-S12-06; `zone_h.holders` [] | Stage 30 per step; Stage 37 | [Verified Fact] |
| Rule authority (3 divergent rule sets) | DW-37 | DR-23, OD-S12-04 | Stage 30 | [Verified Fact] |
| Definition of closed / resolved, 48 h clock | DW-36, DW-39, DW-45 | DR-20, OPD-01/02 | Stage 30 / 34 | [Verified Fact] |
| Source contract owner | DW-10, DW-38 | U-17-IP-2, OD-S12-11 | Stage 30 | [Unknown] |
| Legacy-output consumers | DW-11, DW-37..DW-39 | U-14-01 | Stage 21 / 30 | [Unknown] |
| Steady-state owner of repo, data, runbooks | DW-46, DW-47 | DR-30, GD-13 | Stage 37 | [Verified Fact] GAP |
| Parallel legacy-customer workflow owner | DW-49 | OPD-15 | Stage 37 | [Verified Fact] GAP |
| Second reviewer for GxP-relevant changes | all A cells | DR-10, GD-05 | Stage 25 (DQ-17) | [Verified Fact] open |

## Evidence References
`docs/02-stakeholders/stakeholder-map.md` (SH register, coverage gaps); `decision-rights-map.md` DR-01..DR-31; OD log.

## Assumptions
- A-18-OM-1 [Assumption] Dinesh remains the sole accountable owner for all remaining stages (A-0B-06 / A-ENG-02 provisional authority). Confirm: Engagement lead (Dinesh Naik).
- A-18-OM-2 [Assumption] A separate agent invocation for Stage 26 counts as procedural (not organisational) independence. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-18-OM-1 Holders of SH-03..SH-15; any receiving operations team.

## Unresolved Issues
- Independence of approvals and walkthroughs (single human).

## Residual Risks
- RR-OM-1 Concentration of all accountability in one person: decision latency directly gates W2-W5 (High for schedule-free throughput; Medium for quality).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
