---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "scope-boundaries.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/discovery-summary.md", "docs/00-preflight/discovery/system-landscape.md", "docs/00-preflight/discovery/assumptions-unknowns.md", "README.md L42-44, L71-77", "operations/runbook.md L3-5", ".fde/engagement-context.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Scope for the **GxP Quality Hub Modernisation** engagement (client: GxP Quality (FDE Capstone)) is derived from Stage 0A evidence and the engagement context only. No SOW, engagement brief or client policy exists in the repository or was supplied; therefore **every scope statement below is PROVISIONAL** until confirmed by the engagement lead in Stage 2 (stakeholders / decision rights) and closed in Stage 37. In scope: the single repository `gxp-quality-hub-legacy/` and its synthetic data, executed only in local/disposable environments. Out of scope: any real client system, production environment, real (non-synthetic) data, and any real GxP decision (e.g. batch disposition).

## Findings

### In scope (PROVISIONAL — confirm Stage 2, close Stage 37)

| ID | Item | Class | Evidence | Confidence |
|---|---|---|---|---|
| SCOPE-IN-01 | Repository `gxp-quality-hub-legacy/` (branch `main`, baseline commit `a6eb4e8`, 548 tracked files at 0A) — all source, config, docs, tests | [Verified Fact] (repo exists) / [Assumption] (that it is the whole engagement scope) | `.fde/engagement-context.md` REPO_ROOT; `git log` | High |
| SCOPE-IN-02 | Components SL-01…SL-11 (Legacy Quality API, Source Gateway, Gateway Bridge, Partner Feeds, Vendor file-drop, Night-shift recon, Java month-end recon, JS policy consumer, reporting, generators, ops scripts) | [Verified Fact] | `system-landscape.md` | High |
| SCOPE-IN-03 | Synthetic data under `data/` (6 SQLite DBs, 1,084 lake JSON/JSONL/CSV, 422 git-tracked documents) — read and sandbox-copy only | [Verified Fact] | `find data -type f` = 1,512 files; `git ls-files data` = 422 | High |
| SCOPE-IN-04 | Engagement artifacts under `docs/<stage-folder>/` produced by the 46-stage spine | [Verified Fact] | `.fde/orchestrator-decisions.md` OD-01 | High |
| SCOPE-IN-05 | Workflows: intake, feed reconciliation, triage/priority, monthly measures, night-shift reconciliation | [Verified Fact] | `workflow-overview.md` | High |
| SCOPE-IN-06 | Local execution in a disposable copy outside the repo (sandbox) and, later, local Docker/Compose on an isolated network | [Verified Fact] (sandbox used in 0A) / [Assumption] (Compose host availability) | `discovery-summary.md` Evidence References; U-09 | Medium |

### Out of scope / explicit exclusions (PROVISIONAL)

| ID | Exclusion | Class | Evidence / reasoning |
|---|---|---|---|
| SCOPE-OUT-01 | Any real client production system, MES/EBR, LIMS-QMS, partner gateway, ERP/CRM, SharePoint/ECM | [Verified Fact] none are integrated | `system-landscape.md` SL-12…SL-16; `operations/runbook.md` L5 |
| SCOPE-OUT-02 | Real (non-synthetic) personal, patient, product or batch data | [Verified Fact] only synthetic data present | README L44; `app/archived_documents.py` L1 docstring; `example.invalid` addresses (DF-07) |
| SCOPE-OUT-03 | Making or automating real GxP decisions — batch disposition / release, QA signature, e-record approval | [Verified Fact] not implemented; [Assumption] A-07 performed outside | `workflow-overview.md` WF-05; `operations/runbook.md` L5 |
| SCOPE-OUT-04 | Compliance certification (21 CFR Part 11 / GMP) of this code | [Assumption] A-08 | README L44 "not certified"; `docs/domain-assurance.md` |
| SCOPE-OUT-05 | Cloud provisioning, paid services, real identity providers, real secrets | [Inference] none referenced in repo | SO-04 (no secrets); no IaC in repo |
| SCOPE-OUT-06 | Rewriting VCS history of `main`, or changing `.fde/` control files from a stage agent | Contract rule | OD-01; this contract |

### Ambiguous (needs decision)

| ID | Item | Class | Why ambiguous | Confirming stage |
|---|---|---|---|---|
| SCOPE-AMB-01 | Java (`legacy_java/`) and JS (`legacy_js/`) consumers, `sql/legacy_reports.sql` — modernise, retire or leave? | [Unknown] U-04/U-07/U-19 | No schedules or consumers evidenced | 2 / 5 |
| SCOPE-AMB-02 | Night-shift estate (`enterprise_legacy.sqlite3`) and data lake — part of the modernisation target or reference only? | [Unknown] | Disjoint data models (DF-09) | 2 / 5 |
| SCOPE-AMB-03 | Authoritative "before" dataset (125-case shipped DB vs 6,000-case seed 4326) | [Unknown] U-13; OD-02 provisional default = shipped DB | Test residue | 1 → 4 |
| SCOPE-AMB-04 | Whether an AI/agentic capability is a target outcome (zero model calls today) | [Unknown] | No brief/SOW | 1 / 2 |
| SCOPE-AMB-05 | Security hardening (authn/z, TLS) — in scope or only documented | [Unknown] U-22 | SO-01..03 | 24 |
| SCOPE-AMB-06 | Publishing the repo to GitHub remote (OD-05) — content leaves the device | [Verified Fact] OD-05 "Pending repo creation" | Data egress boundary | 25 |

## Evidence References

`.fde/engagement-context.md`; `.fde/orchestrator-decisions.md` OD-01…OD-05; `README.md` L42-44 ("educational simulated enterprise system … not certified"); `operations/runbook.md` L5 ("no access to production customer systems … or pharmaceutical batch disposition"); 0A `system-landscape.md`, `workflow-overview.md`, `data-flow-overview.md`; command output `find data -type f | wc -l` → 1512, `git ls-files data | wc -l` → 422.

## Assumptions

- A-0B-01: No SOW or engagement brief exists beyond `.fde/engagement-context.md`; scope is therefore inferred. Confirm: Engagement lead (Dinesh Naik), Stage 2.
- A-03, A-07, A-08 (from 0A) carried forward unchanged.

## Unknowns

- U-0B-01: The engagement's desired business outcome / success criteria (Stage 1/3).
- SCOPE-AMB-01…06 above.

## Unresolved Issues

- All scope items are PROVISIONAL; none have stakeholder approval.

## Residual Risks

- Scope creep into real-system integration if later stages assume A-03 real contracts exist (R-10 documentation drift).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional scope from Stage 0A evidence. |
