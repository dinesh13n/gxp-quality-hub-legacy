---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "escalation-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/02-stakeholders/escalation-map.md ES-01..ES-09, ES-20..ES-25", "docs/23-human-control/escalation-matrix.md EH-01..EH-10", "docs/00-preflight/operating-contract/stop-conditions.md STOP-01..STOP-12", "docs/25-governance/governance-model.md GM-6", "operations/incidents/INC-2025-014.md", "docs/24-security-privacy/residual-security-risks.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Escalation model for steady state. The evidenced ladder is three rungs and ends at one person: **agent -> orchestrator -> Dinesh Naik; no alternate, no level beyond** (ES-09, ES-04 section C). The product-level routes EH-01..EH-10 all end at Dinesh. The domain routes (feed, policy, security, compliance, release) have **no owner at all** (ES-20..ES-25). This model keeps the evidenced rungs, adds *role-based* rungs that are VACANT, and fixes severity and response *classes* without inventing response times (no SLA evidence exists: U-02-13, OD-28 (a)). Stage 29 (incident model) is not available; incident-specific content here is provisional and must be reconciled with it.

## Findings
### EM-1 Ladder (target)
| Rung | Role | Holder | Authority | State |
|---|---|---|---|---|
| L0 | Operator / reviewer (RL-11, or `claude-fde-agent` in-engagement) | agent in-engagement; users VACANT | detect, record, stop, never self-repair (STOP rules) | agent: [Verified Fact]; users VACANT |
| L1 | Service owner (RL-02) | VACANT; Dinesh INTERIM | triage, rollback, kill switch (`hub.kill`), revert | INTERIM |
| L2 | Domain owners: RL-03 process, RL-05 security, RL-06 compliance, RL-08 integration | all VACANT | domain decisions in their area | VACANT |
| L3 | Engagement owner / owner of record (RL-01) | Dinesh Naik | all T0 decisions, risk acceptance, waivers (HAR-14) | INTERIM; the only human rung that exists |
| L4 | Beyond (sponsor, steering, compliance board) | none | none | does not exist (ER-04) |

### EM-2 Triggers and routes (product events from Stage 23; domain from Stage 2)
| Route ID | Trigger | Source | First responder | Escalates to | Today's end of chain | Gap |
|---|---|---|---|---|---|---|
| ER-01 | Zone H requested but no holder (E-GATE-NO-HOLDERS) | EH-01 | L1 | L3 to decide holders (never add one unapproved) | Dinesh | Holder role VACANT |
| ER-02 | Non-holder Zone H attempt repeated | EH-02 | L1 | L2 RL-05 then L3 | Dinesh | RL-05 VACANT |
| ER-03 | Audit/decision chain break (E-SEC-AUDIT-TAMPER-DETECTED, E-DEC-CHAIN-BROKEN) | EH-03 | L1 stops hub | L2 RL-05/RL-06, L3; restore only with HAR-01 | Dinesh | No evidence owner |
| ER-04 | AI package import, egress attempt, model call (tripwires) | EH-04 | L1 blocks release | L3 (HAR-08/09/10) | Dinesh | none beyond |
| ER-05 | Non-loopback bind attempted | EH-05 | L1 | L3 (HAR-05) | Dinesh | none beyond |
| ER-06 | Run totals mismatch | EH-06 | L1 | L2 RL-08 (feed) / RL-03 | Dinesh | no domain owner (ES-21) |
| ER-07 | Flag without `approval_ref` at start-up | EH-07 | L1 | RL-03 for approval, L3 | Dinesh | RL-03 VACANT |
| ER-08 | Release gate failed / secret in audit | EH-08 | L1 | L3 (HAR-14 for any waiver) | Dinesh | agent may never waive |
| ER-09 | `authoritative` capability diverges from human decisions | EH-10 | L0 reviewer | L1 `flip-to-shadow`, then RL-03, L3 | Dinesh | RL-03 VACANT |
| ER-10 | Policy conflict: 48 h closure vs verifiable evidence | ES-20 | L2 RL-03 | RL-06 and Operations; L3 | none | no route exists |
| ER-11 | Feed delay / replay | ES-21; INC-2025-014 | L1 | L2 RL-08 | none | follow-up owner unknown |
| ER-12 | Disputed root cause between application and integration | ES-22 | L1 | RL-02 vs RL-08; tie-break L3 | none | tie-break owner absent |
| ER-13 | Release rollback | ES-23 | L1 | L3 | none | route not recorded historically |
| ER-14 | Security/privacy event | ES-24 | L1 | L2 RL-05 | none | no role, no auth/telemetry in legacy |
| ER-15 | Compliance/audit finding | ES-25 | L1 | L2 RL-06 | none | no role |
| ER-16 | Request to make or simulate disposition/QA release/e-signature | ES-08; STOP-07 | any | refuse; inform L3 | Dinesh | by design the real authority is outside |
| ER-17 | Instruction conflict or suspected fabrication | ES-04, ES-06 | any agent | L3 | Dinesh | none |
| ER-18 | L3 unavailable | ES-09 | - | **nobody** | work pauses | alternate approver absent |

### EM-3 Severity classes (proposed; no time targets)
| Class | Meaning (Inference) | Examples | Minimum rung to close |
|---|---|---|---|
| SEV-A | Integrity, authority or regulated-act risk | chain break, Zone H bypass, simulated disposition, real data in a non-approved place | L3 (and L2 RL-05/RL-06 once staffed) |
| SEV-B | Control degraded or unapproved change of behaviour | tripwire, release gate failure, flag without ref, divergence | L1 plus L3 for any waiver |
| SEV-C | Operational defect with a safe default | run mismatch, late feed, search or UI defect | L1 |
Response and resolution times are **Unknown**; no SLA exists. Proposed rule: define them when a real service owner and users exist, not before.

### EM-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| EF-01 | [Verified Fact] 7 of 18 routes (ER-10..ER-15, ER-18) have no owner or alternate | EM-2 | Incidents in the legacy-parallel domain have no route | High (real use) | High | Stage 29; who owns them? |
| EF-02 | [Verified Fact] Every product-event route ends at one person | EH-01..EH-10 | No independent escalation for a GxP-style system | Medium-High | High | DQ-17 |
| EF-03 | [Inference] Safe by default: most events halt or refuse (default refusal, bind refusal, `hub.kill`), so absence of a responder degrades availability, not integrity | EH-05, EH-09 | Low integrity exposure while inert | Low-Medium | Medium | Re-assess before any activation |

## Evidence References
See `evidence_sources`.

## Assumptions
- A-37-EM-1 [Assumption] Severity classes are agent proposals. Confirm: Engagement lead (Dinesh Naik).
- A-37-EM-2 [Assumption] Routes ER-10..ER-15 mirror the Stage 2 gaps; they are targets, not agreements with any team. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-EM-1 Any external escalation target (mentor, assessor) (U-02-12).
- U-37-EM-2 Response-time expectations (U-02-13).
- U-37-EM-3 Stage 29 incident taxonomy and on-call design (not yet produced).

## Unresolved Issues
- ES-09 alternate approver; ES-20..ES-25 owners; reconcile with Stage 29 when it exists.

## Residual Risks
- RR-37-EM-1 Single point of failure at L3 stalls work or tempts shortcut approvals (High throughput, Medium quality).
- RR-37-EM-2 Domain incidents handled by manual spreadsheet reconciliation as in INC-2025-014 (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
