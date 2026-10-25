---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "logging-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/log.py", "hub/web/app.py", "hub/runs/cli.py", "hub/r2/web.py", "docs/12-specs/security-spec.md", "tests/hub/test_tst_obs_01_09_observability.py", "tests/hub/test_tst_hub_stg31_trace_cli.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
The logging contract of observability-spec OBS-2 is implemented in `hub.obs.log` and is privacy safe by construction. Coverage is narrower than declared: of 21 declared event names only `http_request` (every web request and the `OP-RUN-01` step), `fts_engine_selected` and `startup_selfcheck` are emitted (F-31-01). Everything else that matters is in the audit log. Log output has no file, rotation or retention (F-31-05).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### LS-1 Contract [Verified Fact: hub/obs/log.py]
Fields (exactly these 14, nothing else can be written): `ts level event correlation_id run_id actor actor_kind op_id outcome error_code duration_ms object_ref code_version config_version`. Ids must match `^[A-Za-z0-9._:@#-]{1,80}$` or are written as `redacted`; `error_code` must be `E-*`; `outcome` is success / denied / error; `actor_kind` is human / service / rule / system; levels DEBUG / INFO / WARN / ERROR. Durations use the injected clock (no `time` import in the core, TST-CO-13 b).

### LS-2 Privacy [Verified Fact: tests TST-OBS-04, STG31 D04, T01]
- Prohibited by construction: passwords, tokens, session ids, credential hashes, raw intake bodies, Untrusted free text, SQL. No field can carry them.
- Belt and braces: `hub.obs.log.prohibited_findings` scans produced lines (credential assignment, 64-hex digests, credential-hash field names, markup / SQL injection); Stage 31 re-uses it in the metric lint and in trace reconstruction, which **drops** (counts, never reproduces) a line that fails.
- `actor` is a principal id (pseudonymous); whether it is personal data is Unknown (field classes are a pre-real-data decision, OD-32 DQ-S24).
- Raw PII and secrets are never logged: **this holds for what the code can write; it cannot be proven for a future caller that passes an id-shaped string containing a secret** [Inference]. The id pattern admits letters, digits and `._:@#-`, so an e-mail address would pass as an `actor` or `object_ref` value. Mitigation in this stage: the hub passes principal ids and `job:<name>` refs only (code review of the four emit sites); a stricter pattern is D-31-09.

### LS-3 Events: declared vs emitted [Verified Fact: grep of `.emit(` / `.step(` in hub/]
| Event | Emitted today by |
|---|---|
| `http_request` | `hub/web/app.py` (every request: level by status, outcome, error code, duration, actor); `hub/runs/cli.py` `log.step("OP-RUN-01")` |
| `fts_engine_selected` | `hub/web/app.py`, `hub/r2/web.py` (start) |
| `startup_selfcheck` | `hub/web/app.py` (start), `hub runs selfcheck` |
| `auth_login auth_denied zone_h_attempt decision_appended policy_changed intake_received intake_outcome run_started run_finished run_failed run_abandoned run_refused projection_verify audit_verify golden_compare config_loaded db_busy metric_computed` | **never emitted**; the same facts are audit records (`audit_log`) or run events (`run_event`) |

### LS-4 Correlation [Verified Fact]
A valid incoming `X-Correlation-Id` is echoed, else a fresh id; the same id is on the log line, the audit record and the error envelope (AC-OBS-01). The outbound gateway GET carries **no** correlation id (`hub/adapters/gateway_client.py`), so a pull cannot be joined to source-side logs (F-31-07, D-31-07).

### LS-5 Destination, rotation, retention
`hub web serve` writes lines to stderr (`hub/web/cli.py:62`); the CLI writes them to stderr as well (stdout carries the result, DEV-70). No file sink, rotation or retention exists. BEH-OBS-07 says hold-all until a retention policy exists (OD-S12-09, OD-30): so any file sink must never delete. Proposed (D-31-05): redirect stderr to an append-only file beside the data directory by the launcher; rotation by size only if rotated files are kept.

### LS-6 Levels
INFO for status < 400, WARN for 4xx, ERROR for 5xx (`hub/web/app.py:197`). DEBUG is declared and unused.

### LS-7 Reading logs
`python -m hub.obs traces --log FILE` rebuilds traces by correlation id; `python -m hub.obs evaluate` does not read logs. Log-derived metrics do not exist; metrics come from `obs_metric` (MS-1).

## Evidence References
Stage 12 observability-spec OBS-2/OBS-3; `hub/obs/log.py`; emit sites listed in LS-3; tests `test_tst_obs_01_09_observability.py` (log shape, scan), `test_tst_hub_stg31_trace_cli.py` T01/T02 (a real WebApp request yields one correlated line).

## Assumptions
- A-31-09 Principal ids and object refs are the only identifier values the hub logs (reviewed at the four emit sites; not machine-enforced beyond the pattern).

## Unknowns
- U-31-04 Whether principal ids are personal data under the regime that will apply (field classes pending).
- U-31-03 Stderr destination under the launcher.

## Unresolved Issues
- 18 declared events are never emitted: decide to emit or retire them (D-31-09).
- No file sink, rotation or retention (D-31-05).
- No correlation id on the outbound gateway GET (D-31-07).

## Residual Risks
- RR-31-03 An id-shaped string can still carry an e-mail address. Low (hub passes principal ids only), but untested for future callers.
- RR-31-04 Logs on stderr are lost when the launcher does not capture them. Medium.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
