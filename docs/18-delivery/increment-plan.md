---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "increment-plan.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/delivery-backlog.md (DW-01..DW-50, DQ-01..DQ-19)", "docs/17-implementation-prd/{release-boundaries,finalized-acceptance-criteria,prioritized-capabilities}.md", "docs/14-transformation/{cutover-plan,rollback-strategy,transformation-gates}.md", "docs/16-repo-validation/repo-quality-gate.md QG-4", ".fde/orchestrator-decisions.md (OD-01, OD-08, OD-13, OD-21, OD-23, OD-24)", ".fde/stage-prompts/19..43 (operating modes and artifact paths)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. A plan of increments, not a schedule: no dates, people or costs exist (OD-04). Sizes are relative estimates (synthetic, unvalidated). Owner of every human decision: Engagement lead (Dinesh Naik).**

## Summary
Remaining delivery is planned as **seven waves (W0..W6)** containing **twelve delivery increments (DI-01..DI-12)**, each mapped to a spine stage and its operating mode. Ordering rule (Stage 17 A-17-PC-1): make the build safe to rely on first (W1 change-safety), then trust controls (W2), independent verification (W3), production hardening (W4), and only then release decisions and cutover readiness (W5). W5 and W6 contain the items most likely to stall, because they depend on decisions that are 'accepted open' (OD-22). Each increment has entry criteria, exit evidence, rollback and an explicit value statement. No increment changes legacy code or `data/` (CG-4, OD-03a).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IN-1 Waves
| Wave | Purpose | Stages | Entry | Exit | Tag |
|---|---|---|---|---|---|
| W0 | Plan accepted | 18 | Stage 17 CONDITIONAL PASS | DQ-01, DQ-02 recorded (or accepted at risk) | [Verified Fact] SO-4 |
| W1 | Change safety and build completion | 19, 20, 21 | W0 | FAC-05, FAC-06 met; S16-D10 fixed; structural debt reduced; consumer and contract evidence collected | [Inference] |
| W2 | Control boundaries, security, governance | 23, 24, 25 | W1 merged | FAC-07, FAC-08, FAC-09 met; Stage 12 v0.2 issued; authority switch approval-gated | [Verified Fact] FA-4 item 4 |
| W3 | Independent verification | 26 | W2 merged | TEVV gate issued; walkthroughs recorded; mutation gates run | [Verified Fact] OD-24 |
| W4 | Hardening, resilience, continuity | 27, 28, 29 | W3 | CI on 3.12+ and 3.10 (FAC-11); migrations consolidated; tabletop done | [Verified Fact] FA-4 item 2 |
| W5 | Release readiness and cutover steps | 30, 31 | W4 + per-step decisions | per CUT step: FA-4 items 1-6 met and go/no-go recorded, or step recorded as not run | [Verified Fact] RB-4 |
| W6 | Operate, measure, transfer, close | 32-43 | W5 (whatever ran) | FINAL as-built PRD | [Inference] |

### IN-2 Delivery increments
| DI | Stage (mode) | Branch (OD-01 pattern) | Work items | Value delivered | Size | Entry criteria | Exit evidence | Rollback | Tag |
|---|---|---|---|---|---|---|---|---|---|
| DI-01 | 19 (BUILD, record only) | none (doc) or `stage-19-*` | DW-01 | confirms No-AI boundary for downstream stages | S | OD-08 | `docs/19-intelligence/not-applicable.md`; `no-ai-check` rc 0 | n/a | [Verified Fact] OD-08 |
| DI-02 | 20 (BUILD) | `stage-20-inc01-change-safety` | DW-02, DW-03, DW-05, DW-04 | golden-compare can detect a hub regression; register complete; suite fits device cap | M | DQ-02 | FAC-05/06 tests green; golden-compare report with 0 `declared:`; D5 = 0; data checksum rc 0 | L1 revert | [Inference] |
| DI-03 | 20 (BUILD) | `stage-20-inc02-structure` | DW-06 | one Zone H check; fewer cycles - lowers change risk for every later item | L | DI-02 merged | TST-GATE / TST-SEC green; mutation H1 KILLED; import / cycle report; D5 = 0 | L1 revert | [Inference] |
| DI-04 | 20 (BUILD) | `stage-20-inc03-r1-gaps` | DW-07, DW-08, DW-09 | closes R1 PARTIAL / LIMITED items FR-POL-01, FR-REV-01, FR-GATE-06; CLI errors consistent | M | DI-03 merged; DQ-05 | FAC-13 (proposed), AC-REV-05..08, AC-GATE-18..20, FAC-10 tests green | L1 + L2 (hub store restore) | [Inference] |
| DI-05 | 21 (BUILD) | `stage-21-*` (evidence only; code change only if a defect is found) | DW-10, DW-11, DW-12 | decision support for OD-S12-11 and CUT step 4; read-only integration re-proven | M | DI-02 merged | contract pack; consumer inventory; TST-CO-04/05 green | n/a (no code) | [Inference] |
| DI-06 | 23 (BUILD) | `stage-23-*` | DW-13, DW-14, DW-15, DW-16, DW-17, DW-18 | test gaps SS-04/SS-08 closed; schemas executed; authority switch approval-gated; Stage 12 v0.2 | L | DI-03 merged; DQ-03/04 for final schema text | FAC-07/08/09 green; H3/H5 KILLED; registry diff 0; DW-17 tests both modes | L1 | [Verified Fact] FA-4 item 4 |
| DI-07 | 24 (BUILD) + 25 (DESIGN) | `stage-24-*` | DW-19, DW-20 | security values decided or accepted open; obligations mapped | L | DI-06; DQ-09, DQ-17 | TST-SEC-01..21; scan rc 0; TST-NFR-10; governance map | L1 | [Verified Fact] OD-24 conditions |
| DI-08 | 26 (VALIDATE) | none (evidence in `docs/26-tevv/`) | DW-21, DW-22, DW-23, DW-24 (as triggered) | objective TEVV gate; human walkthrough evidence | L | DI-02..DI-07 merged; DQ-10, DQ-11 | per-runtime results; signed walkthrough records; mutation report | n/a | [Verified Fact] OD-24 |
| DI-09 | 27 (BUILD) | `stage-27-*` | DW-25, DW-26, DW-27, DW-28, DW-29, DW-30, DW-31 | suites gate every change in CI on the production runtime | L | DI-08; DQ-06, DQ-07, DQ-08, DQ-04 | CI runs green (3.12+ and 3.10); reviewed goldens; restore rehearsal | L1; CI change revert | [Verified Fact] FAC-11 |
| DI-10 | 28 (BUILD) + 29 (VALIDATE) | `stage-28-*` | DW-32, DW-33 | resilience proxies and continuity proven in sandbox | M | DI-09 | TST-NFR-01/02/05 labelled proxies; CT-17; tabletop record | L1 | [Inference] |
| DI-11 | 30 (BUILD) + 31 (BUILD) | `stage-30-cut<n>-*` per step; `stage-31-*` | DW-34, DW-35, DW-36..DW-40, DW-41, DW-42 | per-capability cutover readiness; release checklist evidence | L (per step M) | DI-10; DQ-13, DQ-14 per step; DQ-15 for CUT-2..4 | G1..G10 per step; go/no-go record by Dinesh; or "not run - decision accepted open" record | L3 authority flip (needs DW-17) + L1/L2 | [Verified Fact] RB-4 |
| DI-12 | 32-43 (OPERATE / DESIGN / VALIDATE) | per stage | DW-43..DW-50 | measured (synthetic) outcomes, ownership, handover, FINAL | M each | DI-11 (whatever ran) | stage artifacts; FINAL FR dispositions | n/a | [Inference] |

### IN-3 Increment value and size analysis
| Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|
| IF-1 [Inference] DI-02 has the highest value per size: without observed probes (FAC-05), a module regression passes golden-compare, so every later green result is weaker | S16-D01; `hub/golden/run.py` L53 | W1 first | Medium | High | — |
| IF-2 [Verified Fact] DI-06 includes new scope DW-17: the R1 build refuses `capability_authority = authoritative`, so CUT steps and L3 rollback are not executable without it | `hub/config.py` L41-42; rollback-strategy L3 | CUT readiness depends on W2 | Medium | High | Dinesh to accept scope (DQ-02) |
| IF-3 [Inference] DI-09 is the largest increment and sits on three decisions (DQ-06/07/08); the 3.10 line is end-of-life (S16-D07) | S16-D07; OD-24 | production readiness cannot be claimed before W4 | High (production) | Medium | — |
| IF-4 [Verified Fact] DI-11 cannot complete any CUT step today: every step needs at least one accepted-open decision | release-boundaries RB-4 "none can start now" | W5 may end with every step "not run" | High (value) | High | DQ-13/14 timing |
| IF-5 [Inference] DI-04 and DI-03 are optional for cutover safety but reduce rework; they can be deferred if Dinesh prefers, with risk recorded | PS-02 (P2) | ordering flexible | Low | Medium | — |

### IN-4 Parallelism (OD-23 item 3)
[Inference] Doc-only items may run in parallel when neither consumes the other's artifacts: DI-05 (evidence-only) can run beside DI-03/DI-04; DW-18 and DW-20 (documents) beside DI-06 build; DW-44, DW-46 beside W4. Build increments on `main` stay sequential (one PR at a time, OD-13), and every build increment's own new tests run on the laptop while the full hub regression runs once in the orchestrator's cloud workspace before merge (OD-23 items 1-2).

### IN-5 Common increment exit gate (reused from Stage 14 TG-2)
CG-1 sandbox-only; CG-2 CT-01..CT-16 green on unmodified legacy (3.10.12); CG-4 legacy paths unchanged since `baseline-as-found`; CG-5 backup checksum rc 0 before / after; CG-7 No-AI guard green; CG-8 increment tests pass, class-B in both modes; CG-9 D5 = 0; CG-10 rollback described; CG-11 clean status, no DB / lake committed. [Verified Fact] `docs/14-transformation/transformation-gates.md` TG-2. Plus: device call < 180 s (OD-21), sandbox cleanup (OD-16).

## Evidence References
`delivery-backlog.md`; `docs/14-transformation/transformation-gates.md` TG-2; `docs/17-implementation-prd/release-boundaries.md` RB-4; `hub/config.py`.

## Assumptions
- A-18-IN-1 [Assumption] Increment and branch naming `stage-NN-<slug>` as in OD-01 / OD-11. Confirm: Engagement lead (Dinesh Naik).
- A-18-IN-2 [Assumption] Stage 20 hosts the change-safety build (DI-02..DI-04) because its prompt covers application / services build per specification.

## Unknowns
- U-18-IN-1 Whether any CUT step will be executed in this engagement (depends on DQ-13/14).
- U-18-IN-2 Calendar duration of any increment (no calendar; U-17-RB-2).

## Unresolved Issues
- DQ-01/DQ-02 before W1; DQ-05 before DI-04; DQ-03/04 before DI-06 closes; DQ-06/07/08 before DI-09.

## Residual Risks
- RR-IN-1 W5 stalls on accepted-open decisions; mitigation: W5 exit allows a recorded "not run" per step so W6 can proceed honestly (Medium).
- RR-IN-2 Device cap (180 s) and disk (~9.8 GB, OD-16) constrain test growth; DW-03 and DW-31 address it (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
