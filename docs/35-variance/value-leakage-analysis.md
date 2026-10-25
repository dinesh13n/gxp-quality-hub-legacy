---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "value-leakage-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/value-hypothesis.md", "docs/34-measure-after/adoption-metrics.md", "docs/37-operating-model/raci.md", "docs/37-operating-model/target-operating-model.md", "docs/28-reliability/resilience-readiness.md", "docs/26-tevv/tevv-results.md", "docs/32-finops/token-leakage-analysis.md", "docs/32-finops/tco-model.md", ".fde/orchestrator-decisions.md (OD-27, OD-30..OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Value leakage here means **intended value (Stage 3/4 baseline drivers, Stage 0C economics) that cannot yet be realised or is at risk**, each traced to a finding the repository already records. 17 leakage items are listed, sized only by repository counts (never by money). Detail on adoption and cost sits in `adoption-leakage.md` and `cost-leakage.md`. No leakage is accepted.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### VL-1 Leakage register
Columns: where value would flow (driver) / what blocks or erodes it / evidence / size (repository count only) / impact / risk / confidence / unresolved question. Class = the Stage 35 scope list.

| ID | Class | Driver at risk | Leak (finding) | Evidence | Size | Impact | Risk | Conf. | Unresolved question |
|---|---|---|---|---|---|---|---|---|---|
| VL-01 | Adoption | VD-01, VD-02, VD-04 | [Verified Fact] No production use: K-21 = 0 of 125; 0 principals; no hub store in `data/` | `adoption-metrics.md` AD-1 | 0 / 125 cases | All people-time value is nil today | High | High | D-34-01 |
| VL-02 | Adoption | VD-05, SUC-01 | [Verified Fact] Zone H holders EMPTY; no rule set can be activated; rule service ships with no active rule set (K-16 hub side Unknown) | OD-16, OD-17, OD-31; AD-4 | 0 holders; 3 inactive rule sets | Automated/assisted routing value cannot start | High | High | Real holders (Dinesh) |
| VL-03 | Control friction | all | [Verified Fact] Decision-authority switch ships OFF; CLI + `approval_ref` only; scheduler OFF | OD-19, OD-26, OD-31 | 2 switches off | Value that needs a hub-authoritative state is deferred by design | Medium | High | Stage 30 cutover decision |
| VL-04 | Unwired controls | VD-03, availability | [Verified Fact] Stage 28 resilience mechanisms (retry/breaker, listener cap 64, budget) are built but NOT wired into gateway-pull / `hub web serve` | OD-35; `resilience-readiness.md` RR-28-01 | 0 of the mechanisms wired in serve path | Protection assumed by the design is absent at run time | Medium | High | D-28-xx wiring decision |
| VL-05 | Unwired controls | audit/CI | [Verified Fact] Hardening CI `ci/hub-hardening.yml` NOT installed (HAR-07 approval needed) | OD-34 | 1 workflow not installed | Regression protection that guards value not running | Medium | High | HAR-07 |
| VL-06 | Vacant roles | all steady-state | [Verified Fact] 0 of 28 production assets have an accepted steady-state owner; 17 of 24 RACI activities have a VACANT Accountable; all roles except Dinesh VACANT | OD-34; `raci.md` | 0/28; 17/24 | No one to realise, report or defend value; RL-09 cost owner vacant | High | High | Owners to be named by Dinesh |
| VL-07 | Control friction | VD-05 | [Verified Fact] Single approver risk (DQ-17 accepted by Dinesh in OD-30 as a *risk acceptance of the single-approver design*; second reviewer not appointed) and no authorised external dispositioner exists | OD-30; `raci.md` | 1 human | Every approval waits on one person | High | High | DQ-17 second reviewer |
| VL-08 | Unsigned walkthroughs | VD-05, SUC-02 | [Verified Fact] Manual reviewer walkthroughs TST-REV-03/04/08 UNSIGNED (agent rehearsal only) | OD-24, OD-33; `tevv-results.md` | 3 of 3 unsigned | Reviewer-facing controls untested by a human | Medium | High | Human sign-off at TEVV |
| VL-09 | Open risks | all | [Verified Fact] Open and none accepted: RS-01..RS-16, RP-01..RP-12, VA-01..VA-07, RTR-01..RTR-15, F-11 + 9 complex functions | OD-33..OD-35 | 16 + 12 + 7 + 15 open registers | Risk exposure could erase value after go-live | Medium | High | Routing by Dinesh |
| VL-10 | Definition drift | VD-04, SUC-10 | [Verified Fact] DR-20/DR-21 (closed/resolved) undecided; hub policies `candidate`, none adopted; D-FIN undefined | K-11; Stage 34 | 2 of 2 undecided | Different parties may report different 'closed' figures again; K-04/K-10 stay unmeasurable | High | High | Decider for DR-20/21 |
| VL-11 | Measurement | all | [Verified Fact] No closure/evidence/effort timestamps anywhere (K-04, K-05, K-22 Unknown); no time capture in the hub | OD-07; Stage 34 C5 | 5 KPI ids Unknown both sides | Even after adoption, time benefits cannot be demonstrated | High | High | Capture design (Stage 30/31) |
| VL-12 | Measurement | all | [Verified Fact] Hub metrics use wall-clock `as_of`, so ageing cannot be compared at the frozen reference time | Stage 34 CC-2; D-34-03 | 1 parameter missing | Baseline comparison for backlog age is lost | Medium | High | D-34-03 |
| VL-13 | Measurement | all | [Verified Fact] Stage 4 freeze unsigned; v0.2 addendum for A-04-01 refutation not raised | `kpi-baseline-signoff.md`; Stage 34 | 1 sign-off missing | Baseline itself contestable | Medium | High | D-34-04 |
| VL-14 | Workflow displacement | VD-01 | [Inference] If the hub runs beside the legacy path (shadow/coexistence), reviewers would do the same work twice; the repo has no parallel-run definition. Reasoning: backfill parity shows mirroring, AD-2 notes no parallel-run coverage defined | `adoption-metrics.md` AD-2, AD-3 | not sized | Time cost before any time saving | Medium | Low | Parallel-run plan |
| VL-15 | Errors/rework (build) | cost | [Verified Fact] Late-caught defects: S21-DEV-02 (No-AI R2 defect in a test helper), S24-DEV-05 (2 I6 failures), S28-DEV-08 (4 red groups) found by the orchestrator's full regression | OD-28, OD-32, OD-35 | 3 incidents | Rework effort (hours not recorded) | Low | High | Rework hours |
| VL-16 | Latency (toolchain) | cost | [Verified Fact] Full regression 2,403 s per pass on the laptop (25 groups, 526 methods) under a 180 s call cap | `token-leakage-analysis.md` TL-03 | 2,403 s | Engineering wait time | Low | High | Cloud wall time |
| VL-17 | Cost (unpriced) | economics | [Verified Fact] Four TCO terms unpriced; actual effort unrecorded; toolchain accounts Unknown | `tco-model.md` TCO-F2, TCO-F4 | 4 terms | Net value cannot be stated | Medium | High | Inputs in TC-1 |

### VL-2 Quantification statement
[Verified Fact] Leakage is quantified as **counts of documented blockers** (17 items; 0/28 owners; 17/24 vacant A; 3/3 walkthroughs unsigned; 2 switches off; 0/125 adopted). [Unknown] Monetary and time leakage: no rate, volume or time capture exists (0C C-1..C-5, K-22). The gate wording "leakage is quantified" is met in this limited sense only.

### VL-3 Leakage classes from the stage scope with no evidence
- Overrides: no override has occurred (0 principals, 0 human dispositions; `human-override-metrics.md`). Leakage from overrides is Unknown, not zero.
- Latency: no production latency exists (`production-performance-report.md`); only toolchain latency VL-16.

## Evidence References
`docs/34-measure-after/adoption-metrics.md` AD-1..AD-4, `human-override-metrics.md`, `production-performance-report.md`; `docs/37-operating-model/raci.md`, `target-operating-model.md` TOM-2; `docs/28-reliability/resilience-readiness.md`; `docs/26-tevv/tevv-results.md`; `docs/32-finops/token-leakage-analysis.md`, `tco-model.md`; OD-16..OD-35.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).
- A-35-04 [Assumption] Leakage = intended-value-at-risk, not realised loss; nothing has been lost because nothing has been delivered to users. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-06 Time and money size of every item. U-35-07 Whether VL-14 (double work) is real; needs a parallel-run definition.

## Unresolved Issues
- VL-04 and VL-05 need Dinesh's decisions (wiring; HAR-07). VL-06 needs named owners. VL-07: DQ-17 was recorded in OD-30; wording here follows OD-30 and does not extend it.

## Residual Risks
- RR-35-07 Leakage list read as a loss figure. RR-35-08 Items treated as closed because a mechanism exists (built is not wired is not adopted).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
