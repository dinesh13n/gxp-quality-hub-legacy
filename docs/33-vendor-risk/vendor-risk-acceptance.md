---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "vendor-risk-acceptance.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

**Nothing is accepted in this document.** It proposes, for each material third-party risk, a recommended treatment, a compensating control that exists today, and a review trigger, and names the **authorised owner: Engagement lead (Dinesh Naik)**, the only role that can accept vendor risk (accountability-map AM-1; TP-14; HAR-11). Procedure is the Stage 25 acceptance procedure RR-C: Dinesh answers in his own message or via AskUserQuestion, and the orchestrator appends an OD entry; only then may a row change status. **Default-answer authority (OD-32) covers scope and sequencing only and explicitly does not cover accepting risks**, so every row below stays PROPOSED.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Already accepted by Dinesh (quoted, not re-decided; OD entries)
| ID | Accepted item | OD |
|---|---|---|
| VA-A1 | Production on Python 3.12+ with code floor 3.10; goldens remain 3.10.12-specific | OD-24 (2) |
| VA-A2 | Test-once and cloud-regression split (laptop 3.10.12 goldens, cloud 3.13 regression) | OD-23 |
| VA-A3 | Single-approver risk and the general risk-register posture (RP-01..RP-12 stay open, none accepted) | OD-30 (RS-16 recorded as accepted general risk) |
| VA-A4 | PRs on the private GitHub remote with orchestrator merge | OD-13 |

### Proposed for decision (status PROPOSED, not accepted)
| ID | Linked risks | Recommended treatment | Compensating control today | Review trigger | Decision owner | Status |
|---|---|---|---|---|---|---|
| VA-01 | TP-01, TP-02, CR-01 | Treat (not accept): verify EOL date, pin runtimes at Stage 27, re-baseline goldens when runtime moves | stdlib-only; 3.10 floor; OD-24 | Stage 27; any Python/SQLite CVE | Dinesh | PROPOSED |
| VA-02 | TP-03, CR-02, LI-03 | Accept with conditions: keep private; add a second remote mirror before Stage 38 handover; check 2FA and branch protection | local clones; OD log in repo | handover; any account change | Dinesh | PROPOSED |
| VA-03 | TP-04, TP-05, TP-10, CR-03 | Accept with conditions: synthetic data only; terms and costs recorded by Dinesh; no product runtime dependency | plain-text artefacts; tests; OD-08 | any real data, terms change, or Stage 32 cost review | Dinesh | PROPOSED |
| VA-04 | TP-11, CR-04, CR-05 | Accept for pilot; add CI parity at Stage 27 | AEF-3 documents the two-key setup | Stage 27 | Dinesh | PROPOSED |
| VA-05 | TP-07, TP-09, LR-1..LR-4 | Defer: no hosting or real data; route legal flags to qualified reviewers before either | HAR-05, HAR-09, HAR-15 stops | any hosting / real-data / SSO decision | Dinesh | PROPOSED |
| VA-06 | TP-08 | Treat at Stage 27 under HAR-07 (SHA pins) | CI never run | Stage 27 | Dinesh | PROPOSED |
| VA-07 | TP-12, TP-06 | Keep No-AI deny-list as release gate; no vendor added without ADR + Dinesh decision | TST-CO-11/12 | any model/vendor proposal | Dinesh | PROPOSED |

### Findings
- [Verified Fact] No acceptance decision for vendor risk exists in the OD log beyond VA-A1..VA-A4, which are runtime/process items.
- [Verified Fact] The Completion Gate requires that "risk acceptance has an authorised owner": the owner is identified (Dinesh, per accountability-map AM-1 and OD-30), but **no vendor-risk acceptance has been given**. Per this stage's rule this is a documented non-blocking gap with owner and due condition, not a blocker, because nothing in the product depends on a vendor and no acceptance is needed to proceed to Stage 34 (a measurement stage).
- [Unknown] Whether Dinesh wishes to accept, treat or defer VA-01..VA-07.
- Proposed due date for his decision: before Stage 37 (ownership) and Stage 41 (retirement) consume this stage; latest at Stage 38 handover [Assumption: proposed, not agreed].

## Evidence References
docs/25-governance/risk-acceptance-register.md (RR-A, RR-B, RR-C); docs/25-governance/accountability-map.md AM-1; OD-23, OD-24, OD-30, OD-32; HAR-05, HAR-09, HAR-11, HAR-15.

## Assumptions
A-33-16 Proposed decision timing (before Stage 37/41, latest Stage 38) is a suggestion. A-33-17 OD-32 defaults do not accept risks.

## Unknowns
U-33-21 Dinesh's answers on VA-01..VA-07.

## Unresolved Issues
UI-33-12 Open item for Dinesh: accept / treat / defer VA-01..VA-07 (see Residual Risks).

## Residual Risks
All vendor risks remain unaccepted. Until decisions are logged, the compensating controls listed are the only protection and they are largely manual (RP-05).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
