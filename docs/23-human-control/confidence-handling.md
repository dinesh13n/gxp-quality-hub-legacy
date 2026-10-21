---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "confidence-handling.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/08-ai-qualification/qualification-decision.md", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md BR-AI-1..7", "hub/review/search.py OCR_LOW", "hub/r2/divergence.py", "hub/obs/", ".fde/orchestrator-decisions.md OD-08"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
**The product produces no probabilistic output, so there is no model confidence to threshold.** Stage 23 therefore defines no numeric confidence threshold and invents none. Where the hub does express uncertainty it does so deterministically: documented reason codes, "unknown" values, quarantine, and one data-quality field carried from the source (`ocr_confidence`, with a fixed low-flag at 0.70). If an AI element is ever admitted (BR-AI-1, HAR-10, re-qualification RQ-1..RQ-3), its thresholds and its fallback must be defined and approved first; this document lists what that would have to include.

## Findings
### Where uncertainty appears today
| ID | Signal | Source | Handling | Threshold | Tag |
|---|---|---|---|---|---|
| CH-01 | `ocr_confidence` of a document | source data field (shipped documents) | shown with `ocr_low = true` when below `OCR_LOW`; missing value shown as `unknown` | 0.70 (constant in `hub/review/search.py`, set in INC-09; not a client-approved threshold) | [Verified Fact] |
| CH-02 | Intake outcome class (VALIDATED, VALIDATED_WITH_FLAGS, QUARANTINED, EXCEPTION, NOOP_DUPLICATE) | `hub/intake/` | flagged and quarantined items go to the exception queue for a human | none (categorical) | [Verified Fact] |
| CH-03 | Rule divergence between as-found rule sets | `hub/r2/divergence.py` | reported; a null (not comparable) output is not counted as divergence | none | [Verified Fact] |
| CH-04 | Metric not reproducible / not available / source refused | `hub/metrics/` | explicit error codes; no estimate is substituted | none | [Verified Fact] |
| CH-05 | `manual_review_required` flag from a rule | rule output | queue item for a reviewer | rule-defined (legacy rules, synthetic) | [Verified Fact] |
| CH-06 | `facts.derivation = human_only` | config | facts are entered by a person; derivation off | n/a | [Verified Fact] |

### Required if an AI element is ever proposed (not built, not approved)
1. A labelled test set and a measured shortfall of the deterministic baseline (BR-AI-6).
2. A numeric threshold per decision class, set by the owner and recorded in the OD log (HAR-11), with Unknown until then.
3. Below threshold: route to a human (HITL); never auto-act; above threshold: still not Zone H.
4. A deterministic fallback when the model is off (BR-AI-5) and an injection test set (BR-AI-4).
5. Output stored apart from decision tables (BR-AI-2).

### Findings
- [Verified Fact] No code in `hub/` reads a model score; `model_calls_total` is 0 in every group that reports it.
- [Verified Fact] The only fixed numeric threshold that resembles a confidence cut-off is `OCR_LOW = 0.70`.
- [Assumption] The 0.70 value is a build default, not a decision (confirm: Dinesh Naik, or the document owner when one exists).
- [Unknown] The real distribution of `ocr_confidence` (synthetic, unvalidated) and whether 0.70 suits it.

## Evidence References
`hub/review/search.py`; Stage 8 `deterministic-vs-ai-boundaries.md`; groups C1 / E-groups (tripwire 0).

## Assumptions
- A-23-09 OCR_LOW 0.70 stays until a document owner sets one.

## Unknowns
- U-23-10 Real `ocr_confidence` distribution.

## Unresolved Issues
- None for the No-AI product.

## Residual Risks
- If AI is added later without this section being completed, the BR-AI rules would be the only guard (RR-HC-4, Low while the deny-list holds).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
