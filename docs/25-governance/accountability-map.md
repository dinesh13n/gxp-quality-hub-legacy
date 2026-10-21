---
stage: "25 — Governance + Compliance + Assurance"
artifact: "accountability-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/ownership-map.md (OM-1..OM-3)", "docs/02-stakeholders/{stakeholder-map,decision-rights-map,approval-authority-map}.md (SH-01..SH-15, DR-01..DR-31)", "docs/00-preflight/operating-contract/{provisional-human-approval-rules,provisional-tool-agent-permissions}.md", "docs/17-implementation-prd/implementation-prd.md IP-7", "docs/25-governance/{compliance-obligations,compliance-control-matrix}.md", "hub/security/settings.py (zone_h.holders)", ".fde/orchestrator-decisions.md (OD-04, OD-13, OD-17, OD-23)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The only human who exists is Dinesh Naik, Engagement lead (OD-04). Every role below that is not him or an agent is a GAP: the repo names the role in some documents but never a holder. No holder, owner or approval is invented in this map. "Accountable" means Dinesh is the person who would have to answer; it is not an assignment of legal liability.**

## Summary
Accountability is single-point: **A (accountable) = Engagement lead (Dinesh Naik) for all 16 obligations, all 22 controls and all open decisions**. **R (responsible for doing)** is split between three agent roles that hold no decision rights (Build agent, Stage agent, Orchestrator, all `claude-fde-agent`). **C (consulted)** roles are the client roles SH-03..SH-15; none has a holder, so each is a GAP carried to Stage 37. One role is missing in a way that matters most for a GxP-style system: the **authorised human for batch disposition (SH-15)** — the product is built to wait for that person, and the person does not exist in the engagement.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AM-1 Roles and holders
| Role | Holder | Decision rights | Source | Tag |
|---|---|---|---|---|
| Engagement lead (Dinesh Naik) | Dinesh Naik (SH-01) | Approves HAR items, OD / OD-S12 / OPD / DQ decisions, gate acceptance, risk acceptance, go / no-go | OD-01, OD-04; wider authority A-0B-06 | [Verified Fact] for recorded decisions; [Assumption] beyond |
| Orchestrator | `claude-fde-agent` | Merges after review (OD-13); runs full regression (OD-23); records OD entries; **no approval rights** (TP-14) | OD-13, OD-23 | [Verified Fact] |
| Build agent / Stage agent | `claude-fde-agent` | Writes code or documents inside its stage; sets own gate status (self-assessed, TP-13); no approval rights | TP-03, TP-04, TP-13 | [Verified Fact] |
| Independent verifier | none (Stage 26 is a separate agent invocation; walkthroughs are by Dinesh) | procedural independence only | OD-24; A-18-OM-2 | [Inference] GAP |
| Zone H holder / dispositioner (SH-15 in the product) | **none** (`zone_h.holders` ships empty) | Would hold ZH-01..ZH-10 | OD-17; DR-22; OD-S12-06 | [Verified Fact] GAP |
| Quality operations lead (SH-03) | none | consulted on definitions, policy, review | `stakeholder-map.md` | [Verified Fact] role / [Unknown] holder |
| Enterprise application owner (SH-04) | none | release, interfaces | `stakeholder-map.md` | GAP |
| Finance partner (SH-05) | none | cost, month-end | `stakeholder-map.md` | GAP |
| Risk and security partner (SH-06) | none | authorisation, retention, audit evidence | `stakeholder-map.md` | GAP |
| Integration lead (SH-07); legacy technical owner (SH-08); source owners (SH-14) | none | contracts, legacy code, feeds | `stakeholder-map.md`; ADR-archived-007 ("owner transferred 2024", unnamed) | GAP |
| Compliance team (SH-09); legal / compliance (SH-11) | none | evidence before closure; state definitions | `stakeholder-map.md` | GAP |
| Operations leadership (SH-10); reviewers (SH-13) | none | 48 h closure; daily review | `stakeholder-map.md` | GAP |

### AM-2 Accountability by obligation (R = who runs the control; A = accountable)
| Obligation | R (control operation) | A | C (role, holder GAP) | I |
|---|---|---|---|---|
| OB-01 audit trail | Build agent (code); Orchestrator (runs `verify-audit` and regression) | Engagement lead (Dinesh Naik) | SH-06, SH-09 | Operations |
| OB-02 human disposition | Zone H holder (GAP) performs the human act; Build agent maintains the gate | Engagement lead (Dinesh Naik) | SH-15, SH-09, SH-06 | — |
| OB-03 no e-signature claim | Stage agent (wording); Build agent (ZH-03 semantics) | Engagement lead (Dinesh Naik) | SH-09, SH-11 | — |
| OB-04 data integrity themes | Build agent; Orchestrator (checksums) | Engagement lead (Dinesh Naik) | SH-06, SH-07 | — |
| OB-05 retention | Build agent (hold-all); policy owner GAP | Engagement lead (Dinesh Naik) | SH-06 | — |
| OB-06 access control | Build agent | Engagement lead (Dinesh Naik) | SH-06, SH-04 | — |
| OB-07 evidence before closure | Build agent (structural check) | Engagement lead (Dinesh Naik) | SH-09, SH-03 | — |
| OB-08 privacy | none assigned | Engagement lead (Dinesh Naik) | SH-06, SH-11 | — |
| OB-09 cross-tenant | none assigned | Engagement lead (Dinesh Naik) | SH-04 | — |
| OB-10 No-AI | Build agent (guard); Orchestrator (runs it) | Engagement lead (Dinesh Naik) | — | — |
| OB-11 change control | Orchestrator | Engagement lead (Dinesh Naik) | SH-04 | — |
| OB-12 no fabrication | all agents | Engagement lead (Dinesh Naik) | — | — |
| OB-13 untrusted content | Build agent | Engagement lead (Dinesh Naik) | SH-06 | — |
| OB-14 contractual | none | Engagement lead (Dinesh Naik) | — | — |
| OB-15 external AI governance | none | Engagement lead (Dinesh Naik) | SH-06, SH-11 | — |
| OB-16 behaviour-change approval | Build agent (register); Dinesh approves | Engagement lead (Dinesh Naik) | SH-03, SH-07, SH-10 | consumers of legacy outputs (Unknown, OD-28) |

### AM-3 Accountability by control owner
Control operator = who keeps it working; control owner of record = Engagement lead (Dinesh Naik) for GC-01..GC-22 (no other owner can be named, OD-04). Controls where the operator is an agent and no human reviews the result routinely: GC-01 (nobody runs `verify-audit` on a schedule), GC-11 (manual), GC-10 (manual). [Inference]

### AM-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| AF-01 | [Verified Fact] 13 of 15 stakeholder rows (SH-03..SH-15; SH-01 is Dinesh, SH-02 is the agent) have no holder | `stakeholder-map.md` | Consultation is nominal | High (real use) | High | Who would fill them? Stage 37 |
| AF-02 | [Verified Fact] The single accountable person also performs the walkthroughs and would stand in as the only tester of the disposition gate (with synthetic data only, A-10-07) | OD-24; ADR-006 A-10-07 | No independence; a self-review | Medium | High | DQ-17 |
| AF-03 | [Inference] If Dinesh were named a Zone H holder for tests, it would be a test configuration on synthetic data, not a real authorisation | A-10-07; OD-17 | Must not be read as a production holder | Medium | Medium | Confirm if a test holder is wanted |
| AF-04 | [Verified Fact] Steady-state owners for repo, data, runbooks, legacy-parallel workflow and ADR-007 file exchange are GAPs | DR-26, DR-30, OPD-15, GD-13 | Ownership vacuum at handover | High | High | Stage 37 |

## Evidence References
`docs/18-delivery/ownership-map.md` OM-1..OM-3 (this map extends it to obligations and controls); `stakeholder-map.md`; `decision-rights-map.md`.

## Assumptions
- A-25-AM-1 [Assumption] Dinesh remains sole accountable owner through Stage 43 (A-18-OM-1). Confirm: Engagement lead (Dinesh Naik).
- A-25-AM-2 [Assumption] Agent R-assignments describe execution, not liability.

## Unknowns
- U-25-AM-1 Holders of SH-03..SH-15, and whether any receiving team exists.
- U-25-AM-2 Whether a qualified quality reviewer will ever see this map.

## Unresolved Issues
- OD-S12-06 holders; DQ-17 second reviewer; steady-state owners (Stage 37).

## Residual Risks
- RR-AM-1 Concentration of accountability: decision latency gates W2-W5 (High for throughput).
- RR-AM-2 Roles named in documents (not people) could be mistaken for staffed functions: Low; every GAP is labelled.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
