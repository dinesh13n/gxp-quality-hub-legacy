---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cost-guardrails.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/{preliminary-finops-baseline,preliminary-tco,cost-scenarios,volume-assumptions}.md", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/{finops-ownership,escalation-model,raci,decision-rights}.md", "docs/33-vendor-risk/{vendor-inventory,vendor-risk-acceptance,exit-plan}.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "hub/guards/no_ai.py", "hub/guards/egress.py (referenced by tests)", "hub/obs/metrics.py", "hub/ops/release.py G5", "tests/hub/test_tst_co_11_no_ai_denylist.py", "tests/hub/test_tst_co_12_egress_tripwire.py", "tests/hub/test_tst_hub_stg27_egress_guard.py", "docs/27-hardening/evidence/no-ai-check.json", "docs/26-tevv/release-thresholds.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
The guardrails that keep cost at its designed level and that stop optimisation from breaching quality. **Centrepiece: a zero-model-call tripwire design**, built from controls that already exist in code and tests (No-AI deny-list, egress guard, counters, release gate G5), with an honest statement of what each layer can and cannot prove. Proposals are marked PROPOSED and need human approval; none is installed. Risk acceptance is not given here.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CG-1 The tripwire stack (what exists)
| Layer | Control | Evidence | Catches | Does not catch |
|---|---|---|---|---|
| L1 Static deny-list | `hub/guards/no_ai.py`: R1 AI/ML/LLM imports (also `importlib` / `__import__` string literals), R2 HTTP/RPC client imports outside `adapters/`, R3 deny-listed distributions in `pyproject.toml` / `requirements*.txt`; exit 9, `E-CO-DENYLIST-IMPORT` | TST-CO-11; `no-ai-check.json` `findings: []` over hub, tests/hub, pyproject.toml | Named packages and clients added to the project | A package not on the list; vendored code; a call through a shell subprocess or a data URL; code under `adapters/` (R2 exempt). The list is heuristic (A-12-F10-2) |
| L2 Runtime egress guard | socket connect patched to record non-loopback attempts; suites re-run under it | TST-CO-12 (C1..C3), E8, E9, E20, E21, E23, E24, E26, E27 | Any non-loopback connection during those suites | Production traffic (guard runs in tests only); code paths the suites do not exercise |
| L3 Counters | `model_calls_total`, `egress_attempts_total` exported at end of every CLI run; must equal 0; `check_tripwires()` raises | `hub/obs/metrics.py` | A model call that goes through `record_model_call()` or the egress guard | A call that bypasses both: the model counter has no independent sensor, nothing increments it by design |
| L4 Release gate | G5 "deny-list clean, no egress, model_calls_total = 0" (FR-CO-04) | `hub/ops/release.py` | Release with L1-L3 failing | Anything L1-L3 miss |
| L5 Escalation | non-zero count is SEV-B; L1 blocks release; L3 (Dinesh) decides; agent cannot waive | `escalation-model.md` ER-04 | Process failure after detection | n/a |

### CG-2 What proves no model call happens
[Inference] No single layer proves it. Together they give **evidence of absence in the tested paths**: no AI package or client is declared (L1), the test suites open no non-loopback socket (L2), the counters read 0 (L3), and the release gate reruns this (L4). Weakest point: L3 reads 0 largely because nothing increments it. **Proposals (PROPOSED, need human approval and a change under C6):**
| ID | Proposal | Closes |
|---|---|---|
| CG-P1 | Deploy-time network policy: deny all non-loopback egress on whatever host runs the hub, and test it | L2 gap (production) |
| CG-P2 | Run L1 (`hub.guards.no_ai`) in CI on every PR; the CI file `ci/hub-hardening.yml` exists but is not installed (HAR-07 approval needed, D-27-03) | L1 only runs on demand |
| CG-P3 | Pin and review the allow-list under `adapters/` in the deny-list check, so R2's exemption is explicit | R2 exemption |
| CG-P4 | Alert on P1/P2 > 0 per `production-token-dashboard-spec.md` DS-2 | detection latency |
| CG-P5 | Periodic review of the deny-list names against current AI client libraries (a reviewed PR, as the module states) | list rot |

### CG-3 Cost guardrails (role-based; no amounts)
| ID | Guardrail | Owner role | State |
|---|---|---|---|
| CG-1x | Any new paid dependency or service is a C6 change needing RL-01 plus RL-05; no vendor without an ADR | RL-01, RL-05 | In `finops-ownership.md` FO-2; PROPOSED control |
| CG-2x | No budget cap or alert threshold in currency is set, because no budget exists (DR-31); when one is set, record owner, currency and period | RL-09 (VACANT) | Unknown; input from Dinesh |
| CG-3x | Cost lines FC-02..FC-10 reviewed per release once any is non-zero | RL-09 | PROPOSED |
| CG-4x | A cost figure may be reported only with its class (Measured / Assumed / Unknown) and its source | all | Rule |
| CG-5x | S3/S4 numbers (USD 533 / 719 per month) must not be quoted as the No-AI run cost | all | Rule (FF-03) |
| CG-6x | Re-qualification of any AI element (RQ-1..RQ-3) restarts this stage: token budgets, price verification from a dated vendor page, and a new Dinesh decision first | RL-01 | Rule (OD-08) |

### CG-7 Quality guardrail on optimisation
No optimisation may: drop or skip a regression group; weaken the E-groups; lower a threshold RT-01..RT-15 of `docs/26-tevv/release-thresholds.md`; edit a test to pass without a listed work item (`tests/hub/non_add_edits.json`, TST-CO-05 c); or relax OD-03a sandbox isolation and the data checksum gate. Efficiency changes must show before-and-after group counts (executed = expected) and checksum rc 0.

### CG-8 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CGF-1 | [Verified Fact] Four tripwire layers exist in code/tests and a fifth in the escalation model | CG-1 | Zero-model-call is monitored, not just stated | Low | High | none |
| CGF-2 | [Verified Fact] CI does not cover `hub/` and the hub hardening workflow is not installed | `vendor-inventory.md` V-06; OD-34 | L1 is not automatic | Medium | High | HAR-07 decision |
| CGF-3 | [Inference] Production egress control is the largest open assurance gap, because L2 runs only in tests. Reasoning: no host is chosen | ADR-015 | Zero model calls in production is unobserved | Medium | Medium | Hosting decision |

## Evidence References
Test files and modules listed in `evidence_sources`; `docs/37-operating-model/escalation-model.md` ER-04; OD-34 D-27-03.

## Assumptions
- A-32-20 CG-P1..CG-P5 are suggestions only; scope choice under OD-32, not approvals. Confirm: Dinesh (HAR-07 for CI).

## Unknowns
- U-32-26 Budget cap and alert thresholds (none exist). U-32-27 Host-level egress control.

## Unresolved Issues
- Install of `ci/hub-hardening.yml` awaits HAR-07; legacy Dockerfile/compose hardening at Stage 30.

## Residual Risks
- RR-32-18 A tripwire reading 0 interpreted as proof. Medium.
- RR-32-19 Deny-list gaps (CG-1 L1). Medium.
- RR-32-20 Production egress unobserved until a host exists. Medium. None of these risks is accepted by this stage.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
