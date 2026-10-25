---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "model-ownership.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-08, OD-25", "docs/08-ai-qualification/qualification-decision.md", "docs/25-governance/{ai-system-register,model-card,system-card}.md", "docs/20-application/deterministic-ai-boundary.md", "hub/guards/no_ai.py", "docs/33-vendor-risk/vendor-inventory.md V-04", "docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01, FB-02"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
**Scope result: N/A for the product, with two real items.** The product is No-AI by Dinesh's decision (OD-08): rules, keyword/FTS search, templates and a deterministic core; **0 model calls, USD 0 token spend** (FB-01, FB-02). There is therefore **no model, prompt, retrieval index, embedding, fine-tune, evaluation set for a model or model vendor to own.** Stating an owner for these would be inventing an asset. What this document does instead is (1) record the N/A with the guard that keeps it true, (2) assign ownership of that guard and of the re-qualification path, and (3) cover the one AI-related asset that does exist: the AI coding assistant used to build (dev tooling).

## Findings
### MO-1 Model-related asset classes
| Class | Exists in product? | Evidence | Owner | State |
|---|---|---|---|---|
| Foundation/hosted model | No | OD-08; MS-1 N/A in `model-service-scorecard.md`; no provider in V-01..V-11 | none | N/A |
| Prompts / prompt templates | No (FR-REV-04 "templates" are non-AI text templates, switched off, OD-25 PCH-22) | `prioritized-capabilities.md` | none (templates fall under PA-06) | N/A |
| Retrieval / embeddings / vector index | No (keyword/FTS only) | `hub/search/`, `hub/r2/`; `deterministic-ai-boundary.md` | none | N/A |
| Fine-tuned model, evaluation set for a model | No | - | none | N/A |
| Model card / system card | Documents exist and say No-AI | `docs/25-governance/{model-card,system-card,ai-system-register}.md` | RL-01 for content (INTERIM) | INTERIM |
| No-AI guard (deny-list import check, egress tripwire, "zero model calls" tracking) | Yes | `hub/guards/no_ai.py`, `hub/guards/egress.py`; TST-CO-11/12; EH-04 | RL-02 runs, RL-05 sets policy | INTERIM / VACANT |
| AI coding assistant (build tooling) | Yes, outside the product | V-04; OD-08; AI register entry kept (OD-31); 51 of 51 main-branch commits carry the co-author trailer (Stage 33) | RL-12 toolchain owner | INTERIM; terms Unknown |

### MO-2 Ownership statements
1. **Today:** no product-model owner is needed. The invariant "no model in the product" is owned by RL-01 (the decision) and operated by RL-02 (the tripwires).
2. **Trigger for ownership:** any change under SDR-14 / C7 (re-qualification RQ-1..RQ-3 plus a new Dinesh decision plus HAR-08/09/10) must name, **before building**, an owner for each of: model and version, prompts, retrieval corpus, evaluation set, cost budget, and vendor terms. Until then none may be assumed.
3. **Coding assistant:** the code it writes is owned by the engagement owner of record, not by the assistant. The assistant holds no approval rights (TP-14) and is not an owner of anything. Its terms of use and data handling are Unknown (U-33-01).

### MO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| MF-01 | [Verified Fact] No product model, prompt or retrieval asset exists | OD-08; FB-01; TST-CO-11/12 | No model ownership is required | Low | High | none |
| MF-02 | [Verified Fact] The No-AI guard is a manual release gate; no CI runs it | RP-05; V-06 | A model import could slip in unnoticed between manual runs | Medium | High | Stage 27 CI |
| MF-03 | [Verified Fact] The AI coding assistant's terms and data handling are undocumented | V-04, U-33-01, VA-03 (PROPOSED) | Build provenance rests on terms nobody has reviewed | Medium | High | Dinesh to record terms or mark N/A |
| MF-04 | [Inference] Mis-reading "AI coding assistant in the register" as "AI in the product" is a documentation risk | OD-31 | Misleading audit trail | Low | Medium | Keep the dev-tooling label |

## Evidence References
See `evidence_sources`.

## Assumptions
- A-37-MO-1 [Assumption] The N/A holds as long as OD-08 stands. Confirm: Engagement lead (Dinesh Naik).
- A-37-MO-2 [Assumption] The ownership requirement list in MO-2 item 2 is a proposed pre-condition, not an existing policy. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-MO-1 Terms and data handling for the AI coding assistant (V-04).
- U-37-MO-2 Whether a client AI governance function would require its own register (OB-15 external AI governance, no owner).

## Unresolved Issues
- VA-03 decision; CI for the No-AI guard (Stage 27).

## Residual Risks
- RR-37-MO-1 Unreviewed AI re-introduction by a future team: Medium; mitigated by tripwires and HAR-10, not eliminated.
- RR-37-MO-2 Unrecorded assistant terms: Medium; open.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
