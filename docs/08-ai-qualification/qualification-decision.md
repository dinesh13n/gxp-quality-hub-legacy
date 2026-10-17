---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "qualification-decision.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/intervention-options.md", "docs/08-ai-qualification/ai-vs-no-ai-matrix.md", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/08-ai-qualification/minimum-intelligence-assessment.md", "docs/08-ai-qualification/minimum-agency-assessment.md", "docs/08-ai-qualification/intervention-hypothesis.md", "docs/08-ai-qualification/economics-baseline-reconciliation.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/06-root-cause/root-cause-readiness.md", "docs/07-repo-assessment/repo-transformation-readiness.md", "docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/00-preflight/ai-economics/*", "docs/00-preflight/operating-contract/*", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Recommended decision: No-AI.** Neither GenAI nor Agentic AI is justified by the evidence in this engagement. The recommended intervention is the deterministic package P-NOAI (process decisions + deterministic core + scheduled runs + shared metric definitions + rules/search/templates). Minimum intelligence: L0-L2. Minimum agency: A0/A1. Agentic AI is explicitly rejected.

**APPROVAL STATUS: NOT APPROVED. This is the agent's recommendation. The final adoption (or rejection) of any AI element is the decision of Dinesh Naik, the sole approver (HAR-10, HAR-11). No approval is recorded in `.fde/orchestrator-decisions.md` for this stage.** Nothing in this document introduces, authorises or schedules any AI call.

Label: synthetic repository, unvalidated against any organisation (Stage 6 scope statement). All 0C economic figures are unverified assumptions.

## Findings

### QD-1 Decision per touchpoint

| Touchpoint | Recommended outcome | One-line justification | Confidence |
|---|---|---|---|
| T1 Case triage explanation | **Rules** (rule-trace text); No-AI | Three-input 8-line rule; trace is an exact explanation (NFR-15) | High |
| T2 Partner-feed exception classification | **Rules** with reason codes and quarantine; No-AI, no ML | Fixed-key, enumerated content; no labels; injection channel | High (synthetic) / Medium (real) |
| T3 Document Q&A | **Rules** now (keyword/field search). AI-assisted NOT selected; conditional re-qualification via RQ-1..RQ-3 | Current content cannot show a keyword-search shortfall; real corpus Unknown | Medium |
| T4 Deviation/CAPA narrative | **Rules/template**; narrative generation not selected | No workflow, no requirement, regulated authorship | Medium |
| T5 Cross-store investigation | **Rules** (crosswalk after RC-7); **Agentic rejected** | Gap is a missing key; agent would guess | High |

Overall: **No-AI.** GenAI: not selected (T3 held as conditional option). Agentic AI: rejected.

### QD-2 Justification chain (each link cited)

1. [Verified Fact] All eight confirmed root causes are absences or defects of design (`confirmed-root-causes.md` CR-A); none concerns interpreting uncertain or unstructured input.
2. [Verified Fact] RC-3 (no owned definition) is a governance decision and RC-4's "which rule is right" depends on it (CR-D). AI cannot supply an owner.
3. [Verified Fact] Candidate-touchpoint content is categorical and tiny: 11 fixed keys in 8,567/8,567 feed rows, `notes` with 6 distinct values, `policy_exceptions.explanation` 5 distinct values over 224 rows, 3 distinct first body lines over 1,200 documents, archive files averaging 339 bytes. (Appendix EA-1..EA-6.)
4. [Verified Fact] No business requirement BR-01..BR-13 asks for language understanding, generation or prediction; BR-08 forbids automating disposition.
5. [Verified Fact] Injection-like strings are present in the data (NFR-13; 86 feed rows, 22 of 1,200 document bodies, EA-5), so any LLM consumer carries a risk that rules do not.
6. [Inference] The AI options score 0 of 8 on root-cause coverage and lowest on the matrix (O6 = 8, O7 = 9, O8 = 2 of 21) and fail or conditionally fail gates G2/G3 (`ai-vs-no-ai-matrix.md`).
7. [Inference] The decision is insensitive to price: AI loses on fit and risk with token cost set to zero (`economics-baseline-reconciliation.md` ER-3).
8. [Inference] The deterministic package is also the precondition for any honest later AI evaluation (ground truth, ids, history) (`intervention-hypothesis.md` IH-5).

### QD-3 What AI would have to demonstrate (re-qualification triggers)

Thresholds are proposals (Assumptions) for Dinesh to set; none is a measurement.

| ID | Trigger for re-opening Stage 8 for a specific element | Evidence required before any build |
|---|---|---|
| RQ-1 | Real or realistic document corpus becomes available (U-V02) | A labelled question set (proposal: at least 50 questions with known answer documents) and the measured recall of the keyword/FTS baseline; AI considered only if baseline recall is below a threshold Dinesh sets (proposal: 80% at top-5) |
| RQ-2 | Real content is multilingual or OCR-noisy in a way the baseline fails (the synthetic `locale` and `ocr_confidence` fields hint at this but bodies read are English stubs) | Baseline failure examples per language/quality band |
| RQ-3 | A named stakeholder requests a language-based touchpoint and accepts a reviewer-time budget | Recorded request with owner (HAR-11) and measured reviewer minutes |
| RQ-4 (agency) | Only after RQ-1..RQ-3 produced an approved AI element and RC-7 crosswalk exists: a residual set of cross-store cases that the crosswalk cannot resolve | Measured residual size and a showing that read-only deterministic queries cannot resolve it |

Each re-qualification must also satisfy BR-AI-1..BR-AI-7 (`deterministic-vs-ai-boundaries.md`), including HAR-08/09/10 approvals and an injection test set.

### QD-4 Implications for downstream stages (if approved)

| Stage | Implication |
|---|---|
| 9 PRD | State the problem per Stage 6 scope statement; no AI functional requirements; include an "AI non-goals and re-qualification triggers" section (QD-3). Safe to draft on the recommendation: it introduces nothing requiring HAR-10; rework risk if Dinesh chooses otherwise |
| 10 Architecture | Deterministic core; Zone H/D/A boundaries as constraints; platform choice (U-S02) is not driven by model availability |
| 19 Intelligence core | **Nothing to build.** Recommend recording "not applicable: no AI justified at Stage 8", or reduce scope to the deterministic rule-evaluation/explanation module (T1/T2 rules) if the PRD wants a named component |
| 22 Agentic engineering | **Not triggered.** Agency rejected (`minimum-agency-assessment.md` MA-4/MA-5) |
| 32 FinOps | Track P-NOAI: S1 plus non-ML S2 basis; token and model-call lines asserted as zero; S3/S4 budgets dormant; add reviewer-time measurement for rule-flagged items (omitted in 0C S1/S2); re-estimate build effort at Stage 9/13 |
| 14/15 | Transformation proceeds only after R-1 (executable), R-2, R-4, R-5 (Stage 7); this stage does not lift the no-go on code change |
| 23-26 | Human-control rules still needed (Zone H, HAR-12) even without AI, because the decision write path creates the gate |

### QD-5 Decisions that belong to Dinesh Naik (not made here)

| ID | Decision | Why it matters | Needed by |
|---|---|---|---|
| DN-1 | Approve, amend or reject this recommendation (No-AI, P-NOAI) | Controls Stages 19, 22, 32 | Before acting on skips at Stage 19/22; ideally before Stage 9 finalises |
| DN-2 | RC-3: owner and definition of closed/resolved/approved, or record "accepted open" (C-2) | O2 rule table and O4 cannot be finalised | Before Stage 13 |
| DN-3 | R-4 dataset baseline (125-case DB vs 6,000-case regenerable) and R-5 authority for rule conflicts (fix vs preserve) | Stage 7 no-go conditions | Before Stage 14/15 |
| DN-4 | Where batch disposition and the decision-of-record live (U-05-02, C-3) | Shape of the Zone H gate | Stage 9 |
| DN-5 | Whether buy-vs-build (O9) is in scope | O9 not evaluated | Stage 9/10 |
| DN-6 | Confirm a deterministic scheduler is not an HAR-10 "automated action" | Minimum-agency A-08-09 | Before Stage 15 |
| DN-7 | Thresholds for RQ-1 (question-set size, recall) if he wants triggers made operational | Re-qualification discipline | Stage 9 |

### QD-6 Completion Gate evaluation (honest)

| Gate condition | Status | Basis |
|---|---|---|
| Every option evaluated, rejected options explained | **Met** (O9 recorded as Not evaluated/Unknown, explicitly) | `intervention-options.md` F-08-OPT-1 |
| Any selected AI names the specific requirement that justifies it | **Met by vacuity**: no AI selected; T3 conditional option lists the exact requirement that would justify it (RQ-1/RQ-2) | QD-3 |
| Agentic behaviour justified or explicitly rejected | **Met**: explicitly rejected | `minimum-agency-assessment.md` |
| Stage 0C economics reconciled | **Met, conditional on approval**; prices remain unverified and dormant | `economics-baseline-reconciliation.md` |
| All required artifacts exist | **Met**: 8 of 8 under `docs/08-ai-qualification/` | this folder |
| Critical gaps resolved or documented | **Documented** (QD-5, Unknowns) | below |
| Evidence supports the conclusion | **Met at repo/synthetic level; not met for any real organisation** | Stage 6 scope statement |

**Gate: CONDITIONAL PASS.** No blocking condition. Conditions below are non-blocking; owner for all: **Engagement lead (Dinesh Naik)**. Calendar dates are not committed (no stakeholders; Dinesh to assign), so resolving stages are given.

| # | Condition | Risk if left open | Blocking? | Resolving stage |
|---|---|---|---|---|
| CD-1 | DN-1: Dinesh has not yet approved this recommendation | Downstream stages treat a recommendation as a decision (HAR-11) | No (proceeding on the more conservative non-AI path introduces nothing) | Before 19/22 are skipped; ideally 9 |
| CD-2 | DN-2 RC-3 open (C-2 from Stage 6) | Engineering silently encodes one rule | No | Before 13 |
| CD-3 | DN-3/DN-4: R-4, R-5, disposition location open | Stage 7 no-go on code change persists | No | 9 / 14 |
| CD-4 | DN-5 O9 not evaluated | Build-vs-buy blind spot | No | 9/10 |
| CD-5 | DN-6 HAR-10 interpretation | Delay at Stage 15 | No | Before 15 |
| CD-6 | 0C C-2..C-5 carried forward (volumes, dataset, real document size, benefits/labour) | Budget order-of-magnitude error; RQ-1 cannot be tested | No | 4/5/10/34 |
| CD-7 | Single-person authorship and approval (ER-11) | No independent challenge of an "AI rejected" conclusion that rests on synthetic data | No | Dinesh's own review; Stage 34 |

If Dinesh rejects the recommendation, the gate becomes BLOCKED for Stages 19/22 until the missing evidence (RQ-1..RQ-4) exists, because no requirement currently names what AI would do.

## Evidence References

Prior-stage artifacts listed in front matter. Prompt: `.fde/stage-prompts/08_AI-vs-No-AI-Qualification.md`.

### Evidence Appendix (read-only measurements, 2026-10-17)

All queries used `sqlite3` with `file:data/legacy.sqlite3?mode=ro&immutable=1` or plain file reads under `python3 -I`; the working-tree data was not written. No application code was run. SQLite FTS5 availability was tested in an in-memory database on the device (version 3.37.2); it is an Inference for the target runtime.

| ID | Measurement | Result |
|---|---|---|
| EA-1 | Table counts, `data/legacy.sqlite3` | cases 125; partner_feeds 8,567 (NEW 8,000, RETRY 500, REPLAY 67); policy_exceptions 224; deviations 42; capa_actions 21; vendor_file_rows 2,400 |
| EA-2 | `partner_feeds.raw_json` keys across 8,567 rows | `object_type, subtype, state, quantity, unit, currency, policy_version, quality_flag, notes, source_version` in 8,567; `business_key` in 8,357 |
| EA-3 | Distinct `notes` values in feeds | 6 (five fault phrases of about 1,640-1,790 rows each plus the injected "SYSTEM NOTE" text) |
| EA-4 | Distinct `policy_exceptions.explanation` | 5 values in 224 rows; `deviations.root_cause`: NULL 21 of 42, else 3 distinct phrases |
| EA-5 | `data/documents/source_documents.jsonl` | 1,200 docs; 3 distinct first body lines; 22 bodies contain "IGNORE"/"RELEASE" instruction text; `locale` es-MX 267, ja-JP 242, en-US 239, de-DE 230, en-IN 222; `ocr_confidence` null for 900, minimum 0.653 otherwise; regex scan for instruction-like phrases over both document stores: 44 hits |
| EA-6 | `data/archive_documents/` | 421 files (.eml/.html), mean size 339 bytes, one-sentence notes |
| EA-7 | `app/legacy_logic.py` | 8 lines, two functions over status/severity/amount |
| EA-8 | Integrity | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` run after the work: result recorded in Change History |

## Assumptions

- A-08-14 Content statistics from synthetic data are a fair proxy for the structure of real content. Confirm: Engagement lead (Dinesh Naik), Stage 5/10 (real sample). This is the single most consequential assumption of this stage.
- A-08-15 RQ thresholds are proposals only.
- All 0C numbers: unverified assumptions (A-08-12).

## Unknowns

- U-08-04 real document language/size/quality; U-08-08 benefit magnitude; U-08-09 P-NOAI build effort; U-08-01 O9; U-08-02 real decision-of-record location; whether any user wants natural-language Q&A (U-S01).

## Unresolved Issues

- CD-1..CD-7 above.

## Residual Risks

- False negative on AI: real documents may be large, multilingual or noisy, so keyword search disappoints. Mitigation: RQ-1..RQ-3, deterministic fallback built first.
- Confirmation by one reviewer: author and sole approver are one human/agent pair.
- Reader may treat this recommendation as client policy; it is not an approval.
- If approved, retiring S3/S4 budgets removes visibility of AI spend; mitigated by Stage 32 asserting zero model calls as a tripwire.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial recommendation; status DRAFT, approval pending Dinesh Naik. |
| v0.1 | 2026-10-17 | claude-fde-agent | Integrity check after work: `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` passed (no output, exit 0); `git status --porcelain` shows only `docs/08-ai-qualification/` untracked. |
