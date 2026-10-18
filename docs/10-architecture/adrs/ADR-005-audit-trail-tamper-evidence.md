---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-005-audit-trail-tamper-evidence.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/09-initial-prd/nfrs.md PNFR-09", "docs/09-initial-prd/functional-requirements.md FR-SEC-02"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-005 — Tamper-evident audit trail (hash chain in application layer). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-SEC-02, FR-DEC-01, FR-POL-03, FR-GATE-03; PNFR-09; RC-1, RC-2; framing only, not 21 CFR Part 11 certification (DR-29).

### Context
[Verified Fact] No audit trail, no logging exist in shipped code (Stage 0A; PNFR-09 gap). [Verified Fact] Libraries: none; Python stdlib has `hashlib`, `hmac`. [Inference] Insert-only triggers (ADR-004) do not detect offline edits of the file; a hash chain does.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Triggers only | Immutability via SQL triggers | Simple | Offline file edit undetected | Poor tamper evidence |
| B. Hash chain over audit records - RECOMMENDED | Each audit/decision record stores SHA-256 of canonical record plus previous hash; periodic anchor (head hash) exported to a separate location and recorded in run records; `verify-audit` command recomputes; tamper test is a release gate | Detects edits, deletes, reorders; stdlib only; deterministic | Head hash must be anchored outside the DB to be meaningful; key management only if HMAC added | Fit High; lock-in none; cost minimal |
| C. External WORM / ledger service | Cloud immutable storage | Strong guarantees | Vendor lock-in without evidence; no environment; HAR-09 egress | Deferred |

### Decision / recommendation
Recommend B. Anchor location is a configuration (initially a file outside the DB directory); where the anchor lives for a real deployment is Unknown.

### Consequences
- Positive: PNFR-09 verification (deliberate tamper detected) is testable.
- Negative: any schema change touching audited tables must preserve canonicalisation.

### Trigger to decide / revisit
Decide at Stage 11/24; revisit if a regulated deployment demands external WORM.

## Evidence References
docs/09-initial-prd/nfrs.md PNFR-09; docs/09-initial-prd/functional-requirements.md FR-SEC-02

## Assumptions
A-10-06 Framing-only compliance acceptable (A-08 / DR-29).

## Unknowns
U-10-09 Anchor location and audit retention.

## Unresolved Issues
Retention OPD-09.

## Residual Risks
A compromised host can rewrite chain and anchor together.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

