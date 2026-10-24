---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "third-party-risk-assessment.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Risk assessment across availability and contractual terms, security/privacy and data use, regulatory constraints and price risk. **Legal interpretation is excluded and flagged for review (LR-1..LR-4).** 12 third-party risks (TP-01..TP-12). **None is rated High-likelihood; the largest are runtime end-of-life (TP-01), single-owner GitHub account (TP-03) and AI-assistant dependency (TP-04).** Compensating controls are repository-evidenced (no third-party packages, loopback-only, egress tripwires, deny-list test). No risk is accepted here.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
Rating L/M/H for likelihood and impact is agent judgement ([Inference]).

| ID | Finding | Evidence | Impact | Risk (L / I) | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| TP-01 | Python 3.10 reaches end of life about Oct 2026 and the SQLite 3.37 floor is old; the reference laptop and goldens run 3.10.12 | RS-10 ("recalled, re-check"); DM-01; OD-24 (2) accepts production on 3.12+ with a 3.10 code floor | patches stop on the evidence host; moving to a newer Python changes goldens (10/16 CT checks differ on 3.13 by environment only, OD-23) | M / M | Medium | exact EOL date (verify at python.org); when to re-baseline goldens (Stage 27/30) |
| TP-02 | Runtime patch drift breaks evidence (Node patch drift already failed CT-13) | S24-DEV-04; OD-32 | harness red for environmental reasons | M / L | High | pin policy for Node/JDK/Python used by the harness |
| TP-03 | GitHub remote is a single personal-account repo (`dinesh13n`); bus factor 1; terms unknown | `git remote -v`; OD-05, OD-13 | loss of PR/review trail; access loss blocks merges | L / M | Medium | org ownership, backup mirror, 2FA / branch protection (not visible in repo) |
| TP-04 | Build depends on an AI coding assistant for all 51 commits; availability, model change or terms change affects delivery | `git log`; CP-10; AI register | schedule; review-quality drift; no product runtime impact | M / M | Medium | continuity plan; who reviews assistant output (single approver, RP-01) |
| TP-05 | Data use / retention by the AI assistant and cloud workspace of repo content and copied test data | CP-10; OD-23 (git-ignored data copied to the cloud workspace) | synthetic data exposure now; real data would breach HAR-09 / HAR-15 | L / H (if real data) | Low | terms of both; confirm only synthetic data is ever sent (OD-04; `data_origin` synthetic) |
| TP-06 | The product has no vendor data processors today | SS-01; privacy-impact-assessment; ADR-015 | positive finding | L / L | High | any change (hosting, backup storage, SSO) creates processors (see data-processing-dependencies.md) |
| TP-07 | Regulatory constraints on future vendors: DPDP / GDPR named as candidates only; Part 11 framing only; no external AI-governance obligations cited | OB-08, OB-15; GD-11 (OD-30) | a future cloud/SaaS choice would trigger residency, processor and validation questions | L (today) / H (if adopted) | Low | qualified review before real data or a hosted service (LR-2) |
| TP-08 | Supply-chain hygiene: Actions pinned to a major tag not a SHA; Docker base tag floating; SQLite not pinned | DM-06; Dockerfile | upstream tag move changes CI/image behaviour | L / M | High | pin at Stage 27 (HAR-07 approval needed) |
| TP-09 | Hosting vendor unknown and unpriced; infra USD 20-100/month is an Assumption only | `preliminary-tco` assumption; ADR-015 option C ("no evidence") | price risk unmeasurable; lock-in decision deferred | L / M | Low | hosting target and operator (Unknown) |
| TP-10 | No licence/subscription cost recorded for V-03/V-04/V-05; Stage 32 not run | OD-04; no docs/32 | TCO understates toolchain cost | M / L | Low | obtain actual costs or confirm free tier |
| TP-11 | Evidence concentrated on two environments (laptop 3.10.12 + cloud 3.13) | AEF-3; OD-23 | audit reproducibility depends on both | M / M | Medium | CI parity (FAC-11, Stage 27) |
| TP-12 | Future pressure to add a model vendor bypassing re-qualification | RS-15; OD-08 triggers RQ-1..RQ-3; TST-CO-11 deny-list | AI added without a new Dinesh decision | L / H | Medium | gate stays manual until CI exists (RP-05) |

### Availability and contractual terms
- [Verified Fact] No SLA, support contract, DPA or exit clause exists for any entry; `docs/operations-service-levels.md` describes the legacy estate's internal service levels, not a vendor SLA.
- [Unknown] Whether GitHub, the AI assistant or the cloud workspace offer terms that matter (uptime, data location, termination assistance).

### Legal / contract review flags (excluded from this analysis)
- LR-1 Licence terms of CPython / SQLite / Node / OpenJDK for any redistribution (the Dockerfile bakes code into an image).
- LR-2 Data-protection regime and processor terms if any hosted service is added (DPDP, GDPR named in OB-08).
- LR-3 IP ownership and permitted-use terms of AI-assistant output (V-04).
- LR-4 GitHub and cloud-workspace terms for GxP-regulated content.
All four are **flagged for qualified legal review; no interpretation is given.** Owner of routing: Engagement lead (Dinesh Naik).

## Evidence References
docs/24-security-privacy/residual-security-risks.md RS-10, RS-15; threat-model.md T-21, CP-09, CP-10; docs/25-governance/compliance-obligations.md OB-08, OB-14, OB-15; docs/00-preflight/ai-economics/preliminary-tco.md; docs/25-governance/audit-evidence-index.md AEF-3; OD-23, OD-32.

## Assumptions
A-33-06 RS-10 EOL date is recalled, not verified (carried from Stage 24).
A-33-07 Only synthetic data is ever sent to V-04 or V-05 (OD-04, A-0B-01); confirm: Engagement lead (Dinesh Naik).

## Unknowns
U-33-08 Terms of V-03/V-04/V-05. U-33-09 Hosting target and operator. U-33-10 Branch protection, 2FA and ownership settings of the GitHub repository.

## Unresolved Issues
UI-33-04 LR-1..LR-4 await legal review. UI-33-05 TP-08 pinning needs HAR-07 approval at Stage 27.

## Residual Risks
All 12 risks remain open; none accepted (proposals in vendor-risk-acceptance.md).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
