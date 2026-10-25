---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "benefits-realisation-dashboard-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/34-measure-after/adoption-metrics.md", "docs/35-variance/corrective-action-backlog.md", "docs/32-finops/production-token-dashboard-spec.md", "docs/36-roi/roi-model.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
Specification (text only, no build) for a benefits-realisation dashboard, plus the benefits-realisation plan: which Stage 34 KPI would evidence which driver, the order in which conditions must be met, and what each tile shows **today**. Design rule: **a tile shows a value only when its input status is Verified; otherwise it shows 'Unknown' or 'Not computable' with the reason.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BD-1 Design rules
1. Status badge on every tile: Verified Fact / Inference / Assumption / Unknown. Default Unknown.
2. No tile may show ROI, NPV or payback while any required slot in `roi-model.md` RM-2 is EMPTY; it shows 'NOT COMPUTABLE: missing I-xx'.
3. Parity is displayed as 'parity (imported status)', never green/up.
4. Sandbox and production values are never on one axis; sandbox values carry a 'synthetic' tag.
5. Money appears only if the rate comes from a finance-approved source (I-10).
6. The dashboard is read-only and changes no metric definition (operating mode).

### BD-2 Tiles and their state today
| Tile | Source KPI / artefact | Driver | Today's state |
|---|---|---|---|
| T1 Adoption | K-21, principals (AD-1/AD-2) | all | 0 of 125 (sandbox); production Unknown |
| T2 Readiness gates | PC-1..PC-10 (`payback-analysis.md` PB-3) | all | 0 of 10 closed |
| T3 Reconciliation effort | K-22 (new capture, CA-06) | VD-01 | Unknown both sides |
| T4 Rework | K-15 | VD-02 | parity 6.4 % = 6.4 % (imported); effect Unknown |
| T5 Incidents | K-07 and incident log | VD-03 | sandbox mechanism evidence only; frequency Unknown |
| T6 Month-end | K-10 (after redefinition, OD-07), close-time capture | VD-04 | Unknown (K-10 compares unrelated populations) |
| T7 Evidence completeness | K-02, K-05 | VD-05 | K-02 legacy 0 of 20; hub rate Unknown (0 human decisions) |
| T8 Decision record | K-11 | enabler | 2 of 2 'accepted open', none decided |
| T9 Control invariant | K-01 | guardrail | 0 in the Stage 26 attack suite (test result); operational Unknown |
| T10 Cost actual vs 0C range | Stage 32 tiles | cost | Model USD 0 (by design); other terms Unknown |
| T11 ROI / NPV / payback | `roi-model.md`, `npv-model.md`, `payback-analysis.md` | net | NOT COMPUTABLE |
| T12 Double-counting guard | `double-counting-check.md` | integrity | 0 monetised; rules defined |
| T13 Open risks | RS, RP, VA, RTR, F registers | risk | all open, none accepted (counts as in OD-33..OD-35) |

### BD-3 Benefits-realisation plan (stages of evidence; every step PROPOSED, needs Dinesh)
| Phase | Objective | Actions (Stage 35 backlog) | Exit evidence | Benefit allowed to be claimed |
|---|---|---|---|---|
| R0 Confirm | Know whether anything is live | CA-02, CA-01 | Written confirmation of status; after-window, exposure, data owner defined | none |
| R1 Fix the yardstick | Comparable definitions | CA-05, CA-07, CA-03, CA-06 | Stage 4 v0.2 signed; closed/resolved decided; `as_of` available; time capture designed | none |
| R2 Enable adoption | Remove leakage blockers | CA-08, CA-09, CA-10, CA-11, CA-12, CA-14 | Owners named or waived; Zone H decision; parallel-run plan; risk routing recorded by Dinesh | none |
| R3 Pilot with comparison | Produce attributable data | CA-04 | Pre-registered KPIs; comparison group or stable pre-trend; fixed window | none until R4 |
| R4 Measure and verify | Verified benefits | CA-17 (re-run Stage 34, then 35) | At least one KPI pair passing the four-part test (`verified-benefits.md` VB-1) | Only the passing KPI, in its own unit |
| R5 Value | Convert to money | CA-13 | Finance-approved rate, volume, cost inputs, cost owner | Money for verified benefits only |
| R6 Re-run Stage 36 | ROI/NPV/payback | this stage v0.2 | All used slots filled with evidence; double-count check re-run | ROI/NPV/payback as computed, with sensitivity |

### BD-4 Roles [Verified Fact: as recorded]
Every owner role except Dinesh Naik is VACANT (OD-34). The plan assigns every phase to Engagement lead (Dinesh Naik) by default; this is not a staffing decision. A benefits owner and a cost owner (RL-09) are needed and unnamed.

### BD-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BDF-1 | [Verified Fact] No dashboard tile can show a verified benefit today | BD-2 | A dashboard now would be nearly all Unknown | Medium | High | R0..R4 |
| BDF-2 | [Verified Fact] No benefits owner exists | OD-34 | Realisation has no accountable person | High | High | Naming (Dinesh) |
| BDF-3 | [Inference] Phases R0 to R2 cost effort that is not in the 0C range (Adopt/Dbl terms), so realisation planning adds to cost before any benefit. Reasoning: CM-1 unpriced terms | `cost-model.md` | Cost understated | Medium | Medium | CA-13 |


## Evidence References
`docs/34-measure-after/after-intervention-kpi-sheet.md`; `adoption-metrics.md`; `docs/35-variance/corrective-action-backlog.md` CA-01..CA-17; `docs/36-roi/payback-analysis.md` PB-3.

## Assumptions
- A-36-13 [Assumption] Phase ordering follows Stage 35 CB-2 sequencing (agent Inference). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-12 Dates, owners and effort for every phase.

## Unresolved Issues
- Dashboard not built; no platform chosen (Stage 31 not merged at time of writing).

## Residual Risks
- RR-36-16 A dashboard shows green on parity (Medium; rule 3). RR-36-17 Plan read as approved (all PROPOSED).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
