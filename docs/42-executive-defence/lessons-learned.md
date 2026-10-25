---
stage: "42 — Executive Defence & Final Value Story"
artifact: "lessons-learned.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md", "docs/35-variance/value-leakage-analysis.md", "docs/26-tevv/", "docs/37-operating-model/", "docs/04-baseline-kpis/"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Lessons are drawn only from recorded events. Each states what happened, the evidence, and the change it implies. Some lessons are about the product; most are about running an evidence-first delivery with one human and several agents.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### LL-1 What worked (kept, with evidence)
| ID | Lesson | Evidence | Class |
|---|---|---|---|
| LL-01 | **Independent full regression before merge catches what build agents miss.** Four late defects (S21-DEV-02, S24-DEV-05, S28-DEV-08, S31-DEV-08) were found by the orchestrator, not the author. | OD-28, OD-32, OD-35, OD-36 | [Verified Fact] |
| LL-02 | **Declare thresholds before results and never edit them after.** TEVV committed thresholds first (a42ffe6) and disclosed one earlier baseline run. | `tevv-results.md` TR-0 | [Verified Fact] |
| LL-03 | **Sandbox-only execution with a checksum gate** (OD-03a) protected the baseline across the whole engagement: rc 0 before and after every run. | OD-03, OD-03a; Stage 16/26 | [Verified Fact] |
| LL-04 | **Safe defaults: everything consequential ships off.** No cutover, holder, rule set or schedule could activate by accident. | `implementation-prd.md` | [Verified Fact] |
| LL-05 | **Characterisation before refactor.** The harness (134/134) and mutation gate (15/15 vs the shipped suite's 1/15) made behaviour change visible. | Stage 15/16 | [Verified Fact] |
| LL-06 | **Refusing to compute.** Stage 36 refused ROI/NPV/payback rather than invent inputs; Stage 34 refused to call parity an improvement. | Stages 34-36 | [Verified Fact] |
| LL-07 | **Qualifying AI out.** The No-AI decision was argued from root causes, with re-qualification triggers instead of a closed door. | Stage 8 | [Verified Fact] |

### LL-2 What did not work (changes implied)
| ID | What happened | Evidence | Implication |
|---|---|---|---|
| LL-08 | **The baseline was synthetic and partly residue.** 97.98 % of feed rows reference cases not in the database; no closure/evidence/effort timestamps exist; A-04-01 was refuted a stage later. Many KPIs ended Unknown. | `baseline-kpi-sheet.md`; OD-07 | Qualify data realism before baselining; do not choose KPIs the data cannot support; capture time from day one |
| LL-09 | **Value was never quantified at framing.** All five drivers stayed unquantified; Stage 36 had nothing to compute. | `value-hypothesis.md`; `benefit-assumptions.md` | A value case with no volumes, rate or time capture is a hypothesis, and must be flagged as such in Stage 1-3 gates |
| LL-10 | **No stakeholders existed.** Every owner field says Dinesh; separation of duties is procedural; roles are VACANT. | OD-04; `raci.md` | Do not run a production-delivery spine without at least one accountable counterpart per decision class, or mark stages "capstone/synthetic" at the start |
| LL-11 | **Decisions pile up at one desk.** Dozens of D-xx items, 40 approvals, unsigned walkthroughs; OD-32 default-answer authority helped scope but could not approve risk, holders or cutover. | OD-32..OD-37 | Make decision batching a first-class deliverable; time-box "accepted open"; recruit a second reviewer |
| LL-12 | **Control built, not wired.** Resilience mechanisms, CI hardening workflow and observability exports exist but do not run in the serve path. Protection on paper. | OD-34, OD-35, OD-36; VL-04, VL-05 | Wiring should be a gate of the build stage, not a later decision |
| LL-13 | **"Test once" has a cost.** It pushed defects to the merge-time regression and long group walls (S26 145 s, E26 174 s of a 180 s cap; full pass 2,403 s). | `tevv-results.md`; `token-leakage-analysis.md` TL-03 | Budget for faster feedback; split heavy groups earlier |
| LL-14 | **Rework effort was not recorded.** We know defects happened; not what they cost. | VL-15, VL-17 | Record effort actuals from the start; otherwise cost is unknowable |
| LL-15 | **Documents drifted from code and from each other.** FR counts 43/9 vs 41/11; ADR-018 vs pyproject; `28-resilience` vs `28-reliability`; Stage 25 matrix stale after Stages 23/24; Stage 4 sheet not updated for A-04-01. | OD-10; `knowledge-drift-metrics.md`; RP-10 | Schedule v0.2 reissues as part of the merge of the stage that invalidates them |
| LL-16 | **Prompt/path mismatches** (stage prompt paths vs repo folders) cost time and had to be recorded as deviations. | S28-DEV-05; Stage 42 deviation | Fix prompt paths at the source |
| LL-17 | **Severity and thresholds were agent-assigned.** High/Medium ratings and SLO numbers are agent inference/assumptions, easy to mistake for approved. | OD-33, OD-36 | Show the assumption label in the artefact title block, not only the body |
| LL-18 | **Environment drift hit tests**: Node patch version (CT-13), Python 3.10 vs 3.13 goldens. | S24-DEV-04; OD-23 | Pin or containerise the reference toolchain before golden recording |

### LL-3 Lessons about presenting this to executives
1. Lead with the diagnosis and the decision discipline; do not lead with test counts.
2. Put "not released, value unknown" on the first slide, not the last.
3. Treat "sandbox parity" as a reason to proceed to a pilot, never as a result.
4. Keep the owner/approver slide: the project's blocking items are human decisions, not engineering.

## Evidence References
`.fde/orchestrator-decisions.md`; `docs/35-variance/value-leakage-analysis.md`; `docs/26-tevv/`; `docs/37-operating-model/raci.md`; `docs/39-drift/`; claims C-31, C-27, C-03, C-24.

## Assumptions
Lessons LL-11, LL-13 and LL-17 contain [Inference] about causes; owner to confirm: Dinesh.

## Unknowns
Effort and cost of the late-caught defects; whether a second reviewer would have changed outcomes.

## Unresolved Issues
Deferred lessons: handover (Stage 38) and retirement (Stage 41) were not produced and may yield further lessons.

## Residual Risks
Lessons not adopted (they are recommendations); `next-step-recommendations.md` carries the actionable ones.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
