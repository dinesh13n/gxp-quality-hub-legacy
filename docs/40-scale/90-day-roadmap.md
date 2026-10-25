---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "90-day-roadmap.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/40-scale/reuse-readiness-assessment.md", "docs/40-scale/scale-out-backlog.md", "docs/40-scale/scale-risk-assessment.md", "docs/40-scale/adjacent-use-case-inventory.md", "docs/14-transformation/dependency-sequence.md", "docs/14-transformation/cutover-plan.md", "docs/26-tevv/tevv-release-gate.md", "docs/27-hardening/production-readiness-checklist.md", "docs/28-reliability/resilience-readiness.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/36-roi/roi-model.md", "docs/36-roi/payback-analysis.md", "docs/37-operating-model/target-operating-model.md", ".fde/orchestrator-decisions.md (OD-01..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 40 adds files under `docs/40-scale/` and changes nothing else). This roadmap is a PROPOSAL sequenced by dependency and by the open decisions the repository already records. It uses relative days (D+0..D+90) and roles; Dinesh Naik is the only named person. It does NOT say the value case is proven (Stage 36: ROI NOT COMPUTABLE, 0 verified benefits). It schedules NO cutover: Stage 30 is prepared separately and the cutover decision is Dinesh's. It accepts no risk on his behalf. No date, budget, headcount, stakeholder or commitment is invented.**

## Summary
**What the roadmap is:** a gated sequence that takes the hub from "built in a sandbox, nothing switched on" to a decision on whether to widen use, in four phases inside 90 relative days, with three scale steps defined by what must be true before each: **Pilot (S1) -> Limited (S2) -> Broader (S3)**. **What it is not:** a plan to cut over, a business case, or a commitment.

**Three honest results.**
1. **Gates, not days, control progress.** All 17 scale pre-conditions are unmet at main `ef72e4e` (`reuse-readiness-assessment.md` RR-1). Day windows are the earliest relative envelope; if a gate's criteria are not met when its window ends, the next phase does not start (slip rule RM-6).
2. **90 days reaches, at most, a limited-entry decision (G2).** Limited (S2) and Broader (S3) are defined but not scheduled; they fall after D+90.
3. **Value may still be unproven at D+90.** A 30-day pilot window (D+46..D+75) is the maximum the envelope allows; whether it is long enough to measure persistence or a month-end is Dinesh's call (D-34-02). Unless the window completes and the Stage 36 slots are filled with measured values and a finance-approved rate, the correct statement at D+90 remains "ROI not computable".

## Findings
### RM-1 Reading rules [Verified Fact: derived from the Stage 40 constraints and OD-32]
- **D+0** = the day Dinesh records a go-ahead for this roadmap (SB-01). It is not a calendar date; mapping to calendar dates is Unknown until he sets it.
- **Owners are roles.** Dinesh Naik = Engagement lead. Every other role is Unknown / TBD / VACANT (`target-operating-model.md` TOM-4). "Orchestrator (agent)" executes regression and merges under OD-13 and holds no approval right.
- **A decision exists only when Dinesh answered or approved it** (OP-A, GP-2). 'Accepted open' is a legitimate answer; the roadmap then carries the open item as a standing constraint on later gates.
- **Default-answer authority (OD-32)** covers scope and sequencing choices in this file (taken as Assumptions A-40-xx). It does not cover accepting risk, naming Zone H holders or stakeholders, approving cutover, or any irreversible step.

### RM-2 Scale steps defined (Assumptions, A-40-12)
| Step | Meaning | What it is not | Units |
|---|---|---|---|
| S0 Sandbox (today) | Hub built beside legacy; synthetic 125-case data; everything consequential OFF; loopback only | production | n/a |
| S1 Pilot | Real reviewers use the hub in **shadow beside legacy** for **one unit** (one site or one feed; Dinesh chooses), under an approved data decision. Legacy stays authoritative | Not a cutover. CUT-1..CUT-5 (`cutover-plan.md`) are untouched and unscheduled; no capability becomes authoritative unless Dinesh separately approves it (DW-17) | 1 |
| S2 Limited | More units of the same use case (AU-01 sites, AU-02 feeds), one at a time | Not adjacent use cases | N = Unknown; Dinesh sets N |
| S3 Broader | Adjacent use cases beyond AU-01/AU-02 (AU-03, AU-04, later AU-05/06) and steady-state operation | Not AU-07 (AI), excluded under OD-08 | Unknown |

### RM-3 Phases (relative days; backlog IDs from `scale-out-backlog.md`)
| Phase | Window | Purpose | Backlog items | Ends with | Value-evidence output |
|---|---|---|---|---|---|
| P0 Decide | D+0 .. D+14 | Close the decisions everything else waits on; consume Stage 39 | SB-01, 02, 03, 08, 09, 37, 38 | Gate G0 | none (decisions only) |
| P1 Make fit to pilot | D+15 .. D+45 | Close the pilot pre-conditions: owners and holders, data and exposure decisions, 3.12+ evidence, F-29-01, wiring or 'not used', backup drill, walkthroughs, after-window definition | SB-04..07, 10..15, 16..21, 22, 26..28, 31, 32 | Gate G1 | window definition, capture method |
| P2 Pilot (conditional) | D+46 .. D+75 | Operate S1 for one unit; daily tripwire and chain checks; capture K-21, time, cost inputs | SB-23, 25, 29 (and operation of the pilot) | end of the defined window | first production-basis values (K-21 etc.), if real people use it |
| P3 Evaluate and decide | D+76 .. D+90 | Re-run Stages 34/35/36 as v0.2 on whatever window completed; decide limited entry; re-issue this roadmap as v0.2 | SB-24, 30, 33, 34, 39 | Gate G2 decision | Stage 34/35/36 v0.2 |
| After D+90 | not scheduled | S2 Limited, then S3 Broader | SB-33..36, 40 | G3, G4 | |

Sub-order inside P1 (dependency order, not dates): (a) D+15..D+25 decisions and small fixes: SB-04, 05, 06, 08->12, 18, 20, 21, 10; (b) D+26..D+40 build and verification: SB-13, 16, 17, 14, 19, 11, 22, 26, 27, 28, 31, 32; (c) D+41..D+45 gate review. Reason: wiring (SB-16/17) must precede the TEVV delta (SB-14); the 3.12+ run (SB-12) needs the floor decision (SB-08); the after-window definition (SB-27) needs owners and definitions (SB-05, 06).

### RM-4 Dependency spine
```
SB-01 -> SB-02 -> {SB-04,05,06,08,20,21} -> SB-12 -----------\
SB-09 (Stage 39) ---------------------------------------------+-> G0 -> P1
SB-18 (F-29-01) -> SB-23                                       |
SB-16/17 (wire or 'not used') -> SB-14 (TEVV delta) -----------+-> G1 (pilot entry)
SB-05,06 -> SB-27 (window) -> SB-28 -----------------------------|
SB-10 (Stage 30 outcome, Dinesh's decision, NOT scheduled here) -/
G1 -> P2 pilot window -> SB-30 (v0.2 of 34/35/36) -> G2 (limited entry)
G2 -> S2 limited -> G3 -> S3 broader -> G4
```
Critical path [Inference]: **SB-02 -> SB-05/06 -> SB-27 -> pilot window -> SB-30**. It runs through Dinesh's decisions, not through code (RRF-2).

### RM-5 Gates: entry and exit criteria
HARD = must be met. SOFT = may be recorded by Dinesh as 'accepted open' with its effect stated; the gate outcome is then CONDITIONAL (a gate outcome uses the stage vocabulary: PASS / CONDITIONAL / HOLD; HOLD = a HARD criterion unmet, next phase does not start).

**G0 Roadmap go-ahead and decisions (end of P0)**
| ID | Criterion | Class | Backlog | Evidence |
|---|---|---|---|---|
| G0-1 | Go-ahead (or not) and meaning of D+0 recorded | HARD | SB-01 | OD entry |
| G0-2 | Every open item in the Stage 26-37 lists has an answer, including 'accepted open' | HARD | SB-02 | Disposition table |
| G0-3 | Scale gate rules adopted or amended | HARD | SB-37 | OD entry |
| G0-4 | Stage 39 merged and read, or deferral recorded | HARD | SB-09 | Roadmap v0.2 or note |
| G0-5 | Python floor decision | HARD | SB-08 | OD entry |
| G0-6 | Scale risks routed or left open explicitly | SOFT | SB-38 | Register |

**G1 Pilot entry (end of P1): what must be true before S1**
| ID | Criterion | Class | Backlog | Evidence / pre-condition |
|---|---|---|---|---|
| G1-1 | Walkthroughs TST-REV-03/04/08 signed (reviewers will use these surfaces) | HARD | SB-11 | PRE-01, RTR-07 |
| G1-2 | Full regression green on Python 3.12+/3.13 at the then-current HEAD; checksum gate rc 0 | HARD | SB-12 | PRE-02, RT-14 |
| G1-3 | Zone H holders named, or Zone H declared unused for the pilot; no capability authoritative | HARD | SB-04 | PRE-06, PC-2 |
| G1-4 | Pilot responder named (support, escalation) and ownership of the pilot unit's assets recorded, or single-approver stated explicitly by Dinesh | HARD | SB-05, SB-31 | PRE-07, PC-3 |
| G1-5 | Data decisions made: field classes, tenant, regime, retention | HARD | SB-21 | PRE-11 |
| G1-6 | Exposure posture decided; if wider than loopback, TLS, second factor and token expiry MET | HARD | SB-20 | PRE-10, PR-06/07/14 |
| G1-7 | Off-device backup and a timed restore drill done | HARD | SB-19 | PRE-08, PR-25 |
| G1-8 | F-29-01 fixed and tested; remaining F-xx dispositioned | HARD | SB-18 | PRE-09 |
| G1-9 | Stage 28 controls wired, or recorded 'not used'; TEVV delta green | HARD | SB-16, 14 | PRE-04 |
| G1-10 | After-window defined: start, unit, minimum duration, data owner; capture method for time and effort | HARD | SB-27, 28 | PRE-12, D-34-02 |
| G1-11 | Stage 30 outcome and Dinesh's cutover decision recorded (the roadmap takes no position) | HARD | SB-10 | PRE-17 |
| G1-12 | Non-carry checklist run for the pilot unit | HARD | SB-40 | RC-4 |
| G1-13 | CI gate installed with pinned actions | SOFT | SB-13 | PRE-03 |
| G1-14 | Observability wired; SLOs adopted or left as candidates | SOFT | SB-17 | PRE-05 |
| G1-15 | Stage 4 v0.2 addendum / `as_of` decision | SOFT | SB-26 | PRE-13 |
| G1-16 | Source contract for the pilot feed (if the unit is a feed) | SOFT | SB-22 | OD-28 |
**No-pilot branch:** if no real reviewers or real data exist when P1 ends (D-34-01 says none exist today), the roadmap **holds at G1**. P2 does not start. Dinesh then decides whether to stop, hold, or continue to prepare. That is not a failure state of the roadmap; it is the honest result that the value case cannot be tested.

**G2 Pilot exit and limited entry (end of P3): what must be true before S2**
| ID | Criterion | Class | Evidence |
|---|---|---|---|
| G2-1 | The defined after-window completed (whatever length Dinesh set) | HARD | Window record |
| G2-2 | Zero tripwire breaches: model calls 0, egress 0, service-actor accepted 0; audit chain verifies at window end | HARD | INV-01..03, `verify-audit` |
| G2-3 | Legacy unchanged (checksum rc 0); no unexplained difference between legacy and hub results | HARD | TST-CO-05, parity checks |
| G2-4 | No open High or Medium finding from the pilot; incidents of SEV-A/B reviewed | HARD | TEVV delta, incident log |
| G2-5 | Stage 34, 35, 36 v0.2 produced on the completed window | HARD | `docs/34..36` v0.2 |
| G2-6 | Value statement is whichever the evidence supports. If slots I-01..I-14 are filled with measured values and a finance-approved rate: computed. Otherwise: stated 'unproven / not computable'. Proceeding either way is Dinesh's explicit recorded decision, labelled as economic or non-economic grounds. **This roadmap does not choose** | HARD (statement), decision is his | `roi-model.md` RM-3 |
| G2-7 | Owners of the assets in use accepted, or each gap accepted by Dinesh in writing | HARD | `raci.md` |
| G2-8 | Reviewer feedback captured; K-21 measured | SOFT | pilot record |
| G2-9 | First reuse trial recorded (grade E2 until a real second unit runs) | SOFT | SB-25 |
| G2-10 | Cost inputs filled for the pilot (toolchain, hosting, effort) | SOFT | SB-29 |

**G3 Limited exit and broader entry (after D+90, not scheduled): what must be true before S3**
G3-1 each S2 unit completed its own window under G2-2..G2-4; G3-2 steady-state owners ACCEPTED for every asset in use (today 0 of 28); G3-3 SLOs decided and measured, cost owner named and cost model terms filled; G3-4 for each adjacent candidate: a sponsor, a Stage 3-style framing, definitions signed, readiness re-scored; G3-5 at least one component reused in a second unit with passing checks (first real E3); G3-6 governance (Stage 25) and risk registers re-issued for the larger footprint; G3-7 non-carry checklist per unit; G3-8 retention and data rules decided; G3-9 TEVV re-run. **G4** (steady-state / broader decision) is outside the 90 days.

### RM-6 Slip, hold and stop rules
- **Slip:** a phase starts only when the previous gate has no unmet HARD criterion. Days not used are not recovered by compressing later work.
- **Hold:** a HARD criterion answered 'accepted open' by Dinesh is no longer unmet; it becomes a recorded constraint and the gate outcome is CONDITIONAL. The roadmap does not decide that for him.
- **Stop:** any SG-6 stop condition (`scale-governance.md`) halts scaling and returns to the previous step; consequential switches go back OFF (PT-03). Resuming is Dinesh's decision.
- **The 90 days is an envelope, not a deadline.** Missing it makes the roadmap longer, not weaker.

### RM-7 Prioritisation by value and readiness
| Workstream | Evidence value for the value case [Inference] | Readiness today | Order |
|---|---|---|---|
| W0 Decide (SB-01..10) | Unlocks everything (all PC-1..10 start with a decision) | Ready: needs only Dinesh | 1 |
| W2 Hardening and wiring (SB-16..21) | Low direct; removes SR-05, SR-09, SR-10 | Mostly ready (small build; some approvals: HAR-07, HAR-09) | 2 |
| W1 Verification (SB-11..15) | Protects honesty of any value claim | Ready for SB-12; SB-11 needs Dinesh | 2 |
| W4 Measurement (SB-26..30) | **Highest**: fills I-01..I-14 | Blocked on SB-05/06/27 | 3 (starts early, completes after pilot) |
| W3 Operating model (SB-31, 32) | Required for any real use | Blocked on role holders | 2 |
| W5 Packaging (SB-22..25) | Reuse, not value | Partly ready | 4 |
| W6 Adjacent (SB-33..36) | Candidate-dependent; Unknown | Not ready; after G2 | 5 |
| W7 Governance (SB-37..40) | Control | Ready | 1 |

### RM-8 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RMF-1 | [Verified Fact] No pilot is possible from repository evidence alone: the hub is not in production, no real reviewer has used it, no holder or owner exists | D-34-01, K-21 = 0 of 125, OD-34 | Roadmap holds at G1 unless people and data exist | High | High | Do real reviewers and data exist or can they be obtained? |
| RMF-2 | [Inference] The first-order work is decisions (W0, W3, W4 definitions), not engineering; engineering items are small relative to them | RRF-4 | Sequencing around Dinesh's availability | Medium | Medium | Decision capacity (SR-06) |
| RMF-3 | [Verified Fact] The roadmap contains no cutover, date, budget, headcount or named stakeholder other than Dinesh | this file | Compliant with the engagement constraints | Low | High | none |
| RMF-4 | [Inference] The value case cannot be proven inside 90 days unless Dinesh defines a window that fits and real data arrives | PC-1, I-02, SR-11 | G2-6 will likely read 'unproven' | High | Medium | Window length (D-34-02) |
| RMF-5 | [Unknown] Effect of Stage 39 drift findings on any phase | Stage 39 not merged | v0.2 may change phases | Medium | n/a | SB-09 |

## Evidence References
See `evidence_sources`; criteria cite `reuse-readiness-assessment.md` PRE-01..PRE-17, `scale-out-backlog.md` SB-xx, `scale-governance.md` SG-xx.

## Assumptions
- A-40-12 Scale-step definitions (RM-2): pilot = shadow beside legacy for one unit. Confirm: Engagement lead (Dinesh Naik).
- A-40-13 Phase windows (14 / 31 / 30 / 15 days) are an agent envelope, not a measured duration. Confirm: Engagement lead (Dinesh Naik).
- A-40-14 HARD/SOFT classification of gate criteria is the agent's. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-14 Calendar mapping of D+0 and any real deadline (none recorded).
- U-40-15 Number of units in S2 (N) and who staffs them.
- U-40-16 Whether a pilot unit with real reviewers can be found.

## Unresolved Issues
- Stage 30 (prepared separately) and Stage 38 outcomes feed G1-11 and SB-32; Stage 39 feeds G0-4.

## Residual Risks
- SR-01, SR-02, SR-03, SR-06, SR-07, SR-11 (`scale-risk-assessment.md`) remain open throughout.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
