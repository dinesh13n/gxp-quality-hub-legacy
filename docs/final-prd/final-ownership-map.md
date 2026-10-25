---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-ownership-map.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/37-operating-model/service-ownership-map.md", "docs/37-operating-model/target-operating-model.md", "docs/37-operating-model/raci.md", "docs/38-handover/", "docs/41-retirement/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
Ownership is designed but unstaffed: one interim human owner, 13 of 14 roles vacant or interim, no accepted steady-state owner for any of the 28 assets, no receiving team.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OW-1 Position [Verified Fact]
Dinesh Naik is the **only human** on the engagement (OD-04) and the owner of record for everything. **0 of 28 production-relevant assets (PA-01..PA-28) has an accepted steady-state owner.** 25 have Dinesh as INTERIM owner of record, 1 is N/A (PA-28, No-AI), 2 are VACANT with no owner at all (PA-25 nightly file exchange, 'transferred 2024', unnamed; PA-26 parallel workflow CO-WF-01, OPD-15). A further 6 INTERIM assets (PA-02, 04, 05, 11, 12, 20) also depend on a vacant client-side role. 17 of 24 RACI activities have a VACANT Accountable. No receiving team exists (HO-01).

### OW-2 Roles
| Role | Holder | State |
|---|---|---|
| RL-01 Engagement owner / owner of record | Dinesh Naik | INTERIM (steady-state acceptance Unknown) |
| RL-02 Service owner | none | VACANT |
| RL-03 Product/process owner (definitions, policy content) | none | VACANT |
| RL-04 Authorised dispositioner / Zone H holder | none | VACANT; `zone_h.holders` empty |
| RL-05 Risk and security owner | none | VACANT |
| RL-06 Compliance/quality oversight | none | VACANT |
| RL-07 Data owner(s) | none | VACANT |
| RL-08 Integration/source-contract owner | none | VACANT |
| RL-09 Finance/FinOps (cost) owner | none | VACANT |
| RL-10 Legacy technical owner | none (unnamed) | VACANT |
| RL-11 Reviewers (end users) | none | VACANT |
| RL-12 Toolchain owner | Dinesh holds the accounts in effect | INTERIM |
| RL-13 Independent verifier | none | VACANT; single approver accepted as a general risk (OD-30), not as a Stage 37 acceptance |
| RL-14 Build / stage / orchestrator agents | `claude-fde-agent` | execution only; not owners, no approval rights |

### OW-3 Decision rights [Verified Fact]
Only Dinesh may: accept risks, approve behaviour deviations, name Zone H holders, approve release/cutover/rollback, accept handover, sign benefits, adopt definitions and policies, install CI under `.github` (HAR-07). Agents execute within a stage and record assumptions; OD-32 default authority covers scope/sequencing only. Who runs orchestrator duties (stage method, full regression, merges) after Stage 38 is undecided (HO-04, D-39-06, SB-32).

### OW-4 Toolchain ownership [Verified Fact / Unknown]
Local clones and a private GitHub repo `dinesh13n/gxp-quality-hub-legacy` (OD-05, corrected OD-31; remote tracking `origin/main` observed). [Unknown] Remote branch-protection state and 2FA (D-39-07, VA-02); durable home for the git-ignored baseline and the cloud workspace provider (HO-13, PA-18).

### OW-5 Handover state [Verified Fact]
Stage 38 BLOCKED: no receiver (HO-01), 0 of 10 operator exercises (HO-02), acceptance sign-off OPEN and blank (HO-03). Exercise gaps OX-G1..OX-G6 (no install script, no read-only verify, observe not wired, kill switch for a live server, no off-device exercise, Python 3.12+ untested).

### OW-6 Retirement ownership [Verified Fact]
Stage 41 BLOCKED: nothing eligible; legal-hold check INCOMPLETE (hold-all); no QA/legal owner exists; D-41-01..16 open. Legacy stays authoritative.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-16 [Assumption] No ownership change occurred after Stage 37/38 (nothing in the OD log says so).

## Unknowns
- U-43-18 Whether any real person would accept a role.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
