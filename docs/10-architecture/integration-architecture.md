---
stage: "10 — Target Architecture + ADRs"
artifact: "integration-architecture.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "integration/source-contract-v1.json", "integration/source-gateway.json", "app/gateway_bridge.py", "services/source_gateway/server.py"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Integration is pull-based and read-only toward legacy; no real external systems exist (OD-04). Each integration point is mapped to a pattern, a contract and an unknown.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IA-1 Integration points
| ID | Point | Direction | Pattern | Contract / evidence | Notes |
|---|---|---|---|---|---|
| I1 | Source gateway (`services/source_gateway/server.py`, default 127.0.0.1:8090) | in | Adapter polls over HTTP; checkpointed; timeouts and bounded retry added in adapter | `integration/source-contract-v1.json`, schema revs 1.0/1.1/2.0 | [Verified Fact] today `urlopen` 5 s, no retry (DM-15); URL scheme must be allow-listed to http(s) loopback |
| I2 | Partner feeds CSV / `partner_feeds` table | in | Raw append-only + validate + classify | `domain-profile.json`; Java reads positional columns (DM-17) | content hash for idempotency |
| I3 | Legacy case DB `data/legacy.sqlite3` | in | Read-only adapter (`mode=ro&immutable=1` for fixtures) | `app/store.py` schema | never write; copy for tests |
| I4 | Enterprise/historic stores (`enterprise_legacy`, `historical_*`) | in | Read-only adapter | schemas in `docs/data-dictionary.md` | no shared keys (RC-7) |
| I5 | Document corpus (1,200 source + 420 archive) | in | Indexer for FTS (R2) | `docs/` + `data/` | bodies are Untrusted |
| I6 | Legacy rule implementations (py/js/batch) | in (as data) | Extract thresholds into named rule sets; compare to goldens | CT-01..03, CT-13 | not executed by the product |
| I7 | Month-end SQL/Java | side | Comparators in harness only | CT-11, CT-12 | not called by product |
| I8 | Disposition system of record | out/ref | `external_ref` mode: store reference only; no API calls | none: Unknown | OPD-05 |
| I9 | Identity provider | in | Authenticator interface | none exists | ADR-013 |
| I10 | Scheduler | trigger | OS-level job invoking CLI | none | OPD-11 |

### IA-2 Rules
1. [Inference] Idempotency key = (source, external key, content hash); same hash = no-op; different content = quarantine.
2. Contracts versioned; unsupported revision = explicit rejection with reason code.
3. All inbound text is Untrusted (FR-INT-07).
4. Timeouts, bounded retries, and outstanding-backlog reporting on every pull (FR-RUN-03).
5. No egress beyond loopback (HAR-05/09, PNFR-18).
6. Table-name interpolation (DM-16) is not reused: new adapters use allow-listed identifiers.

### IA-3 Failure modes
Gateway down -> run record 'source unavailable', backlog preserved. Contract drift -> quarantine, not drop. Duplicate delivery -> no change to totals.

## Evidence References
integration/*.json; app/gateway_bridge.py; docs/07-repo-assessment/dependency-map.md DM-15..18.

## Assumptions
Gateway behaves as in code; no real partners.

## Unknowns
Real partner SLAs; OPD-05 target system.

## Unresolved Issues
OPD-05, OPD-11.

## Residual Risks
Unknown real-world feed formats.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

