---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-008-intake-pipeline.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/partner_feeds.py", "app/gateway_bridge.py", "integration/source-contract-v1.json", "services/source_gateway/server.py"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-008 — Intake pipeline: append-only raw store, content-hash idempotency, quarantine. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-INT-01..08, FR-RUN-02, FR-RUN-03, FR-REV-02, FR-CO-03; PNFR-11, PNFR-13; RC-6, RC-5, RC-7.

### Context
[Verified Fact] `app/partner_feeds.reconcile` overwrites `processing_status` in place and marks every REPLAY as DUPLICATE without content comparison; invalid gateway events are counted not stored; `integration/source-contract-v1.json` is not enforced; Java skips unparsable amounts silently (RC-6). [Verified Fact] Bridge polls the gateway over HTTP, 5 s timeout, no retry (DM-15). [Verified Fact] Planted instruction strings in feed notes (86 rows).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Patch reconcile in place | Add checks to existing function | Small diff | Edits a High-risk destructive path (heat map); keeps in-place state | Poor brownfield safety |
| B. New pipeline stages with immutable records - RECOMMENDED | receive (store raw + source + schema revision + hash, append-only) -> validate against declared contract, revisions 1.0/1.1/2.0 -> classify (rule-based reason codes) -> match via crosswalk (unique/none/ambiguous) -> outcome record (separate table). Same hash = no-op; different content under same key = quarantine for human. Text fields typed Untrusted. Reads gateway/legacy feeds through adapters | Replay-safe; lossless; testable with replay fixtures; reason codes deterministic | More tables; backfill of legacy rows needed | Fit High; resilience High |
| C. Message broker / stream processor | Kafka-like pipeline | Scales | No scale evidence; HAR-05/08; cost | Over-built |

### Decision / recommendation
Recommend B. Contract validation uses a small stdlib validator driven by `source-contract-v1.json` (no jsonschema dependency unless HAR-08 approved).

### Consequences
- Positive: PNFR-11 targets (0 duplicate effects, 0 silent overwrites, raw count = received count) are checkable.
- Negative: quarantine queue needs human capacity (volume Unknown).

### Trigger to decide / revisit
Decide at Stage 11/12.

## Evidence References
app/partner_feeds.py; app/gateway_bridge.py; integration/source-contract-v1.json; services/source_gateway/server.py

## Assumptions
A-10-09 Fixed-key synthetic feeds represent real structure (A-09-05).

## Unknowns
U-10-13 Real revision/correction frequency.

## Unresolved Issues
None blocking.

## Residual Risks
Contract file incomplete vs real feeds.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

