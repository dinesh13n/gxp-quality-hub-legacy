---
stage: "39 — Drift + Continuous Improvement"
artifact: "agent-drift-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/qualification-decision.md", "docs/22-agentic-engineering/", "docs/37-operating-model/agent-tool-ownership.md", "docs/37-operating-model/change-governance.md", "docs/00-preflight/operating-contract/change-control-rules.md", "tests/hub/non_add_edits.json", "tests/hub/test_tst_co_05*.py", "docs/31-observability/agent-telemetry-spec.md", ".fde/orchestrator-decisions.md (OD-01, OD-08, OD-13, OD-23, OD-27, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
**Product agents: NOT APPLICABLE.** The product runs no agents, tools or model loops (OD-08; Stage 22 not applicable; Stage 31 `agent-telemetry-spec.md` specifies none to collect). What can drift is how AI coding assistants and engagement agents change the repository. Those are development tooling (OD-08) but they are the most plausible source of an "untracked change" in this engagement, so six process monitors (AM-01..AM-06) are defined on evidence that already exists (branch-per-stage, PR plus squash, non-add edit list, frozen-file rule, checksum gates).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AD-1 Process monitors
| ID | Metric | How measured | Candidate threshold (Assumption) | Tier | State |
|---|---|---|---|---|---|
| AM-01 | Commits on `main` not from a merged PR | `git log --first-parent main` versus PR numbers in subjects (history shows `(#NN)` squash subjects, plus orchestrator log commits such as `OD-36: ...`) | a code or doc change on main with neither a PR number nor an orchestrator-log commit | INVESTIGATE | [Verified Fact] convention visible in `git log` (e.g. `stage-36: ... (#24)`); [Unknown] no branch protection or server-side enforcement is evidenced (remote settings not evidenced, OD-05) |
| AM-02 | Non-add edits to existing files | `tests/hub/non_add_edits.json` and test TST-CO-05 c: only edits listed with a work item pass; each later build stage resets the list (OD-27 DEV-05) | any non-add edit without a list entry | CHANGE blocked (test fails) | [Verified Fact] |
| AM-03 | Docs-only stages touching code | `git diff --stat main...stage-NN-*` limited to the stage's docs path | any path outside the stage's allowed path | INVESTIGATE | [Inference] derived from stage contracts (this stage: only `docs/39-drift/`) |
| AM-04 | Frozen-file edits | Stage 12 frozen files and Stage 4 KPI sheet are changed only by addendum (OD-07, OD-10) | an in-place edit of a frozen file | CHANGE (C0 errata process) | [Verified Fact] rule; [Unknown] no automated check |
| AM-05 | Test-before-merge | orchestrator's full regression (`tests/hub/run_hub_groups.py --all`, executed = expected) before squash-merge (OD-23); history shows regressions caught pre-merge at Stages 21, 24, 28, 31 | a merge without a recorded regression result | INVESTIGATE | [Verified Fact] practice and four catches; [Unknown] only recorded in decision log text, not in a machine-readable merge gate |
| AM-06 | Agent self-approval | any artifact that says "approved", "accepted" or "signed" for a human decision without an AskUserQuestion answer logged as OD-nn | any occurrence | CHANGE (revert wording; HAR-11, TP-14) | [Verified Fact] rule; scan by grep is feasible (IB-10) |

### AD-2 If an agent is ever introduced (conditional design)
Not active. If C7 (AI introduction) is ever approved, the agent drift set to add is: tool-allow-list hash, prompt/system-instruction hash with a version id, model id and parameters per call, tool-call trace volume per task, refusal and escalation rate, and cost per task, each tied to Stage 31's `agent-telemetry-spec.md` and Stage 32's token dashboard. These are listed so the requirement is not forgotten; **no value, baseline or threshold is proposed**, because none can be anchored.

## Evidence References
See header; `git log` of `main` at ef72e4e.

## Assumptions
- A-39-11 Monitoring development-agent behaviour through repository facts (diff, PR, tests) is in scope for "no untracked changes". Confirm: Dinesh.

## Unknowns
- U-39-09 Whether the remote repository (dinesh13n/gxp-quality-hub-legacy, private; push by orchestrator, OD-05) enforces branch protection. Resolve: Dinesh checks repository settings.

## Unresolved Issues
- HAR-07: CI file `ci/hub-hardening.yml` is not installed under `.github`; without CI, AM-02/AM-05 depend on the orchestrator running them.

## Residual Risks
- RR-39-09 The orchestrator is one process and Dinesh is the only human; process drift detection has the same single point of failure as approval (DQ-17 accepted-risk question still open). Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
