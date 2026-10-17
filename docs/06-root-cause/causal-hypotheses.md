---
stage: "6 — Root-Cause Analysis"
artifact: "causal-hypotheses.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/problem-framing-canvas.md", "docs/03-problem-value/problem-statement.md", "docs/05-current-state/current-state-summary.md", "docs/05-current-state/control-points.md", "docs/05-current-state/process-bottlenecks.md", "docs/05-current-state/business-workflow-map.md", "docs/05-current-state/integration-landscape.md", "docs/05-current-state/manual-handoffs.md", "docs/05-current-state/dependency-hotspots.md", "docs/02-stakeholders/decision-rights-map.md", "docs/correspondence/operations-vs-risk-2024.md", "app/store.py", "app/legacy_logic.py", "app/partner_feeds.py", "app/gateway_bridge.py", "sql/legacy_reports.sql", "legacy_java/ReconcileLegacy.java", "data/legacy.sqlite3 (read-only, immutable)", ".fde/orchestrator-decisions.md (OD-04, OD-07)"]
supersedes: "none"
---
## Summary

Register of every causal hypothesis considered in Stage 6: 16 live hypotheses (H-01..H-16) and 10 rejected or demoted ones (R-01..R-10). All rejected hypotheses are preserved with the reason. Evidence is **repository-only** (code, schema, synthetic data, synthetic documents; OD-04), so the status vocabulary is deliberately two-tier:

| Status | Meaning in this stage |
|---|---|
| **CONFIRMED (repo-level)** | Passed its validation method on repository evidence (code/schema/SQL). Confirms the *structural condition exists* and that it mechanically produces the named symptom class (control, traceability, consistency, measurability). Does **not** confirm size, frequency or business cost. |
| **SUPPORTED (not confirmed)** | Reasoned from verified facts ([Inference]); validation method not yet passable with repo evidence. |
| **UNKNOWN** | Insufficient evidence either way; only a real process study can resolve it. |
| **REJECTED** | Evidence contradicts it, or it was an artefact of the generator (preserved). |
| **LATENT RISK FACTOR** | Real defect, but not a cause of any Stage 3 symptom; carried to risk, not to the causal tree. |

Symptoms analysed (Stage 3 S1-S5, plus two control-level symptoms drawn from Stage 5):

| ID | Symptom | Source |
|---|---|---|
| S1 | "Rising exception-handling effort" (claim; no trend data) | `problem-framing-canvas.md` |
| S2 | Feed rows inconsistent with core records | canvas S2; IO-10 |
| S3 | "Closed" means different things at different sites | canvas S3 |
| S4 | Replay inflated exception queue (2025); delayed feed forced manual spreadsheet reconciliation (INC-2025-014) | canvas S4 |
| S5 | Finance and operations monthly figures disagree | canvas S5 |
| S6 | Decisions/closures cannot be attributed or reconstructed (no audit trail, no decision record) | `control-points.md` CG-01..03 |
| S7 | Contradictory closure states across cases/batches/deviations/CAPA are possible | CG-04 |

## Findings

### H-A. Live hypotheses

| ID | Hypothesis (cause -> symptom) | Category | Symptoms | Status | Confidence | Class |
|---|---|---|---|---|---|---|
| H-01 | The decision-of-record step (case decision, closure, `batch_disposition`) has **no representation in the system**: no write path exists for it | Technology / Process | S3, S6 | **CONFIRMED (repo-level)** | High | [Verified Fact] |
| H-02 | State is a **mutable snapshot** with no history model: `cases.status` is overwritten-in-place by design, `version` never changes, no transition events | Data / Architecture | S6, S7 | **CONFIRMED (repo-level)** | High | [Verified Fact] |
| H-03 | There is **no owned definition** of "closed", "resolved", "approved" (documented conflict; decision right DR-20 and DR-23 are GAPs) | Policy / Organisation | S3, S5 | **CONFIRMED (repo-level, documentary)** | Medium | [Verified Fact] (documents) / [Inference] (effect) |
| H-04 | There is **no decider** for the speed-vs-evidence trade-off (48 h vs verifiable evidence; faster month-end vs more evidence) (DR-21 GAP) | Policy / Organisation | S3, S6 (indirect) | **CONFIRMED (repo-level, documentary)** | Medium | [Verified Fact] |
| H-05 | The approval/priority rule exists as **three unsynchronised implementations** with no single source | Technology / Policy | S3, S5, S7 | **CONFIRMED (repo-level)** | High | [Verified Fact] |
| H-06 | Every job is **manually started, capacity-capped, unscheduled and leaves no run record** (reconcile: 1,000/run vs 8,567 backlog) | Process / Technology | S4 (partly), backlog | **CONFIRMED (repo-level)** for mechanism; effect on delay **SUPPORTED** | High (mechanism) / Low (impact) | [Verified Fact] / [Inference] |
| H-07 | Intake is **destructive and content-blind**: in-place status overwrite, silent drops of invalid events, every REPLAY treated as DUPLICATE, contracts unenforced | Technology / Data | S2, S4 | **CONFIRMED (repo-level)** for mechanism; real frequency **UNKNOWN** | High / Low | [Verified Fact] |
| H-08 | There is **no shared identity or referential model** across case, batch, deviation, CAPA and feed records, so contradictory states and orphans are permitted | Data / Architecture | S2, S7 | **CONFIRMED (repo-level)** for schema; orphan rate is a generator artefact (see R-05) | High (schema) | [Verified Fact] |
| H-09 | Month-end figures are computed by **independent implementations without a shared definition** (Java `double` + silent skip; SQL join inflating sums; API counts) | Technology / Process | S5 | **CONFIRMED (repo-level)** for mechanisms; K-10 divergence is NOT evidence (R-04) | Medium-High | [Verified Fact] |
| H-10 | Evidence needed to justify closure is **not linked to the case** (no evidence reference in `cases`; where evidence lives is unknown) | Data / Process | S3, S6 | **SUPPORTED (not confirmed)** | Low-Medium | [Inference] |
| H-11 | Manual reconciliation and the "parallel workflow" depend on **undocumented tribal knowledge** (key-person risk) | People | S4 | **UNKNOWN** | Low | [Unknown] |
| H-12 | **Capacity/staffing shortfall** (headcount, skills) drives backlog and rising effort | People / Organisation | S1 | **UNKNOWN** (untestable without stakeholders) | Low | [Unknown] |
| H-13 | **Volume growth** drives rising effort | Process | S1 | **UNKNOWN**; the only repo "evidence" for it was rejected (R-01/R-10) | Low | [Unknown] |
| H-14 | **Single shared SQLite file** contention slows or blocks work | Architecture | backlog | **SUPPORTED (not confirmed)**; lock timeout is config only, not observed | Low | [Inference] |
| H-15 | **Untrusted instruction-like text** flows into decision-adjacent fields (86 feed rows, notes, lake events) | Data / Technology | none of S1-S7 | **LATENT RISK FACTOR** (presence confirmed) | High (presence) | [Verified Fact] |
| H-16 | **No authentication/authorisation/tenant control** on the API; audit holds only `read` | Technology | none of S1-S7 directly (feeds S6 if decisions were recorded) | **LATENT RISK FACTOR** | High (presence) | [Verified Fact] |

### H-B. Rejected or demoted hypotheses (preserved)

| ID | Hypothesis | Why rejected | Evidence | Stage 5/OD ref |
|---|---|---|---|---|
| R-01 | "`operating_costs` shows effort rising / cost per case is meaningful" (S1 evidence) | `n` per month is drawn independently of `cases`; labour hours are random multiples of `n`; no trend is possible | `app/generate.py` last loop; OD-07 | A-04-01 refuted |
| R-02 | "P-01 (median 12.06 h created->first review) shows slow operations response" | Mechanically bounded: `etime = created + randint(1,300) min`, review = `etime + randint(0,24) h`, max 29 h by construction | `app/generate.py`; `process-bottlenecks.md` PB-00a | OD-07 |
| R-03 | "P-03 evidence-arrival lag (median 36 h) shows late evidence" | Deterministic sawtooth `((i*3) % 72) h`; no signal | `app/enterprise_legacy.py` L43; PB-00b | OD-07 |
| R-04 | "P-04/K-09 open-case age (median 565 d) shows an ageing mechanism" and "K-10 (125 vs 108) shows month-end loss of cases" | Case dates uniform over 1,100 days, status drawn independently; K-10 compares two unrelated populations | `app/generate.py`; PB-00c; OD-07 | A-04-01, A-04-03 |
| R-05 | "8,394 of 8,567 partner feeds reference missing cases proves a real feed-matching failure" | Feeds are produced by a separate generator (default 8,500, seed 20261017) over ids that do not intersect the 125-case DB (test residue). Schema absence of FK (H-08) is real; the 98% orphan rate is not a business measurement | `app/partner_feeds.py` generator; DH-03 | OD-02 |
| R-06 | "The 2025 change of approval roles in the policy archive is an operating control" | Not read by any workflow; only `legacy_policy.js` reads limits, roles unused | `control-points.md` CP-06; `contracts/decision-policies-archive.json` | D-05/D-07 |
| R-07 | "`gateway_inbox` / `qa_disposition` events feed case or disposition changes" | Only reader of `gateway_inbox` is a `COUNT(*)` in `app/operational_report.py` | IL-03 | U-05-11 |
| R-08 | "INC-2025-014's 'queue retried twice' is explained by this repo's mechanisms" | No queue or retry code exists; the incident describes a runtime not present in the repo. Incident stays an unexplained anecdote | `integration-landscape.md` IN-03 | U-05-10 |
| R-09 | "`access_audit` containing only reads proves users never approved" | Generator indexing bug (`i%3==0` selects action index 0) | `app/enterprise_legacy.py` L50 | MH-11 |
| R-10 | "An AI/automation capability gap is a root cause" | Not a cause; a solution assumption (H6) explicitly unproven; deferred to Stage 8 | `problem-framing-canvas.md` | stage guardrail |

### H-C. Interactions (summary; detail in `root-cause-tree.md`)

H-03/H-04 (no owner) -> H-05 (nobody to choose one rule) -> S3/S5. H-01 + H-02 -> S6 (no decision, no history). H-06 + H-07 -> S4 (manual starts over destructive intake). H-08 + H-02 -> S7. H-09 amplified by H-03.

## Evidence References

See `evidence-confidence-matrix.md` for per-hypothesis evidence. Re-validation performed in this stage (read-only): grep for writers (`UPDATE cases` / `INSERT INTO cases`: only `app/generate.py:37`); no `version` increments; no scheduler tokens; `legacy_logic` importers (`app/server.py`, `app/baseline.py`, `tests/test_workflow.py`); SQL on `legacy.sqlite3` opened `mode=ro&immutable=1`; backup checksum OK afterwards.

## Assumptions

- A-06-01: Synthetic repository documents (correspondence, history notes) stand in for client statements; they can establish that a *claim* exists, not that it is true. Confirm: Engagement lead (Dinesh Naik).
- A-06-02: "CONFIRMED (repo-level)" is an acceptable gate meaning for this engagement; stronger confirmation needs a real process study. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-01 Magnitude, trend and live status of S1-S5 (carries U-03-01). U-06-02 Whether H-11/H-12/H-13 contribute at all. U-06-03 Where decisions and evidence actually live (U-05-02).

## Unresolved Issues

- Which of RP1-RP3 dominates (U-03-02) cannot be settled: dominance needs effect sizes; none exist.

## Residual Risks

- Readers may read "CONFIRMED (repo-level)" as proven business cause. Mitigation: scope statement repeated in `confirmed-root-causes.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial hypothesis register. |
