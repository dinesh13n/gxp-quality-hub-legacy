---
stage: "22 — Agent, Tool, Harness, Loop & Graph Engineering"
artifact: "not-applicable.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-08 (and OD-19, OD-25, OD-26)", ".fde/stage-prompts/22_Agent-Tool-Harness-Loop-and-Graph-Engineering.md (Conditional stage clause; Required Artifacts note)", "docs/08-ai-qualification/minimum-agency-assessment.md (MA-1..MA-5)", "docs/08-ai-qualification/qualification-decision.md (T5 row; Stage 22 row; QD-3 RQ-4)", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/10-architecture/adrs/ADR-010-run-orchestration-scheduling.md", "docs/10-architecture/model-service-scorecard.md", "docs/17-implementation-prd/implementation-prd.md (OD-S12-10 / OPD-11 schedule OFF)", "docs/18-delivery/delivery-backlog.md (l.14, l.80)", "docs/18-delivery/evaluation-rubric.md", "docs/19-intelligence/not-applicable.md", "docs/15-modernization/test-execution-log.md (TST-CO-11/12, E05..E09EGRESS)", "docs/16-repo-validation/evidence/cloud-regression.log, obs-cloud.json", "docs/16-repo-validation/regression-results.md, security-scan-summary.md SS-01, architecture-conformance-report.md", "hub/runs/ (service.py, jobs.py, catalogue.py, flag.py, __init__.py)", "hub/gate/ (service.py, modes.py, actions.py)", "hub/review/service.py", "hub/guards/no_ai.py, hub/guards/egress.py, hub/obs/metrics.py, hub/ops/release.py (G5)", "tests/hub/test_tst_run_01_15_runs.py, test_tst_gate_01_22_disposition_gate.py, test_tst_co_11_no_ai_denylist.py, test_tst_co_12_egress_tripwire.py, test_inc05..09_egress_guard.py"]
supersedes: "none"
---
## Summary

**Stage 22 is NOT APPLICABLE.** The stage prompt's conditional clause applies: *"If Stage 8 rejected agentic AI, create only `not-applicable.md` with the justification and stop. Do not invent agent artifacts."* Stage 8 explicitly rejected agentic behaviour (`minimum-agency-assessment.md` MA-4/MA-5: minimum agency A0/A1, A4 multi-step planning with tool use rejected). Dinesh Naik approved the No-AI decision, which states "Stage 22 not triggered" (OD-08, 2026-10-18). There is no planner, tool gateway, agent state or memory, workflow graph, agent loop or model tool-calling to engineer. The 15 artifacts under "Required Artifacts" (`agent-architecture.md` … `agent-readiness-gate.md`) are therefore **not produced**.

**Outcome: NOT APPLICABLE (skipped, as Stage 18 planned).** The skip is fully evidenced. No blocking condition. Next stage: 23. Label: synthetic repository, unvalidated against any organisation.

## Findings

### NA-1 Justification

| # | Finding | Evidence | Label |
|---|---|---|---|
| 1 | No-AI was approved by the sole approver, and OD-08 says verbatim "Stage 22 not triggered". | `.fde/orchestrator-decisions.md` OD-08 ("Approved by Dinesh (2026-10-18)") | Verified Fact |
| 2 | Stage 8 found no requirement that needs a system to choose between alternatives or plan over several steps. The only candidate, T5 cross-store investigation, is blocked by a missing key (RC-7), and "planning cannot create a key". Agentic option O8 was evaluated and rejected (injection surface, non-deterministic trace conflicts with NFR-09/NFR-16). | `minimum-agency-assessment.md` MA-2, MA-4; `qualification-decision.md` T5 row ("Agentic rejected") and Stage 22 row ("Not triggered") | Verified Fact |
| 3 | MA-5 defines the consequence: when the recommendation is approved, Stage 22 is recorded as "not applicable: agency rejected at Stage 8". | `minimum-agency-assessment.md` MA-5 | Verified Fact |
| 4 | Downstream records agree: ADR-002 and the model-service scorecard say "no model calls, no agents". Stage 18 plans no Stage 22 work item ("Stage 22 is skipped (OD-08)") and leaves the form of record open as "OD log entry or a note in `docs/22-agentic-engineering/`". This file is that note. Stage 19 is already NOT APPLICABLE (OD-25/OD-26). | `ADR-002` Context; `model-service-scorecard.md` l.19; `docs/18-delivery/delivery-backlog.md` l.14, l.80; `docs/19-intelligence/not-applicable.md` | Verified Fact |
| 5 | The prompt depends on Stage 20. Stage 20 is in progress on branch `stage-20-application` and does not change the skip. OD-26 scopes Stage 20 to the deterministic application. Read-only check on 2026-10-21: `stage-20-application` HEAD = `main` = 41098c0 with a clean tree, so no new code exists yet. | `git rev-parse`, `git status` (read-only); OD-26 | Verified Fact (state at check) / Inference (no dependency) |
| 6 | The seven analysis dimensions (role design, tool schema strictness, permission scope, loop/termination control, token/time/tool budgets, state/memory hygiene, failure recovery) have no agent object to analyse. Where a deterministic analogue exists, it is covered in NA-2 and is owned by Stages 15/16/23/26, not by this stage. | Findings 1-5 | Inference |

### NA-2 Deterministic orchestration that covers multi-step work (read-only inspection of `main` 41098c0)

| Multi-step need | Deterministic component | Why it is not an agent loop | Label |
|---|---|---|---|
| Batch runs (intake, backfill, projection rebuild/verify, audit verify, metrics snapshot) | `hub/runs/catalogue.py`: a **closed** job catalogue of 9 jobs and 2 triggers (`manual`, `scheduled`). `hub/runs/jobs.py`: each job is `fn(ctx) -> result`. | No job selection at runtime, no text interpretation, no plan change. The job is named by the operator. | Verified Fact |
| Loop bound / termination | `hub/runs/jobs.py` `run_ordered`. The work plan (`items_after` per source) is fixed **before** the loop. Each iteration consumes `batch_size` items, and the cap is configuration or `--batch-size`, never a constant (BEH-RUN-05). `--until-empty` iterates only over the pre-computed finite plan. | Termination is structural: a finite list consumed monotonically. `limit_reached` and `backlog_remaining` are exact, and the remainder resumes from a checkpoint. | Verified Fact |
| Run service / state / recovery | `hub/runs/service.py` `RunService`. Insert-only `run_event` rows (RUN_STARTED → RUN_CHECKPOINT* → exactly one terminal event). A single-flight lock with heartbeat (BEH-RUN-06). Stale runs are closed as RUN_ABANDONED. Resume is idempotent through the backfill rule (BEH-RUN-07). Totals are reconciled (BEH-RUN-04). One hash-chained audit record per start/terminal event. Tripwires are exported at every run end (BEH-OBS-06). | State is an append-only run record with no memory or context accumulation. Recovery is checkpoint and idempotent replay, with no retry heuristics. | Verified Fact |
| Scheduler | **OFF.** `hub/runs/__init__.py`: "this package contains no scheduler, timer, daemon or loop". `--trigger scheduled` is refused with E-RUN-SCHEDULE-DISABLED unless the ZH-09 flag is on. ZH-09 is Zone H, and `zone_h.holders` ships empty. `schedule.enabled: true` in config is refused (DEV-64). | Held by OPD-11 / OD-S12-10, "Accepted open – schedule OFF" (`implementation-prd.md` l.79, l.148; ADR-010 option B). | Verified Fact |
| Privilege separation | `hub/runs/jobs.py` imports nothing from `hub.gate` and calls only `SERVICE_CALLS`. The AST test in `tests/hub/test_tst_run_01_15_runs.py` compares every call with ZONE_H_METHODS (AC-RUN-12). Run roles are `quality_lead`, `compliance` and `integration` (BEH-RUN-01). | This is the deterministic analogue of a "tool permission map": a closed call list enforced by a test. | Verified Fact |
| Gate / HITL flows | `hub/gate/service.py`: the closed Zone H action list ZH-01..ZH-10 is executable only by a **human** principal (service, scheduler, importer and integration identities are rejected) who has role dispositioner, is listed in `zone_h.holders` (ships empty) and holds a fresh step-up re-auth. Every attempt is audited. `hub/gate/modes.py`: disposition mode `none` by default, and "Config can not weaken the human gate". `hub/review/service.py`: the reviewer queue is read-only, has no import path to `hub.gate` (AC-GATE-11), and labels free text `untrusted`. Tests: `test_tst_gate_01_22_disposition_gate.py`. | Every consequential decision stays with a named human (HAR-12, STOP-07). No automated actor can reach Zone H. | Verified Fact |
| Planned human control extension | DW-17 is an approval-gated authority switch. It works only with a recorded human approval, ships off, and is built at Stage 23 (OD-26). | Human-control work, not agency. | Verified Fact (plan) |

### NA-3 Evidence that no agent loop or model tool-calling exists

| # | Evidence | Result | Source | Label |
|---|---|---|---|---|
| E-1 | Structural deny-list `hub/guards/no_ai.py` (ADR-002 B(1)). Its DENY_MODULES include the agent/orchestration frameworks `langchain*`, `langgraph`, `llama_index`, `semantic_kernel`, `autogen` and `crewai`. DENY_DISTRIBUTIONS include `openai_agents`. Prefix families include `openai`, `anthropic` and `langchain`. | TST-CO-11 a-d PASS. | `docs/15-modernization/test-execution-log.md` l.63; `tests/hub/test_tst_co_11_no_ai_denylist.py` | Verified Fact |
| E-2 | Egress guard `hub/guards/egress.py` (loopback only, counts `egress_attempts_total`). TST-CO-12 e re-runs the suite under the guard. | 0 attempts, `model_calls_total` 0. | `test-execution-log.md` l.64; `docs/15-modernization/evidence/inc03|inc04/hub-final-C_inner-egress-run.json` | Verified Fact |
| E-3 | E05EGRESS..E09EGRESS: each later increment's modules run under the guard and assert `egress_attempts == []` and both tripwires == 0. | All ok: "0 attempts, model_calls_total 0". | `test-execution-log.md` l.164 (E05), l.180/203 (E06), l.198 (E07), l.217/228 (E08), l.239 (E09); `tests/hub/test_inc05..09_egress_guard.py` | Verified Fact |
| E-4 | Stage 16 cloud regression at 2c63b07 (Python 3.13). | I45 88 ok (incl. E05EGRESS), E8 1 ok, E9 1 ok, 0 FAIL/ERROR. Observed tripwires `egress_attempts_total: 0`, `model_calls_total: 0`. | `docs/16-repo-validation/regression-results.md` l.30-36; `evidence/cloud-regression.log`; `evidence/obs-cloud.json` l.607-608 | Verified Fact |
| E-5 | `model_calls_total` has one incrementer, `record_model_call`, and nothing in the product calls it. Release gate G5 requires: "deny-list clean, no egress, model_calls_total = 0". | — | `hub/obs/metrics.py`; `hub/ops/release.py` l.16; `docs/19-intelligence/not-applicable.md` E-3 | Verified Fact |
| E-6 | Stage 16: ADR-002 conforms (manual gate). SS-01: "zero model calls (No-AI OD-08 holds)". | — | `architecture-conformance-report.md` l.14; `security-scan-summary.md` l.47 | Verified Fact |
| E-7 | Read-only `git grep -i -E "langgraph\|langchain\|crewai\|autogen\|semantic_kernel\|tool_call\|function_call\|openai\|anthropic\|agent"` on `main -- hub` (excluding `no_ai.py`) on 2026-10-21. | **0 matches**. The only working-tree hits are planted test strings in `tests/hub/test_tst_co_11_no_ai_denylist.py` l.49-50, which prove the deny-list fires. | this stage, read-only | Verified Fact |
| E-8 | All evidence above comes from sandbox and test runs. No production or runtime telemetry exists (OD-04). | — | OD-04 | Verified Fact (limitation) |

### NA-4 Triggers that would restart this stage

Stage 22 restarts **only** if all three of the following happen. First, Stage 8 is re-run and approves an AI element through RQ-1..RQ-3, with Stage 19 restarted for it. Second, **RQ-4** fires: a measured residual cross-store set exists that deterministic crosswalk queries cannot resolve, and this is shown only after the crosswalk exists (`qualification-decision.md` QD-3; `docs/19-intelligence/not-applicable.md` NA-4). Third, Dinesh records a new decision that supersedes OD-08 for agency (HAR-10/HAR-11; BR-AI-1, BR-AI-6). On restart, Stage 22 must start from the MA-4 limits: read-only tools, no write tools, a step cap per `provisional-loop-budget.md`, human review of every conclusion, and every model call routed through `record_model_call`, so that G5 becomes budgeted counting rather than being bypassed.

Deterministic scheduling **does not** restart this stage. Enabling the schedule (OPD-11 / ZH-09) is automation of a fixed procedure (MA-3), not agency.

### NA-5 What downstream stages inherit

| Stage | Inherits |
|---|---|
| 23 Human control | There is no agent control surface to govern. Human control covers the deterministic Zone H gate (ZH-01..ZH-10, human-only, holders empty), disposition mode `none`, the reviewer queue (read-only), the schedule flag (ZH-09, OFF) and DW-17 (approval-gated authority switch, ships off). |
| 24 Agent security | Nothing agent-specific to test. Tool misuse, privilege expansion and recursion threats apply only as the deterministic analogues in NA-2 (AC-RUN-12, AC-GATE-11). The deny-list's heuristic coverage of agent frameworks (A-22-02) is a Stage 24 review item. |
| 26 TEVV | No agent tests (misuse, recursion, recovery). TEVV covers deterministic behaviour, including the run-loop bound, single flight, resume and abandoned-run tests (`test_tst_run_01_15_runs.py`), the gate tests, the No-AI gates TST-CO-11/12 + E05..E09EGRESS, and release gate G5. |
| 31 Observability | No agent telemetry (steps, tool calls, tokens). `egress_attempts_total` and `model_calls_total` remain zero-tripwires, and run records and the missing-run detector cover orchestration. |
| 32 FinOps | Token, model-call and tool-call cost lines are asserted as 0, and zero model calls is tracked as a tripwire (OD-08). The 0C agent loop cost (6-step loop, MA-4) and the loop budget stay **dormant** and retired as active assumptions (`economics-baseline-reconciliation.md`). |
| 27 / CI | The No-AI gates still run manually (RTD-14 / S16 RG-05). Until CI wiring lands, G5 is a manual gate. |

## Evidence References

See front-matter `evidence_sources`. The repo was inspected read-only at `main` 41098c0 (branch `stage-20-application`, same commit, clean tree at time of check) through `git show` / `git grep` / `ls`. No code was run. No git state was changed. Nothing outside `docs/22-agentic-engineering/` was written.

## Assumptions

- A-22-01 [Assumption] The sandbox egress-guarded runs (NA-3 E-2..E-4) are representative of how the product will run, while it stays stdlib-only and loopback-only (A-10-03, A-19-01). Confirm: Engagement lead (Dinesh Naik), Stage 27.
- A-22-02 [Assumption] The heuristic deny-list covers the agent frameworks likely to be introduced (LangGraph, LangChain, AutoGen, CrewAI, Semantic Kernel, OpenAI Agents). New frameworks need a reviewed PR to `hub/guards/no_ai.py`. Confirm: Stage 24.
- A-22-03 [Assumption] Stage 20 adds no agent or model code, as scoped by OD-26. This is re-verified by the No-AI gates in the Stage 20 pre-merge regression. Owner: Orchestrator.

## Unknowns

- U-22-01 [Unknown] Whether a residual cross-store set (RQ-4) exists once the crosswalk runs on real data. This is resolved only through RQ-4 measurement after RQ-1..RQ-3.
- U-22-02 [Unknown] HAR-10 interpretation for the deterministic scheduler (A-08-09 / OPD-11). It does not affect this skip (MA-3), but it remains open for Dinesh.

## Unresolved Issues

- UI-22-01 The No-AI gates (including the agent-framework deny-list) run only manually, with no CI enforcement (RTD-14 / RG-05). Owner: Orchestrator. Resolving stage: 27. Non-blocking for the skip.
- UI-22-02 OPD-11 / OD-S12-10 (schedule) is accepted open, with the schedule OFF. Owner: Engagement lead (Dinesh Naik). Non-blocking.

## Residual Risks

- RR-22-01 Agency creep: the scheduled job or the reviewer queue could acquire decision logic over time (Stage 8 residual risk). Mitigations: the closed job catalogue, the AC-RUN-12/AC-GATE-11 import tests, and human-only Zone H.
- RR-22-02 Silent reintroduction: a renamed or transitive agent framework could slip past the heuristic deny-list. Mitigations: the egress guard (no outbound network), the `model_calls_total` / G5 tripwire, and Stage 32 monitoring. The risk stays elevated until CI enforces the gates (UI-22-01).
- RR-22-03 One person is both author and sole approver of the No-AI/no-agency conclusion, on synthetic data (Stage 8 CD-7).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial record: Stage 22 NOT APPLICABLE under the prompt's conditional clause (OD-08; Stage 8 MA-4/MA-5). No agent, tool, harness, graph or loop artifacts produced. |
