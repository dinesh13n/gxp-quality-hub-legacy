---
stage: "6 — Root-Cause Analysis"
artifact: "confirmed-root-causes.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/causal-hypotheses.md", "docs/06-root-cause/evidence-confidence-matrix.md", "docs/06-root-cause/validation-plan.md", "docs/06-root-cause/root-cause-tree.md", "app/generate.py", "app/store.py", "app/server.py", "app/legacy_logic.py", "app/partner_feeds.py", "app/gateway_bridge.py", "legacy_js/legacy_policy.js", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "sql/legacy_reports.sql", "docs/02-stakeholders/decision-rights-map.md", "docs/correspondence/operations-vs-risk-2024.md", "data/legacy.sqlite3 (read-only, immutable)"]
supersedes: "none"
---
## Summary

**Eight root causes pass their repo-level validation method (V-01..V-08).** They are confirmed as **structural causes of the control, traceability, consistency and measurability symptoms (S2-S7) in the system as shipped**. They are **not** confirmed as causes of delay, cost or rising effort (S1), because no valid flow-time, volume or cost data exists (OD-04, OD-07), and none has been validated against a real organisation. Two of them (RC-3 and, in part, RC-1) are governance gaps that engineering cannot close by itself; Stage 8 must treat them as decisions.

**Scope statement (must accompany every citation of this file):** "Confirmed (repo-level)" means: observed in code/schema/SQL, a disconfirmation search was run and failed, and a contradictory reading was considered. It means nothing about magnitude, frequency or business cost.

## Findings

### CR-A. Confirmed root causes

| RC | Root cause (stated without a remedy) | Symptoms explained | Validation | Contradictory evidence weighed | Confidence | Impact | Risk | Class |
|---|---|---|---|---|---|---|---|---|
| RC-1 | The step that records a case decision, closure or batch disposition (with actor and basis) has no representation in the system. The only writer of `cases` is the data generator (`app/generate.py:37`); the API is GET-only (`app/server.py`) | S3, S6 | V-01 PASS | Decision may be recorded in an external "local system" (`business-context.md` step 4); absence is of the repo, not of the organisation | High (repo) / Unknown (org) | Closure and disposition cannot be attributed, timed or audited from system data; K-04/K-05 unmeasurable | Human approval gate (`domain-assurance.md` L4) exists only on paper in this repo; any change near it risks bypassing an unseen control | [Verified Fact] |
| RC-2 | Case state is a mutable snapshot: `cases.version` = 1 for 125/125 with no code that increments it; creation event stores the *current* status (125/125); only 2 event types exist; 8 REOPENED cases have 0 reopen events | S6, S7 | V-02 PASS | Enterprise `state_history` exists but is 1 row/object (`to_state` = current); an external system may keep history | High | History cannot be reconstructed; contradictions undetectable after the fact | Attributability/contemporaneity of records (ALCOA+ concerns; not assessed against regulation here) | [Verified Fact] |
| RC-3 | No owned definition of "closed / resolved / approved", and no decider for the speed-vs-evidence trade-off (DR-20, DR-21, DR-23 are GAPs; `operations-vs-risk-2024.md`: "never formalized") | S3, S5, S7 | V-03 PASS (documentary) | Single synthetic source family; conflict may be resolved since 2024 (U-03-03); Dinesh could decide (A-03-16) | Medium | Same case counted, closed and costed differently; any KPI built on "closed" is undefined | Engineering may silently encode one party's rule (CG-7 in Stage 3) | [Verified Fact] (documents) |
| RC-4 | The approval/priority logic exists as three unsynchronised implementations: `app/legacy_logic.py` (>50,000), `legacy_js/legacy_policy.js` (regional limit x 1.05, default 999,999), `legacy_batch/shift_reconciliation.py` (threshold 2,500-8,500); the Java/SQL month-end paths do not call the Python rule despite the header comment | S3, S5, S7 | V-04 PASS | Three rules answer different questions; none declared authoritative (U-05-05); 0 of 125 shipped cases exceed 50,000 | High (existence) / Medium (outcome divergence, Inference) | Same input can yield different outcomes; unknown region/year silently gets 999,999 | Approval limit effectively removed for unknown region/year | [Verified Fact] |
| RC-5 | Execution is manual-start, capacity-capped and unrecorded: no scheduler anywhere; `reconcile(limit=1000)` vs 8,567 backlog rows (9 runs); reconcile writes no run record | S4 (partly), backlog | V-05 PASS | External scheduling possible (A-05-06); backlog size is a generator parameter; cap is a default argument | High (mechanism) / Low (impact) | Feed-driven work waits for a person; no run evidence | Late/missing reconciliation; divergence of totals | [Verified Fact] / [Inference] impact |
| RC-6 | Intake is destructive and content-blind: reconcile overwrites `processing_status` in place; every REPLAY becomes DUPLICATE without content comparison; invalid gateway events are counted, not stored; `source-contract-v1.json` is not enforced; Java skips unparsable amounts | S2, S4 | V-06 PASS | Frequency of corrected replays unknown; INC-2025-014 mechanism not traceable to this code (R-08) | High (mechanism) / Low (frequency) | Evidence lost or mis-classified at the door | Corrected replay discarded; data-integrity exposure | [Verified Fact] |
| RC-7 | No shared identity or referential model: `cases` has no batch/deviation/CAPA/feed key; `partner_feeds.ref_id` has no FK; five status vocabularies; no constraint across case/batch/deviation/CAPA/lab states | S2, S7 | V-07 PASS | CG-04 counts and the 98% orphan rate are generator-shaped (R-05); only the **absence of constraints** is claimed | High (schema) | Contradictory and orphaned records are permitted; cross-id lookup is manual (MH-09) | Closure of questionable batches goes undetected | [Verified Fact] |
| RC-8 | Month-end figures are computed independently without a shared definition: SQL `LEFT JOIN events` inflates `SUM(amount)` by 19.3% on the shipped data (742,956.61 vs 622,826.44, re-executed read-only); Java `double` with silent `NumberFormatException` skip; API counts | S5 | V-08 PASS | Size depends on events per case (generator); whether finance consumes the SQL report is Unknown; K-10 not used (R-04) | High (mechanism) / Low (org impact) | Totals differ by method | Finance/ops disagreement; effort spent explaining differences (effort Unknown) | [Verified Fact] |

### CR-B. Not confirmed (carried forward as hypotheses)

| ID | Status | Why not confirmed | What would confirm |
|---|---|---|---|
| H-10 closure evidence not linked | SUPPORTED | Evidence location Unknown | V-09 walk-through |
| H-11 tribal knowledge | UNKNOWN | Two one-sentence notes only | V-10 |
| H-12 capacity | UNKNOWN | No data | V-11 |
| H-13 volume growth | UNKNOWN | Only rejected evidence | V-12 |
| H-14 SQLite contention | SUPPORTED | Config only | V-13 sandbox test |
| H-15, H-16 | LATENT RISK | Not causes of S1-S7 | n/a; carried to risk register |
| S1 itself | UNKNOWN | No trend | Real series |

### CR-C. Rejected (see `causal-hypotheses.md` H-B)

R-01..R-10 remain recorded with reasons, including the Stage 4 proxies P-01/P-03/P-04 and K-10 (OD-07: cited only as generator-bounded proxies / unrelated populations).

### CR-D. Which root causes are decisions rather than defects

| RC | Nature | Implication for later stages |
|---|---|---|
| RC-3 | **Decision gap** (governance) | Needs an owner decision or an explicit "accepted open"; Stage 8 must not choose a side |
| RC-1 | Mixed: absent system function plus an unknown external gate | Must not bypass or simulate the human disposition (DR-22, HAR-12, STOP-07) |
| RC-4 | Defect, but "which rule is correct" is a decision (RC-3) | Characterise first (Stage 7), do not merge by assumption |
| RC-2, RC-5, RC-6, RC-7, RC-8 | Engineering-addressable defects of design | Eligible for option analysis in Stage 8 |

## Evidence References

All sources listed in front matter; re-validation outputs recorded in `validation-plan.md` VP-A. Evidence ceiling: repository plus synthetic data.

## Assumptions

- A-06-02, A-06-03, A-06-04 (see sibling artifacts). Owner: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-01..U-06-14 (see `causal-hypotheses.md`, `validation-plan.md`). Most consequential: whether the organisation records decisions and history elsewhere (U-05-02, U-06-05).

## Unresolved Issues

- Self-confirmation: author and approver of Stage 6 conclusions are the same single human/agent pair (ER-11); no independent review.
- Stage 4 KPI sheet still cites A-04-01; correction deferred to Stage 4 v0.2 addendum (OD-07).

## Residual Risks

- Root causes describe the shipped system, not the client organisation; interventions justified solely by them may address a system that is not the real one.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial confirmation at repo level. |
