---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "substitution-strategy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

For each critical entry, a named substitute path, trigger and readiness level. **Substitution is cheap for toolchain items (V-03, V-04, V-05) and not needed in the product, because the product has no vendors.** The runtime pair (V-01, V-02) is substituted by *version change*, not by vendor change. Nothing here selects or endorses a real vendor; candidates are categories.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Substitute (category, not endorsement) | Trigger | Readiness today | Work to switch | Constraints | Confidence |
|---|---|---|---|---|---|---|
| V-01 CPython | newer CPython (3.12+ per OD-24); alternative CPython distribution | 3.10 EOL (RS-10); CVE on host version | Partly ready: Dockerfile/CI already say 3.12; code keeps 3.10 floor; hub regression ran on 3.13 | re-baseline goldens (Stage 27/30); CI on both (FAC-11) | HAR-07 for CI/Docker/pyproject edits | Medium |
| V-02 SQLite | newer SQLite via newer Python; for scale-out, a server database behind the existing repository interface (designed in ADR-004, not built) | SQLite version CVE; multi-user concurrency need; HA need (PNFR-01) | Ready for version bump; **not ready** for engine change | DDL/trigger port, audit-chain migration with re-verification, new tests | requires an ADR and Dinesh decision; HAR-09 if off-host | Low-Medium |
| V-03 GitHub | another git host (any), or self-hosted git | outage, policy/terms change, account loss | Ready for code (`git push --mirror`); PR history not portable | create target remote; export PR text; adjust OD-05/OD-13 workflow wording | HAR-09 (off-device remote needs approval); private only | Medium |
| V-04 AI coding assistant | another assistant, or human developers | unavailability, terms or price change, quality drift | Ready by design (plain text, tests/specs hold behaviour); no switch plan written | document the working agreement (`.fde/`), re-validate with golden-compare and hub regression after any switch | single approver (RP-01) is the review limit | Low-Medium |
| V-05 Cloud workspace | any Python host/CI runner; the laptop for smaller groups | provider change, cost, outage | Ready in principle (procedure recorded); not rehearsed | provision runner, copy checksum-gated data, run `run_hub_groups.py --all` | disk and 180 s call cap noted (OD-21); HAR-09 for off-device data | Medium |
| V-06..V-09 | pin by SHA / digest; alternative distributions | tag move; EOL | Ready | Stage 27 pinning (HAR-07) | | Medium |

### Findings
- [Verified Fact] Substitution does not require data return from any vendor, because no vendor holds product data.
- [Inference] The only substitution that would be expensive is an engine change for V-02; keep repository interfaces and avoid new SQLite-only features to keep it open.
- [Assumption] A-33-12 No candidate vendor has been evaluated; categories only. Selection, if ever needed, goes through an ADR and Dinesh.

## Evidence References
docs/10-architecture/adrs/{ADR-004,ADR-015}; docs/10-architecture/architecture-options.md; docs/24-security-privacy/residual-security-risks.md RS-10; OD-24 (2), OD-14, OD-23; docs/25-governance/risk-acceptance-register.md RP-01.

## Assumptions
A-33-12 as above. A-33-13 Triggers are proposals, not adopted thresholds.

## Unknowns
U-33-19 Whether Dinesh wants a second git remote or CI runner as a standing control.

## Unresolved Issues
UI-33-10 No written assistant-switch plan or second runner exists (non-blocking).

## Residual Risks
Switch plans are untested; times and costs are Unknown.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
