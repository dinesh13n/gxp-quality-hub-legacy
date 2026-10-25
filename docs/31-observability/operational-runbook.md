---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "operational-runbook.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/29-incident-bcdr/containment-procedures.md", "docs/29-incident-bcdr/recovery-procedure.md", "docs/29-incident-bcdr/incident-severity-matrix.md", "operations/runbook.md", "hub/admin/cli.py", "hub/web/cli.py", "hub/runs/cli.py", "hub/obs/cli.py", "docs/28-reliability/failure-mode-analysis.md", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
How to look at the hub's telemetry and what to do when an alert rule lists something. Every command named here exists; every step that touches a store is run on a **sandbox copy**, never on the working-tree `data/` (OD-03a). There is no on-call: the operator is Dinesh Naik (RL-02 interim, OD-34). Procedures were exercised only on synthetic data and by the STG31 tests; no human has run them under pressure.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RB-00 Routine evaluation (start and end of a working session)
1. Export the latest samples to a file (from `obs_metric`, or `hub runs obs-snapshot` first, then read the rows) and keep the previous file.
2. `python -m hub.obs evaluate --samples NOW.json --previous BEFORE.json [--availability A.json --timeliness T.json]` -> exit 0 clean; 1 = something fires or lint finds; 2 = unreadable input.
3. Read `alerts.firing` first, then `alerts.no_data` (gaps are not "fine"), then `slo`. 4. `hub report health` for run records and the audit anchor.
5. Write what you saw in the run notes. The label 'synthetic, unvalidated' stays on every figure.

### RB-01 ALT-01 model call recorded (SEV-B)
1. Do not clear or reset the counter. 2. Stop any release in progress (gate G5 fails by design). 3. Find who called `record_model_call`: `grep -rn record_model_call hub/` and the deny-list scan (`python -m hub.admin scan`, TST-CO-11). 4. Contain per `containment-procedures.md`. 5. Dinesh decides; a model in the product contradicts OD-08 and needs a new qualification decision. 6. If the alert is `sensor_absent`: the evaluation was fed samples without tripwires - re-export including `collect.samples`; if the sample is truly missing from the store export, treat as a telemetry defect (RB-09).

### RB-02 ALT-02 egress attempt recorded (SEV-B)
1. Identify the destination and the module from the egress guard's refusal record (stderr / test report). 2. Confirm the host policy: the hub is loopback-only (OD-34 D-27-09). 3. Contain; no outbound allow-list is added without Dinesh. 4. If it came from a test, fix the test; if from product code, SEV-B incident.

### RB-03 ALT-03 Zone H act accepted for a non-human actor (SEV-A)
1. Stop: no further disposition work. 2. On a **copy** of the store run `python -m hub.admin verify-audit` (known defect F-29-01: it can raise a KeyError on some stores; if it does, record that and compare `audit_log` rows for `ZONE_H_ATTEMPT` with `outcome='success'` and `actor_kind<>'human'` by SQL). 3. SEV-A per the severity matrix (a regulated act was automated); Dinesh decides on restore (`dr-plan.md`). 4. `zone_h.holders` is empty in the shipped config, so this should be impossible: a non-zero value means config, code or data differs from what was shipped - hash the config and compare.

### RB-04 ALT-04 / ALT-05 integrity: audit chain or projection (SEV-A / SEV-B)
Both metrics are not exported yet, so these alerts report no_data. Manual equivalent: `verify-audit` on a sandbox copy (RB-03 note on F-29-01) and the projection verify of the decision service. Confirmed break -> `recovery-procedure.md` RV-2 with a backup that predates it.

### RB-05 ALT-06 server errors (SEV-C)
1. In the samples find the `op_id` with status 5xx. 2. Collect the stderr log lines; `python -m hub.obs traces --log FILE` lists traces with outcome `error` and their `error_code`. 3. `E-STORE-*` or a 503 means a store fault: check disk, run `PRAGMA integrity_check` on a copy, see FM rows in `failure-mode-analysis.md`. 4. `E-HUB-INTERNAL` means an unexpected exception: reproduce on a sandbox copy before touching code.

### RB-06 ALT-07 / ALT-08 failed logins and rate limiting (SEV-C)
1. `python -m hub.admin user list` shows principals and roles; no credential material is shown. 2. A lockout is working as designed (`auth_failures_total{reason=locked}`); an unknown caller on loopback means a local process, not the network. 3. Rate-limited (`rate_limited`, 429 after 100 refusals in 60 s, A-27-04): find the caller; adjust only with Dinesh's decision. 4. Rotate a service token with `token revoke` then `token issue` if one may be exposed.

### RB-07 ALT-09 scheduled run missed (SEV-C)
The scheduler ships OFF (HAR-10), so this fires only if the schedule was enabled by a recorded decision. Run the manual idempotent catch-up (`python -m hub.runs run JOB --principal ... --trigger manual`), then `hub report health`; record why it was missed. Late deliveries need a manual catch-up (OD-28).

### RB-08 ALT-10 / ALT-11 breaker open, retry budget refused (SEV-C)
Applies only once `GuardedGateway` is wired (D-28-01). Meanwhile the shipped `gateway-pull` is bounded but unguarded. When wired: check the source (it is the dependency that failed), do not restart in a loop, wait for the cooldown probe (60 s default), and read `resilience_calls_total` vs `resilience_attempts_total` to see how much the budget prevented.

### RB-09 ALT-12 telemetry privacy or schema finding (SEV-B)
1. `python -m hub.obs evaluate` prints the lint findings as index + kind only. 2. Find the sample at that index in your own file; do not paste it anywhere. 3. Kinds: `prohibited_content` = treat as a possible leak (IS-04: contain, rotate any credential that could be involved, SEV-A if real data); `unknown_label` / `bad_label_value` = a producer started exporting free text or a new label: stop that producer; `unknown_metric` / `bad_kind` = catalogue drift (update `hub/obs/catalog.py` through a normal change); `cardinality` = runaway labels. 4. The lint never echoes the text, so the report can be shared; the samples file cannot until checked.

### RB-10 ALT-13 error budget red or exhausted (SEV-C)
Follow `error-budget-policy.md` EB-3: re-run, identify the SLO and its SLI source, decide change posture (EB-2), write the paragraph, Dinesh records any waiver.

### RB-11 Reading a trace
`python -m hub.obs traces --log FILE` -> per correlation id: spans, worst outcome, error codes, events. Join to the audit record by the same correlation id (`audit_log.correlation_id`). The outbound gateway call carries no correlation id (D-31-07): join pulls by `run_id` and time.

### RB-12 What this runbook cannot do
No paging, no remote access, no automatic remediation, no host metrics. Anything beyond the loopback, synthetic-data engagement scope needs the Stage 29 plans and Dinesh.

## Evidence References
`hub/obs/cli.py` (commands and exit codes), `hub/admin/cli.py` (verify-audit, scan, user list, backup), `hub/web/cli.py` (token issue / revoke), `docs/29-incident-bcdr/`, `docs/28-reliability/failure-mode-analysis.md`.

## Assumptions
- A-31-15 The operator reads the evaluation output; nothing alerts them. Confirm: Dinesh.

## Unknowns
- U-31-13 Whether `verify-audit` still fails on stores of other shapes (F-29-01 open).

## Unresolved Issues
- RB-03 / RB-04 depend on the F-29-01 fix; RB-08 on wiring.

## Residual Risks
- RR-31-15 Procedures not exercised by a human under pressure; the Stage 29 tabletop had no participants. Medium.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
