---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "finops-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/{preliminary-finops-baseline,preliminary-tco,cost-scenarios,volume-assumptions}.md", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/{finops-ownership,escalation-model,raci,decision-rights}.md", "docs/33-vendor-risk/{vendor-inventory,vendor-risk-acceptance,exit-plan}.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "hub/obs/metrics.py", "hub/obs/collect.py", "docs/02-stakeholders/stakeholder-map.md SH-05"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
A role-based FinOps model for a No-AI product whose measured run cost is empty. It reuses the cost objects FC-01..FC-10 and owner roles from `docs/37-operating-model/finops-ownership.md` rather than redefining them, and adds the unit-economics definitions, tags, cadence and reporting template that Stage 37 left to this stage. **Cost owner = role: RL-09 (finance partner, SH-05), VACANT.** Dinesh Naik is interim owner of record for the toolchain accounts only (RL-12); nothing is accepted by this document.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FM-1 Cost objects and measurement state (reuses FC-xx)
| FC | Cost object | Owner role | Holder | Measured now | What would make it measured |
|---|---|---|---|---|---|
| FC-01 | Product model/token spend | RL-09 | VACANT | USD 0, tripwire design in CG-2 | Production counters (host needed) |
| FC-02 | Hosting / compute / storage | RL-09 + RL-02 | VACANT | Unknown | Hosting decision and invoice |
| FC-03 | Code host | RL-12 | Dinesh (INTERIM) | Unknown | Plan and charge |
| FC-04 | AI coding assistant | RL-12 | Dinesh (INTERIM) | Unknown | Plan, seats, usage export |
| FC-05 | Cloud workspace for the full regression | RL-12 | Dinesh (INTERIM) | Unknown (laptop times measured; cloud times not) | OB-02 |
| FC-06 | CI minutes | RL-12 | Dinesh (INTERIM) | USD 0 observed: workflow never run, does not cover `hub/` | none until CI is installed (HAR-07) |
| FC-07 | Human operating cost | RL-09 + RL-03 | VACANT | Assumption USD 15.02 per case | OB-05 |
| FC-08 | Retention / storage growth | RL-09 + RL-05 | VACANT | Unknown | OB-11 |
| FC-09 | Support staffing | RL-09 + RL-02 | VACANT | Unknown | support model decision |
| FC-10 | Legacy run cost (parallel run) | RL-09 + RL-10 | VACANT | Unknown | cutover plan |

### FM-2 Unit economics definitions
Request, case, workflow, outcome: see `cost-per-request.md`, `cost-per-case.md`, `cost-per-workflow.md`, `cost-per-outcome.md`. Common rule: each unit cost is `(token + compute + storage + review + allocated_fixed) / units`, token = 0, every other term reported as Measured / Assumed / Unknown, never blended into one unqualified figure.

### FM-3 Allocation tags
Reuse the 0C tags (`engagement=gxp-quality-hub`, `env`), set `scenario=P-NOAI` (S3/S4 retired, ER-1), drop `touchpoint=T1..T5` model tags (no model), add `cost_object=FC-01..FC-10`, `owner_role=RL-xx`. [Assumption] no billing system exists to apply tags to.

### FM-4 Operating loop and control points
| Step | Control | Evidence |
|---|---|---|
| Inform | Cost lines FC-02..FC-10 get an entry or an explicit "Unknown" each review | this model |
| Zero-model check | Release gate G5; tripwire counters; deny-list | `hub/ops/release.py`; `hub/obs/metrics.py` |
| Any paid dependency | C6 change, RL-01 plus RL-05 (VA-07); no vendor without an ADR | `finops-ownership.md` FO-2 |
| Non-zero model call or egress | SEV-B: L1 blocks release, L3 decides; the agent cannot waive | `escalation-model.md` ER-04 |
| Review cadence | Per release once any cost line is non-zero; Unknown before that | FO-2 item 4 |
| Reporting | Template FM-6; no number without its class | Evidence rules |

### FM-5 Reconciliation with Stage 37 (`finops-ownership.md`)
| Stage 37 statement | Stage 32 result |
|---|---|
| "Stage 32 (cost/TCO) has not produced outputs" | Now produced (DRAFT). |
| FF-02 "A TCO cannot be stated" | A TCO **structure** and a reproduced 0C gross range exist; a measured TCO still cannot be stated (`tco-model.md`). |
| FF-03 AI scenarios do not apply | Confirmed; this stage keeps S3/S4 dormant. |
| FC-01..FC-10 | Adopted unchanged. Nothing contradicts them. |
| Owner RL-09 VACANT | Unchanged; this stage names no holder. |

### FM-6 Report template (per release)
Tripwire status (model calls, egress attempts) / cost lines with class / regression wall time and price / new paid dependencies / open Unknowns / decisions needed from RL-01.

### FM-7 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| FM-F1 | [Verified Fact] No cost owner holder exists besides Dinesh interim | FF-01; SH-05 | Nobody can approve or report spend | Low now, Medium at first paid service | High | Who is RL-09? |
| FM-F2 | [Inference] The FinOps program has no operating data; its value now is the control points (tripwire, C6 gate, owner roles) rather than reports | FM-1 | Do not build dashboards before data exists | Low | Medium | none |

## Evidence References
`docs/37-operating-model/finops-ownership.md`; `raci.md`; `escalation-model.md`.

## Assumptions
- A-32-16 RL-09 maps to SH-05 (same as A-37-FO-2). Confirm: Dinesh.
- A-32-17 Review cadence "per release" is a placeholder. Confirm: Dinesh.

## Unknowns
- U-32-22 Budget, currency and cost centre (DR-31, OQ-07). U-32-23 Who holds RL-09 and RL-12 after the engagement.

## Unresolved Issues
- Operating-contract closure (OC-5) and vacant roles remain open from Stage 37 (OD-34).

## Residual Risks
- RR-32-15 Unowned spend appears at the first hosting or real-data decision. Medium (same as RR-37-FO-1).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
