---
stage: "28 — Reliability & Resilience Engineering"
artifact: "ai-disabled-mode.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
**AI-disabled operation is not a mode the hub switches into; it is the only mode (OD-08, Accept No-AI).** The requirement "preserve core business continuity when AI is disabled" is met by construction and is tested in three ways: the results of the core flow are byte-identical with AI-style environment variables present or absent (STG28 A01), no code or configuration key refers to a model, provider or AI environment variable (A02), the dependency deny-list is clean and the tripwires `model_calls_total` and `egress_attempts_total` read 0 (A03), and the whole Stage 28 suite runs under the egress guard with zero egress attempts (E28 S90). There is no AI feature to disable, no AI fallback to maintain and no AI kill switch to test; adding one would be a regression against OD-08.

## Findings
### AI-1 Definition
| Item | Definition | Tag |
|---|---|---|
| AI-disabled mode | The product runs with no model client, no embedding, no prompt, no external inference endpoint and no AI-related configuration | [Verified Fact] |
| Core business continuity | intake, matching, rule evaluation (inactive candidate rule sets only), decisions, Zone H gate, reviewer queue, search (keyword FTS), reports, audit, backup / restore work exactly the same | [Verified Fact] (regression: 27 groups green at Stage 27; STG28 A01) |
| Tripwires | `model_calls_total` and `egress_attempts_total` must be 0; Stage 32 tracks them | [Verified Fact] |
| Re-qualification | AI-assisted document Q&A (T3) may be re-qualified only via RQ-1..RQ-3 and a new Dinesh decision | OD-08 |

### AI-2 Test mapping
| Test | Proves |
|---|---|
| STG28 A01 | same reports, queue snapshot and table digest with `OPENAI_API_KEY`, `AZURE_OPENAI_*`, `ANTHROPIC_API_KEY`, `HUB_AI_ENABLED`, `HUB_MODEL`, `LLM_PROVIDER` set (synthetic values) as with them unset |
| STG28 A02 | environment variables read by `hub/` are the operator ones only; no configuration key (any depth) contains an AI word |
| STG28 A03 | `hub.guards.no_ai.check` over `hub/`, `tests/hub` and the manifests finds nothing; tripwires 0 |
| E28 S90 | all Stage 28 tests under the egress guard: 0 attempts, `model_calls_total` 0, no skip |
| TST-CO-11, TST-CO-12 (regression) | deny-list and egress tripwire for the whole hub |
| STG26 `noai_walkthrough` | Stage 26 No-AI walkthrough (human steps TST-REV-03/04/08 stay unsigned) |

### AI-3 What "fallback model/provider" means here
Not applicable: nothing to fall back from. If AI is ever introduced (it needs a new Dinesh decision), this document must be re-issued with a provider fallback chain, per-provider timeouts and breakers (the Stage 28 primitives are reusable), a deterministic non-AI fallback path for every AI-assisted step, and a kill switch tested like Zone H (approval-gated, off by default).

### AI-4 Findings
| ID | Finding | Impact | Risk | Confidence |
|---|---|---|---|---|
| F-AI-01 | The AI-disabled proof is behavioural and static; it cannot prove the absence of AI in the host environment (OS, proxies) | none for the product | Low | High |
| F-AI-02 | AI coding assistants used to BUILD the system are dev tooling, not product AI (OD-08); their outage does not affect operation | none at run time | Low | High |

## Evidence References
OD-08, `docs/08-ai-qualification/qualification-decision.md`, `docs/19-intelligence/not-applicable.md`, `docs/22-agentic-engineering/not-applicable.md`, `hub/guards/no_ai.py`, `hub/obs/metrics.py`, `tests/hub/test_tst_hub_stg28_ai_capacity.py`, `test_tst_hub_stg28_egress_guard.py`.

## Assumptions
- A-28-AI-1 [Assumption] No AI will be introduced into the product before a new decision. Owner: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-09 None specific to this artifact.

## Unresolved Issues
- None blocking.

## Residual Risks
- RR-28-09 A future AI feature would need this artifact re-issued before release.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
