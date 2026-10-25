---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "adjacent-use-case-inventory.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/scope-exclusions.md", "docs/03-problem-value/value-hypothesis.md", "docs/archived-enterprise-interfaces.md", "docs/partner-feed-operations.md", "docs/business-context.md", "domain.json", "domain-profile.json", "docs/24-security-privacy/", "docs/08-ai-qualification/", "docs/37-operating-model/target-operating-model.md", "docs/36-roi/roi-model.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-28, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL. No value claim (Stage 36: ROI NOT COMPUTABLE), no cutover scheduled, no risk accepted for Dinesh Naik.**

## Summary
**No adjacent use case is named by any stakeholder or sponsor in the repository** (no client sponsor exists, OD-04). The seven entries below are *candidates derived from the repository's own boundaries* (exclusions, open scope questions, stated future surfaces). Each is a hypothesis for Dinesh to confirm, edit or strike; none is a requirement, a commitment or a validated opportunity. **Value is Unknown for every candidate**: Stage 3 never quantified a benefit, 0 verified benefits exist, and ROI is NOT COMPUTABLE. The only value this inventory ranks is *evidence value* (how much a candidate would help fill the empty slots I-01..I-14 in `docs/36-roi/roi-model.md`), which is an Inference, not a business value.

## Findings
| ID | Candidate (hypothesis) | Basis in repo [Verified Fact] | What is common with the first use case [Inference] | What is new / different | Value | Dependencies | Tag |
|---|---|---|---|---|---|---|---|
| AU-01 | The same workflow at more sites or regions | Baseline already spans six sites (BR-SP, DE-BY, GB-ENG, IN-BLR, JP-KN, US-TX; K-09-OPS split); "multi-region" and other sites Unknown (U-03-08) | Everything: same hub, same rules, same intake | Local rule owners, local reviewers, local regulatory regime (Unknown), site-level data classes | Evidence value: High (widens the K-21 population). Business value: Unknown | Pilot on one unit first (G2); role holders; field classes / tenant decisions (DQ-S24) | Inference |
| AU-02 | Additional partner feeds / sources on the same workflow | 13 outputs and their consumers inventoried; outside consumers Unknown (OD-28); `partner-feed-operations.md`; source-contract-v1 `record_only` | Intake, natural key, crosswalk, contract record | New source behaviour (Unknown, U-28-01), new schema versions, late-delivery handling | Evidence value: Medium. Business value: Unknown | Per-source contracts (SB-22); resilience wiring (D-28-01); real source owner (RL-08 VACANT) | Inference |
| AU-03 | Finance / month-end read surface | Finance partner SH-05 unfilled; no finance read surface built (OD-32, DQ-S24); K-10 compares unrelated populations (OD-07); I-09, I-10 need finance input | Metrics framework, access rules | New data class (finance), new owner (RL-09 VACANT), new definition of month-end close | Evidence value: High for I-09/I-10 (the largest empty value slots). Business value: Unknown | Field classes decided before real data; finance owner exists; Stage 4 v0.2 addendum (PC-6) | Inference |
| AU-04 | Archived enterprise estate and lake as an additional data source | Excluded as separate data models (EX-06; DF-09, DF-10); `docs/archived-enterprise-interfaces.md` | Read-only adapter pattern (PT-01) | A different data model; no join defined; ownership of the archive Unknown | Evidence value: Low-Medium. Business value: Unknown | A scoping decision (EX-06 reversal); legacy technical owner (RL-10 VACANT, 'owner transferred 2024' unnamed) | Inference |
| AU-05 | The parallel workflow kept for older customers | Out of scope, owner unknown (EX-04, SC-07) | Possibly the decision record | Entirely unknown process and customers | Unknown | Owner identified; Stage 5-style discovery would be needed first | Unknown |
| AU-06 | Another regulated-quality regime or tenant | DQ-S24: tenant and regime to be decided before real data; Part 11 framed only, no 'compliant' claim (OD-30, GD-11) | Governance pattern, audit | Different regime, retention, access, validation expectations | Unknown | Regime decision; compliance oversight (RL-06 VACANT); retention rule | Unknown |
| AU-07 | AI-assisted document Q&A for reviewers (T3) | OD-08 'Accept No-AI'; T3 may be re-qualified only via RQ-1..RQ-3 and a new Dinesh decision | Reviewer surfaces | Introduces a model, tokens, vendor and prompt risk; breaks INV-01 / INV-02 and the No-AI guard | Unknown; Stage 32 token cost model would be needed | A new Dinesh decision, HAR-08/09/10 approvals (OB-10); Stage 8 re-qualification | Assumption (listed for completeness) |

**Excluded from the roadmap timeline:** AU-05, AU-06 and AU-07 (no sufficient evidence to assess readiness; AU-07 contradicts an approved decision unless Dinesh reopens it). They are kept so the exclusion is visible.

**Not listed:** any application, channel or use case that nothing in this repository refers to. Adding one needs a sponsor or Dinesh's instruction, not inference.

## Evidence References
`docs/03-problem-value/scope-exclusions.md` (EX-04, EX-06; U-03-08); `docs/partner-feed-operations.md`; `docs/archived-enterprise-interfaces.md`; `docs/36-roi/roi-model.md` RM-2; `.fde/orchestrator-decisions.md` OD-08, OD-28, OD-32.

## Assumptions
- A-40-05 [Assumption] Candidates AU-01..AU-04 are the plausible "next units" by repository evidence alone. Confirm or replace: Engagement lead (Dinesh Naik).
- A-40-06 [Assumption] "Evidence value" is a valid proxy for ranking when business value is Unknown. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-07 Which adjacent use cases (if any) a real sponsor would want. Resolution: a sponsor or Dinesh names them; until then this list is agent-derived.
- U-40-08 Volume, users, owners and regime for every candidate.

## Unresolved Issues
- No sponsor, so no demand signal for any candidate.

## Residual Risks
- Treating a derived candidate as a requested one (SR-03).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
