---
stage: "39 — Drift + Continuous Improvement"
artifact: "evaluation-cadence.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/39-drift/drift-framework.md", "docs/39-drift/change-trigger-thresholds.md", "docs/31-observability/operational-runbook.md", "docs/31-observability/error-budget-policy.md", "docs/26-tevv/tevv-plan.md", "docs/28-reliability/capacity-plan.md", "tests/hub/run_hub_groups.py", ".fde/orchestrator-decisions.md (OD-03a, OD-16, OD-19, OD-21, OD-23, OD-28, OD-34)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
Five cadences, tied to events more than to the calendar, because the hub has no scheduler (scheduler stays OFF, OD-19/OD-28), no alert delivery and exactly one human. **Every evaluation is a manual run by Dinesh Naik (interim) or by an agent he starts**, on a sandbox copy (OD-03a); nothing runs by itself. Calendar frequencies are CANDIDATES. Run-time figures are from recorded Stage 26/31 evidence on the reference laptop and cloud workspace and are not re-measured here.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EC-1 Cadence table
| Cadence | When (candidate) | Detectors | Mode / where | Evidence for effort |
|---|---|---|---|---|
| E0 Per change | every PR / stage merge (already practised, OD-13, OD-23) | full hub regression (`tests/hub/run_hub_groups.py --all`, executed = expected), `no-ai-check`, data checksum rc before and after, TST-CO-05 (non-add edits, legacy bytes), doc-vs-code tests; characterization harness on the reference laptop | stage branch; orchestrator runs the full regression once before merge in the cloud workspace; harness and checksums on the laptop (OD-23) | [Verified Fact] Stage 31 group wall times from 58 s to 127 s per group; group C about 105-145 s of the 180 s device cap (OD-19..OD-21) |
| E1 Periodic hygiene | candidate: first working day of each month while the engagement is active; skipped when nothing changed and no trigger is open (Assumption) | pins (TRG-02), backup checksum (TRG-03), toolchain versions (TRG-05, `selfcheck`), `hub.obs evaluate` on the latest samples if any exist, knowledge metrics KM-01..KM-08, open-decision ageing, search status if search is enabled | sandbox copy; read-only | [Inference] under an hour of operator time if the checklist in `continuous-evaluation-plan.md` is followed; not measured |
| E2 Dated / event-driven | on the date or event itself: Python 3.10 end of life (TRG-04), Node/Java/Python/SQLite upgrade, base-image rebuild, a new stage's merge, a dependency proposal | whichever detector the trigger names | sandbox | dates from `change-trigger-thresholds.md` |
| E3 Pre-gate | before any pilot, cutover step, non-loopback bind, real data, or activation of a rule set or flag | all of E0 plus E1, plus Stage 26 release gate re-computed, plus TRG-13 re-baseline | sandbox, then Dinesh decision | cutover cannot start today (RB-4) |
| E4 Review | candidate: quarterly, and at engagement close-out (Stage 40/FINAL) | the evaluation log as a whole: false alarms, missed drifts, thresholds to recalibrate, backlog health | document | no history yet: first review has nothing to review (Unknown) |

### EC-2 Rules
1. Evaluation results are appended as new dated files; earlier results are never overwritten (Global Execution Contract; `continuous-evaluation-plan.md` CEP-3).
2. A skipped evaluation is recorded as skipped with the reason; silence is not "green".
3. A detector that could not run (for example `verify-audit` raising KeyError, F-29-01, routed to Stage 30; or an alert in `no_data`) is reported as NOT-RUN, not as pass. Stage 31 already reports `no_data` separately for the same reason.
4. Evaluations never run against the working-tree `data/`; they use full sandbox copies outside the repo (OD-03a) and verify the backup checksum before and after.
5. The cadence does not create a service level. Missing a candidate monthly run is not a breach of anything; it is a recorded gap.

### EC-3 Why not more frequent or automated [Inference]
With no traffic and no scheduler, a daily or continuous cadence would produce identical results. The detectors are cheap enough to automate later (`hub.obs evaluate` is offline and stateless), but turning on a scheduler is itself a C3 change that is open (OPD-11/HAR-10) and not taken here.

## Evidence References
See header.

## Assumptions
- A-39-15 Monthly hygiene and quarterly review are placeholders. Confirm: Engagement lead (Dinesh Naik); revisit at TRG-13.
- A-39-16 "Operator" is Dinesh or an agent he starts, until RL roles are filled (OD-34).

## Unknowns
- U-39-11 Who runs E1 after Stage 38 (OD-34: who runs orchestrator duties).

## Unresolved Issues
- No place records evaluation results yet (CEP-3 proposes one; creating it is a future run, not this docs-only stage).

## Residual Risks
- RR-39-11 A monthly manual run depends on a person remembering; there is no reminder. Medium. (A scheduled reminder could be created outside this repository by Dinesh; not done here.)

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
