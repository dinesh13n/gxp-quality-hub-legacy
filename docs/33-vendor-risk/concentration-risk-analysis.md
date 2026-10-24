---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "concentration-risk-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Concentration is **high in the toolchain and in the language/datastore pair, and absent in commercial services**. Five concentration points (CR-01..CR-05): CPython+SQLite as the single runtime/datastore pair; GitHub as the single code and review host; the AI coding assistant as the single author of all 51 commits; the cloud workspace as the single authority for the full regression; and the laptop as the single host for Python 3.10.12 goldens. There is **no vendor concentration in the product's data path** because there are no vendors there. Concentration exists because the engagement is small (one approver, one orchestrator), not because of contractual lock.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Concentration point | Share / evidence | Failure scenario | Impact | Mitigation present | Gap | Confidence |
|---|---|---|---|---|---|---|---|
| CR-01 | CPython + SQLite are 100% of runtime and storage | DM-01, DM-02, SS-01 | security flaw or EOL in the pair | all functions; audit store | stdlib-only keeps surface small; 3.10 floor tolerates newer Pythons; hash-chain + checksum backups | EOL date unverified; SQLite version unpinned | Medium |
| CR-02 | GitHub holds the only remote of history and the PR/approval trail | `git remote -v`; OD-13 | account lockout, outage, policy change | merges blocked; review trail lost; local clones keep code | git is distributed; OD log in-repo records decisions | no mirror; single owner account | Medium |
| CR-03 | One assistant family authored 51/51 commits | `git log`; CP-10 | unavailability, behaviour change, terms change | delivery halts; consistency drift | plain-text artefacts; tests and goldens carry behaviour; single approver reviews (RP-01) | no continuity plan; reviewer independence procedural only (A-18-OM-2) | Medium |
| CR-04 | One cloud workspace runs the full hub regression | OD-23; AEF-3 | provider change or loss | cannot reproduce full-regression evidence | procedure documented; checksum-gated data | no second runner; provider Unknown | Low |
| CR-05 | One laptop (Python 3.10.12) hosts goldens | OD-23; OD-24 | hardware or OS loss | cannot reproduce 10/16 CT goldens | data backup with SHA256SUMS (OD-03); repo in remote | goldens environment-specific; runtime move requires re-baseline | Medium |

### Cross-cutting concentration
- [Inference] CR-02 and CR-03 correlate: both are cloud services reached over the network from the same operator account(s); an account or network problem hits both. Reasoning: all PR workflow runs through the assistant session and GitHub.
- [Inference] CR-04 and CR-05 are complementary (laptop for goldens, cloud for regression) so neither alone can certify a release; this is a *two-key* concentration. (AEF-3.)
- [Verified Fact] Nothing in the product depends on CR-02..CR-05 at runtime.

### Geographic / jurisdictional concentration
[Unknown] Provider locations for V-03, V-04, V-05; operator is in India (profile), but data residency of any provider is not evidenced. Flag LR-2.

### Thresholds (proposed, not adopted)
Proposed trigger to act: any new third party that holds product data or sits in the product runtime path. Today: none. Owner of the threshold: Engagement lead (Dinesh Naik).

## Evidence References
docs/07-repo-assessment/dependency-map.md; docs/25-governance/audit-evidence-index.md AEF-3; docs/24-security-privacy/residual-security-risks.md RS-10, RS-16; docs/25-governance/risk-acceptance-register.md RP-01, RP-05; OD-03, OD-13, OD-23.

## Assumptions
A-33-09 Operator-account correlation between GitHub and the assistant is assumed from the PR workflow; confirm: Engagement lead (Dinesh Naik).

## Unknowns
U-33-14 Provider geography; U-33-15 whether a second runner or mirror is wanted.

## Unresolved Issues
UI-33-07 No mirror/second runner decision exists; deferred to Stage 27/37 (ownership).

## Residual Risks
Concentration will worsen if a hosting vendor or a managed DB is later chosen as a single provider; ADR-015 keeps that decision open.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
