---
stage: "6 — Root-Cause Analysis"
artifact: "fishbone-analysis.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/06-root-cause/causal-hypotheses.md", "docs/06-root-cause/evidence-confidence-matrix.md", "docs/05-current-state/dependency-hotspots.md", "docs/05-current-state/control-points.md", "docs/05-current-state/manual-handoffs.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary

Fishbone (Ishikawa) for the effect **"Case handling cannot be shown to be consistent, attributable and measurable (S3, S5, S6, S7) and external-feed reconciliation depends on manual effort (S2, S4)"**. Seven categories required by the stage prompt: process, people, policy, data, technology, organisation, architecture. Every bone is tagged with hypothesis ID, class and whether it is a **root** (RC), a **contributor**, a **latent risk**, or **Unknown/empty**. Empty or thin categories are reported as such: the People category has no verified content.

## Findings

```
 PROCESS                    PEOPLE                      POLICY
  |- decision step not        |- (no verified cause)      |- closed/resolved/approved
  |  in system (RC-1)         |- tribal knowledge          |  undefined (RC-3)
  |- manual-start jobs,       |  H-11 [Unknown]           |- speed vs evidence: no decider
  |  1,000-row cap (RC-5)     |- capacity H-12 [Unknown]  |  (RC-3)
  |- month-end done 3 ways    |- skills/training: no      |- approval roles changed 2025
  |  (RC-8)                   |  evidence at all          |  but unenforced (R-06)
  |- ad hoc manual recon      |                           |- retention not acted on (CG-11,
  |  (MH-02) [claim]          |                           |  latent)
  \_______________________    |                           |
                          \   |                           |
                           ===+===========================+=====> EFFECT
                          /   |                           |
  /-----------------------    |                           |
  DATA                       TECHNOLOGY                   ORGANISATION / ARCHITECTURE
  |- state snapshot, no       |- no scheduler (RC-5)      |- ORG: 10 decision rights unowned
  |  history (RC-2)           |- in-place overwrite,      |  (DR-20..28,30,31) (RC-3)
  |- no shared key across     |  silent drops (RC-6)      |- ORG: no owner/SLA for any
  |  case/batch/dev/CAPA      |- three rule copies (RC-4) |  handoff (MH-01..13)
  |  (RC-7)                   |- Java float + silent skip |- ARCH: shared SQLite as
  |- instruction-like text    |  (RC-8)                   |  integration bus (DH-01) [H-14]
  |  in data (H-15, latent)   |- no authN/Z (H-16 latent) |- ARCH: hard-coded data paths
  |- status vocab x5 (RC-3/7) |- unenforced contracts     |  (DH-02) [contributor to
                              |  (RC-6)                   |  engineering risk, not symptom]
```

### FB-A. Bone register

| Category | Bone | Hyp / RC | Role | Class | Confidence |
|---|---|---|---|---|---|
| Process | Decision-of-record not in system | H-01 / RC-1 | Root | [Verified Fact] | High |
| Process | Manual-start, 1,000-row cap, no run record | H-06 / RC-5 | Root | [Verified Fact] | High (mechanism) |
| Process | Month-end by three methods | H-09 / RC-8 | Root | [Verified Fact] | Medium-High |
| Process | Manual spreadsheet reconciliation practice | MH-02 | Contributor (claim) | [Unknown] frequency | Low |
| People | Tribal knowledge / key person | H-11 | Candidate | [Unknown] | Low |
| People | Capacity / headcount | H-12 | Candidate | [Unknown] | Low |
| People | Skills, training, incentives | - | **No evidence in repo** | [Unknown] | n/a |
| Policy | No owned definition of closed/resolved/approved | H-03 / RC-3 | Root | [Verified Fact] (documentary) | Medium |
| Policy | No decider for speed vs evidence | H-04 / RC-3 | Root | [Verified Fact] (documentary) | Medium |
| Policy | Policy archive roles not enforced | R-06 | Rejected as control; contributes to RC-4 | [Verified Fact] | High |
| Policy | Retention/legal hold not acted on | CG-11 | Latent risk | [Verified Fact] | Medium |
| Data | Mutable snapshot, no history | H-02 / RC-2 | Root | [Verified Fact] | High |
| Data | No shared identity / referential model | H-08 / RC-7 | Root | [Verified Fact] | High |
| Data | Closure evidence not linked | H-10 | Contributor (supported) | [Inference] | Low-Medium |
| Data | Instruction-like text in data | H-15 | Latent risk | [Verified Fact] | High (presence) |
| Technology | Destructive, content-blind intake | H-07 / RC-6 | Root | [Verified Fact] | High (mechanism) |
| Technology | Three rule implementations | H-05 / RC-4 | Root | [Verified Fact] | High |
| Technology | No authN/Z; reads-only audit | H-16 | Latent risk | [Verified Fact] | High (presence) |
| Organisation | 10 business-domain decision rights unowned (DR-20..28, 30, 31) | H-03/H-04 / RC-3 | Root | [Verified Fact] | Medium |
| Organisation | No owner/SLA/queue on any handoff | MH-01..13 | Contributor to RC-3, RC-5 | [Verified Fact] | High |
| Organisation | Engagement self-approval | CG-12 | Out of product scope; programme risk | [Verified Fact] | High |
| Architecture | Shared SQLite as integration bus; DDL on read routes | H-14 / DH-01 | Contributor (unconfirmed) | [Inference] | Low |
| Architecture | Hard-coded repo-relative data paths | DH-02 | Engineering risk; not a symptom cause | [Verified Fact] | High |
| Architecture | Generator as only data origin | DH-03 | **Limits the analysis itself**, not a cause | [Verified Fact] | High |

### FB-B. Category coverage honesty check

| Category | Verified content? | Note |
|---|---|---|
| Process | Yes (3 roots) | Code-level only; practice Unknown |
| People | **No** | All entries Unknown; cannot be filled from a repository |
| Policy | Yes (documentary) | One synthetic correspondence document is the principal source |
| Data | Yes | Several counts generator-shaped; used for absence of constraints only |
| Technology | Yes | Strongest category |
| Organisation | Partly | Via Stage 2 decision-rights map (a Stage 2 inference from the same corpus) |
| Architecture | Partly | Contributor-level; no performance evidence |

## Evidence References

`dependency-hotspots.md` DH-01..DH-10; `control-points.md` CG-01..CG-12; `manual-handoffs.md` MH-01..MH-13; `decision-rights-map.md` L40-44, L67.

## Assumptions

- A-06-07: The seven-category frame is sufficient; categories such as "environment/measurement" are folded into Data and Architecture. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-06-12 Any People-category cause. U-06-13 Whether Organisation-level decision gaps are real or artefacts of the synthetic corpus.

## Unresolved Issues

- People category is empty of evidence; the stage cannot complete it without interviews (none available).

## Residual Risks

- A technology-heavy diagram may bias later stages toward technology fixes for what are (RC-3) decisions.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial fishbone. |
