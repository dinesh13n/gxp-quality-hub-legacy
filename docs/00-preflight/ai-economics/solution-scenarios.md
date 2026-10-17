---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "solution-scenarios.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/workflow-overview.md WF-01..WF-11", "docs/00-preflight/discovery/integration-overview.md", "docs/00-preflight/operating-contract/data-use-constraints.md DU-03,X-3", "app/legacy_logic.py", "legacy_batch/shift_reconciliation.py", "workload-assumptions.md"]
supersedes: "none"
---
## Summary

Five comparable scenarios across the same hypothetical touchpoints. **Nothing here claims AI is justified; Stage 8 decides whether any AI portion remains applicable and may retire S3/S4 and their cost assumptions.** S0-S2 are non-AI and are modelled first-class in every cost artifact.

## Findings

Candidate touchpoints (HYPOTHETICAL; derived from workflows in Stage 0A, none exist in code):

| ID | Touchpoint | Workflow anchor (evidence) |
|---|---|---|
| T1 | Case triage explanation / review summary | WF-03 `app/legacy_logic.priority()`, `manual_review_required()` |
| T2 | Partner-feed exception classification | WF-02 `app/partner_feeds.py` reconcile; policy_exceptions never consulted |
| T3 | Document Q&A over source/archive documents | 1,200 + 420 docs (W-05); no search exists today |
| T4 | Deviation/CAPA narrative drafting | WF-04 data-only; no transition logic |
| T5 | Multi-step case investigation across the 3 disjoint stores (agentic only) | DF-09 no cross-store keys; WF-06 divergent rules |

| Scenario | Description | Model calls | Handles which touchpoints | Key evidence-based caveat |
|---|---|---|---|---|
| S0 As-is (reference) | Current system, manual operations | 0 | none automated | Baseline for before/after; hours_per_case 0.6 is synthetic (W-07) |
| S1 Deterministic software | Consolidate the three divergent threshold rules into one table-driven rule service; SQL/FTS5 search over documents; templated summaries from fields; implement missing disposition-gate workflow with human approval | 0 | T1 (templated), T2 (rules), T3 (keyword/FTS), T4 (template) | Rule divergence (WF-06/R-06) is a *logic* defect that AI would not fix; U-16 must be answered first |
| S2 Conventional automation | S1 plus ETL/scheduled jobs, regex/dictionary normalisation of unit variants and statuses, classical ML (e.g. gradient-boosted classifier for feed exceptions) trained on synthetic labels, RPA-style CSV file-drop | 0 | T1-T4, T2 stronger | Labelled training data does not exist; synthetic labels would not transfer (Assumption) |
| S3 GenAI (single-pass, RAG) | LLM calls with bounded context for T1-T4; retrieval over documents; human reviews every output | T1,T2(flagged only),T3,T4 | T1-T4 | Untrusted instruction-like text in corpora (DF-08, DU-03) makes unguarded LLM consumption a High risk |
| S4 Agentic AI | S3 plus tool-using loop for T5 on ~10% of cases (read-only tools only, per 0B) | S3 + T5 | T1-T5 | Highest token amplification (quadratic context re-send), highest injection exposure; loop limits mandatory |

[Inference] Because workload volumes are small (Base 167 cases/month), the *economic* differentiator between scenarios is engineering effort, oversight labour and compliance burden, **not token spend** (quantified in `cost-scenarios.md`).

## Evidence References

Stage 0A workflow-overview WF-01..WF-11; 0B data-use-constraints DU-03/X-3/X-4; `app/legacy_logic.py` L2-8.

## Assumptions

- A-S01 Touchpoints T1-T5 represent plausible demand; none has been requested by a stakeholder. Confirm: Engagement lead (Dinesh Naik); stage 1/2.
- A-S02 Any model API call needs data egress approval HAR-09 (0B X-3); synthetic data only.

## Unknowns

- U-S01 Whether any touchpoint is wanted by users at all. Stage 1/2.
- U-S02 Model/platform choice (Azure OpenAI/Foundry vs other) - not decided; Stage 8/10.

## Unresolved Issues

- None blocking. Stage 8 reconciles S3/S4 with the AI-vs-No-AI decision.

## Residual Risks

- Anchoring on AI-shaped touchpoints could hide that the dominant gaps (T-less) are deterministic: missing disposition workflow (WF-05), divergent rules (WF-06).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
