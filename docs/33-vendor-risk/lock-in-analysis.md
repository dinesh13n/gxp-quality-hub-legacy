---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "lock-in-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Lock-in is **low in the product and low-to-moderate in the toolchain**. The product uses only standard-library Python and SQLite with deliberate repository interfaces; the highest lock-in is to SQLite-specific behaviour in the hub store (WAL, insert-only triggers, optional FTS5) and to GitHub-specific workflow metadata. Nothing in the repo depends on a proprietary API, SDK, model, cloud service or licensed software.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Lock-in surface | Evidence | Severity | Reversal effort | Confidence |
|---|---|---|---|---|---|
| LI-01 | SQLite-specific features in `hub/store/` (pragmas, WAL, triggers that make audit records insert-only, FTS5 if available) | hub/store, hub/runtime.py, ADR-004, ADR-012 | Medium | Medium: DDL and trigger rewrite, audit chain migration with re-verification | Medium |
| LI-02 | Python version-specific behaviour: goldens are Python 3.10.12-specific; 3.13 differs on 10/16 CT checks by environment only | OD-23, OD-24 | Low-Medium | re-baseline goldens once (Stage 27/30) | High |
| LI-03 | GitHub PR/review metadata and Actions syntax | OD-13; verify.yml | Low-Medium | history portable by `git push`; PR text lost unless exported | Medium |
| LI-04 | AI-assistant-shaped working practices: `.fde/` stage prompts, OD log, session trailers in commits | `.fde/`, `git log` | Low | plain Markdown; trailers are text; a different assistant or human team can continue | Medium |
| LI-05 | Cloud workspace procedure (regression grouping, checksum-gated copy) | OD-23; `tests/hub/run_hub_groups.py` | Low | runnable on any Python host with the data copy | Medium |
| LI-06 | Legacy estate: JDK and Node scripts with positional CSV parsing and cwd-relative paths | DM-13, DM-17 | Low (legacy, being replaced) | retire at Stage 41 | High |
| LI-07 | Contractual lock-in: minimum term, auto-renewal, exit fees, data-return rights | none visible | Unknown | Unknown | Low |

### Findings
- [Verified Fact] No proprietary API, SDK or licensed component is imported anywhere (DM-08; TST-CO-11 deny-list covers AI/ML/HTTP-client packages; stdlib-only test S30).
- [Verified Fact] The architecture states 12-factor design (env config, no repo-relative writes, stdout logs) so hosting stays open (ADR-015).
- [Inference] The largest *future* lock-in risk is not present: choosing a managed cloud DB/PaaS (ADR-015 option C) or a model provider (excluded by OD-08). Both are reversible today because neither exists.
- [Unknown] LI-07: terms for V-03/V-04/V-05.

## Evidence References
hub/runtime.py; hub/security/tables.py; docs/10-architecture/adrs/{ADR-004,ADR-012,ADR-015}; docs/10-architecture/architecture-options.md; docs/07-repo-assessment/dependency-map.md DM-13, DM-17; OD-13, OD-23, OD-24.

## Assumptions
A-33-10 Severity ratings are agent judgement.

## Unknowns
U-33-16 Contractual lock-in terms for V-03/V-04/V-05.

## Unresolved Issues
UI-33-08 SQLite version/floor to be pinned (OD-S12-12 records 3.37 floor; confirm in Stage 27).

## Residual Risks
LI-01 grows if more SQLite-specific features are added; keep repository interfaces honest.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
