---
stage: "16 — Validate the Good Repo"
artifact: "repo-quality-gate.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/regression-results.md", "docs/16-repo-validation/test-results.md", "docs/16-repo-validation/behavior-difference-report.md", "docs/16-repo-validation/architecture-conformance-report.md", "docs/16-repo-validation/security-scan-summary.md", "docs/16-repo-validation/dependency-scan-summary.md", "docs/16-repo-validation/data-contract-results.md", "docs/16-repo-validation/remaining-debt-register.md", "docs/16-repo-validation/validation-signoff.md", "docs/16-repo-validation/evidence/", "docs/15-modernization/modernization-summary.md (Stage 15 close-out CONDITIONAL PASS)", "docs/14-transformation/transformation-gates.md (TG-4, G1..G10)", ".fde/stage-prompts/16_Validate-the-Good-Repo.md", ".fde/orchestrator-decisions.md (OD-03a, OD-04, OD-08, OD-09, OD-22, OD-23)"]
supersedes: "none"
---
**Label: synthetic repository; all figures synthetic, unvalidated - method validation only. Nothing here approves a deviation, a rule, a policy or a release.**

## Summary
**Gate outcome: CONDITIONAL PASS.** The transformed repository at `main` 2c63b07 is behaviour-preserving for the legacy estate and its hub shadow build passes every executed suite; every behaviour difference against the Stage 7 baseline is explained (**D5 = 0**). It is not a PASS because several conditions depend on human decisions or on later stages, listed below with owner, due point and risk. No blocking condition remains inside Stage 16's authority.

Headline evidence:
- Legacy characterisation (laptop, Python 3.10.12): **134/134** in 6 runs, digests identical to INC-01; mutation gate **15/15**; shipped tests 15 OK, post-run DB = Stage 7 R1.
- Hub suites (cloud, OD-23): **396 ok, 1 skipped, 0 fail** (all 397 methods, incl. the 241 planned Stage 13 tests and TST-CO-03).
- Behaviour comparison: 9 registered proposed deviations (D4) observed on the **built** modules, 2 unregistered-but-explained differences, 0 approved, 0 unexplained; environment A/B on 3.13 explained.
- New checks: hub mutation gate INC-08/09 **8/10** killed; 105/105 Decimal-vs-double boundary cases identical; 8 of 10 Stage 12 schemas exact, 2 lag the code by documented additive fields; no HIGH static finding in hub; zero third-party dependencies; No-AI holds.
- Data checksums rc 0 before and after every run; no file outside `docs/16-repo-validation/` changed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
[Verified Fact] Commit identity: Stage 16 started when `main` was `6a4472d`; during the stage the orchestrator reset `main` on both the laptop and the cloud clone to `origin/main` `2c63b07` (reflog `reset: moving to refs/remotes/origin/main`). Both commits have the same parent `ad5514f` and the **same tree `0d2e5c73b64f…`** (`git diff --quiet 6a4472d 2c63b07` = no difference), so every result here applies to `2c63b07` unchanged.

### QG-1 Completion-gate check (Stage 16 prompt)
| Condition | Status | Evidence | Tag |
|---|---|---|---|
| Every behaviour difference is explained | **Met** - D5 = 0; BD-00..BD-14 and ENV-1..ENV-6 each with cause and class | behavior-difference-report.md | [Verified Fact] |
| Required test suites pass or failures are dispositioned | **Met** - all pass; 1 skip (no python3.9), CT-17/18 NOT-RUN by design, 2 surviving mutants dispositioned as test-gap debt, human walkthroughs dispositioned as pending | test-results.md, regression-results.md | [Verified Fact] |
| Validation sign-off is recorded | **Met for the agent; human acceptance pending** | validation-signoff.md | [Verified Fact] |
| All required artifacts exist at the paths | **Met** - 10 artifacts + evidence/ | this folder | [Verified Fact] |
| Critical gaps resolved or explicitly documented | **Met (documented)** | remaining-debt-register.md | [Verified Fact] |
| Evidence supports the conclusion | **Met** for a shadow build; **not** for any cutover / exposure | all | [Inference] |

### QG-2 Required analysis dimensions
| Dimension | Result | Artifact |
|---|---|---|
| 1 Regression | none | regression-results.md |
| 2 Architecture conformance | safety decisions conform; structural deviations (layer leak, cycles, 7 migration runners, triple Zone H check, 2 entry points, runtime 3.10) | architecture-conformance-report.md |
| 3 Security scans | no HIGH in hub; 2 test gaps (SS-04, SS-08); Stage 24 decisions open | security-scan-summary.md |
| 4 Dependency scans | 0 third-party deps; runtime 3.10 EOL (High for production) | dependency-scan-summary.md |
| 5 Data-contract results | 8/10 schemas exact; 2 additive-field lags; source contract fails for 3/4 shipped sources (record_only) | data-contract-results.md |
| 6 Behaviour differences | D0/D1 legacy; D4 x9 + 2 unregistered; D5 0 | behavior-difference-report.md |

### QG-3 Why not PASS / why not BLOCKED
- **Not PASS** [Verified Fact]: (a) release gate G1 is red by design - golden-compare exits 6 while DV-01..DV-09 are unapproved (OD-S12-13); (b) human walkthroughs TST-REV-03/04/08 not run; (c) two security-relevant mutants survive; (d) suites run manually only, not in CI; (e) the reference runtime is end-of-life and deviates from ADR-018; (f) human acceptance of this gate is pending.
- **Not BLOCKED** [Inference]: none of (a)-(f) is a defect in the delivered build or a failed test; each is a documented human decision or a later stage's deliverable, and the product ships with everything consequential switched off (no holders, nothing adopted or active, scheduler off, gate mode `none`, search / drafts off, loopback only).

### QG-4 Non-blocking gaps (owner, due point, risk)
| # | Gap | Owner | Due | Risk |
|---|---|---|---|---|
| 1 | DV-01..DV-09 preserve-or-fix; register addendum DV-07 / DV-09 / DEV-29 (S16-D02) | Engagement lead (Dinesh Naik) | Stage 17 (addendum), Stage 30 (decisions) | Medium |
| 2 | Runtime decision 3.10 vs 3.12+ incl. SQLite (S16-D07, OD-S12-12) | Engagement lead (Dinesh Naik) | Stage 17 decision, Stage 27 build | High (production) |
| 3 | Security test gaps SS-04 / SS-08 (S16-D09) | orchestrator | Stage 23 | Medium |
| 4 | golden-compare declared probes (S16-D01) | orchestrator | Stage 17 plan, before any CUT | Medium |
| 5 | Schema addenda + schema tests (S16-D11) | Dinesh approves / orchestrator builds | Stage 17 / Stage 23 | Medium |
| 6 | CI wiring (RTD-01/02/14) | orchestrator | Stage 27 | High (process) |
| 7 | Human walkthroughs TST-REV-03/04/08 (S16-D13) | Engagement lead (Dinesh Naik) | Stage 26 or accept-open | Medium |
| 8 | Regression script selector TST-CO-03 (S16-D10) | orchestrator | next regression | Medium |
| 9 | Structural debt S16-D03..D06, D08 | orchestrator | Stage 17 refactor plan | Medium |
| 10 | Source contract vs data (S16-D15) | Engagement lead (Dinesh Naik) | Stage 17 | Medium |

### QG-5 Human decisions needed (Dinesh Naik)
1. **Accept this CONDITIONAL PASS** and its conditions (validation-signoff VS-3), or ask for rework.
2. **Runtime target** (OD-S12-12): stay on the 3.10 floor (EOL) or move to 3.12+ (and which SQLite); this also decides the harness baseline (ENV-1..6).
3. **Deviation register addendum**: agree to add DV rows for DEV-29 (partial-year match) and the intake outcome classification (BD-07), and to correct the DV-09 label - registration only, not approval.
4. **Human walkthroughs** TST-REV-03/04/08: run them (who?) or accept them as open until Stage 26.
5. Still open from earlier stages and unchanged by Stage 16: OD-S12-13 per DV, Zone H holders (OD-S12-06), rule-set activation (OD-S12-04), scheduler vs HAR-10 (OPD-11), retention (OD-S12-09), OPD-01..06 definitions, source contract owner / mode (OD-S12-11).

## Evidence References
- Artifacts in this folder; raw outputs, scripts and `SHA256SUMS.txt` in `evidence/`.

## Assumptions
- A-16-QG-1 [Assumption] OD-23's split (hub regression in the cloud on 3.13; harness and checksums on the 3.10.12 laptop) is valid evidence for this gate. Confirm: accepted by Dinesh in OD-23.

## Unknowns
- U-16-QG-1 Production behaviour, load and exposure - not in scope of a sandbox shadow build (Stages 24-31).

## Unresolved Issues
- QG-4 and QG-5.

## Residual Risks
- RR-QG-1 The shadow build is safe; any use beyond the sandbox before QG-4 items 2, 3, 6 and the Stage 24 decisions are closed would carry High risk.

## Recommended next action
Engagement lead records acceptance (or rework) of this gate; then **Stage 17 (Implementation PRD)**, carrying QG-4 / QG-5 and the Stage 12 addenda.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue - gate outcome CONDITIONAL PASS at main 2c63b07. |
