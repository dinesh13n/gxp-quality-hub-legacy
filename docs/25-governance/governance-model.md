---
stage: "25 — Governance + Compliance + Assurance"
artifact: "governance-model.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/02-stakeholders/{decision-rights-map,approval-authority-map,escalation-map,stakeholder-map}.md", "docs/00-preflight/operating-contract/{provisional-human-approval-rules,provisional-tool-agent-permissions,stop-conditions,change-control-rules,evidence-contract,open-governance-decisions}.md", "docs/18-delivery/{ownership-map,delivery-backlog}.md", "docs/17-implementation-prd/implementation-prd.md IP-7", "docs/10-architecture/adrs/ADR-002,005,006,007", "docs/14-transformation/feature-flag-plan.md", "hub/security/zone_h.py", "hub/ops/release.py", ".fde/orchestrator-decisions.md (OD-01..OD-29)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. This is a description of how governance works in this engagement and in the built system, not an organisational policy that anyone has adopted. No committee, board or client approver exists (OD-04). Owner of every human decision: Engagement lead (Dinesh Naik).**

## Summary
Governance here has **two layers**: (1) the **engagement layer**, run by one human (Engagement lead, Dinesh Naik) and one agent identity (`claude-fde-agent` in three roles), recorded in the OD log, branch/PR history and stage gates; and (2) the **product layer**, where the built hub enforces its own governance in code: Zone H for human-only decisions, hash-chained audit, inactive rule sets, safe-default flags, a deviation register, a release checklist and a No-AI tripwire. Layer 1 is evidenced and working but has **no separation of duties** (DQ-17 open). Layer 2 is strong on enforcement and **empty of named human holders** (`zone_h.holders` []). The model below makes the decision tiers, approval points, assurance lines and escalation explicit, and states what is missing instead of filling it.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### GM-1 Governance principles (each traced to a recorded decision)
| ID | Principle | Source | Tag |
|---|---|---|---|
| GP-1 | No fabrication: missing evidence is Unknown / Assumption owned by the Engagement lead | OD-04 | [Verified Fact] |
| GP-2 | A decision exists only when Dinesh answered or approved it (own message, or an "Approved" OD entry); an agent text naming him as approver is a proposal | `approval-authority-map.md` AG-5; HAR-11; TP-14 | [Verified Fact] |
| GP-3 | Open decisions may be answered "accepted open"; the build ships the safe default meanwhile | OD-12, OD-22; `feature-flag-plan.md` FF-2 rule 1 | [Verified Fact] |
| GP-4 | Disposition, QA release and e-signature stay with an authorised human outside the engagement; no component simulates them | HAR-12; STOP-07; ADR-006 | [Verified Fact] |
| GP-5 | The product is No-AI; AI coding assistants are development tooling | OD-08 | [Verified Fact] |
| GP-6 | Nothing consequential is on by default (no active rule set, no adopted policy, no schedule, loopback only, shadow beside legacy) | `release-boundaries.md` RB-0; SS-02 | [Verified Fact] |
| GP-7 | Compliance language stops at "framing"; no "compliant" or "validated" claim | A-08, DR-29, GAP-13-22 | [Verified Fact] |

### GM-2 Decision tiers
| Tier | Examples | Who decides | How recorded | Evidence it works |
|---|---|---|---|---|
| T0 Engagement direction | run order, stop-only-on-BLOCKED, runtime target, PRD baseline, AI vs No-AI | Dinesh | OD-01, -08, -22, -24 via AskUserQuestion, entered in `.fde/orchestrator-decisions.md` | OD-01..OD-29 | 
| T1 Delegated execution | merge after review, test-once / cloud regression, parallel doc stages | Orchestrator under a standing Dinesh approval | OD-13, OD-23 | PR #1..#11 |
| T2 Open product decisions | OD-S12-xx (19), OPD-01..16, DQ-01..19 | Dinesh (or "accepted open") | OD log; IP-7 | IP-7; DQ answers in OD-25..OD-29 |
| T3 Product-level human decisions (runtime) | batch disposition, QA release, close-exception, policy adopt / withdraw, rule-set activation, mode change, schedule enable (ZH-01..ZH-10) | A Zone H holder: **no holder exists** | audited Zone H event | `hub/security/zone_h.py`; AC-GATE-02 (every request refused on a fresh install) |
| T4 Agent self-assessed gates | stage gate status | Stage agent proposes; orchestrator accepts; Dinesh overrides | stage artifact + commit message `stage-NN: <title> v0.1 (<GATE>)` | CC-02, CC-08, TP-13 |

### GM-3 Approval points (where a human must act)
| Point | Trigger | Approver | Evidence form | State |
|---|---|---|---|---|
| AP-1 | HAR-01..HAR-16 actions | Dinesh | OD entry or his message | 3 confirmed or evidenced in effect (HAR-04 via OD-13, HAR-11 via OD-04, HAR-16 via OD-03a); others PROVISIONAL (see `operating-contract-governance-updates.md`) |
| AP-2 | Gate acceptance (CONDITIONAL PASS carried to later stages) | Dinesh | OD entry (OD-24, OD-25, OD-27, OD-28 are examples) | working |
| AP-3 | Deviation DV-xx approved (preserve-or-fix) | Dinesh (HAR-06) | register row `approved` with `approval_ref` | none approved; golden-compare exits 6 by design |
| AP-4 | Rule-set activation, policy adoption, mode change, schedule | Zone H holder (and Dinesh for OD-S12-xx) | audited Zone H event | not exercisable (no holder) |
| AP-5 | CUT-1..CUT-5 go / no-go | Dinesh (HAR-11) | go / no-go record per step | none can start (RB-4) |
| AP-6 | Exposure beyond loopback | Dinesh (HAR-05) + Stage 23/24 decisions | `exposure_approved` + `exposure_approval_ref` + TLS | not approved; bind refused even then (DEV-75) |
| AP-7 | Risk acceptance | Dinesh only | `risk-acceptance-register.md` + OD entry | no entry accepted by this stage |
| AP-8 | Re-qualification for AI | Dinesh (new decision) + HAR-08/09/10 | OD entry | not triggered |

### GM-4 Lines of assurance (what exists instead of an organisation)
| Line | Normal meaning | What exists here | Independence | Tag |
|---|---|---|---|---|
| 1st: operate controls | process owners | the hub's own controls (code) and the build agent | none (same author as tests) | [Verified Fact] |
| 2nd: oversight | risk / compliance function | none (SH-06, SH-09 unfilled); this stage's mapping is documentary | none | [Verified Fact] gap |
| 3rd: independent verification | audit / assurance | Stage 26 TEVV run as a separate agent invocation; human walkthroughs TST-REV-03/04/08 performed by Dinesh (OD-24) | procedural only (A-18-OM-2) | [Inference] |
| Compensating | automated detection | mutation gates (8 of 10 hub mutants killed, 15 of 15 legacy), golden-compare, release checklist, No-AI tripwire, checksum gates | independent of the author's intent, not of the author | [Verified Fact] |

### GM-5 Change control (engagement and product)
- **Engagement artifacts:** CC-06/07 versioned, errata not overwrite; Stage 12 files frozen, changes by addendum (IC-1..IC-8, HAR-13).
- **Code:** one `stage-NN-*` branch per BUILD, PR, orchestrator review and full regression (OD-23), squash-merge (OD-13); legacy paths unchanged since `baseline-as-found` (CG-4).
- **Rule sets and flags:** per `compliance-control-matrix.md` CM-3. Summary: rule sets arrive inactive; activation is a Zone H event with a recorded decision; decision flags ship at the safe value and move only by an `OD-S12-xx` answer; the code-enforced `approval_ref` / `CONFIG_CHANGED` audit for flag moves is **DW-17, planned at Stage 23** and must be re-checked when merged.
- **Behaviour changes:** characterisation baseline first (CC-05), deviation row proposed, golden-compare red until approved, release checklist G1 requires zero unapproved differences.

### GM-6 Escalation
Unchanged from Stage 2 (`escalation-map.md` ES-01..ES-09): stage agent -> orchestrator -> Dinesh; **no alternate approver exists (ES-09)**. Domain escalation (policy conflict, security event, audit finding) has **no route** (ES-20..ES-25 GAPs); Stage 29 / 37 should address it. [Verified Fact]

### GM-7 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| GF-01 | [Verified Fact] All decision and approval authority is one person; the OD log holds 30 rows (OD-01..OD-29 plus OD-03a; OD-03a, OD-06 and OD-07 are orchestrator records; OD-01, -04, -08, -09, -18, -22, -24..-29 record his approvals or answers), so the channel works, but there is no second reviewer and no alternate | OD-01..OD-29; ES-09; GD-05 | Latency and no separation of duties | High (throughput), Medium (quality) | High | DQ-17: second reviewer or accepted risk? |
| GF-02 | [Verified Fact] The product's human-only gate is enforced but unusable without a named holder | `zone_h.holders` [] (OD-17); AC-GATE-02 | Safe by default; no governance value delivered until holders are named | Medium | High | OD-S12-06 |
| GF-03 | [Verified Fact] Many 0B governance items are still PROVISIONAL because no one asked Dinesh item by item; several are now evidenced by later OD entries | `operating-contract-confirmations.md`; OD-13, OD-23 | Governance baseline is partly implicit | Medium | High | See `operating-contract-governance-updates.md` for the proposed confirmation list |
| GF-04 | [Inference] Governance quality depends on tests that nobody runs automatically (no CI) | RTD-01/02/14; RR-AI-1; PNFR-19 | A control could regress unnoticed between manual runs | Medium | High | Stage 27 |
| GF-05 | [Verified Fact] No client-side governance function exists to receive the hub: no steady-state owner, no incident owner, no compliance owner | DR-30, GD-13, ES-24, ES-25 | Handover would transfer a system without an owner | High (for any real adoption) | High | Stage 37 |

## Evidence References
See `evidence_sources`; mapping in `compliance-control-matrix.md`; owners in `accountability-map.md`.

## Assumptions
- A-25-GM-1 [Assumption] The AskUserQuestion answers recorded in the OD log are Dinesh's own words, so each counts as a valid approval form (EV-07). Confirm: Engagement lead (Dinesh Naik).
- A-25-GM-2 [Assumption] The decision tiers T0-T4 are a description of observed practice, not a policy he has adopted. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-25-GM-1 Whether an organisational change board, quality unit or equivalent would own any of AP-2..AP-7 in a real adoption.
- U-25-GM-2 Whether the escalation ladder is acceptable to any real stakeholder.

## Unresolved Issues
- DQ-17 (second reviewer); OD-S12-06 (holders); domain escalation routes; steady-state governance owner (Stage 37).

## Residual Risks
- RR-GM-1 Governance documents may be mistaken for adopted policy: Medium; status stays IN REVIEW until Dinesh records approval.
- RR-GM-2 Approval fatigue across a long run (0B residual): Medium; mitigated by conditions recorded in OD entries.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
