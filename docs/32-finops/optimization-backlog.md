---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "optimization-backlog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/{preliminary-finops-baseline,preliminary-tco,cost-scenarios,volume-assumptions}.md", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/{finops-ownership,escalation-model,raci,decision-rights}.md", "docs/33-vendor-risk/{vendor-inventory,vendor-risk-acceptance,exit-plan}.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "docs/26-tevv/release-thresholds.md RT-01..RT-15", "docs/27-hardening/production-readiness-checklist.md PRC-R", "tests/hub/non_add_edits.json", "tests/hub/regression_groups.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
A backlog of cost and effort items, ordered by what the evidence supports. **Every item is PROPOSED; none is started, approved or accepted.** Items that would touch production behaviour, metric definitions or controls go through the controlled change process with human approval (operating mode). **No item may lower test coverage or weaken a Stage 26 threshold (RT-01..RT-15) or edit a test to pass (TST-CO-05 c).** Token optimisation items do not exist because there are no tokens; the first five items are measurement items, because the largest gap is missing data, not waste.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Item | Type | Evidence it rests on | Expected effect | Quality impact | Owner role | Trigger / due | Status |
|---|---|---|---|---|---|---|---|---|
| OB-01 | Keep the zero-model-call tripwire layers and add the proposals in `cost-guardrails.md` CG-2 | Control | MU-F1..F5 | Keeps token spend at 0 | None; raises assurance | RL-02, RL-05 (VACANT; Dinesh interim) | Before any hosting or real data; no date set | PROPOSED |
| OB-02 | Record wall time, number of full passes and price of each cloud regression run | Measurement | TL-03, TL-05; U-32-19 | Turns an Unknown into a cost line | None | RL-12 (Dinesh interim) | Each full regression; no date set | PROPOSED |
| OB-03 | Record plan, charge and billing owner for code host, AI assistant, cloud workspace | Measurement | FC-03..FC-05; U-33-01 | Fills the TCO toolchain lines | None | RL-12 (Dinesh) | When Dinesh supplies them | PROPOSED, input needed |
| OB-04 | Record build and review effort in person-days per stage from now on | Measurement | BA-F3 | Allows comparison with 0C effort ranges | None | RL-12 / RL-01 (Dinesh) | From the next stage | PROPOSED |
| OB-05 | Measure reviewer minutes per rule-flagged item in the walkthroughs TST-REV-03/04/08 (unsigned) and later real use | Measurement | U-24; walkthroughs UNSIGNED (OD-33) | Gives the human-cost term | None | RL-03 (VACANT), RL-11 | When a human walkthrough happens | PROPOSED |
| OB-06 | Define the business outcome unit | Decision | COUT-F1 | Enables cost per outcome | None | RL-03 (VACANT; Dinesh interim) | Before Stage 36 | PROPOSED, decision needed |
| OB-07 | Obtain a hosting price estimate for the chosen topology (loopback-only today) | Measurement | FC-02; ADR-015 | Fills infra TCO line | None | RL-09 with RL-02 (VACANT) | At the hosting decision | BLOCKED on input |
| OB-08 | Reduce duplicate regression passes: keep "test once" (OD-23); log how many full passes each stage needed | Efficiency | TL-05 | Fewer wall-clock minutes | None if the full pass still runs once before merge | Orchestrator (agent) / RL-12 | Ongoing | In effect (OD-23); counting PROPOSED |
| OB-09 | Label the AI-option cost files in `docs/00-preflight/ai-economics/` as "AI option, not the chosen product" via a new version | Documentation | FF-03, TL-02 | Removes the risk of quoting USD 533 / 719 | None | RL-12 / RL-09 | Next re-baseline (Stage 34) | PROPOSED; not done here because the files are preserved baselines |
| OB-10 | Evaluate sandbox reuse across groups to cut the per-group rebuild | Efficiency | TL-04 | Less wall time | Must keep OD-03a isolation and checksum gating; any weakening is rejected | RL-12 | Only if wall time becomes a constraint | PROPOSED, low priority |
| OB-11 | Estimate storage growth under hold-all retention once a retention rule exists | Measurement | FC-08; OD-30 | Fills storage line | None | RL-09 with RL-05 | After retention policy | PROPOSED |
| OB-12 | Reconcile `finops-ownership.md` with this stage's TCO structure | Documentation | finops-ownership "Stage 32 reconciliation" | Consistent cost objects | None | RL-12 | Next Stage 37 re-issue | PROPOSED (see `finops-model.md` FM-5) |

### Excluded on purpose
| Candidate | Why excluded |
|---|---|
| Prompt compression, model routing, cache tuning, batch/async APIs | No model exists (ER-1); would invent a token metric |
| Removing slow test groups or skipping E-groups | Breaches RT thresholds and the zero-model-call evidence |
| Cheaper-model swap | Same as above; also needs an RQ re-qualification and a Dinesh decision (OD-08) |

## Evidence References
PRC-R; `docs/26-tevv/release-thresholds.md`; OD-21, OD-23, OD-33.

## Assumptions
- A-32-14 Priorities follow "measure first" because the baseline and actual cost data are missing (default-answer authority, OD-32; scope choice only).
- A-32-15 Owner roles are the roles in `raci.md`; holders other than Dinesh are VACANT.

## Unknowns
- U-32-21 Due dates: none exist; the triggers above are conditions, not dates.

## Unresolved Issues
- No budget, deadline or success criteria exist (DR-31, OQ-07), so priority by value cannot be set.

## Residual Risks
- RR-32-13 The backlog is read as approved work. It is not. Low.
- RR-32-14 Efficiency items erode evidence quality if the exclusions are ignored. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
