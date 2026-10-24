---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "exit-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

Exit plans for **every critical entry (V-01..V-05)** plus a short plan for the non-critical items. Each plan has trigger, steps, data return, verification, owner, rough effort and what is unknown. **Owner of every plan is proposed as the Engagement lead (Dinesh Naik) with role holders for SH-04/SH-06/SH-07 vacant (GAP, accountability-map AM-1)**; no other owner exists. Effort figures are order-of-magnitude [Inference] and not costed (Stage 32 absent). Because no contract exists, there is no notice period, exit fee or data-return clause to cite: those are Unknown, not "none".

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Common steps for every exit
1. Trigger recorded as an OD entry by the orchestrator after Dinesh's message (HAR-11).
2. Freeze: stop merges to main; tag the current HEAD.
3. Export: take the assets listed in `portability-assessment.md`; write SHA256SUMS.
4. Stand up the replacement; run verification; compare to the frozen tag.
5. Cut over by a recorded human decision; keep the old service read-only until verification passes.
6. Record lessons in the change history of this artifact (new version, never overwrite).

### Per-vendor plans
| ID | Exit trigger | Steps specific to this vendor | Data / asset return | Verification | Effort (order of magnitude) | Unknown |
|---|---|---|---|---|---|---|
| V-01 CPython | EOL or unfixed CVE on production/evidence host | adopt 3.12+ on hosts; run CI both versions; re-baseline goldens; update ADR-018 / OD-S12-12 record | none (no data held) | hub regression all groups; golden-compare with approved deviations only | days (Assumption) | EOL date; distro patch cadence |
| V-02 SQLite | engine CVE, concurrency/HA need | (version bump) install newer SQLite/Python and rerun; (engine change) ADR + port repository layer + migrate audit chain and re-verify | DB files are already local; copy with SHA256SUMS | `verify-audit`, checksum, hub regression | days (version) / weeks (engine change) (Assumption) | production concurrency profile |
| V-03 GitHub | lockout, outage, terms change, ownership change | create new remote; `git push --mirror`; export PR text; update remote URL records (OD-05); re-point CI file | full history is in local clones; PR text exported manually | `git ls-remote` SHAs match; `git fsck` | hours to a day | terms, export tooling, repo settings |
| V-04 AI coding assistant | unavailability, terms or price change, quality problem | pause build work; document working agreements (`.fde/`); hand to another assistant or developers; require golden-compare and hub regression on every first change | none held by the product; session context is lost | tests unchanged and green; reviewer reads diffs | days to onboard (Assumption) | terms, retained context, output licence (LR-3) |
| V-05 Cloud workspace | provider change, cost, outage | provision another runner with Python >=3.10; copy checksum-gated data; run `run_hub_groups.py --all`; confirm 419 methods executed = expected | delete copies at the old provider (HAR-09 off-device data) and record deletion | executed = expected; data checksums | hours to a day | provider's deletion/retention terms |
| V-06 Actions | tag move, outage | pin by SHA or drop CI | none | CI green once enabled | hours | |
| V-07 Docker image | image change | pin digest or build without Docker | none | smoke test (HAR-05 needed to run) | hours | |
| V-08 / V-09 | version drift | pin versions or retire legacy at Stage 41 | none | CT harness | hours | |
| V-10 Laptop/VM | hardware loss | restore repo + data backup to another Python 3.10.12 host | backup `_data-backup-2026-10-17` + SHA256SUMS | goldens equal baseline | day (Assumption) | OS vendor |
| V-11 Counterparties | none real | n/a | n/a | n/a | n/a | re-plan if real sources named |

### Findings
- [Verified Fact] The product can be exited from every vendor above without vendor cooperation, because assets are local files and git history is replicated.
- [Verified Fact] Completion Gate "every critical vendor has a scorecard and exit plan": satisfied on paper for V-01..V-05; none of the plans has been rehearsed [Unknown/Inference].
- [Unknown] Data deletion proof for V-03/V-04/V-05 (relevant only if non-synthetic data were ever sent).

## Evidence References
docs/33-vendor-risk/{portability-assessment,substitution-strategy}.md; docs/25-governance/accountability-map.md AM-1; docs/10-architecture/deployment-architecture.md DA-3; OD-03, OD-05, OD-13, OD-21, OD-23, HAR-09, HAR-11.

## Assumptions
A-33-14 Effort figures are rough and uncosted. A-33-15 The proposed owner (Dinesh) has not accepted the plans.

## Unknowns
U-33-20 Notice periods, deletion proofs and data-return rights (no contracts).

## Unresolved Issues
UI-33-11 No exit rehearsal done; recommended before any production use. Owner: Engagement lead (Dinesh Naik).

## Residual Risks
Unrehearsed exits may take longer than stated.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
