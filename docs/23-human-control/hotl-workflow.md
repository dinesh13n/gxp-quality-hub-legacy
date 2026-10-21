---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "hotl-workflow.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/runs/", "hub/runs/detector.py", "hub/runs/schedule.py", "hub/core/errors.py E-HUB-KILLED", "hub/control/cli.py flip-to-shadow", "hub/obs/", "hub/security/audit.py", "docs/08-ai-qualification/minimum-agency-assessment.md MA-3", "tests/hub/test_tst_run_01_15_runs.py", "tests/hub/test_tst_hub_stg23_controls.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Human-on-the-loop (HOTL) applies where the system runs a fixed procedure without waiting for a person: the scheduled intake / reconcile run (A3-lite), the shadow comparison of rule output with human decisions, audit verification and the tripwires. In each the human supervises through records and can stop or revert it. **The schedule ships OFF and enabling it is ZH-09 (a Zone H act); no HOTL monitor role is filled.**

## Findings
### HOTL loops
| ID | Autonomous part | What the human watches | Intervention (who can stop it) | Evidence |
|---|---|---|---|---|
| HL-01 | Scheduled intake / reconcile run (fixed procedure, idempotent, append-only, run id) | run records, totals check (E-RUN-TOTALS-MISMATCH), missing-run detector and timeliness report (`hub/runs/detector.py`; with the flag OFF it reports "schedule disabled", never failures) | ZH-09 disable; `hub.kill` (E-HUB-KILLED, exit 3); stop the process | TST-RUN-01..15 |
| HL-02 | `capability_authority = shadow`: the rule result is recorded beside the human decision, never acted on | divergence report (`hub/r2/divergence.py`; null outputs not counted as divergence) | none needed (no effect); an `authoritative` setting is flipped back with `flip-to-shadow --reason` (L3, audited) | STG23 S13 |
| HL-03 | Audit chain append | `audit verify` / `anchor`; tamper detection E-SEC-AUDIT-TAMPER-DETECTED | operator stops the hub | TST-SEC |
| HL-04 | Egress and model-call tripwires | `egress_attempts_total`, `model_calls_total` (both must be 0) | release is blocked (E-CO-RELEASE-BLOCKED) | TST-CO-12, E-groups |
| HL-05 | Config start-up record | CONFIG_LOADED with the config hash; a `capability_authority` edit made in the file is audited at start | operator compares hashes | TST-SEC-21, STG23 S14 |

### Findings
- [Verified Fact] The only autonomous behaviour the root causes need is a scheduled fixed procedure (Stage 8 MA-3); nothing in the hub plans, chooses tools or interprets text.
- [Verified Fact] With the shipped defaults the schedule is OFF, every capability is `shadow` and the rule sets are inactive: no HOTL loop is live.
- [Verified Fact] The L3 rollback is rehearsed: `set-flag` to authoritative with a synthetic reference, then `flip-to-shadow` (audited with `rollback: L3`), then a second flip is a no-op (`evidence/l3-flip-log.json`).
- [Inference] HOTL is only as good as the person watching. No client role owns monitoring, on-call or incident response (ES-24; Stage 2 gaps), so alert delivery is Unknown: the hub records, it does not notify anyone.
- [Unknown] Alert thresholds and response times (no data; synthetic, unvalidated).

## Evidence References
Tests above; `evidence/l3-flip-log.json`, `authority-switch-audit.json`; Stage 2 `escalation-map.md`.

## Assumptions
- A-23-06 Operator-run CLI checks are an acceptable HOTL mechanism for a synthetic capstone.

## Unknowns
- U-23-05 Who monitors runs and the audit chain in a real deployment; U-23-06 notification channel.

## Unresolved Issues
- No notification path exists (out of scope; Stage 29 operations).

## Residual Risks
- An unattended schedule with no monitor could let a failed run go unnoticed; the detector reports it only when someone reads the report (RR-HC-2, Medium once the schedule is enabled).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
