---
stage: "20 — Application & Services Engineering"
artifact: "deterministic-ai-boundary.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md OD-08", "docs/08-ai-qualification/qualification-decision.md", "docs/19-intelligence/not-applicable.md", "hub/guards/no_ai.py", "docs/20-application/evidence/no-ai-check.json", "tests/hub/test_tst_co_11_no_ai_denylist.py", "tests/hub/test_tst_co_12_egress_tripwire.py", "tests/hub/test_tst_hub_stg20_egress_guard.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08, approved by Dinesh 2026-10-18); Stage 19 is NOT APPLICABLE (OD-25). AI coding assistants used to build the system are dev tooling, not product AI.**

## Summary
The deterministic-AI boundary is enforced in code and unchanged by Stage 20: there is no model client, no prompt, no embedding and no network path beyond loopback. Every Stage 20 addition (observation, withdrawal, trace producer, Zone H rule) is deterministic rules / SQL / templates. Enforcement evidence was re-run.

## Findings
| Control | Evidence | Result | Tag |
|---|---|---|---|
| Dependency / import deny-list (`python -m hub no-ai-check`) | `evidence/no-ai-check.json` (sandbox, 3.10.12) | rc 0, findings [] | [Verified Fact] |
| TST-CO-11 deny-list tests | targeted run with TST_CO_11 / TST_CO_13 | 40/40 ok in that run | [Verified Fact] |
| Model-call tripwire (`model_calls_total` = 0) and no `record_model_call` site | TST-CO-12 c/d (group C1 green); golden-compare report `tripwires` | 0 / 0 | [Verified Fact] |
| Egress guard over the Stage 20 tests (E20EGRESS) | group E20 run: green, 0 egress attempts, 0 model calls, nothing skipped | pass | [Verified Fact] |
| Egress guard over the INC-02 core suite (TST-CO-12 e1/e2/e3) | groups C1, C2, C3 green | pass | [Verified Fact] |
| No `random` / wall clock in core dirs (TST-CO-13 b) | new golden module `observe.py` imports neither (uses the injected `hub.security.canonical.utc_now` only for scratch-store timestamps) | pass | [Verified Fact] |
| Rule explanations are template text, not generated (AC-REV-07) | producer stores rule-service results; text from `hub/review/templates.py` | pass (TST-REV, STG20 S14) | [Verified Fact] |
- [Verified Fact] No business rule was moved into a prompt (there are no prompts). Free text stays Untrusted (flag trail returns `{text, trust: untrusted}`).
- [Inference] The boundary is structural (deny-list + egress guard + tripwire) and therefore holds for future edits only while those tests run on every change - CI wiring is Stage 27 (RR-RG-1).

## Evidence References
As in the table; `application-test-summary.md`.

## Assumptions
- None new.

## Unknowns
- None new (re-qualification triggers RQ-1..RQ-3 unchanged).

## Unresolved Issues
- None for Stage 20.

## Residual Risks
- RR-AI-1 No CI gate yet; a later change could add a dependency unnoticed until a manual run (Medium until Stage 27).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
