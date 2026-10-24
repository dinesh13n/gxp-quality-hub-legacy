---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "responsible-ai-controls.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", ".fde/orchestrator-decisions.md", "docs/08-ai-qualification/", "docs/25-governance/ai-system-register.md", "docs/23-human-control/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Responsible-AI position. The product contains no AI (OD-08), so the model-specific duties (bias, hallucination, model drift, explainability of generated text) do not arise in the product. What does apply is responsible automation: deterministic rules whose every outcome is traceable, human authority at every consequential action, and a door that stays closed to AI until re-qualified. The AI coding assistant used to build the repository is the only AI in the programme and is registered as such (OD-31).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RA-1 Principles and how they are met [Verified Fact unless marked]
| Principle | Control | Evidence |
|---|---|---|
| Human accountability | Zone H actions need a named holder plus a fresh re-auth; holders list is EMPTY in the shipped config, so nothing can be authorised by default | TST-GATE-01..22 |
| No automated consequential decision | Hub output is advisory; shadow mode; authority switch needs CLI + `approval_ref` (OD-31) | Stage 23 S10..S16 |
| Transparency | Every decision carries a rule trace; audit trail hash-chained; reasons recorded for C3 reads | Stage 11 traces, TST-SEC-09 |
| Fairness | Rules are deterministic and apply to all accounts alike. [Inference] Fairness across tenants or populations is not tested because no outcome-level ground truth exists | Unknown |
| Reliability and safety | Kill switch, runtime floor, quarantine rather than auto-correction | TST-CO-14, TST-INT |
| Privacy | PIA, field classes, masking | `privacy-impact-assessment.md` |
| Security | This stage | all |
| Contestability | Dispositions are insert-only; a decision can be superseded, never edited | S04, TST-NFR-10 |
### RA-2 What would be required if AI were added [Inference]
OD-08 re-qualification triggers RQ-1..RQ-3; model register entry; evaluation set from existing fixtures; human-in-the-loop for every Zone H effect; prompt/response logging without secrets; bias and drift monitoring; a new Stage 24 pass. None is built.
### RA-3 Honest limits [Verified Fact]
The estate and every figure are synthetic. No stakeholder has validated that the rules reflect real policy. Responsible-AI claims here describe design properties, not validated organisational behaviour.

## Evidence References
`docs/08-ai-qualification/`, `docs/25-governance/ai-system-register.md`, `docs/23-human-control/autonomy-matrix.md`, `hub/guards/no_ai.py`, TST-GATE, TST-CO-11.

## Assumptions
- A-S24-RA-1 Scope of 'Responsible AI' for a No-AI product is limited to responsible automation (DQ-S24-10).

## Unknowns
- U-S24-RA-1 Organisation's AI policy (none provided). U-S24-RA-2 Whether fairness testing is expected for rule-based triage.

## Unresolved Issues
- DQ-S24-10 scope confirmation.

## Residual Risks
RS-15, RS-16.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
