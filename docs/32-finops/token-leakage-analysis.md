---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "token-leakage-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-2", "docs/37-operating-model/finops-ownership.md FC-01..FC-10", "docs/33-vendor-risk/vendor-inventory.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32", "docs/27-hardening/production-readiness-checklist.md PRC-R, risks table", "docs/00-preflight/ai-economics/cost-scenarios.md (anti-pattern: all 100,020 lake events through an LLM)", "tests/hub/regression_groups.json", "docs/37-operating-model/finops-ownership.md FF-03, FF-04"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
**Token leakage: none possible in the product, because there are no tokens.** The 0C anti-pattern (sending 100,020 lake events through an LLM, about USD 23 / 270 / 1,350) is documented as a guardrail and was not done. The honest leakage content is **value leakage in the toolchain and in documentation**: repeated regression wall time, rework caught late, unowned toolchain accounts, and the risk that dormant AI cost numbers are misread. None can be priced; each is sized only by what the repository measured.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TL-1 Leakage register
| ID | Type | Finding | Evidence | Size (measured only) | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|---|---|
| TL-01 | Token | [Verified Fact] No input/output/context/retrieval/tool/agent-loop tokens exist | MU-F1..F5 | 0 | none | Low | High | none |
| TL-02 | Documentation | [Verified Fact] Dormant AI cost files (S3 USD 533, S4 USD 719 per month at Base) still sit in `docs/00-preflight/ai-economics/` and could be quoted as the run cost | FF-03 | 2 files of numbers | Misleading forecast | Medium | High | Label them AI-option-only (proposal OB-09; not edited here) |
| TL-03 | Toolchain time | [Verified Fact] A full regression is 25 groups, 526 methods, 2,403 s on the laptop because the 180 s device-call cap forces one group per call; groups were split (C1..C3, S26a/b) to fit | PRC-R; OD-21; hardening notes | 2,403 s per full pass | Engineering time, not money | Low | High | Cloud pass has no cap (OD-33); its wall time is not recorded |
| TL-04 | Toolchain time | [Verified Fact] Sandbox rebuild overhead is paid per group: one observed sandbox build took 95 s | PRC-R notes (S26 situation) | 95 s observed once | Part of TL-03 | Low | Medium | Whether a shared sandbox is safe (OD-03a requires a full copy) |
| TL-05 | Duplicate runs | [Verified Fact] Stage 27 notes the laptop re-ran only S27, E27, B and characterization at the final tree; the cloud full run is authoritative. OD-23 adopted "test once" to cut duplication | PRC-R notes; OD-23 | not measured | Duplicate regression passes cost wall time | Low | Medium | Count of full passes per stage |
| TL-06 | Rework | [Verified Fact] The orchestrator's full regression caught defects that build-stage runs missed: a No-AI R2 defect in a test helper (S21-DEV-02) and two I6 failures (S24-DEV-05) | OD-28, OD-32 | 2 incidents recorded | Rework effort; shows value of the full pass | Low | High | Rework hours not recorded |
| TL-07 | Account | [Verified Fact] Code host, AI assistant and cloud workspace charges sit on accounts Dinesh controls; plans Unknown | V-03..V-05; FF-04 | Unknown | Hidden cost on inheritance | Medium | High | U-33-01, U-33-02 |
| TL-08 | Storage | [Unknown] Hold-all retention (OD-30) grows storage without a purge | FC-08 | Unknown | Future hosting cost | Medium | High | Retention policy |
| TL-09 | Hosting | [Unknown] Idle hosting once a host exists | FC-02 | Unknown | Fixed cost | Medium | High | Hosting decision |

### TL-2 Findings summary
- [Verified Fact] No token leakage exists; every row above is non-token.
- [Inference] The largest controllable cost lever visible in the repository is engineering and test wall time, not run cost. Reasoning: TL-03/TL-06 are measured; run cost is empty.
- Optimisations must not reduce coverage below Stage 26 thresholds (`docs/26-tevv/release-thresholds.md` RT-01..RT-15); see `optimization-backlog.md`.

## Evidence References
PRC-R table and notes; OD-21, OD-23, OD-28, OD-32; `docs/00-preflight/ai-economics/cost-scenarios.md`.

## Assumptions
- A-32-13 Wall time is a fair proxy for engineering cost only where a person waits on it; unattended cloud runs may cost differently. Confirm: Dinesh.

## Unknowns
- U-32-19 Cloud regression wall time, price and number of full passes. U-32-20 Rework hours.

## Unresolved Issues
- TL-02 needs an edit to Stage 0C files, outside this docs-only stage; routed as a proposal.

## Residual Risks
- RR-32-12 Cutting test time by dropping coverage (breaches RT thresholds). Medium; barred by guardrail CG-7.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
