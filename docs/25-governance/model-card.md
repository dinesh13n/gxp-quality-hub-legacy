---
stage: "25 — Governance + Compliance + Assurance"
artifact: "model-card.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md (OD-08, OD-16)", "docs/19-intelligence/not-applicable.md", "docs/20-application/deterministic-ai-boundary.md", "docs/20-application/evidence/no-ai-check.json", "hub/policy/rulesets.py", "hub/policy/as_found_pins.json", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/10-architecture/adrs/ADR-007-policy-and-rule-service.md", "docs/16-repo-validation/behavior-difference-report.md BD-12"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. There is no model. This card exists to say so precisely, to describe the deterministic decision components that stand where a model might have been, and to state what would have to be true before a model card with content could be written. Owner: Engagement lead (Dinesh Naik).**

## Summary
**Model: none.** The product makes zero model calls, holds no model weights, prompt, embedding or vector store, and has no network path beyond loopback (OD-08; `no-ai-check.json`: rc 0, findings []). Stage 19 (intelligence core) is NOT APPLICABLE (OD-25). A conventional model card (training data, evaluation, bias) therefore has nothing to describe. Instead this card documents (1) the absence claim and how it is enforced, (2) the three **as-found deterministic rule sets** that are the only decision logic the hub carries, all **inactive**, and (3) the conditions under which this card would be replaced by a real one.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### MC-1 Card
| Field | Value | Evidence | Tag |
|---|---|---|---|
| Model name / version / vendor | none | OD-08; `not-applicable.md` | [Verified Fact] |
| Model type | none (rules, SQL, keyword / field search, templates) | `qualification-decision.md` QD-1 | [Verified Fact] |
| Intended use | n/a | — | — |
| Training / fine-tuning data | none | no training code or data exists | [Verified Fact] |
| Prompts | none; rule explanations are template text from `hub/review/templates.py` (AC-REV-07), not generated | `deterministic-ai-boundary.md` | [Verified Fact] |
| Inference location / egress | none; loopback only; egress guard over tests (E05..E09, E20EGRESS) | `deterministic-ai-boundary.md` | [Verified Fact] |
| Evaluation | not applicable; the absence is tested (TST-CO-11 deny-list 40/40 in the Stage 20 run; TST-CO-12 tripwire; `no-ai-check` rc 0) | `no-ai-check.json` | [Verified Fact] |
| Known limitations of the absence claim | guard is manual (RTD-14); development tooling is out of the guard by definition; static check of untrusted use not built (AC-INT-23) | RR-AI-1 | [Verified Fact] |

### MC-2 Deterministic decision components (the nearest thing to "models")
Source: OD-16 and `hub/policy/rulesets.py`; values are as-found legacy rules, **not endorsed**, not owned by anyone (RC-3 / RC-4, DR-23, OD-S12-04).

| Component | Behaviour (as found) | State | Behaviour evidence | Owner of rule decision |
|---|---|---|---|---|
| Rule set 1: Python threshold | amount > 50,000 | candidate, **INACTIVE** | TST-CO-03 parity (3/3 green) | GAP; Engagement lead (Dinesh Naik) decides |
| Rule set 2: JS regional limit | regional limit x 1.05 tolerance; fallback 999,999 for unknown region / year; partial years differ by design (DEV-29, DV-11) | candidate, **INACTIVE** | 105/105 boundary cases identical (BD-11); DV-06, DV-11 proposed | GAP |
| Rule set 3: night-shift | 2,500 to 8,500 window | candidate, **INACTIVE** | TST-CO-03 | GAP |
| Divergence | the Python and JS sets disagree on 3 of 125 cases (C00000059, C00000077, C00000080); reported, not resolved | report only | BD-12; INC-09 | GAP |
- [Verified Fact] No rule set is active in a fresh store: `evaluate` without a rule-set reference returns `E-POL-NO-ACTIVE-RULESET`; activation needs a Zone H holder and a recorded decision (FAC-04). With `zone_h.holders` empty (OD-17), activation is impossible by design.
- [Inference] These rule sets are the only logic that could affect an approval or priority outcome; they are therefore governed as decision logic (HAR-06), not as software configuration.

### MC-3 Conditions for a real model card
A model card would be written only after all of: a new Dinesh decision re-opening Stage 8 for a named element (OD-08); RQ-1 / RQ-2 / RQ-3 evidence (labelled question set and measured baseline recall, or a failing multilingual / noisy corpus, or a recorded named request with reviewer-time budget); BR-AI-1..BR-AI-7; HAR-08, HAR-09, HAR-10 approvals; an injection test set; and a model-service scorecard (`docs/10-architecture/model-service-scorecard.md` currently records N/A: no AI service in scope). None has happened. [Verified Fact]

## Evidence References
`no-ai-check.json`; `hub/guards/no_ai.py`; `hub/policy/rulesets.py`; Stage 16 `behavior-difference-report.md`.

## Assumptions
- A-25-MC-1 [Assumption] Rule values listed are copied from OD-16's description of the as-found sets; only the Python threshold 50000 was seen in code (`hub/policy/asfound.py` L65); the JS and night-shift constants were not re-read here. Confirm: Stage 26 or the orchestrator against `hub/policy/as_found_pins.json`.

## Unknowns
- U-25-MC-1 Which of the three rule sets, if any, an organisation would adopt (RC-3 / RC-4).

## Unresolved Issues
- OD-S12-04 (rule authority); OD-S12-13 (preserve-or-fix DV-05, DV-06, DV-11).

## Residual Risks
- RR-MC-1 A reader treats "no model card" as "no governance of decision logic": Low; MC-2 closes that gap.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
