---
stage: "12 — Spec-Driven Design"
artifact: "nfr-spec.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/nfrs.md", "docs/operations-service-levels.md", "docs/03-problem-value/nfrs.md", "pyproject.toml", "docs/00-preflight/ai-economics/", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

NFR specification: all 20 PNFRs translated into measurement methods and 20 acceptance criteria (AC-NFR-01..20), with Assumption-class targets reported as measurements against 'unvalidated working targets' rather than pass/fail claims; test capacity envelope and six derived non-functional specs (Python >=3.10 floor per pyproject.toml).

## Findings
### NFR-1 How the 20 product NFRs become testable [Verified Fact: PNFR text; Inference: translation]
Targets for PNFR-01..05 are archived working targets that the source itself calls 'not measured guarantees' (`docs/operations-service-levels.md`); they remain **Assumptions** (A-09-04, owner Engagement lead (Dinesh Naik)). PNFR-06 and PNFR-10 have no number by design. The spec never turns an Assumption into a pass/fail claim about the system: where the target is an Assumption the criterion is "the figure is measured and reported with its method"; a verdict against the target is shown only labelled 'against an unvalidated working target'.

| PNFR | Category | Spec translation | Measurement method | Acceptance criteria (this stage) | Also covered by |
|---|---|---|---|---|---|
| PNFR-01 | Availability 99.5% (Assumption) | Availability = 1 - (down minutes / scheduled-hour minutes) from a self-probe of `/healthz` every 60 s logged as `http_request`; downtime = consecutive failed probes | probe log over a window | AC-NFR-01 | OBS metrics `http_requests_total` |
| PNFR-02 | Overnight completion by 06:00 local (Assumption) | `run_finished_before_0600_local` per scheduled run, `site.timezone` configured (Unknown) | run records | AC-NFR-02 | AC-RUN-01, OBS-4 |
| PNFR-03 | Feed accepted within 4 h of source event (R2, Assumption) | `delay = receipt_time - source_ts` per item; report share <= 4 h | intake records | AC-NFR-03 | AC-INT-28 |
| PNFR-04 | Stale risk signal <= 24 h (R2, Assumption) | 'signal' is not defined anywhere in the repo (Unknown); spec measures age of the newest accepted item per source | intake records | AC-NFR-04 | |
| PNFR-05 | RTO 8 h / RPO 24 h (Assumption) | restore `hub.sqlite3` + anchor from backup in a sandbox; time it; verify checksum, audit chain, projection | rehearsal log | AC-NFR-05 | AC-CO-09 |
| PNFR-06 | Performance: measure only (Unknown target) | p50/p95 latency of queue and search calls on the 125-case baseline | timers | AC-NFR-06 | AC-OBS-05, AC-REV-19 |
| PNFR-07 | Authenticated, authorised access | every route authenticated and authorised | route-registry and negative tests | AC-NFR-07 | AC-SEC-01..08 |
| PNFR-08 | Transport and secrets | loopback by default, TLS before exposure, secret scan 0 | scan + start-up tests | AC-NFR-08 | AC-SEC-06, 15, 16, 18 |
| PNFR-09 | Audit and tamper evidence (framing only) | hash chain + anchor + verify | tamper tests | AC-NFR-09 | AC-SEC-09..14 |
| PNFR-10 | Retention hold | zero deletions while no policy | trigger + grep | AC-NFR-10 | AC-DEC-03, AC-SEC-13, 18 |
| PNFR-11 | Integrity of imports | idempotent, contract-validated, lossless | replay suite; raw count = received count | AC-NFR-11 | AC-INT-01..06, 29 |
| PNFR-12 | Data protection (R2) | field class coverage | per-class access test | AC-NFR-12 | AC-SEC-19, 20 |
| PNFR-13 | Untrusted content | 0 effects from planted strings (86/22/44) | fixture suite | AC-NFR-13 | AC-INT-22, AC-GATE-13 |
| PNFR-14 | Observability | 100% runs recorded; every R1 KPI computed or explained | reports | AC-NFR-14 | AC-OBS-01..03, 08 |
| PNFR-15 | Understand and override | every rule output shows trace and override | output registry test | AC-NFR-15 | AC-GATE-18..20, AC-REV-05..08 |
| PNFR-16 | KPI auditability | documented and reproducible | reproduce test | AC-NFR-16 | AC-MET-14, 15 |
| PNFR-17 | Determinism | identical input -> bit-identical output | cross-environment hash test | AC-NFR-17 | AC-POL-22, AC-CO-13, AC-MET-21 |
| PNFR-18 | No AI | 0 model calls, 0 egress | deny-list, socket patch, tripwire | AC-NFR-18 | AC-CO-11, 12, AC-OBS-06 |
| PNFR-19 | Change safety | rollback rehearsed; replay gate | rehearsal + gate | AC-NFR-19 | AC-CO-09, 10, 15 |
| PNFR-20 | Honest labelling | 100% KPI outputs labelled | output scan | AC-NFR-20 | AC-MET-02 |

### NFR-2 Capacity envelope used for tests [Assumption / Verified Fact as marked]
| Item | Value | Class |
|---|---|---|
| Shipped baseline | 125 cases, seed 4100 (OD-09) | Verified Fact |
| Case volume | 167/month base, up to 1,670/month high (Stage 0C volume assumptions) | Assumption |
| Partner feed rows | 8,567 shipped; stress fixture 10x = 85,670 rows | Verified Fact / test choice |
| Documents | 1,200 JSONL + 420 archive (R2) | Verified Fact |
| Concurrent human users | <= 10 (single-host stdlib server; ADR-004 trigger if contention measured) | Assumption |
| Event store size | designed for >= 1,000,000 rows without functional change; performance not promised | test choice |
The envelope defines fixtures, **not** commitments.

### NFR-3 Additional non-functional specifications (not in PRD NFR list; derived from ADRs) [Inference]
| ID | Topic | Specification | Source |
|---|---|---|---|
| NF-A1 | Portability | Runs on Python >= 3.10 and SQLite >= 3.37 with no third-party packages; FTS5 optional with fallback | pyproject.toml, ADR-018, OD-S12-12 |
| NF-A2 | Configurability | no repo-relative writes; all paths via config/env | ADR-015, DM-10..12 |
| NF-A3 | Modularity | import-graph test enforces interface-contracts IF-1 rules | ADR-001 |
| NF-A4 | Maintainability | each service has a deterministic test double for `Clock`; no global state | ADR-018 |
| NF-A5 | Accessibility/i18n | UTF-8 everywhere, locale-independent formatting; accessibility level is Unknown (no requirement) | DQ-22 |
| NF-A6 | Backup | backup = copy of `hub.sqlite3` + anchor + `SHA256SUMS`; cadence configurable; default documented as daily (matches RPO assumption) | PNFR-05 |

### NFR-4 Acceptance criteria (non-functional)
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-NFR-01 | a probe log for a simulated 30-day window with known 216 down minutes in 43,200 | availability is computed | 99.50% is reported with method and the label 'against an unvalidated working target'; no claim is made about real availability | PNFR-01 | positive |
| AC-NFR-02 | schedule enabled in a sandbox test with a fixed clock and 30 simulated nights | scheduled runs complete | `run_finished_before_0600_local` reported per night; share reported; production timeliness is stated as unproven | PNFR-02 | edge |
| AC-NFR-03 | R2: items with delays 1 h, 3.9 h, 4.1 h, and a future `source_ts` | the delay report runs | share within 4 h = 2 of 3 non-future items (66.7%); the future item is flagged and excluded from the share | PNFR-03 | edge |
| AC-NFR-04 | R2: a source whose newest accepted item is 25 h old | the freshness report runs | source listed as older than 24 h with age | PNFR-04 | positive |
| AC-NFR-05 | a pre-release backup | restore is rehearsed in a sandbox from the written procedure | store restored, SHA-256 matches, `verify-audit` ok, `verify-projection` 0 mismatches; elapsed restore time recorded and compared (labelled) with 8 h | PNFR-05 | positive |
| AC-NFR-06 | the 125-case baseline fixture | latency is measured | p50/p95 recorded for queue, rule-trace, evidence-pack, state; no threshold | PNFR-06 | positive |
| AC-NFR-07 | the route registry | enumerated | 100% of routes authenticated and authorised; 0 anonymous reads/writes of case data in test | PNFR-07 | negative |
| AC-NFR-08 | the code base and start-up configs | secret scan and start-up tests run | 0 secrets; non-loopback without approval+TLS refused | PNFR-08 | negative |
| AC-NFR-09 | 100% of decision events in a test run | audited | each has actor/time/basis, chain verifies, deliberate tamper detected | PNFR-09 | positive |
| AC-NFR-10 | the full acceptance run | table row counts before and after | 0 deletions of case, evidence, event, audit, intake rows | PNFR-10 | negative |
| AC-NFR-11 | the replay suite (AC-INT-04/05/29) | run | 0 duplicate effects, 0 silent overwrites, raw count = received count | PNFR-11 | positive |
| AC-NFR-12 | R2: one fixture per field class | access tests run | 100% field classes covered | PNFR-12 | positive |
| AC-NFR-13 | planted-string fixtures: 86 feed rows, 22 document bodies, 44 regex-hit strings | processed | 0 effects on any decision field | PNFR-13 | negative |
| AC-NFR-14 | a run history and the KPI registry | health and coverage reports run | 100% of runs have records; every R1 KPI has a value or a stated reason | PNFR-14 | positive |
| AC-NFR-15 | the rule-output registry | iterated | 100% show trace and offer override with reason | PNFR-15 | positive |
| AC-NFR-16 | all KPIs | documentation and reproduce tests run | 100% documented; identical value on re-run | PNFR-16 | positive |
| AC-NFR-17 | core paths run across hash seeds, time zones, locales | outputs compared | bit-identical | PNFR-17 | positive |
| AC-NFR-18 | the full suite | dependency, import and socket checks run | 0 model calls, 0 egress, deny-list clean | PNFR-18 | negative |
| AC-NFR-19 | a release candidate | rollback rehearsal and replay gate run | both pass before ready status | PNFR-19 | positive |
| AC-NFR-20 | all KPI outputs and reports generated while data are synthetic | scanned | 100% carry 'synthetic, unvalidated' | PNFR-20 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-NFR-1 The capacity envelope is a set of test fixtures, not a commitment; real volumes are unknown (OD-04).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-NFR-1 Real availability needs, business calendar and time zone, latency expectations (OPD-14), 'risk signal' definition for PNFR-04.

## Unresolved Issues
- PNFR-01..05 targets await Dinesh's confirmation or replacement (OPD-13 / A-09-04).

## Residual Risks
- PNFR-01 99.5% is likely unattainable on a single host without HA (ADR-015); the spec measures and reports honestly instead of promising it.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
