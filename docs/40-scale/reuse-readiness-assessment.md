---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "reuse-readiness-assessment.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/40-scale/reusable-components.md", "docs/40-scale/adjacent-use-case-inventory.md", "docs/27-hardening/production-readiness-checklist.md", "docs/26-tevv/residual-tevv-risks.md", "docs/28-reliability/resilience-readiness.md", "docs/37-operating-model/target-operating-model.md", "docs/36-roi/payback-analysis.md", "docs/35-variance/corrective-action-backlog.md", ".fde/orchestrator-decisions.md (OD-33..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL. No value claim (Stage 36: ROI NOT COMPUTABLE), no cutover scheduled, no risk accepted for Dinesh Naik. Ratings are ordinal (High / Medium / Low) agent Inference; no score is computed from invented weights.**

## Summary
Readiness has two layers. **Layer 1 (the first use case)** is not yet ready to be the base for scaling: 14 of 38 production-readiness checks are NOT MET or UNKNOWN, 0 of 28 assets have an accepted steady-state owner, every client-side role is VACANT, and no production after-window exists. **Layer 2 (reuse into adjacent candidates)** inherits all of that and adds per-candidate gaps. Result: *no adjacent candidate is ready now; AU-01 and AU-02 are the least unready*, and they become assessable only after the first use case passes pilot entry (Gate G1) and pilot exit (G2) in `90-day-roadmap.md`.

## Findings
### RR-1 Pre-conditions for scaling (status at main `ef72e4e`) [Verified Fact unless marked]
| ID | Pre-condition | Status | Source |
|---|---|---|---|
| PRE-01 | Human walkthroughs TST-REV-03/04/08 signed | NOT MET (blank records) | RTR-07, OD-24, OD-33 |
| PRE-02 | Regression evidence on Python 3.12+; floor decision | NOT MET (3.10 only; 3.10 end of life 2026-10-01 per PR-28; production target 3.12+ per OD-24) | PR-28, PR-29, U-27-01, RTR-08, D-27-02 |
| PRE-03 | CI gate installed with pinned actions | NOT MET (`ci/hub-hardening.yml` written, not installed; HAR-07 approval needed) | PR-30, PR-31, D-27-03 |
| PRE-04 | Stage 28 resilience wired | NOT MET (built, not wired) | D-28-01, D-28-02, S28-DEV-01 |
| PRE-05 | Stage 31 observability wired; SLO numbers decided | NOT MET (nothing wired; 5 CANDIDATES; SLO-04, SLO-05 have no SLI) | D-31-01..10, F-31-01..07 |
| PRE-06 | Zone H holders named, or Zone H declared unused | NOT MET (`zone_h.holders` empty) | OD-17, OD-31, PC-2 |
| PRE-07 | Steady-state owners accepted | NOT MET (0 of 28 assets; RL-02..RL-11 VACANT) | OD-34, TOM-2 |
| PRE-08 | Off-device backup and restore drill | NOT MET | HAR-09, PR-25, Stage 29 Q-29-01..09 |
| PRE-09 | Known defect F-29-01 (`verify-audit` KeyError) and open findings F-11 + 9 complex functions routed | NOT MET | OD-35, OD-34 |
| PRE-10 | Exposure controls matched to posture (TLS, second factor, token expiry) | NOT MET but NOT APPLICABLE while loopback-only | PR-06, PR-07, PR-14; RS-01, RS-02, RS-08 |
| PRE-11 | Data decisions before real data: field classes, tenant, regime, retention | NOT MET (hold-all interim) | DQ-S24, OD-S12-09, GD-07 |
| PRE-12 | Real after-window defined and the measured values exist | NOT MET (hub not in production; K-21 = 0 of 125) | D-34-02, PC-1 |
| PRE-13 | Stage 4 v0.2 addendum + `as_of` decision; definitions closed/resolved/48 h | NOT MET | D-34-03, D-34-04, PC-4, PC-6 |
| PRE-14 | Open risk registers routed (accept / fix / defer): RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-xx | NOT MET (none accepted, many open) | PC-10, CA-14 |
| PRE-15 | Economics: cost owner, finance-approved rate, discount rate | NOT MET | I-10, PC-9, RL-09 |
| PRE-16 | Stage 39 drift evidence consumed | NOT MET (Stage 39 not merged at `ef72e4e`) | U-40-09 |
| PRE-17 | Stage 30 outcome and Dinesh's cutover decision recorded (whichever way) | NOT MET (Stage 30 prepared separately; cutover is Dinesh's decision; this stage does not schedule it) | OD-32 |

### RR-2 Layer 1: components (summary of `reusable-components.md`)
| Tier | Count | Readiness reading |
|---|---|---|
| A | 3 | Ready to extract once PRE-02, PRE-09 close (RC-02) |
| B | 13 | Ready conditionally; most conditions are PRE items or owner decisions |
| C | 4 | Not ready: wiring (PRE-04, PRE-05) or deliberately off (RC-16) |
| X | 11 | Excluded |

### RR-3 Layer 2: adjacent candidates (six dimensions, ordinal, Inference)
| Candidate | Reuse evidence | Value (evidence value / business value) | Readiness | Commonality | Dependencies | Scale risk | Priority (this stage's rule) |
|---|---|---|---|---|---|---|---|
| AU-01 more sites | Medium (E2 for components, E3 none) | High / Unknown | Low (needs PRE-01..PRE-14 and a pilot) | High | 6 (PRE-06, PRE-07, PRE-11, PRE-12, regime, local owners) | Medium | **1** |
| AU-02 more feeds | Medium | Medium / Unknown | Low-Medium (contract + schema exist; per-source contracts and source owner do not) | High | 5 | Medium | **2** |
| AU-03 finance read surface | Low (not built; data class new) | High / Unknown | Low (no owner, no finance classes, no read surface) | Medium | 6 | High (data protection) | **3** |
| AU-04 archived estate | Low | Low-Medium / Unknown | Low | Low-Medium | 4 | Medium | 4 (scoping decision first) |
| AU-05 parallel workflow | None | Unknown | Not assessable | Unknown | Unknown | Unknown | not ranked |
| AU-06 another regime/tenant | None | Unknown | Not assessable | Unknown | Unknown | High | not ranked |
| AU-07 AI doc Q&A | None | Unknown | Not applicable under OD-08 | Low | New decision + approvals | Very high | excluded |

**Priority rule (A-40-07):** order by (1) readiness *after* the gate conditions in the roadmap can be met, then (2) evidence value (helps fill I-01..I-14), then (3) lower scale risk. It is not a value ranking and implies no benefit.

### RR-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RRF-1 | [Verified Fact] No component has been reused (E3 = 0) | `reusable-components.md` RC-1 | Reuse claims are structural | High if overstated | High | First reuse outcome |
| RRF-2 | [Inference] The binding constraint is human and decision capacity (one named human; 10 vacant roles), not code | TOM-4, OD-04 | Scale steps wait on decisions | High | High | Who can hold roles |
| RRF-3 | [Verified Fact] All 17 pre-conditions are NOT MET at `ef72e4e` (PRE-10 is not applicable while the hub stays loopback-only) | RR-1 | Nothing scales yet | High | High | Order of closure |
| RRF-4 | [Inference] Closing PRE items is mostly decisions and approvals; the build items (wire resilience/observability, fix F-29-01, 3.12 evidence) are small relative to the decisions | D-28, D-31, D-27 lists | Plan around decisions | Medium | Medium | No effort data (U-40-05) |

## Evidence References
See `evidence_sources`; per-row IDs.

## Assumptions
- A-40-07 Priority rule above. Confirm: Engagement lead (Dinesh Naik).
- A-40-08 [Assumption] PRE-10 is not required while the hub stays loopback-only (D-27-09 "stay loopback-only" is an open decision).

## Unknowns
- U-40-09 Stage 39 drift findings (not available).
- U-40-10 Demand, owners, volumes for adjacent candidates.

## Unresolved Issues
- Stage 36 inputs I-01..I-19 and preconditions PC-1..PC-10 remain open and gate any value statement.

## Residual Risks
- Reading "least unready" as "ready" (SR-03).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
