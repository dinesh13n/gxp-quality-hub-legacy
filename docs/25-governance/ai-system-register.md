---
stage: "25 — Governance + Compliance + Assurance"
artifact: "ai-system-register.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md (OD-08, OD-25)", "docs/08-ai-qualification/{qualification-decision,deterministic-vs-ai-boundaries}.md", "docs/19-intelligence/not-applicable.md", "docs/22-agentic-engineering/not-applicable.md", "docs/20-application/deterministic-ai-boundary.md", "docs/20-application/evidence/no-ai-check.json", "hub/guards/no_ai.py", "docs/17-implementation-prd/finalized-nfrs.md PNFR-18", "docs/09-initial-prd/non-goals.md NG-01", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md HAR-10"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. No organisation maintains an AI system register for this engagement (Unknown); this register is created because the Stage 25 prompt requires one. Entry owner: Engagement lead (Dinesh Naik). No external AI-governance framework is cited in the repo and none is applied (OB-15).**

## Summary
The register has **one product entry (AIS-01) whose classification is "not an AI system"** (No-AI, OD-08), registered so that the absence is explicit and testable, **one development-tooling entry (AIS-02)** for the AI coding assistant that builds the system (not product AI, OD-08), and **one candidate entry that is not built (AIS-03, AI-assisted document Q&A)** that can only open through RQ-1..RQ-3. Agentic AI is rejected (AIS-04). Counts: models in production 0; model calls 0; prompts 0; embeddings 0; third-party runtime dependencies 0.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AR-1 Register
| Field | AIS-01 GxP Quality Hub (`hub/`) | AIS-02 AI coding assistants used to build | AIS-03 Candidate: AI-assisted document Q&A (T3) | AIS-04 Candidate: agentic investigation (T5) |
|---|---|---|---|---|
| Classification | **Not an AI system**: rules, SQL, keyword / field search, templates, deterministic core | Development tooling (`claude-fde-agent`) | **Not selected**; conditional re-qualification only | **Rejected** (`minimum-agency-assessment.md` MA-4/5) |
| Status | Shadow implementation, loopback, synthetic data (RB-0) | Active during the engagement | Not built | Not built |
| Decision record | OD-08 (Dinesh, 2026-10-18); Stage 19 NOT APPLICABLE (OD-25); Stage 22 NOT APPLICABLE | OD-08 sentence "AI coding assistants used to BUILD the system are dev tooling, not product AI" | QD-1 T3; QD-3 RQ-1..RQ-3 | QD-1 T5; RQ-4 |
| Owner | Engagement lead (Dinesh Naik) | Engagement lead (Dinesh Naik) | Engagement lead (Dinesh Naik) | Engagement lead (Dinesh Naik) |
| Purpose | Attributable decision record, safe handling of external case information, figures with declared definitions; disposition stays human | Write code, tests and documents on branches under review; no approval rights (TP-14) | Would answer questions over documents | Would investigate across stores |
| Model(s) | none | not a product component; vendor and version are recorded in commit attributions, not in the product | none | none |
| Autonomy level | A0 / A1 deterministic (no agency); no automated action (scheduler OFF) | Executes inside stage permissions TP-01..TP-15; humans approve | n/a | n/a |
| Data used | synthetic FX-BASE125 (125 cases, seed 4100, OD-09) and fixtures | repo content; no real data exists (OD-04) | n/a | n/a |
| Human oversight | Zone H (human-only, holders []); reviewer overrides with reason; rule traces | Dinesh approves merges via delegation (OD-13); gate acceptance by OD entry | RQ-3 requires a named requester and reviewer-time budget | n/a |
| Controls | GC-11 tripwire, GC-12, GC-10 G5; PNFR-18 | GC-14, GC-16, STOP-01..12, TP matrix | BR-AI-1..BR-AI-7; HAR-08/09/10; injection test set | same |
| Risk rating | Not rated by any authority [Unknown]; PRD risk PR-14 (framing mistaken for certification) | Not rated | Not rated | Not rated |
| Evidence | `no-ai-check.json` rc 0, findings []; TST-CO-11 (40/40 in the Stage 20 run); TST-CO-12; E05..E09, E20EGRESS; zero third-party dependencies (SS-01) | git history and commit attributions | `qualification-decision.md` | `minimum-agency-assessment.md` |
| Change trigger | Any dependency, import or egress that the deny-list flags; any request for an AI element | n/a | RQ-1 (labelled corpus + baseline recall below Dinesh's threshold), RQ-2, RQ-3 | after RQ-1..3 produce an approved AI element (RQ-4) |
| Review cadence | Every release checklist run (G5) and Stage 32 / 39 | per stage | on trigger | on trigger |
| Tag | [Verified Fact] | [Verified Fact] | [Verified Fact] decision; thresholds are proposals | [Verified Fact] |

### AR-2 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| AI-F1 | [Verified Fact] The product contains no AI; the proof is structural (deny-list, egress guard, zero counter) and manual | `deterministic-ai-boundary.md`; RTD-14 | Register entry stays "not an AI system" only while the guard is run | Medium until CI (Stage 27) | High | CI gate owner |
| AI-F2 | [Unknown] Whether the organisation's AI register scope covers AI used as development tooling (AIS-02) | no policy exists | Entry may be unnecessary or insufficient | Low | Medium | Dinesh decides whether AIS-02 stays in the register |
| AI-F3 | [Verified Fact] RQ-1..RQ-3 thresholds (>= 50 questions, 80 % top-5) are proposals, not decisions | `qualification-decision.md` QD-3 | Re-qualification cannot start without Dinesh setting them | Low | High | OPD-12 |
| AI-F4 | [Inference] A scheduled deterministic reconcile is probably not an "automated action" in the HAR-10 sense, but nobody has decided | OPD-11; OD-S12-10 | Schedule stays OFF | Medium (value) | Medium | OD-S12-10 |

## Evidence References
See `evidence_sources`; mechanisms described in `model-card.md` and `system-card.md`.

## Assumptions
- A-25-AR-1 [Assumption] "Not an AI system" is the correct classification of rule-based, SQL and keyword-search components. The classification follows OD-08; it was not tested against any external definition. Confirm: Engagement lead (Dinesh Naik); qualified review if an external definition applies.

## Unknowns
- U-25-AR-1 Risk tier under any external AI framework (none chosen).
- U-25-AR-2 Whether keyword / FTS5 search (FR-REV-03, built dark) is treated as AI by any reader (it is not by OD-08).

## Unresolved Issues
- AIS-02 scope question (AI-F2); OPD-11; OPD-12.

## Residual Risks
- RR-AR-1 A later contributor adds a model or SDK without noticing the manual guard: Medium (mitigated by deny-list tests; CI wiring planned).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
