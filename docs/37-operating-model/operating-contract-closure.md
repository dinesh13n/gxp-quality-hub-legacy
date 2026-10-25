---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "operating-contract-closure.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/operating-contract/ (12 files; Stage 0B originals, not modified)", "docs/02-stakeholders/operating-contract-confirmations.md", "docs/23-human-control/operating-contract-updates.md", "docs/25-governance/operating-contract-governance-updates.md", "docs/37-operating-model/ (this stage)", "docs/18-delivery/ownership-map.md OM-3", ".fde/orchestrator-decisions.md OD-01..OD-33", "git tag baseline-as-found (a6eb4e8)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
This document **proposes** the formal closure of the Stage 0B provisional operating contract and records the Stage 37 gate assessment. **It does not close the contract.** Closure is a decision only Dinesh Naik can make (HAR-13, HAR-11, TP-14); an agent text that says "closed" would be a fabricated approval (OD-04). What this stage delivers: (1) a clause-by-clause disposition of C1..C10, GD-01..GD-15 and the Stage 37 items, (2) the successor documents that replace the contract in steady state, (3) the preservation rules for 0B history, and (4) a **draft closure record** for Dinesh to adopt, edit or reject. Until he records it, the 0B contract stays in force as amended by the OD log and the Stage 2, 23 and 25 update documents.

## Findings
### OC-1 Preservation of 0B history (non-negotiable)
- The 12 files under `docs/00-preflight/operating-contract/` are **not edited** by this stage or by closure; they stay at v0.1 DRAFT. Updates live beside them (`operating-contract-confirmations.md`, `operating-contract-updates.md`, `operating-contract-governance-updates.md`, this file). [Verified Fact] (HAR-13; CC-06, CC-07).
- Baseline commit a6eb4e8 is tagged `baseline-as-found` (OD-06) and stays immutable (C8).
- Closure adds a record; it does not delete, rewrite or reinterpret earlier decisions. A later reopening is a new record, not an edit.

### OC-2 Clause disposition (proposed)
| 0B clause | Proposed disposition at closure | Successor / carried rule | Evidence |
|---|---|---|---|
| Parties and authority | Engagement-phase authority ends at closure. Steady-state authority is the RL roles. Dinesh remains owner of record INTERIM until he names otherwise | `target-operating-model.md` TOM-4; `decision-rights.md` | OD-01, OD-04 |
| C1 Scope (one repo, synthetic data, local only, no real GxP decision) | **CARRIED** unchanged as long as the system is synthetic and inert | `data-ownership.md` DO-2; STOP-04 | `scope-boundaries.md` |
| C2 Repository writes (default deny; git writes orchestrator-only; no history rewrite) | **CARRIED**, reworded as change classes | `change-governance.md` CG-1..CG-2 | `repository-write-boundaries.md` |
| C3 Environments (E3/E4 incl. production denied to all) | **CARRIED**; any production use needs RL-01 plus RL-05 (SDR-07, C5) | `change-governance.md` C5 | `environment-access-boundaries.md` |
| C4 Data (synthetic; untrusted text is data; no egress beyond private remote) | **CARRIED** | `data-ownership.md`, `security-ownership.md` | `data-use-constraints.md` |
| C5 Agents/tools (TP-01..TP-15) | Engagement only (confirmed OD-31); steady-state policy needed if agents continue | `agent-tool-ownership.md` AT-2 | OD-31 |
| C6 Human approval (HAR-01..HAR-16, +HAR-17) | **CARRIED** as decision rights; approvals map to SDR rows | `decision-rights.md` DRT-2 | OD-31 |
| C7 Evidence (EV-01..EV-08, NE-1..NE-6) | **CARRIED**; evidence rules stay in force for all later documents | `docs/25-governance/evidence-retention-policy.md` | `evidence-contract.md` |
| C8 Change control (CC-01..CC-12) | **CARRIED**, mapped to classes C0..C8 | `change-governance.md` | `change-control-rules.md` |
| C9 Stop conditions (STOP-01..STOP-12) | **CARRIED**; stops route per `escalation-model.md` | `escalation-model.md` ER-01..ER-18 | `stop-conditions.md` |
| C10 Open items GD-01..GD-15 | Each item dispositioned in OC-3 | OC-3 | `open-governance-decisions.md` |

### OC-3 GD-01..GD-15 status at Stage 37 (from the record, nothing newly decided)
| ID | Status | Basis (quoted record) | Remaining action and owner |
|---|---|---|---|
| GD-01 decision rights | EVIDENCED IN PRACTICE; wider authority [Assumption] | OD-01..OD-33 | Dinesh to adopt `decision-rights.md` or amend |
| GD-02 baseline dataset | CLOSED | OD-09 | none |
| GD-03 checksum manifest | ACKNOWLEDGED | OD-31 (GD-03/08/14 acknowledged) | none |
| GD-04 permission matrix | CONFIRMED for the engagement | OD-31 (TP-01..TP-15 confirmed) | steady-state re-confirmation if agents continue |
| GD-05 separation of duties | Single-approver risk accepted as a general risk; separation not achieved | OD-30 (DQ-17) | second reviewer role VACANT |
| GD-06 environment ownership | OPEN; two real environments named in OD-23 | owner of record proposed: RL-12 (PA-17, PA-18) | Dinesh to confirm |
| GD-07 retention of sandbox logs | OPEN; hold-all interim | OD-30 (OD-S12-09) | RL-05/RL-06 VACANT |
| GD-08 baseline tag | ACKNOWLEDGED | OD-31 | none |
| GD-09 remote + CI-on-push | PARTLY: remote and PR flow exist (OD-13); CI-on-push not wired, OD-14 revisit at Stage 27/30 | OD-05, OD-13, OD-14 | Stage 27/30 |
| GD-10 scope ambiguities | OPEN | OD-28 (b) | Dinesh |
| GD-11 GxP/Part 11 framing | Framing only, no "compliant" claim | OD-30 | none; wording rule carried |
| GD-12 human-control for AI | PARTLY: No-AI (OD-08); Zone H built; holders empty | OD-08, OD-31 | holder decision (OD-S12-06) |
| GD-13 steady-state ownership | **ADDRESSED IN DESIGN, NOT ACCEPTED**: this stage defines roles and interim owner; no acceptance exists | `service-ownership-map.md` | Dinesh (accept or name receivers) |
| GD-14 full-repo sandbox | ACKNOWLEDGED | OD-31 | none |
| GD-15 instruction precedence | PARTLY EVIDENCED (OD log binding); full order not approved | `governance-model.md` | Dinesh to confirm the order |

### OC-4 Stage 37 completion-gate assessment
| Gate condition | Met? | Evidence | Gap |
|---|---|---|---|
| Every production asset has an **accepted** owner | **NOT MET** | `service-ownership-map.md`: 0 of 28 ACCEPTED (25 INTERIM, 1 N/A, 2 VACANT) | needs Dinesh acceptance and/or named receivers; cannot be supplied by an agent |
| The 0B contract is **formally closed** | **NOT MET** | OC-5 draft only | needs Dinesh decision |
| All required artifacts exist at the paths above | MET | 13 files in `docs/37-operating-model/` | - |
| Critical gaps resolved or explicitly documented | MET (documented) | Unknowns/Unresolved sections of every file; RF-01, SF-02, EF-01, DF-01, TF-01 | - |
| Evidence supports the stage conclusion | MET for a CONDITIONAL conclusion | OD-04 makes acceptance by anyone else impossible in this engagement | - |

**Outcome: CONDITIONAL PASS.** Reasoning [Inference]: the two unmet conditions are blocked by facts that no further work in this stage can change (no other human exists; closure is Dinesh-only), no code or data is affected, the system is inert (loopback, no active rules, no holders, no scheduler), and every gap is documented with owner and due point. A stricter reading, "PASS requires acceptance, otherwise BLOCKED", is also defensible; Dinesh may rule that way. Under either reading **Stage 38 must not present ownership as accepted or the contract as closed**, and **no cutover step, exposure, rule-set activation or real data may rely on this stage**.

| Non-blocking gap | Owner | Due point | Risk |
|---|---|---|---|
| Accept RL-01/RL-02 steady-state role or name receivers (28 assets) | Engagement lead (Dinesh Naik) | Before Stage 38 handover is declared complete | High if handed to nobody |
| Record 0B closure (draft in OC-5) | Engagement lead (Dinesh Naik) | Stage 38 | Medium (contract stays provisional) |
| Reconcile with Stage 29 incident model and Stage 32 cost output | Stage 29/32 agents, accepted by Dinesh | When produced; before Stage 38 | Medium |
| Reconcile with Stage 27 hardening and CI | Orchestrator | After Stage 27 merge | Low-Medium |
| Fill VACANT roles or keep "accepted open" per decision | Engagement lead (Dinesh Naik) | Before CUT-1, any exposure or any real data | High |
Calendar due dates are Unknown; no schedule exists (DR-31).

### OC-5 Draft closure record (NOT adopted; for Dinesh to edit, adopt or reject)
> OC-DRAFT. The Stage 0B provisional operating contract is closed as of <date Dinesh chooses>. Its originals remain preserved unmodified. Clauses C1-C4 and C6-C9 are carried into steady state as described in `docs/37-operating-model/operating-contract-closure.md` OC-2. Dinesh Naik is recorded as interim owner of record for the assets in `service-ownership-map.md` until a receiver accepts them; this is [accepted | not accepted] as a steady-state role. GD-13 is [closed | open]. No risk is accepted by this record. Vacant roles remain vacant. Recorded by Dinesh Naik.

To adopt it, Dinesh should answer: (1) accept closure of 0B as proposed? (2) accept the interim owner-of-record placement as a steady-state role, or name receivers (real people/teams only)? (3) adopt `decision-rights.md` SDR-01..SDR-16 as proposals or amend? Then an orchestrator enters an OD row quoting his words. This stage does not write to `.fde/orchestrator-decisions.md`.

### OC-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CF-01 | [Verified Fact] The 0B contract has never been confirmed as a whole; many items were confirmed piecemeal by later OD entries | `operating-contract-confirmations.md`; OD-31 | Closure is cleaner than expected: most items already have a disposition | Low | High | Does Dinesh want a single closing answer? |
| CF-02 | [Verified Fact] GD-06, GD-07, GD-10, GD-13, GD-15 remain open | OC-3 | Contract closes with open items carried by name | Medium | High | Decide or carry |
| CF-03 | [Inference] Closing before handover to a receiver would leave the carried rules owned by nobody except Dinesh | OC-2 | Owner-of-record risk | Medium | Medium | Close at Stage 38 together with the handover |

## Evidence References
See `evidence_sources`. Cross-artifact: all 12 other Stage 37 files.

## Assumptions
- A-37-OC-1 [Assumption] Dinesh intends to close the contract at or before the end of the engagement; no statement says so. Confirm: Engagement lead (Dinesh Naik).
- A-37-OC-2 [Assumption] OC-3 statuses are read correctly from the cited OD rows and update documents; the 0B originals were not edited. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-OC-1 Whether the contract needs closure by any external party (none identified; OD-04).
- U-37-OC-2 Whether Dinesh wants closure at Stage 37, Stage 38 or at Stage 43/46.

## Unresolved Issues
- Both unmet gate conditions; GD-06, GD-07, GD-10, GD-13, GD-15.

## Residual Risks
- RR-37-OC-1 Contract left PROVISIONAL after the engagement ends (Medium).
- RR-37-OC-2 Reader treats the draft in OC-5 as an adopted record (Low; marked NOT adopted).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
