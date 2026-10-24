---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "vendor-scorecards.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Scorecards for every inventory entry. **Scale: 1 = low risk, 5 = high risk** on Criticality, Concentration, Lock-in, Portability (5 = hard to move), Exit feasibility (5 = hard to exit). Scores are agent judgement ([Inference]) with reasoning per row; **confidence is Low-to-Medium because no contract, price, SLA or usage data exists**. No entry scores 5 on exit or lock-in; the highest exposures are **V-03 GitHub** and **V-04 AI coding assistant**, both on the toolchain side and neither in the shipped product.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Dimensions
Criticality (impact if unavailable), Concentration (share of a function held by one provider), Lock-in (proprietary features in use), Portability (effort to move the artefacts), Exit feasibility (effort and time to leave). Availability, security/data use, regulatory and price risk are rated in `third-party-risk-assessment.md`.

### Critical vendors - full scorecards
| ID | Crit. | Conc. | Lock-in | Port. | Exit | Confidence | Reasoning and evidence | Unresolved |
|---|---|---|---|---|---|---|---|---|
| V-01 CPython + stdlib | 5 | 4 | 2 | 2 | 2 | Medium | Every file is Python (35 app files import stdlib only, DM-08). Concentration is on the language, not a vendor: other distributions and versions exist; the code keeps a 3.10 floor and has run on 3.10.12/3.12/3.13 (OD-24 (2), OD-23). Lock-in low: no C extensions or packages. Exit to another language would be a rewrite but is not a realistic trigger; the realistic event is version end-of-life (RS-10: 3.10 EOL about Oct 2026, recalled not verified). [Inference] | distribution/patch level of a production host; EOL date re-check |
| V-02 SQLite | 5 | 5 | 2 | 2 | 3 | Medium | Single datastore for hub and legacy (DM-02), so concentration 5. Lock-in low-moderate: standard SQL and designed repo interfaces for the DB (architecture-options row 4), but `hub/store/` uses SQLite-specific pragmas, WAL, insert-only triggers and optional FTS5, so a move to another engine needs DDL/trigger rewrite and migration of the hash-chained audit store. FTS5 is reported not required (`hub/runtime.py`). Version not pinned; 3.37 floor named in RS-10 / OD-S12-12. [Inference] | pinned minimum SQLite version; concurrency ceiling vs future multi-user use |
| V-03 GitHub | 4 | 4 | 3 | 2 | 2 | Medium | Sole remote of the history and the PR / squash-merge approval trail (OD-13). Local clones hold full history (git is distributed), so loss of the remote does not lose code; PR discussion, review records and Actions logs would be lost. Lock-in: PR metadata and Actions syntax are GitHub-specific; code is portable via `git push` to any host. Private repo, data not committed (HAR-09, SS-02). [Inference] | plan tier; org vs personal account ownership (single owner `dinesh13n`); audit-log and retention terms |
| V-04 AI coding assistant | 4 | 5 | 2 | 2 | 2 | Low | 51/51 commits are co-authored by the assistant; delivery speed depends on it (concentration 5 within the toolchain). It is not in the product (OD-08, CP-10); artefacts are plain Python/Markdown with no assistant-specific format and no runtime call, so lock-in and portability are low: another assistant or humans can maintain the code, and specs and tests carry the behaviour. Risks: productivity loss, model-version drift, data use of repo content sent to the tool (repo is synthetic). `.fde/` prompts and the OD log are plain Markdown. [Inference] | terms of service, data retention, output IP conditions (legal: flag LR-3) |
| V-05 Orchestrator cloud workspace | 3 | 5 | 2 | 2 | 2 | Low | The full hub regression authority runs only here (AEF-3: no single environment reproduces all evidence; laptop 3.10.12 goldens plus cloud 3.13 regression). Concentration 5 for that one evidence function. Any runner with Python and the checksum-gated data copy could replace it; the procedure is recorded (OD-23, `tests/hub/run_hub_groups.py --all`). [Inference] | provider, region, retention, cost, who can read the copied data |

### Non-critical and legacy-only - compact scorecards
| ID | Crit. | Conc. | Lock-in | Port. | Exit | Confidence | Note |
|---|---|---|---|---|---|---|---|
| V-06 GitHub Actions | 1 | 3 | 3 | 2 | 1 | Medium | never run; hub not covered; major-tag pins (TP-08) |
| V-07 Docker base image | 1 | 2 | 1 | 1 | 1 | Medium | optional, never executed, non-loopback use needs HAR-05 |
| V-08 JDK | 1 | 2 | 1 | 2 | 2 | Medium | legacy reconcile only; JDK >= 11 (DM-03) |
| V-09 Node.js | 1 | 2 | 1 | 2 | 2 | Medium | legacy policy script only; CT-13 failure is Node patch drift (S24-DEV-04), an early example of runtime-version risk |
| V-10 Reference laptop / device VM | 3 | 5 | 1 | 2 | 2 | Low | only host of the 3.10.12 goldens; ~9.8 GB disk (OD-16); OS vendor Unknown |
| V-11 Data counterparties | 1 | 1 | 1 | 1 | 1 | High | none real; synthetic; re-score when any real source is named (HAR-15) |

### Reading the scores
- [Inference] Compare rows, do not sum. Criticality and Concentration both at 4-5 (V-01..V-05) trigger a named substitution path in `substitution-strategy.md` and an exit plan in `exit-plan.md`.
- [Verified Fact] No score comes from vendor-supplied evidence (no questionnaire, SOC report, SLA or price list exists in the repo).

## Evidence References
Evidence per row; docs/07-repo-assessment/dependency-map.md; docs/10-architecture/architecture-options.md (row 4); docs/25-governance/audit-evidence-index.md AEF-3; docs/24-security-privacy/residual-security-risks.md RS-10; hub/runtime.py; .github/workflows/verify.yml.

## Assumptions
A-33-04 The 1-5 scale and scores are agent judgement. Confirm or adjust: Engagement lead (Dinesh Naik).
A-33-05 Open-source runtimes are scored on their ecosystem alternatives, not on a contract.

## Unknowns
U-33-06 Real price, SLA and support terms for V-03/V-04/V-05. U-33-07 Ownership structure of the GitHub repository beyond the remote URL.

## Unresolved Issues
UI-33-03 Re-score when Stage 32 supplies cost lines and Dinesh supplies terms. Owner: Engagement lead (Dinesh Naik).

## Residual Risks
Scores can move materially once terms are known; today they carry Low-Medium confidence.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
