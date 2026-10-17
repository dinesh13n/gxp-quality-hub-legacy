---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "minimum-intelligence-assessment.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/ai-vs-no-ai-matrix.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/03-problem-value/business-requirements.md", "app/legacy_logic.py", "app/partner_feeds.py", "data/documents/source_documents.jsonl (read-only)", "data/legacy.sqlite3 (read-only, immutable)"]
supersedes: "none"
---
## Summary

For each evidenced problem the least intelligence that solves it is identified on a ladder L0-L5. **Every confirmed root cause is solved at L0 or L1; every candidate touchpoint at L1 or L2. No evidenced requirement needs L3 or above.** The three tests a problem must pass before L3+ is considered (uncertainty, language, adaptive judgement) are applied explicitly. Recommendation only; final decision with Dinesh Naik.

## Findings

### MI-1 Intelligence ladder

| Level | Meaning | Example here |
|---|---|---|
| L0 | Policy / people / process | Decide who owns "closed" (RC-3) |
| L1 | Deterministic code | Append-only decision log, single rule table, idempotent intake |
| L2 | Rules, lookup, search, templates | FTS5 search, rule-trace text, reason codes |
| L3 | Classical ML | Classifier trained on labels |
| L4 | GenAI (generation / language understanding) | Summaries, Q&A, drafting |
| L5 | Agentic (multi-step autonomous tool use) | Cross-store investigator |

### MI-2 Per-problem minimum (root causes)

| Problem | Minimum level | Why a higher level adds nothing | Confidence |
|---|---|---|---|
| RC-1 no decision step | L1 (plus L0 for placement of the human gate) | A record of who/when/why is a schema and an API; the decider is human | High |
| RC-2 mutable state | L1 | Append-only history is storage design | High |
| RC-3 no owned definition | L0 | A decision, not a computation; AI cannot supply an owner | High |
| RC-4 three rules | L1 after L0 decision | Which rule is right is RC-3; consolidating copies is code | High |
| RC-5 manual runs | L1 | Scheduler and run table | High |
| RC-6 destructive intake | L1 | Keep the original, compare content hash, quarantine on difference | High |
| RC-7 no shared identity | L1 | Keys and crosswalk; fuzzy matching would reintroduce guessing (Stage 6 "must not fabricate links") | High |
| RC-8 independent totals | L1 | Shared definition and one query; the 19.3% inflation is a join defect | High |

### MI-3 Per-touchpoint minimum

| Touchpoint | Minimum | Evidence | Confidence |
|---|---|---|---|
| T1 | L2 | Three inputs, one 8-line function (`app/legacy_logic.py`) | High |
| T2 | L2 | Fixed-key JSON in 8,567/8,567 rows; `notes` 6 distinct values; 4 reconcile branches (`app/partner_feeds.py`) | High (synthetic), Medium (real) |
| T3 | L2 on current content; L4 not excluded for real content | 1,200 docs, 3 distinct first lines; 421 archive files avg 339 bytes | Medium (real corpus Unknown, U-V02) |
| T4 | L2 | 21 of 42 deviations have no root cause; others 3 phrases; no narrative workflow, no BR for it | Medium |
| T5 | L1/L2 after RC-7 | Missing keys | High |

### MI-4 The three AI-justification tests, applied

| Test | Question | Result | Evidence |
|---|---|---|---|
| Uncertainty | Is there a decision where the correct answer is uncertain and a statistical model beats rules on labelled data? | **No evidence.** No labels exist; synthetic labels derive from the generator that created the data (0C `solution-scenarios.md` S2 caveat). Rules reproduce the generator exactly | Unknown whether real data differs |
| Language | Is there unstructured or multilingual text that keyword/field methods demonstrably cannot handle? | **Not shown.** `locale` has 5 values (es-MX, ja-JP, en-US, de-DE, en-IN) but bodies read are English phrases from a 3-phrase set; OCR confidence null for 900 of 1,200 and >= 0.653 where present. Whether real documents are multilingual or noisy is Unknown | U-V02 |
| Adaptive judgement / generation | Is there a task that varies so much that fixed rules cannot be written, or a need to generate text? | **No.** Rules for T1/T2 are tiny; no requirement asks for generated text (BR-01..BR-13) | `business-requirements.md` |

[Inference] Conclusion: the only open door is the Language test for T3, and it is open for lack of data, not because of evidence of failure. This is why T3 is handled with re-qualification triggers rather than a rejection that would be hard to reverse.

### MI-5 Cost of over-provisioning intelligence

[Inference] Token spend is not the cost of too much intelligence: at modelled volumes it is under USD 137/month even in the 0C worst case (assumption). The cost is (a) human review of every model output (0C oversight line; each additional reviewer minute per case is about USD 70/month at Base, assumption), (b) GxP-style validation of a non-deterministic component (cost Unknown, 0C open question), (c) injection exposure that rules do not have.

## Evidence References

`confirmed-root-causes.md`; `business-requirements.md`; `app/legacy_logic.py`, `app/partner_feeds.py`; content statistics from read-only queries (Evidence Appendix, `qualification-decision.md`); `cost-scenarios.md` sensitivity paragraph.

## Assumptions

- A-08-07 Generator-shaped content stands in for real content. Confirm: Engagement lead (Dinesh Naik) once any real or realistic corpus exists (Stage 5/10).
- A-08-08 English-only reading of document bodies is based on the first body line only; later lines were not exhaustively read.

## Unknowns

- U-08-04 Real document language, size and quality (U-V02).
- U-08-06 Real label availability and rate of corrected replays (RC-6 frequency Unknown).

## Unresolved Issues

- None blocking.

## Residual Risks

- Under-provisioning risk: if real documents are noisy and multilingual, L2 search may disappoint users; mitigated by RQ triggers and by building the deterministic fallback first (needed anyway).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial assessment. |
