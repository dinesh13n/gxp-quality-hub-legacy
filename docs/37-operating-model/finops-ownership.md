---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "finops-ownership.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/{preliminary-finops-baseline,cost-scenarios,preliminary-tco,volume-assumptions}.md FB-01..FB-12", "docs/33-vendor-risk/vendor-inventory.md V-03..V-05", "docs/33-vendor-risk/vendor-risk-acceptance.md VA-03", "docs/02-stakeholders/stakeholder-map.md SH-05", ".fde/orchestrator-decisions.md OD-08, OD-23, OD-33"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
**There is no measured run cost to own.** Model spend is USD 0 (0 model calls, FB-01/FB-02); infrastructure cost is Unknown because nothing is deployed (FB-12); the human-cost-per-case figure (USD 15.02) is an assumption at USD 25/h on a synthetic formula (FB-06). The cost scenarios S3/S4 (about USD 533 / 719 per month at Base) were built for an AI option that Dinesh did not choose (OD-08) and must not be read as a forecast for the No-AI product. The only real cost lines that exist are **toolchain accounts** (code host, AI coding assistant, cloud workspace) whose plans and charges are Unknown (U-33-01, U-33-02). Stage 32 (cost/TCO) has not produced outputs; this artifact must be reconciled with it. The finance partner role (SH-05) is unfilled, so the FinOps owner role is VACANT; Dinesh is interim owner of record for the toolchain accounts only.

## Findings
### FO-1 Cost objects and owners
| ID | Cost object | Known amount | Class | Owner role | Holder | State |
|---|---|---|---|---|---|---|
| FC-01 | Product model/token spend | USD 0 (0 calls) | Measured (FB-01/02) | RL-09 | VACANT | N/A today; becomes owned only under C7 |
| FC-02 | Hosting / compute / storage for the hub | Unknown (nothing deployed, ADR-015 "no vendor chosen") | Unknown | RL-09 with RL-02 | VACANT | VACANT |
| FC-03 | Code host (GitHub, private repo) | Unknown plan/charge | Unknown | RL-12 | Dinesh (INTERIM) | INTERIM |
| FC-04 | AI coding assistant (build tooling) | Unknown | Unknown | RL-12 | Dinesh (INTERIM) | INTERIM |
| FC-05 | Orchestrator cloud workspace (full regression) | Unknown (provider Unknown) | Unknown | RL-12 | Dinesh (INTERIM) | INTERIM |
| FC-06 | CI minutes (GitHub Actions) | USD 0 observed: workflow never run | Inference | RL-12 | Dinesh (INTERIM) | INTERIM |
| FC-07 | Human operating cost (review, support, ownership) | Unknown; USD 15.02 per case is an assumption on synthetic hours (0.601-0.603 h/case) | Assumption (FB-05/06) | RL-09 with RL-03 | VACANT | VACANT |
| FC-08 | Retention/storage growth under hold-all | Unknown | Unknown | RL-09 with RL-05 | VACANT | VACANT |
| FC-09 | Support staffing | Unknown | Unknown | RL-09 with RL-02 | VACANT | VACANT |
| FC-10 | Legacy run cost (parallel run until cutover) | Unknown | Unknown | RL-09 with RL-10 | VACANT | VACANT |

### FO-2 FinOps controls to carry (proposed, role-based)
1. **Tripwire as budget guard:** zero model calls is tracked as a tripwire (OD-08; Stage 32 tracks it). Any non-zero count is a SEV-B event (`escalation-model.md`).
2. **Cost approval:** any new paid dependency or service is a C6 change needing RL-01 plus RL-05 (VA-07); no vendor is added without an ADR.
3. **Tagging:** the dimension names proposed in the FinOps baseline (FB table) are reused when actuals exist; none exist.
4. **Review cadence:** Unknown; propose per release once any cost is non-zero.
5. **Business outcomes:** value claims stay "synthetic, unvalidated" (CG-1 fallback); no KPI baseline is measured (OD-07). FinOps cannot report cost-per-outcome until RL-03 defines the outcome.

### FO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| FF-01 | [Verified Fact] No cost owner exists; SH-05 has no holder | `stakeholder-map.md` | Nobody can approve or report spend | Low now; Medium on first paid service | High | Who is RL-09? |
| FF-02 | [Verified Fact] Zero measured run cost: not "zero cost" but "nothing measured" outside model spend | FB-01, FB-12 | A TCO cannot be stated | Medium | High | Stage 32 |
| FF-03 | [Verified Fact] AI cost scenarios do not apply to the chosen No-AI product | OD-08; `cost-scenarios.md` | Risk of quoting USD 533/719 as the run cost | Medium | High | Label scenario files as AI-option only |
| FF-04 | [Verified Fact] Toolchain charges are held on accounts nobody else controls | V-03..V-05 | Hidden cost transfers to whoever inherits the accounts | Medium | High | VA-02..VA-04 |

## Evidence References
See `evidence_sources`. Not available: Stage 32 outputs; any invoice or plan document.

## Assumptions
- A-37-FO-1 [Assumption] Dinesh pays for the toolchain accounts personally or via an unknown party; ownership of those charges is Unknown. Confirm: Engagement lead (Dinesh Naik).
- A-37-FO-2 [Assumption] RL-09 maps to SH-05 finance partner. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-FO-1 All real cost lines in FC-02..FC-10.
- U-37-FO-2 Currency, cost centre, budget (DR-31: no budget, deadline or success criteria; OQ-07).

## Unresolved Issues
- Stage 32 reconciliation; RL-09 holder; budget owner.

## Residual Risks
- RR-37-FO-1 Unowned spend appears at first hosting/real-data decision (Medium).
- RR-37-FO-2 Misuse of AI scenario numbers as forecast (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
