---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "portability-assessment.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Portability is **good for code and documents, moderate for the datastore, and environment-bound for goldens**. Code and docs are plain text in git; the datastore is SQLite files with a checksum-verified backup pattern; goldens are tied to Python 3.10.12. The assessment lists what moves, how, and how it would be verified, without executing anything (docs-only stage).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| Asset | Target form | Portability | Method (proposed) | Verification | Blockers | Confidence |
|---|---|---|---|---|---|---|
| Source code, docs, OD log | any git host | High | `git push --mirror` to another remote; full local clones already exist | commit SHAs equal; `git fsck` | account access only | High |
| PR/review history | export | Low-Medium | export PR text before any host change | manual compare | GitHub-specific data | Medium |
| Hub datastore (`hub.sqlite3`, audit store, anchor file) | same engine on another host; or other engine | High (same engine) / Medium (other engine) | file copy + `sha256sum -c`; audit chain `verify-audit` | chain verifies; SHA256SUMS match (as done for `_data-backup-2026-10-17`) | SQLite version floor 3.37; FTS5 optional | Medium |
| Legacy DBs and data lake | same | High | file copy with SHA256SUMS (OD-03/03a) | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` | working-tree `data/` never run against (OD-03a) | High |
| Test suites | any host with Python | High for hub regression; environment-bound for goldens | `run_hub_groups.py --all` (any Python >=3.10); goldens on 3.10.12 only | 419 methods executed = expected | goldens re-baseline needed to move runtime | Medium |
| Runtime packaging | container or venv | Medium | Dockerfile exists but never executed; non-loopback needs HAR-05 | n/a today | HAR-05, HAR-07 | Low |
| Assistant-authored artefacts | humans or other tools | High | all plain text | review | none | Medium |
| Legacy JDK/Node scripts | any JDK >= 11 / Node | High | run from repo-root cwd | CT harness | cwd-relative paths (DM-13) | High |

### Findings
- [Verified Fact] Backup/restore pattern with checksum manifest exists and was used (OD-03); a restore rehearsal for the hub is an R1 deliverable (PNFR-05) and is not evidenced as done [Unknown].
- [Verified Fact] No data export format of any third-party service is needed to recover product state.
- [Inference] Time to rebuild the whole engagement environment on fresh infrastructure is bounded by golden re-baselining and a pinned runtime, not by vendor data return. Confidence Low (not rehearsed).

## Evidence References
docs/10-architecture/deployment-architecture.md DA-3; docs/07-repo-assessment/dependency-map.md; OD-03, OD-03a, OD-23; tests/hub/run_hub_groups.py (not executed).

## Assumptions
A-33-11 The methods are proposals; none was rehearsed in this docs-only stage.

## Unknowns
U-33-17 Whether a hub restore rehearsal was ever performed. U-33-18 Elapsed time for a clean rebuild.

## Unresolved Issues
UI-33-09 A portability rehearsal (mirror push + clean-checkout regression + restore) is proposed for Stage 38 (handover) / 27; not scheduled. Owner: Engagement lead (Dinesh Naik).

## Residual Risks
Unrehearsed portability is a hypothesis until exercised.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
