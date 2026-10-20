---
stage: "17 — Finalise Implementation PRD"
artifact: "invalidated-assumptions.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/09-initial-prd/*.md (A-09-01..A-09-06, CON-/DEP- tables)", "docs/11-data-context/data-contracts.md (DC-03)", "docs/10-architecture/adrs/ADR-008-intake-pipeline.md, ADR-018-runtime-stack.md", "docs/12-specs/spec-readiness.md (RF-1..RF-10)", "docs/12-specs/schema-specifications.md, error-handling-spec.md", "docs/13-traceability/traceability-summary.md", "docs/14-transformation/schema-migration-plan.md", "docs/15-modernization/transformation-log.md (DEV-06, DEV-08, DEV-28, DEV-29, DEV-48, DEV-54, DEV-89, DEV-97)", "docs/16-repo-validation/{behavior-difference-report,data-contract-results,architecture-conformance-report,remaining-debt-register}.md", ".fde/orchestrator-decisions.md (OD-07, OD-10, OD-14, OD-18, OD-23, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Earlier stage documents are frozen; every correction below is recorded here and cited to its source, not made in the earlier file.**

## Summary
19 assumptions or earlier-stage statements are assessed: **12 invalidated** (IA-01..IA-12), **3 weakened / partly invalidated** (IA-13..IA-15) and **4 confirmed by build evidence** (IA-16..IA-19, kept for traceability because the Stage 9 PRD relied on them). Each carries the correction that the implementation baseline now uses. The most consequential are the re-delivery identity key (IA-02), the source-contract scope (IA-04), the runtime (IA-03) and the assumption that the comparison gate observes built modules (IA-09).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IA-1 Invalidated
| ID | Assumption / statement (source) | What the evidence shows | Correction used in the implementation baseline | Evidence | Impact | Risk | Confidence | Open question | Tag |
|---|---|---|---|---|---|---|---|---|---|
| IA-01 | FR split 41 R1 / 11 R2 (Stage 12 brief) | Register parses to 43 R1 / 9 R2 | 43/9 (PCH-02) | traceability-summary SUM-2; OD-10(b) | plan sizing | Low | High | — | [Verified Fact] |
| IA-02 | Re-delivery identity = `feed_id/business_key` (Stage 11 DC-03; ADR-008 wording) | 2,386 of 2,407 multi-row business-key groups carry different payloads; 67/67 REPLAY rows equal a sibling under the natural key | natural key (partner, record_kind, ref_id, source_ts) (PCH-03) | spec-readiness RF-1; OD-10(a); OD-18 | DC-03 wording would have quarantined thousands of legitimate events | High if unnoticed | High | — | [Verified Fact] |
| IA-03 | Runtime Python 3.12 (ADR-018) | Built and validated on floor 3.10 / SQLite 3.37 (device 3.10.12 / 3.37.2); `pyproject.toml` >= 3.10; 3.10 is end-of-life | decided OD-24: production target Python 3.12+, code keeps the 3.10 floor (PCH-36) | OD-10(c), OD-14, OD-24; S16-D07; dependency-scan-summary | CI / production move and golden re-baseline needed | High until production runs on 3.12+ | High | none (decided); work at Stage 27 | [Verified Fact] |
| IA-04 | FR-INT-04 can be enforced literally on every source (Stage 9 FR-INT-04; Stage 11 DQ) | `source-contract-v1` fails for partner_feed (8,567/8,567), gateway (1/1) and vendor_csv tiny (2,400/2,400); passes source_message (15/15); enforce would quarantine ~99% of the partner feed | per-source `record_only` default, `enforce` via Zone H (PCH-04) | data-contract-results DC-1, DC-04; OD-10(d) | FR-INT-04 is record-only in practice | Medium | High | is the contract or the data wrong? owner Unknown (OD-S12-11) | [Verified Fact] |
| IA-05 | Golden-compare compares legacy with the built modules' functions (BEH-CO-01; Stage 14 TG-4) | 7 of 11 probes still use INC-02 declared target values although modules are built; Stage 16 closed the evidence gap by observation only | remaining scope S16-D01, must-before-CUT (PCH-26, PCH-39) | DEV-08; RTD-15; behavior-difference-report "Golden-compare as built" | a module regression would not turn the gate red | Medium | High | — | [Verified Fact] |
| IA-06 | One forward migration runner and one version table (Stage 14 schema-migration-plan) | 8 migration files M000..M007 in 8 directories; 7 version tables: `schema_migrations` (M000, M001) plus `policy_`, `decision_`, `intake_`, `runs_`, `web_`, `search_schema_migrations`; per-package runners | recorded as built (IC-4); consolidation = S16-D03 | `hub/*/migrations/`, `hub/store/forward/`; DEV-28/42/59/66/76/90; AC-01 | operator error on migrate / restore | Medium | High | consolidate before Stage 27 | [Verified Fact] |
| IA-07 | Stage 12 JSON schemas can be frozen as v0.1 (spec-readiness RF-5) | intake-outcome rejects all 10,983 built objects (extra `contract_missing`, `conflicts_with`, `reason_detail`); metric-value rejects its object (extra `detail`); 12 of 16 schemas not executed by any test | schema addendum IC-7; schema tests at Stage 23 | data-contract-results DC-2, DC-02, DC-03 | consumers would reject valid hub objects | Medium | High | — | [Verified Fact] |
| IA-08 | The 82-code error registry and the spec'd exit codes (6, 7, 8) are complete (error-handling-spec) | Build added exit codes 2-5, 9-32 and dozens of codes; codes 2 and 9 are each shared by two meanings | addendum IC-1/IC-2 | DEV-10/23/37/49/60/68/103; RTD-21, RTD-24 | scripts cannot disambiguate exit 2 / 9 | Low | High | renumber or accept (Stage 27) | [Verified Fact] |
| IA-09 | DV-09 new value: reason `envelope_invalid` (deviation seed) | Built module stores reason `MISSING_ENVELOPE_FIELD` (the Stage 12 code) | label corrected in DV addendum (PCH-35) | BD-09; `hub/coexistence/seed_inc02.json` | stale label misleads the decision-maker | Low | High | — | [Verified Fact] |
| IA-10 | DV-07 fully describes the intake behaviour change ("legacy table untouched; outcomes append-only") | Outcome **classification** also differs: exact ref_id matching makes most legacy-ACCEPTED rows hub EXCEPTION/UNMATCHED_REF (7,903) | DV-07a text + proposed DV-10 (PCH-35) | BD-07 | decision-maker sees an incomplete change list | Medium | High | — | [Verified Fact] |
| IA-11 | All behaviour differences of the new rule service are in DV-01..DV-09 | DEV-29 partial-year prefix match (legacy 15000 vs hub 999999 defaulted) has no DV row | proposed DV-11 (PCH-35) | BD-10; RTD-41 | unregistered deviation | Medium | High | — | [Verified Fact] |
| IA-12 | Legacy characterisation outputs are runtime-independent (implicit in Stage 7 goldens / CON-03) | Same commit on Python 3.13 / SQLite 3.45: 10 of 16 CTs differ (ENV-1..ENV-6); ENV-4 (SQLite float sum) and ENV-6 (http.server error page) are real legacy output changes | goldens valid only on the reference runtime 3.10.12 / 3.37.2 until a reviewed re-baseline (OD-23) | behavior-difference-report ENV table; OD-23 | runtime upgrade changes figures | Medium | High | reviewed `--update-golden` (Stage 27) | [Verified Fact] |

### IA-2 Weakened / partly invalidated
| ID | Assumption | Evidence | Status | Tag |
|---|---|---|---|---|
| IA-13 | PNFR-13 planted-string fixture includes "44 regex hits" | No standalone fixture exists; 86 feed rows + 22 injection documents + 10 variants are used (DEV-89, RTD-73) | target wording change proposed (PCH-31) | [Verified Fact] |
| IA-14 | FR-POL-04/05: all three as-found rule sets are comparable on every case | The batch set's `amount_over_limit` needs a policy_code that the 125 cases do not carry: null for all 125; divergence computed over non-null outputs only (3 of 125, python vs JS) | divergence report states the null set (DEV-97, RTD-85) | [Verified Fact] |
| IA-15 | RTD-42: exact Decimal vs IEEE double may differ at x1.05 boundaries | 105/105 boundary cases (15 limits x 7 offsets down to 1e-10) identical; other functions / random amounts untested | risk reduced, not closed | [Verified Fact] |

### IA-3 Confirmed (Stage 9 relied on them)
| ID | Statement | Evidence | Tag |
|---|---|---|---|
| IA-16 | Month-end fan-out inflates the legacy total by ~19.3% (RC-8) | 742,956.61 / 622,826.44 = 1.193 on FX-BASE125 (synthetic, unvalidated) | [Verified Fact] |
| IA-17 | RH-2: replaying the 67 REPLAY rows changes queues and totals by 0 | 67 NOOP_DUPLICATE, 0 REVISED_CONFLICT; legacy DB sha unchanged | [Verified Fact] |
| IA-18 | No-AI is sufficient for T1/T2 on the shipped data (RH-7) | every exception carries a deterministic reason code; `model_calls_total` = 0; no RQ trigger recorded | [Verified Fact] (synthetic scope) |
| IA-19 | Stage 13 gap "CT-11 requires JDK, absent" | JDK 11 present; CT-11 runs (DEV-06) - the Stage 13 note was wrong, the Stage 9 reliance on CT-11 holds | [Verified Fact] |

### IA-4 Carried from earlier stages (unchanged, still in force)
- [Verified Fact] OD-07: A-04-01 refuted (`operating_costs.total_cases` is random); K-04/K-05 unmeasurable; P-01/P-03/P-04 are generator-bounded proxies. Still true at 2f318be (time to close is `null`, `no_completed_cycles`).
- [Assumption] A-09-01..A-09-06 remain assumptions; none was confirmed by a stakeholder (OD-04).

## Evidence References
Per-row evidence; reproduction commands in `docs/16-repo-validation/behavior-difference-report.md` and `data-contract-results.md`.

## Assumptions
- A-17-IA-1 [Assumption] The FX-BASE125 shipped data is representative enough to invalidate IA-02 and IA-04 for the purpose of this synthetic engagement; with real data the counts would change. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-17-IA-1 Whether the source contract or the shipped data is wrong (IA-04) - owner Unknown.
- U-17-IA-2 Behaviour of the legacy estate on the eventual target runtime (IA-12).

## Unresolved Issues
- IA-03, IA-04, IA-05, IA-06, IA-07, IA-08 need follow-up work or decisions (see release-boundaries.md RB-5 and implementation-prd.md IP-7).

## Residual Risks
- RR-IA-1 Further invalidations are likely once anything meets real data or a second reviewer (single author/approver, PR-10).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
