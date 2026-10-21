---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "delivery-dependencies.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/{delivery-backlog,increment-plan}.md", "docs/17-implementation-prd/{implementation-prd (IP-7, IP-9 DEP-01..DEP-05),release-boundaries (RB-4),prioritized-capabilities (PC-4)}.md", "docs/14-transformation/{cutover-plan,dependency-sequence,rollback-strategy}.md", "hub/config.py L39-42", ".github/workflows/verify.yml", ".fde/orchestrator-decisions.md (OD-14, OD-16, OD-21, OD-23, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Dependencies are logical (what must exist before what); there is no calendar.**

## Summary
Three dependency types: **D-W** work item -> work item, **D-Q** work item -> human decision, **D-X** external / environmental. The **critical path to the first possible cutover step** is: DQ-02 -> DW-02 -> DW-05 -> DW-04 -> DW-06 -> DW-17 -> (DW-13 -> DW-16) -> DW-21 -> DQ-06/DQ-07 -> DW-25/DW-27 -> DW-26 -> DW-34 -> DQ-13 + DQ-14 -> DW-35 -> DW-36..DW-40. Every path into W5 ends on at least one accepted-open human decision, so the plan's completion of W5 is decision-bound, not engineering-bound. [Inference]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DD-1 Work-item dependencies (D-W)
| Item | Needs | Why | Tag |
|---|---|---|---|
| DW-04 | DW-05, DW-02 | observed values must match a registered DV row exactly or they classify as D5; regression must include TST-CO-03 | [Verified Fact] TG-4 |
| DW-06 | DW-02, DW-03 | refactor needs complete, cap-safe regression | [Inference] |
| DW-07, DW-08 | DW-06 | use the single Zone H check | [Inference] |
| DW-16 | DW-13 | schemas must carry the IC-7 additive fields first | [Verified Fact] DC-02 |
| DW-17 | DW-06 | one Zone H / approval path | [Inference] |
| DW-21 | DW-02..DW-17 merged | TEVV verifies the finished W1-W2 build | [Inference] |
| DW-22 | DW-08 | walkthrough of FR-REV-01 / FR-GATE-06 should see the automatic trace producer | [Inference] |
| DW-23 | DW-14, DW-15 | H3 / H5 re-run after the tests exist | [Verified Fact] |
| DW-26 | DW-25, DW-27, DW-03 | CI needs fixtures, a 3.12+ golden set, and cap-free groups | [Verified Fact] RTD-01, S16-D14 |
| DW-28, DW-32, DW-42, DW-43, DW-48 | DW-26 | run on the production runtime / in CI | [Inference] |
| DW-29 | DW-06 | runner consolidation after package clean-up | [Inference] |
| DW-33 | DW-29 | tabletop uses the consolidated restore path | [Inference] |
| DW-34 | DW-04, DW-05, DW-21, DW-26 | G1 needs observed probes; G4/G8/G9/G10 evidence needs TEVV / CI | [Verified Fact] RTD-74 |
| DW-35 | DW-04 | decisions are checked by observed comparison | [Verified Fact] |
| DW-36..DW-40 | DW-17, DW-34, DW-35 (DW-36 not DW-35: CUT-1 has no DV) | authority switch, gates, DV state | [Verified Fact] CF-2 |
| DW-37..DW-39 | DW-11 | consumer re-point (CO-2 step 4) | [Verified Fact] CF-1 |
| DW-38 | DW-10 | contract decision support | [Verified Fact] |
| DW-40 | DW-15, DW-19, DW-26, DW-30 | exposure prerequisites | [Verified Fact] RB-3 |
| DW-41 | DW-30 | R2 items served by the chosen entry point | [Verified Fact] RTD-81 |
| DW-47 | DW-46 | handover needs a receiving owner (GAP) | [Verified Fact] DR-30 |
| DW-50 | all | FINAL dispositions | [Verified Fact] |

### DD-2 Decision dependencies (D-Q)
| Decision | Gates | Can work proceed on the safe default? | Tag |
|---|---|---|---|
| DQ-01, DQ-02 | W1 start | yes, at risk (A-17-SO-1 practice) | [Verified Fact] |
| DQ-03, DQ-04 | DW-13 closure, DW-16 final, DW-26 scripts | yes; addendum stays authoritative | [Verified Fact] A-17-IP-1 |
| DQ-05 | DW-09 | no (two different implementations) | [Inference] |
| DQ-06 | DW-25, DW-26 | partly: hub suites can run in CI without FX-BASE125 tests; harness cannot | [Verified Fact] RTD-01 |
| DQ-07 | DW-27 | harness on 3.12+ cannot pass without a reviewed baseline | [Verified Fact] ENV-1..6 |
| DQ-08 | DW-30, DW-40, DW-41 | yes for loopback; no for exposure | [Verified Fact] |
| DQ-09 | DW-19, DW-40 | yes (proposals, labelled) | [Verified Fact] |
| DQ-10, DQ-11 | DW-22, DW-21 wording | DQ-10: Dinesh performs by default | [Verified Fact] OD-24 |
| DQ-12, DQ-16 | DW-41 | yes; items stay off | [Verified Fact] |
| DQ-13 | DW-35, DW-37..DW-39 | **no**: CUT-2..CUT-4 cannot run | [Verified Fact] CF-3 |
| DQ-14 | DW-36..DW-40 | **no** for the step concerned | [Verified Fact] RB-4 |
| DQ-15 | DW-11, DW-37..DW-39 step 4 | no | [Unknown] |
| DQ-17 | DW-20 | yes; single-approver risk recorded | [Verified Fact] |
| DQ-18 | none planned | yes (hold-all) | [Verified Fact] |
| DQ-19 | DW-45 | yes (synthetic only) | [Verified Fact] |

### DD-3 External / environmental dependencies (D-X)
| ID | Dependency | State | Affects | Tag |
|---|---|---|---|---|
| X-1 | Python 3.12+ interpreter for CI / production | not on the laptop (3.10.12 only); cloud workspace 3.13 | DW-26..DW-28 | [Verified Fact] Stage 14 E-4, OD-23 |
| X-2 | Python 3.10 line end-of-life (Oct 2026) | floor kept for tests / goldens only (OD-24) | production claim | [Verified Fact] S16-D07 |
| X-3 | GitHub Actions runner and repo `dinesh13n/gxp-quality-hub-legacy` | remote exists (OD-05 originally pending; PRs merged since OD-14) | DW-26 | [Verified Fact] OD-13/14 |
| X-4 | Existing `.github/workflows/verify.yml` | runs legacy `tests/` on 3.12 and regenerates a 6,000-case seed-4326 dataset - not the OD-09 baseline and not the hub suites | DW-26 must not treat it as baseline evidence | [Verified Fact] file read |
| X-5 | Git-ignored FX-BASE125 data | local-only; backup in `../_data-backup-2026-10-17/` | DW-25 | [Verified Fact] engagement-context note |
| X-6 | Device limits: 180 s per call; ~9.8 GB disk | group C ~145 s | DW-03, DW-31 | [Verified Fact] OD-16, OD-21 |
| X-7 | Node 22 / JDK 11 for legacy goldens | present on laptop | DW-27 on 3.12+ CI | [Verified Fact] VS-1 |
| X-8 | Real consumers, users, holders | none exist | W5, W6 | [Verified Fact] OD-04 |

### DD-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| DF-1 | [Verified Fact] L3 rollback and every CUT step depend on DW-17 because the R1 config refuses `authoritative` | `hub/config.py` L41-42 | without DW-17 Stage 30 must change code at cutover time | Medium | High | DQ-02 accept scope |
| DF-2 | [Verified Fact] CI cannot run the harness until DQ-06 and DQ-07 are answered | RTD-01; ENV-1..6 | FA-4 item 2 open | High (process) | High | — |
| DF-3 | [Inference] W1 and W2 contain no hard human-decision dependency except DQ-05; they can complete on defaults | DD-2 | engineering progress is possible now | Low | High | — |
| DF-4 | [Verified Fact] CUT-1 depends on no DV decision but on six OD-S12 decisions and Zone H decisions for gate use | RB-4 | CUT-1 is the earliest candidate if Dinesh decides its set | Medium | High | DQ-14 order |

## Evidence References
`delivery-backlog.md`; `docs/17-implementation-prd/release-boundaries.md` RB-4; `hub/config.py`; `.github/workflows/verify.yml`.

## Assumptions
- A-18-DP-1 [Assumption] Stage 14 order recommendation (CUT-2 -> CUT-1 -> CUT-3 -> CUT-4 -> CUT-5) still holds; DF-4 notes CUT-1 may be decision-ready first. Confirm: Engagement lead (Dinesh Naik) at Stage 30.

## Unknowns
- U-18-DP-1 Timing of DQ-13 / DQ-14 answers.

## Unresolved Issues
- Critical path ends on human decisions accepted open (OD-22).

## Residual Risks
- RR-DP-1 Hidden coupling between DV decisions (e.g. DV-07 / DV-10 both change intake outcome classification) may force joint decisions (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
