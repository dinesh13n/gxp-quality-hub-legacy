---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "ai-telemetry-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/08-ai-qualification/qualification-decision.md", "docs/19-intelligence/not-applicable.md", "docs/28-reliability/ai-disabled-mode.md", "docs/32-finops/production-token-dashboard-spec.md", "hub/obs/metrics.py", "hub/guards/no_ai.py", "hub/ops/release.py", "hub/obs/log.py", "hub/obs/collect.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
**AI telemetry for this product is the zero-model-call tripwire and nothing else.** The product is No-AI by Dinesh Naik's decision (OD-08): no model client, prompt, retrieval-augmented generation, embedding, token or tool call exists, so there is no latency, token, cost, quality or hallucination signal to collect and none is invented. What is observable, and now alertable, is that the count stays 0: `model_calls_total` and `egress_attempts_total` (exported at every run end), alert ALT-01 / ALT-02, and a reserved schema below that any future, Dinesh-approved AI element would have to implement before it ships.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AT-1 What is instrumented today [Verified Fact]
| Signal | How | Alert | Evidence |
|---|---|---|---|
| `model_calls_total` | `hub.obs.metrics.record_model_call` is the only sensor; nothing in the product calls it; any call fails release gate G5 | ALT-01 (SEV-B); **absent sensor also fires** | tests A02, A03; `tests/hub/test_tst_hub_stg28_egress_guard.py` pattern `tripwires == 0` |
| `egress_attempts_total` | incremented by the egress guard | ALT-02 (SEV-B) | same |
| deny-list findings | `hub/guards/no_ai.py` (imports of model SDKs refused) | none (test-time) | `docs/27-hardening/evidence/no-ai-check.json` |
| Retrieval | keyword / FTS only; `search_engine{engine}` gauge | none | OBS-4 |

### AT-2 Making the tripwire observable [Verified Fact: test A03]
`collect.samples(con)` includes the three tripwires; `report.evaluate` turns a non-zero value into a firing ALT-01 / ALT-02 and shows them in `tripwires`. The test pulses each counter, checks the alert, puts the counter back, and checks the report returns to clean. This answers RR-32-01 ("a tripwire that reads 0 because nothing increments it is weak evidence") in part: the **sensor path is tested end to end**, and an absent tripwire sample is itself a finding. It does not prove no future code path bypasses `record_model_call`; that remains the deny-list scan (TST-CO-11) plus code review.

### AT-3 Reserved schema (NOT implemented; applies only after a Dinesh-approved re-qualification, RQ-1..RQ-3)
An AI component must emit, via the existing Logger and catalogue only: `model_calls_total{model_id,purpose}`, `model_latency_ms` (histogram), `model_tokens_total{direction}`, `model_errors_total{error_code}`, `prompt_version` and `config_version` on every log line, `retrieval_hits{index}`, guardrail outcomes, and an evaluation score series. Content rules: **no raw prompt, completion or retrieved text in logs or metrics** - ids, hashes and lengths only; sampling of full prompts only under an approved control. Until then these names are not in the catalogue and the lint would reject them (unknown metric), which is the intended fail-closed behaviour.

### AT-4 Token dashboard
Stage 32 retired token panels (ER-1); this stage does not reinstate them.

## Evidence References
`docs/08-ai-qualification` (OD-08), `docs/19-intelligence/not-applicable.md`, `docs/32-finops/production-token-dashboard-spec.md` DS-1 P1/P2, `hub/obs/metrics.py`, tests A02/A03/D04.

## Assumptions
- A-31-12 No AI element will exist before a new Dinesh decision; the reserved schema is a placeholder, not a design.

## Unknowns
- U-31-08 Whether any AI-assisted document Q&A (T3) is ever re-qualified.

## Unresolved Issues
- None blocking. The sensor is never exercised by product code, by design.

## Residual Risks
- RR-31-08 A future caller that bypasses `record_model_call` leaves the tripwire at 0. Medium; controlled by the deny-list and release gate G5.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
