---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "data-processing-dependencies.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Maps which third parties touch which data. **In the product there are none**: the hub processes data in-process on one host (SQLite files, loopback only) and sends nothing off-host (SS-01, privacy-impact-assessment, egress tripwires). Third-party data exposure exists only in the **engagement toolchain**: the AI coding assistant (V-04) sees repository content, GitHub (V-03) stores the repository, and the orchestrator cloud workspace (V-05) receives checksum-gated copies of git-ignored synthetic data. All data in scope is synthetic (`data_origin` synthetic, OD-04, OD-09).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Data classes (from Stage 11/24, synthetic)
Hub DB and audit store; legacy SQLite DBs (`data/legacy.sqlite3`, 125 cases, seed 4100); data lake (partner feed, vendor CSV, documents); repository code and docs; OD log.

### Matrix
| Data | V-01/V-02 runtime | V-03 GitHub | V-04 AI assistant | V-05 cloud workspace | Any other third party |
|---|---|---|---|---|---|
| Source code, specs, docs, OD log | executes | **stored** (private repo) | **read and written** during sessions | cloned/copied for regression | none |
| `data/*.sqlite3`, `data/lake/` | processed locally | **not committed** (git-ignored; DBs and lake never pushed - SS-02, HAR-09) | may be read in sessions by agents with file access [Inference] | **copied once, checksum-gated** (OD-23) | none |
| Hub DB, audit chain, anchor | processed locally | not stored | not product runtime | created in regression sandboxes; deleted after (OD-16) | none |
| Credentials / secrets | none in repo (secret-scan tests S33) | GitHub credentials held by operator (not in repo) | n/a | Unknown | none |
| Telemetry / logs | stdlib logs on the host | n/a | n/a | Unknown | **none leave the host** |

### Findings
- [Verified Fact] No third-party processor receives data from the running product: no outbound destinations other than loopback gateway URLs; deny-list and egress tripwires E05..E09, E20EGRESS, E21, E23 exist (tests green in recorded runs; not re-run here).
- [Verified Fact] DBs and lake are git-ignored and not committed (engagement-context note; SS-02).
- [Inference] Whether the AI assistant "processes" data files depends on which files its sessions open; the repo cannot show what was transmitted. Confidence Low.
- [Assumption] A-33-07: only synthetic data was ever present in these environments; no personal data, no real GxP records (OD-04, A-0B-01).
- [Unknown] Data location/region, retention and training-use terms for V-03, V-04, V-05.

### Triggers that would create real processor relationships
Any of: non-loopback exposure (HAR-05), hosting, backups to off-host storage (HAR-09), SSO/OIDC (ADR-013 deferred), log/metrics shipping (ADR-016 deferred), introduction of real data (HAR-15). Each requires a processor review and qualified legal review (LR-2) first.

## Evidence References
docs/24-security-privacy/{privacy-impact-assessment,attack-surface-map,data-protection-controls}.md; docs/16-repo-validation/security-scan-summary.md SS-01, SS-02; docs/25-governance/operating-contract-governance-updates.md HAR-08, HAR-09; OD-23, OD-16; .fde/engagement-context.md.

## Assumptions
A-33-07 (see risk assessment) synthetic data only. A-33-08 Operator keeps data out of the remote per HAR-09.

## Unknowns
U-33-11 What the assistant's sessions transmitted; U-33-12 region/retention/training terms of V-03/V-04/V-05; U-33-13 who can read the cloud workspace copies.

## Unresolved Issues
UI-33-06 Confirm with Dinesh that no real or customer-derived data was ever in these environments. Owner: Engagement lead (Dinesh Naik).

## Residual Risks
If real data is introduced, every row in the matrix needs a processor review; today's "none" would not hold.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
