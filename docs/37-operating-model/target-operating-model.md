---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "target-operating-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/{governance-model,accountability-map,risk-acceptance-register}.md", "docs/02-stakeholders/{stakeholder-map,decision-rights-map,escalation-map,operating-contract-confirmations}.md", "docs/18-delivery/ownership-map.md", "docs/00-preflight/operating-contract/provisional-operating-contract.md", "docs/33-vendor-risk/vendor-inventory.md", "docs/26-tevv/", ".fde/orchestrator-decisions.md OD-01..OD-33"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
This is the target operating model (TOM) for the gxp-quality-hub after the engagement. The honest result: **the operating model can be fully designed, but it cannot be staffed or accepted from repository evidence.** One human exists (Dinesh Naik, OD-04). No receiving team, support function, quality unit, security function, finance owner or compliance owner exists in any repo document as a person or an accepting party. This TOM therefore defines **roles, responsibilities, tiers, gates and routes**, places each production asset with an **owner of record**, and labels each placement with an ownership state. **Zero steady-state ownerships are ACCEPTED.** Every client-side role is VACANT. Dinesh is the interim owner of record for everything because he is the only evidenced decision-maker (OD-01, OD-04, OD-12, OD-22, OD-24..OD-32), not because he has accepted a steady-state operating role.

Gate for this stage: **CONDITIONAL PASS** (see `operating-contract-closure.md` section OC-4). Two literal completion conditions are not met and cannot be met by an agent: (a) accepted owners for every production asset, (b) formal closure of the Stage 0B contract. Both need Dinesh's recorded decision.

## Findings
### TOM-1 Operating principles (inherited, not new)
| ID | Principle | Source | Tag |
|---|---|---|---|
| OP-A | A decision exists only when Dinesh answered or approved it; an agent text naming him is a proposal | GP-2 (`governance-model.md`); AG-5; HAR-11; OD-04 | [Verified Fact] |
| OP-B | Disposition, QA release and e-signature stay with an authorised human outside the engagement; no component simulates them | HAR-12; STOP-07; ADR-006 | [Verified Fact] |
| OP-C | The product is No-AI; model, prompt and retrieval ownership is N/A and a tripwire guards that | OD-08; `hub/guards/no_ai.py` | [Verified Fact] |
| OP-D | Nothing consequential is on by default (inactive rule sets, empty Zone H holders, loopback only, scheduler off) | OD-16, OD-17, OD-19, OD-20; `release-boundaries.md` | [Verified Fact] |
| OP-E | Compliance language stops at "framing"; no "compliant" claim | OD-30 (GD-11); DR-29 | [Verified Fact] |
| OP-F | No unassigned ownership is shown as assigned (Stage 37 rule) | Stage 37 prompt, Exclude | [Verified Fact] |

### TOM-2 Ownership states used in every Stage 37 artifact
| State | Meaning | Count of steady-state assets in this state |
|---|---|---|
| ACCEPTED | A recorded statement (OD entry or Dinesh's own message) that a named party accepts the steady-state role | **0** |
| ACCEPTED-IN-EFFECT (engagement) | The party has exercised the decision right and Dinesh's approval is recorded in the OD log; applies to **decision rights during the engagement**, not to steady-state asset ownership | decision rights only (`decision-rights.md`) |
| INTERIM | Dinesh is owner of record by default (A-18-OM-1); acceptance of a steady-state role is not recorded | see `service-ownership-map.md` |
| VACANT | A role is needed; no holder exists in the repo; not assigned | every client-side role |
| N/A | The asset class does not exist in the product (No-AI) | models, prompts, retrieval |

### TOM-3 Layered operating model
| Layer | What it is | Who operates it today | Target owner role (VACANT unless stated) | Tag |
|---|---|---|---|---|
| L0 Engagement | Stage gates, OD log, branches, PRs | Dinesh (decides); `claude-fde-agent` in three roles (executes, no approval rights) | ends at Stage 38 handover/closure | [Verified Fact] |
| L1 Service ownership | The hub as a running service | nobody runs it for users; loopback only | Service owner (VACANT) | [Verified Fact] absent |
| L2 Human control | Zone H dispositioner, rule-set activator, policy adopter | nobody (`zone_h.holders` empty) | Authorised dispositioner (SH-15, VACANT; outside any engagement) | [Verified Fact] |
| L3 Assurance | Independent verification, compliance oversight | Stage 26 run as a separate agent invocation; walkthroughs by Dinesh (unsigned) | Quality/compliance oversight (VACANT) | [Verified Fact] |
| L4 Supply chain | Code host, build assistant, workspaces | Dinesh's accounts (terms Unknown) | Toolchain owner (VACANT) | [Verified Fact] usage; [Unknown] terms |

### TOM-4 Target roles (descriptions, not people)
| Role ID | Role | Purpose | Holder | State |
|---|---|---|---|---|
| RL-01 | Engagement owner / owner of record | Decisions, gate acceptance, risk acceptance, approval refs | Dinesh Naik | INTERIM (steady-state acceptance Unknown) |
| RL-02 | Service owner | Accountable for the hub being fit to run; release and change owner; support tier 3 | none | VACANT (maps to SH-04) |
| RL-03 | Product/process owner (quality operations) | Owns closed/resolved/48 h definitions, policy content, review practice | none | VACANT (SH-03; OPD-01..03 open) |
| RL-04 | Authorised dispositioner / Zone H holder | The only role that may perform ZH-01..ZH-10 | none | VACANT; `zone_h.holders` stays empty (OD-17, OD-31) |
| RL-05 | Risk and security owner | Security events, access, retention, exposure | none | VACANT (SH-06) |
| RL-06 | Compliance/quality oversight | Evidence before closure; GxP framing; audit findings | none | VACANT (SH-09, SH-11) |
| RL-07 | Data owner(s) | Case data, source feeds, retention | none | VACANT (SH-14, SH-06) |
| RL-08 | Integration/source-contract owner | Per-source contracts, schema versions, late deliveries | none | VACANT (SH-07, SH-14) |
| RL-09 | Finance/FinOps owner | Cost, month-end, any future spend | none | VACANT (SH-05) |
| RL-10 | Legacy technical owner | Legacy code, nightly file exchange (ADR-007) | none, "owner transferred 2024" unnamed | VACANT (SH-08) |
| RL-11 | Reviewers (end users) | Daily review of queue | none | VACANT (SH-13) |
| RL-12 | Toolchain owner | Code host, CI, workspaces, build assistant terms | Dinesh holds the accounts in effect | INTERIM |
| RL-13 | Independent verifier | Second pair of eyes on GxP-relevant changes | none | VACANT (DQ-17: single approver accepted as a general risk in OD-30, not as a Stage 37 acceptance) |
| RL-14 | Build/Stage/Orchestrator agents | Execute within stage; no approval rights | `claude-fde-agent` | Execution only; not owners |

### TOM-5 Operating cadence (target, proposed)
| Rhythm | Content | Role | Status |
|---|---|---|---|
| Per change | branch, PR, full regression (OD-23), release checklist, squash-merge (OD-13) | RL-02 with RL-01 | [Verified Fact] the engagement form exists; steady-state is [Assumption] |
| Per release | `hub/ops/release.py` checklist, golden-compare (exit 6 until DV approved), checksum verification | RL-02 | [Verified Fact] mechanism; owner VACANT |
| Periodic (cadence Unknown) | `verify-audit`, backup + checksum, risk-register review, vendor review | RL-02, RL-05 | [Assumption]; nobody runs `verify-audit` on a schedule today (AM-3) |
| On event | incident, Zone H attempt, tamper alert, tripwire | see `escalation-model.md` | [Verified Fact] EH-01..EH-10 routes end at Dinesh |

### TOM-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| TF-01 | [Verified Fact] No party other than Dinesh can accept an ownership; therefore no steady-state ownership is ACCEPTED | OD-04; `stakeholder-map.md` (SH-03..SH-15 holders Unknown) | Stage 37 completion condition 1 unmet | High (for real adoption), Low (synthetic) | High | Will Dinesh accept RL-01/RL-02 as steady-state, or name a receiving party? |
| TF-02 | [Verified Fact] The TOM is design-only; no run, cost, support or incident evidence exists to size it | no telemetry (0A SO-01..03); Stage 29 and Stage 32 outputs absent from `docs/` | Targets are placeholders | Medium | High | Re-baseline when Stage 29/32 exist |
| TF-03 | [Inference] The hub is safe to leave unowned only because it ships inert (loopback, no active rules, no holders, no scheduler); the moment any of these is switched on, an owner is required | `release-boundaries.md`; OD-16..OD-20 | Ownership is a precondition to activation | Medium | High | Make owner acceptance a CUT-1 entry condition? |
| TF-04 | [Verified Fact] Domain escalation routes (ES-20..ES-25) have no owner; Stage 29 should address them | `escalation-map.md` | See `escalation-model.md` | High (real use) | High | Stage 29 |

## Evidence References
See `evidence_sources`. Ownership detail: `service-ownership-map.md`, `raci.md`. Decision detail: `decision-rights.md`.

## Assumptions
- A-37-TOM-1 [Assumption] Dinesh remains owner of record until Stage 38 closes and until he records otherwise (extends A-18-OM-1, A-25-AM-1). Confirm: Engagement lead (Dinesh Naik).
- A-37-TOM-2 [Assumption] Role names RL-01..RL-14 are proposals to structure the model, not an organisation chart. Confirm: Engagement lead (Dinesh Naik).
- A-37-TOM-3 [Assumption] Cadences in TOM-5 are placeholders. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-TOM-1 Whether any receiving organisation exists (and so whether RL-02..RL-13 will ever have holders).
- U-37-TOM-2 Intended hosting/runtime for any production use (ADR-015: no vendor chosen).

## Unresolved Issues
- Steady-state acceptance (TF-01); Stage 29 incident model and Stage 32 cost evidence are not available to this stage; DQ-17 second reviewer.

## Residual Risks
- RR-37-1 The model reads as staffed when it is not: mitigated by VACANT/INTERIM labels on every row. Low.
- RR-37-2 Single owner of record means decision latency and no separation of duties (RP-01, RS-16): accepted by Dinesh in OD-30 as a general risk only. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
