---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "cost-leakage.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/32-finops/finops-model.md", "docs/32-finops/tco-model.md", "docs/32-finops/token-leakage-analysis.md", "docs/32-finops/cost-per-outcome.md", "docs/32-finops/optimization-backlog.md", "docs/37-operating-model/finops-ownership.md", "docs/00-preflight/ai-economics/economics-readiness.md", ".fde/orchestrator-decisions.md (OD-08, OD-32, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Cost leakage, built on Stage 32. **Model/token leakage: none possible (No-AI, USD 0 by design, OD-08).** Real cost leakage candidates are engineering/toolchain time, rework found late, unowned accounts and unpriced TCO terms. All are sized only by what the repository measured; **no cost is priced or invented.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CL-1 Cost leakage register
| ID | Source | Finding | Evidence | Measured size | Impact | Risk | Conf. | Unresolved question |
|---|---|---|---|---|---|---|---|---|
| CLK-1 | Tokens | [Verified Fact] No tokens exist; the 0C anti-pattern (100,020 lake events through an LLM) was not done | TL-01; cost-scenarios.md | 0 | none | Low | High | none |
| CLK-2 | Documentation | [Verified Fact] Dormant AI-option cost numbers (S3 USD 533, S4 USD 719 per month) remain in 0C files and could be misread as run cost | TL-02 | 2 files | Misleading expectation | Medium | High | OB-09 (not edited; outside docs-only scope) |
| CLK-3 | Toolchain time | [Verified Fact] Full regression 2,403 s per pass on the laptop; sandbox rebuild 95 s observed once | TL-03, TL-04 | 2,403 s; 95 s | Engineering wait | Low | High | Cloud wall time |
| CLK-4 | Rework | [Verified Fact] Orchestrator full regression caught S21-DEV-02, S24-DEV-05, S28-DEV-08 that build runs missed | TL-06; OD-28, OD-32, OD-35 | 3 incidents | Rework hours Unknown | Low | High | Rework hours |
| CLK-5 | Accounts | [Verified Fact] Code host, AI assistant and cloud workspace charges sit on accounts Dinesh controls; plans Unknown | TL-07; V-03..V-05 | Unknown | Hidden cost on handover | Medium | High | U-33-01/02 |
| CLK-6 | Storage / hosting | [Unknown] Hold-all retention (OD-30) grows storage; no host chosen | TL-08, TL-09 | Unknown | Future fixed cost | Medium | High | Retention policy, hosting decision |
| CLK-7 | Unpriced TCO terms | [Verified Fact] Toolchain, oversight, validation/compliance, exit have no price anywhere; 0C S1/S2 ranges omit them and ER-4 calls zero oversight an omission | TCO-F2 | 4 terms | Gross range USD 7.9k-39.0k (Assumption) is understated by an unknown amount | Medium | High | Inputs in TC-1 |
| CLK-8 | Effort | [Verified Fact] Actual build effort not recorded; may lie at or above S2 (ER-2) | TCO-F4 | Unknown | The key TCO term | Medium | n/a | OB-04 |
| CLK-9 | Ownership | [Verified Fact] RL-09 cost owner VACANT; no finance partner has reviewed anything | OD-35; Stage 32 finops-ownership | 1 role | No one to watch cost | Medium | High | Holder |
| CLK-10 | Control friction (cost of controls) | [Inference] The approval gates and single-approver design add human time to every consequential action; their cost is unmodelled (oversight term = 0 in 0C). Reasoning: ER-4 | `tco-model.md` TC-1 | not sized | Oversight cost hidden | Medium | Low | Reviewer minutes (U-24) |

### CL-2 Cost variance statement
[Verified Fact] Expected cost = 0C ranges (Assumptions). Actual cost = Unknown except model spend USD 0. **Cost variance cannot be stated**, and Stage 32's own guardrails bar reducing test coverage below Stage 26 thresholds (CG-7) as a "saving" (RR-32-12).

### CL-3 Cost-per-case caution
K-13 (USD 23.40 per case) and K-12 (0.603 h/case) are Stage 4 generator-derived figures using the ops-table denominator (108, not 125); they are baselines of a synthetic data set, not hub costs, and not savings (OD-07).

## Evidence References
`docs/32-finops/token-leakage-analysis.md` TL-01..TL-09; `tco-model.md` TC-1..TC-5; `optimization-backlog.md`; `docs/37-operating-model/finops-ownership.md`; `docs/00-preflight/ai-economics/economics-readiness.md`; OD-08, OD-30, OD-35.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-10 Every price, rate, hours figure and account plan (inputs listed in `tco-model.md` TC-1).

## Unresolved Issues
- 0C files not edited (docs-only); OB-09 stays a proposal.

## Residual Risks
- RR-35-11 A 'saving' claimed from reducing regression time that lowers coverage. RR-35-12 Understated TCO taken as budget.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
