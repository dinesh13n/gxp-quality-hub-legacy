---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-007-policy-and-rule-service.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/legacy_logic.py", "legacy_js/legacy_policy.js", "docs/09-initial-prd/functional-requirements.md FR-POL-*"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-007 — Versioned policy objects and one table-driven rule service (no adopted defaults). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B). Content of policies depends on open OPD-01..04.

### Traceability
FR-POL-01..06, FR-DEC-05, FR-DEC-06, FR-MET-01..03, FR-REV-01, FR-GATE-06; RC-3, RC-4; OPD-01, OPD-02, OPD-03, OPD-04, OPD-07.

### Context
[Verified Fact] DR-20..DR-23 are GAPs (decision-rights-map); closed/resolved/approved and the 48 h clock have no owner (RC-3). [Verified Fact] Three divergent rule implementations (RC-4). [Verified Fact] `app/legacy_logic.priority()` is five lines; JS reads `contracts/decision-policies-archive.json` relative to cwd (DM-13/18). [Inference] Shipping any default would silently encode a party's rule (FF-3 interpretation).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Pick one rule/definition and hard-code | Choose python >50,000 as truth | Simple | Invents an answer to OPD-04; HAR-06 breach | Rejected by guardrail |
| B. Policy objects + rule tables as data - RECOMMENDED | Tables `policy_object` (kind, version, owner, effective date, status in candidate/adopted/accepted-open), `rule_set` / `rule_row`. Three as-found sets loaded as named, read-only candidates. Evaluation is a pure function (inputs + rule set version -> outcome + rule trace + `defaulted` marker). Adoption/changes are Zone H and emit events. Active-set selection per policy. No adopted value ships | Neutral; deterministic (PNFR-17); trace for FR-REV-01; divergence report possible | Admin surface needed; risk of config sprawl | Fit High; lock-in none; brownfield High |
| C. External rules engine (Drools etc.) | Adopt a rules product | Rich features | New runtime/JVM, HAR-08, not needed for ~3 small tables, lock-in | Over-built |

### Decision / recommendation
Recommend B. FR-DEC-05 default check is structural presence of an evidence reference (A-09-03); sufficiency is policy (OPD-07). Time-to-close computed from separately stored facts (FR-DEC-06) under every configured clock.

### Consequences
- Positive: RC-3 and RC-4 become visible and parameterised, not "solved".
- Negative: until OPD-01..04 are answered, KPI targets and pass/fail verdicts cannot be produced (accepted open).

### Trigger to decide / revisit
Resolve OPD-01..04 before Stage 13 adoption; architecture does not wait.

## Evidence References
app/legacy_logic.py; legacy_js/legacy_policy.js; docs/09-initial-prd/functional-requirements.md FR-POL-*

## Assumptions
A-10-08 Test policies in fixtures are explicitly synthetic and never "adopted".

## Unknowns
U-10-12 OPD-01..04 outcomes.

## Unresolved Issues
OPD-01..04.

## Residual Risks
Reviewers may read a candidate as adopted; mitigated by status labels on every output.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

