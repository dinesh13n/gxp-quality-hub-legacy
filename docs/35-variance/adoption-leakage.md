---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "adoption-leakage.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/34-measure-after/adoption-metrics.md", "docs/34-measure-after/human-override-metrics.md", "docs/37-operating-model/raci.md", "docs/37-operating-model/target-operating-model.md", "docs/37-operating-model/support-model.md", ".fde/orchestrator-decisions.md (OD-19, OD-26, OD-31, OD-33, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Adoption leakage: value that cannot flow because people, roles and switches that adoption depends on do not exist. **K-21 = 0 of 125 (0 %) on the only basis that exists (repo state plus the engagement-lead instruction that the hub is not in production).** The funnel below shows where each step stops, using repository facts only.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AL-1 Adoption funnel [Verified Fact unless marked]
| Step | Needed for value | State | Source |
|---|---|---|---|
| 1 Hub store exists in a real environment | A place to work | No hub store in the working tree `data/`; only sandbox stores | AD-1 |
| 2 Human principals exist | Someone to act | 0 principals, 0 sessions | AD-1 |
| 3 Zone H holders named | Gated actions possible | EMPTY (OD-31) | OD-31 |
| 4 Rule set activated | Routing/assistance | None active (3 candidate sets inactive) | OD-16 |
| 5 Scheduler / authority switch | Hub-driven runs and authoritative state | OFF / ships off | OD-19, OD-26 |
| 6 Owners accepted | Support and accountability | 0 of 28 assets; all roles but Dinesh VACANT | OD-34 |
| 7 Training / rollout / support | Use | none exist; Stage 38+ items | AD-2 |
| 8 Cutover decision | Production | Stage 30 not run | Stage 34 |
Result: the funnel stops at step 1. [Inference] Any realistic adoption number in the near term is 0 or a controlled pilot (AD-4).

### AL-2 Leakage findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| ADL-1 | [Verified Fact] Adoption is 0 of 125 in every site (BR-SP 25, DE-BY 30, GB-ENG 25, IN-BLR 13, JP-KN 16, US-TX 16) | AD-1 | No users, so the entire people-time driver (VD-01/02/04) is at nil realisation | High | High | D-34-01 |
| ADL-2 | [Verified Fact] Overrides: none occurred, so the override KPI (not defined, D-34-06) cannot show leakage from rejected or overridden hub output | `human-override-metrics.md` | Override leakage Unknown, not zero | Medium | High | D-34-06 |
| ADL-3 | [Verified Fact] K-09U 1.0000 (8,335 of 8,335 open) in the sandbox reflects that no reviewer acted | Stage 34 K-09U row | A full open queue is the expected state before adoption; it must not be read as poor performance, nor later as a baseline | Medium | High | none |
| ADL-4 | [Inference] The first adopters will be the one engagement lead; the single-approver design (OD-30) plus vacant roles means adoption depends on one person's time. Reasoning: only human principal in the repo is Dinesh | OD-04, OD-34 | Bottleneck; leakage through waiting | High | Medium | Second reviewer / role holders |
| ADL-5 | [Verified Fact] Coexistence parity (125 of 125, 0 mismatches) shows the hub can mirror legacy; it does not show anyone will move work to it | AD-3 | Parity may be mistaken for readiness | Medium | High | Parallel-run plan |
| ADL-6 | [Verified Fact] Unwired resilience and uninstalled CI mean an early pilot would run without the designed protections | OD-34, OD-35 | Pilot failure would depress later adoption | Medium | High | VL-04, VL-05 decisions |

### AL-3 Measurements needed once adoption starts (from Stage 34 AD-2; not measured here)
Active users per week by role; share of new cases created or reviewed through the hub (K-21 numerator); share of exceptions worked in the hub queue vs legacy; parallel-run coverage; time-to-first-use, training, support tickets.

## Evidence References
`docs/34-measure-after/adoption-metrics.md` AD-1..AD-4; `human-override-metrics.md`; `docs/37-operating-model/raci.md`, `target-operating-model.md`; OD-16, OD-19, OD-26, OD-30, OD-31, OD-34, OD-35.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-08 Who the intended users are by role and site (no stakeholders exist in the repo beyond Dinesh; none invented here).
- U-35-09 Pilot scope and window.

## Unresolved Issues
- Pilot definition, Zone H holders and role holders are decisions for Dinesh; none is taken here.

## Residual Risks
- RR-35-09 Adoption treated as a technical problem when it is an ownership and people problem. RR-35-10 Sandbox queue state quoted as production performance.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
