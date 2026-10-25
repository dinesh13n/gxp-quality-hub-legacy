---
stage: "39 — Drift + Continuous Improvement"
artifact: "knowledge-drift-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/31-observability/metrics-spec.md", "docs/31-observability/alert-catalog.md", "tests/hub/test_tst_hub_stg31_catalog.py", "tests/hub/test_tst_hub_stg31_slo_alerts.py", "docs/12-specs/spec-readiness.md", "docs/13-traceability/", "docs/16-repo-validation/", "docs/37-operating-model/raci.md", "docs/37-operating-model/service-ownership-map.md", ".fde/orchestrator-decisions.md (OD-10, OD-30..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
"Knowledge" in a No-AI product is the written knowledge the engagement relies on: specs, catalogues, registers, decision log, ownership map. Knowledge drift is the documentation diverging from the code or from itself. The evidence shows it has already happened more than once (OD-10: FR register 43 R1 / 9 R2 versus the brief's 41/11; ADR-018 says Python 3.12 while pyproject requires >=3.10; Stage 28 prompt path `28-resilience` versus `28-reliability`; Stage 25 documents needing v0.2 after later stages). Eight metrics (KM-01..KM-08); the Stage 31 pair has automated tests, the rest are manual or gaps.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### KD-1 Metrics
| ID | Metric | How measured | Candidate threshold (Assumption) | Tier | State |
|---|---|---|---|---|---|
| KM-01 | Metric catalogue vs doc | every name in `hub/obs/catalog.py` appears in `docs/31-observability/metrics-spec.md`, and the reverse | 0 unmatched | INVESTIGATE | [Verified Fact] tests D03 and C05 enforce it (Stage 31 evidence: group S31 19/19 ok) |
| KM-02 | Alert rule vs doc | every id in `hub/obs/alerts.py` RULES is in `alert-catalog.md` with owner, action, runbook entry | 0 unmatched | INVESTIGATE | [Verified Fact] tests A01, D03 |
| KM-03 | Requirement register vs trace | parsed FR register (43 R1 / 9 R2, OD-10b) versus the Stage 13 traceability matrix and the tests that cite each FR | any FR with no row, or any row for a retired FR | INVESTIGATE | [Unknown] no standing script; Stage 13 matrix exists; [Assumption] a read-only parser can be written (backlog IB-06) |
| KM-04 | Counts quoted in docs vs reality | numbers repeated in several docs (test groups "25/27 groups", 419/476 methods, 133/134 CT) compared with the latest recorded run output | 0 contradictions between two docs stating the same quantity at the same commit | WATCH if the docs carry different dates; INVESTIGATE if same date | [Verified Fact] counts differ across stages by design (they grow); [Inference] a dated "as of commit" rule is needed (IB-07) |
| KM-05 | Deviation register vs code | DV-01..DV-11 (Stage 16) and DEV-xx rows versus `python -m hub deviations`; every `approved` row has an `approval_ref` | any code-visible deviation without a row; any approved row without a ref | CHANGE (C2) | [Verified Fact] register and CLI exist; DV corrections (DV-07, DV-09, missing DV for DEV-29) were left to Stage 17 (OD-24) and are [Unknown] whether closed in a register of record |
| KM-06 | Open-decision ageing | count of open items by age in `.fde/orchestrator-decisions.md` and stage "open for Dinesh" lists (D-27-xx, D-28-xx, D-31-xx, D-34-xx, Q-29-xx, CA-xx, RS/RP/VA/RTR/F-xx) | any item with no owner, or open past its stated trigger ("before any pilot or production use" has no date, so ageing cannot be computed: [Unknown]) | INVESTIGATE | [Verified Fact] items are open (OD-33..OD-36); [Unknown] due dates do not exist |
| KM-07 | Ownership coverage | owned assets / total assets in `docs/37-operating-model/service-ownership-map.md`; roles VACANT count in `raci.md` | baseline: 0 of 28 assets with an accepted steady-state owner, all roles except Dinesh VACANT (OD-34); candidate threshold: any decrease, or any new asset without a proposed owner | INVESTIGATE (a decrease is drift; staying at 0 is the known open item, not drift) | [Verified Fact] baseline value |
| KM-08 | Superseded-document hygiene | files that should carry `status: SUPERSEDED` once a v0.2 exists (Stage 25 v0.2 after Stages 23/24; Stage 12 v0.2 IC-1..IC-8; Stage 34/35/36 v0.2 after a real window) | a v0.2 exists and the v0.1 is not marked, or a v0.1 is edited in place | CHANGE (C0: errata, not overwrite, CC-06) | [Inference] check is a front-matter scan; no tool yet (IB-06) |

### KD-2 Findings from this run [Inference, from reading the cited files]
- KD-F1 The strongest anti-drift control for knowledge is a test that fails when a doc and code disagree; it exists only for Stage 31. Confidence: High that others lack one (no equivalent tests found by name in `tests/hub/`); Medium that none exist in other forms.
- KD-F2 Stage prompts name artifact directories that the orchestrator overrides (28, 35, 39). This is a knowledge-drift source: recorded as assumption each time (A-35-01, S28-DEV-05, A-39-01).

## Evidence References
See header.

## Assumptions
- A-39-07 Knowledge drift is measured on repository documents only; no wiki, ticketing or chat knowledge base exists (OD-04). Confirm: Dinesh.

## Unknowns
- U-39-05 Whether outside consumers of the 13 outputs hold their own copies of the contracts (OD-28b: outside consumers Unknown).

## Unresolved Issues
- G-39-02 No automated doc-vs-code check outside Stage 31. G-39-04 Ownership and open-decision ageing are not computed. Owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-39-04 The decision log is the single source for "what was decided"; a wrong edit there is not detected by any test. Medium.
- RR-39-05 Counts in documents silently go stale as the suite grows. Low impact, high frequency.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
