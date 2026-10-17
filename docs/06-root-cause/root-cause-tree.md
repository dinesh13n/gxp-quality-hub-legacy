---
stage: "6 — Root-Cause Analysis"
artifact: "root-cause-tree.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/causal-hypotheses.md", "docs/06-root-cause/evidence-confidence-matrix.md", "docs/03-problem-value/problem-framing-canvas.md", "docs/05-current-state/control-points.md", "docs/05-current-state/business-workflow-map.md", "docs/05-current-state/integration-landscape.md", "docs/05-current-state/process-bottlenecks.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary

Causal tree from the seven symptoms (S1-S7) through proximate and intermediate causes to **eight structural root causes (RC-1..RC-8)**. Nodes carry the hypothesis ID and the evidence class. Branches that end in "Unknown" are shown as such, not completed by imagination. Reading rule: an arrow means "mechanically produces or permits" and is justified in `evidence-confidence-matrix.md`; it never means "has been measured to cause delay or cost".

Root causes (a node is a root when asking "why" again leaves the repository or the organisation's decisions):

| RC | Root cause | Hyp | Type |
|---|---|---|---|
| RC-1 | Decision-of-record has no system representation | H-01 | Technology/Process |
| RC-2 | State model is a mutable snapshot without history | H-02 | Data/Architecture |
| RC-3 | No owned definitions and no decider (closed/resolved/approved; speed vs evidence) | H-03, H-04 | Policy/Organisation |
| RC-4 | Approval/priority logic duplicated with no single source | H-05 | Technology/Policy |
| RC-5 | Manual-start, capped, unscheduled, unrecorded batch execution | H-06 | Process/Technology |
| RC-6 | Intake is destructive and content-blind; contracts unenforced | H-07 | Technology/Data |
| RC-7 | No shared identity or referential model across case/batch/deviation/CAPA/feed | H-08 | Data/Architecture |
| RC-8 | Month-end figures computed independently without shared definition | H-09 | Technology/Process |

## Findings

### RT-A. Tree (text form)

```
S3 "Closed" means different things at different sites   [claim, documented]
 |- proximate: five status vocabularies; no cross-reference                      [Verified Fact]
 |    '- RC-7  No shared identity/referential model (H-08)                       <ROOT>
 |- proximate: nobody defines/owns "closed"                                      [Verified Fact: DR-20 GAP]
 |    '- RC-3  No owned definition, no decider (H-03/H-04)                       <ROOT>
 |- proximate: the closing decision is not captured anywhere in the system       [Verified Fact]
 |    '- RC-1  Decision-of-record not represented (H-01)                         <ROOT>
 '- unknown: how sites actually differ in practice                               [Unknown U-05-02]

S5 Finance and operations monthly figures disagree
 |- proximate: Java sums skip blank/non-numeric rows silently; SQL sum inflated 
 |    +19.3% by LEFT JOIN on events (re-executed read-only); API counts          [Verified Fact]
 |    '- RC-8  Independent computations, no shared definition (H-09)             <ROOT>
 |         '- interacts with RC-3 (no agreed definition to compute to)
 |- proximate: cut-off rules differ between finance and operations               [documented claim]
 |    '- RC-3                                                                    <ROOT>
 '- NOT evidence: K-10 divergence (unrelated populations; OD-07)                 [Rejected R-04]

S4 Replay inflated exception queue (2025); delayed feed forced manual reconciliation
 |- proximate: REPLAY rows classed DUPLICATE without content comparison;
 |    status overwritten in place; invalid events dropped                        [Verified Fact]
 |    '- RC-6  Destructive, content-blind intake (H-07)                          <ROOT>
 |- proximate: reconcile only runs when a human starts it, 1,000 rows/run        [Verified Fact]
 |    '- RC-5  Manual, capped, unscheduled execution (H-06)                      <ROOT>
 |- proximate: totals diverge so a spreadsheet is used                           [documented, MH-02]
 |    '- RC-8 + RC-7                                                             <ROOT>
 '- unknown: whether the 2025/INC-2025-014 mechanisms map to this code           [Rejected R-08 / Unknown]

S2 Feed rows inconsistent with core records
 |- proximate: no FK / key linking partner_feeds.ref_id to cases                 [Verified Fact]
 |    '- RC-7                                                                    <ROOT>
 |- proximate: contract/schema revisions not validated (224 'unsupported' rows)  [Verified Fact]
 |    '- RC-6                                                                    <ROOT>
 '- NOT evidence: 98% orphan rate itself (generator/test residue)                [Rejected R-05]

S6 Decisions/closures cannot be attributed or reconstructed
 |- proximate: no actor/decision/rule-version recorded                           [Verified Fact: CG-01, CG-10]
 |    '- RC-1                                                                    <ROOT>
 |- proximate: status overwritten, version never changes, no reopen/close event  [Verified Fact: CG-02]
 |    '- RC-2  Mutable snapshot state model (H-02)                               <ROOT>
 |- contributing: no authentication, reads-only audit                            [Latent H-16, not a cause here]
 '- contributing (Inference): closure evidence not linked to case (H-10)         [SUPPORTED, not confirmed]

S7 Contradictory closure states are possible
 |- proximate: no constraint across cases/batches/deviations/CAPA/lab results    [Verified Fact: CG-04]
 |    '- RC-7                                                                    <ROOT>
 |- proximate: no history to detect when states diverged                         
 |    '- RC-2                                                                    <ROOT>
 '- proximate: each domain table has its own state vocabulary                     
      '- RC-3 + RC-4 (no owned lifecycle definition)                              <ROOT>

S1 Rising exception-handling effort   [claim; trend UNMEASURABLE]
 |- candidate: volume growth (H-13)       UNKNOWN
 |- candidate: capacity shortfall (H-12)  UNKNOWN
 |- candidate: tribal-knowledge manual work (H-11) UNKNOWN
 |- candidate: duplicated manual reconciliation caused by RC-5/RC-6/RC-8       [SUPPORTED, Inference]
 '- operating_costs evidence REJECTED (R-01)
```

### RT-B. Interaction map between causes

| From | To | Interaction | Basis |
|---|---|---|---|
| RC-3 (no owner/definition) | RC-4 (three rule copies) | No owner means nobody can designate an authoritative rule, so copies were never merged | DR-23 GAP; JS banner "do not consistently agree with server policy" [Inference] |
| RC-3 | RC-8 | No agreed definition of "resolved"/cut-off, so each computation chooses its own | `legacy-operations-history.md` [Inference] |
| RC-1 | RC-2 | Without a decision write path there is nothing to version; conversely a snapshot model offers no place to attach a decision | schema + grep [Inference] |
| RC-2 | RC-7 | Without history, cross-record contradictions cannot be detected after the fact | CG-04 [Inference] |
| RC-5 | RC-6 | Manual cadence + destructive overwrite: a skipped or delayed run leaves the overwritten state as the only record | `partner_feeds.py` [Inference] |
| RC-6 | RC-8 | Silently skipped/overwritten input changes totals that are later computed independently | Java catch; reconcile overwrite [Inference] |
| RC-7 | RC-8 | No shared key makes joins ad hoc (the SQL inflation arises from a join without a controlling key) | `legacy_reports.sql` [Verified Fact] for the join, [Inference] for the link |

**Cluster view [Inference]:** governance cluster (RC-3, RC-4), record-model cluster (RC-1, RC-2, RC-7), execution cluster (RC-5, RC-6, RC-8). The governance cluster cannot be cured by engineering (stage 3 CG-7): RC-3 is a decision, not a defect.

### RT-C. What the tree does not show

- No branch explains **why effort is rising** (S1): the trend itself is unmeasurable.
- No people/skills branch beyond Unknowns (H-11, H-12).
- Latent risks H-15 (instruction-like text in data) and H-16 (no authN/Z) are not roots of S1-S7; recorded in `root-cause-readiness.md` as risks for later stages.

## Evidence References

`causal-hypotheses.md`; `evidence-confidence-matrix.md`; Stage 5 `control-points.md` CG-01..CG-10; `business-workflow-map.md` BW-A..BW-C; `integration-landscape.md` IL-01..IL-07; `docs/02-stakeholders/decision-rights-map.md` DR-20..DR-24; `sql/legacy_reports.sql` (re-executed read-only).

## Assumptions

- A-06-05: Treating a "why" chain as terminated when the next why leaves the repo/organisation decision space is an acceptable stopping rule. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-07 Whether sites differ in practice (S3). U-06-08 Whether finance consumes the SQL month-end report (S5).

## Unresolved Issues

- The tree is a single-evidence-source model; every node is conditional on the synthetic corpus being representative (A-03-01).

## Residual Risks

- A cause omitted because it is invisible in code (e.g. training, incentives, staffing) is structurally under-represented.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial tree. |
