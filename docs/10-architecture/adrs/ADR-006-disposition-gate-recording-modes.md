---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-006-disposition-gate-recording-modes.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/09-initial-prd/open-product-decisions.md OPD-05, OPD-06", "docs/06-root-cause/confirmed-root-causes.md RC-1", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md HAR-12"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-006 — Human disposition gate (Zone H) with two configurable recording modes. Status: PROPOSED - depends on open OPD-05 (where disposition is recorded), OPD-06 (role holders).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED - depends on open OPD-05 (where disposition is recorded), OPD-06 (role holders). Recommended option B (support both, default blocked). Not decidable to a single mode without Dinesh.

### Traceability
FR-GATE-01..06, FR-DEC-01, FR-DEC-05; PNFR-07, PNFR-15; RC-1; DR-22; HAR-12; STOP-07; OPD-05, OPD-06, OPD-01/03.

### Context
[Verified Fact] The disposition step has no representation in the repo (RC-1; `app/generate.py:37` is the only `cases` writer; API GET-only). [Verified Fact] Whether decisions live in an external "local system" is Unknown (`business-context.md` step 4; U-05-02). [Inference] OPD-05 is the largest architectural fork (PRD open-product-decisions OD-3): the new write path is either system-of-record or a mirror of an external one.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Hub is system of record only | Disposition recorded as an event here | Strong audit; simple | Assumes the unknown; may duplicate an external authoritative record (conflict) | Risky if external system exists |
| B. Pluggable recording mode, default NONE (blocked) - RECOMMENDED | Config `disposition.mode` in {none, event, external_ref}. `event`: human action stored as an immutable decision event with actor, basis, evidence. `external_ref`: store only reference id/URI/hash/timestamp of the decision held elsewhere, entered by the authorised human. `none` (default): Zone H transitions unavailable. Role-holder list ships empty (FR-GATE-04). Services/scheduler/importer actors rejected at the gate API (FR-GATE-03). No component can pre-fill, simulate or auto-trigger (FR-GATE-01); evidence pack read-only (FR-GATE-02) | Neutral on OPD-05; human gate intact; tested in both modes | Two code paths to test; `external_ref` cannot verify the external record | Fit High; security High; lock-in none |
| C. Do not build a gate (read-only reporting only) | Leave dispositions entirely outside the product | Lowest regulatory risk | Leaves RC-1 unsolved; PRD CAP-02 Must | Fails requirement |

### Decision / recommendation
Recommend B. The "e-signature" is not implemented as a cryptographic or legal signature; the product records that an authorised human acted (or references where). Real e-signature stays outside the product (HAR-12, DR-22).

### Consequences
- Positive: architecture survives either answer to OPD-05; fresh install is safe by default.
- Negative: until OPD-05/06 are answered there is no usable Zone H in a pilot.
- Mode change is itself a Zone H policy event (FR-POL-03).

### Trigger to decide / revisit
Resolve OPD-05 and OPD-06 (Engagement lead, Dinesh Naik) before pilot use; ADR becomes ACCEPTED only by him. Stage 11 designs the schema for both modes.

## Evidence References
docs/09-initial-prd/open-product-decisions.md OPD-05, OPD-06; docs/06-root-cause/confirmed-root-causes.md RC-1; docs/00-preflight/operating-contract/provisional-human-approval-rules.md HAR-12

## Assumptions
A-10-07 Sole approver Dinesh can act as the authorised human in tests only with synthetic data.

## Unknowns
U-10-10 Existence and shape of external system of record; U-10-11 named role holders.

## Unresolved Issues
OPD-05, OPD-06.

## Residual Risks
Misuse of `event` mode as if it were a validated e-signature; mitigated by labelling and DR-29 framing.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

