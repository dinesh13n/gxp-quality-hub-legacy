---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "assumptions-unknowns.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["all Stage 0A discovery artifacts", "docs/*.md", "README.md", "PRELOADED_DATA.md"]
supersedes: "none"
---
## Summary

Register of every assumption (8) and unknown (24) raised during Stage 0A, with how each will be resolved, the owner and the resolving stage. No stakeholder is available to this run; all owners default to the engagement lead. One unknown (U-13 / A-02, identity of the baseline dataset) is **blocking for Stage 4** but not for Stages 0B–1. U-14 (original data snapshot) is urgent because the baseline data is git-ignored and is destroyed by the documented test commands.

## Findings

### Assumptions

| ID | Assumption | Class | How to confirm | Owner | Resolving stage | Blocking? |
|---|---|---|---|---|---|---|
| A-01 | Commit `a6eb4e8` reproduces the supplied legacy archive unmodified (commit message claims so). | [Assumption] | Compare against original ZIP checksum. | Engagement lead (Dinesh Naik) | 1 | No |
| A-02 | The documented dataset (`app.generate --count 6000 --seed 4326`) is the intended 'before' baseline, not the 125-case DB actually shipped. | [Assumption] | Decision by engagement lead; record in Stage 4 baseline plan. | Engagement lead (Dinesh Naik) | 4 (decide by Stage 1) | No for 0A; **Yes for Stage 4** |
| A-03 | Named upstream systems (EBR/MES, LIMS-QMS, PartnerGateway) stand in for real client systems; their real contracts are out of repo scope. | [Assumption] | Confirm with Integration lead role. | Engagement lead (Dinesh Naik) | 2 / 5 | No |
| A-04 | Python 3.10 upstream EOL is Oct 2026 (public CPython schedule, not repo evidence). | [Assumption] | Check python.org release schedule. | Engagement lead (Dinesh Naik) | 7 | No |
| A-05 | The Compose topology is the best proxy for the 'production-like' runtime. | [Assumption] | Confirm with Enterprise application owner role. | Engagement lead (Dinesh Naik) | 0B / 5 | No |
| A-06 | Real upstream delivery semantics resemble the simulator (offset pull, replays, schema drift). | [Assumption] | Integration lead interview. | Engagement lead (Dinesh Naik) | 5 | No |
| A-07 | `batch_disposition` is performed and recorded outside this system ('local systems'). | [Assumption] | Quality operations lead interview. | Engagement lead (Dinesh Naik) | 2 / 5 | No |
| A-08 | GxP / 21 CFR Part 11 references are framing for a training simulator, not a compliance obligation on this code. | [Assumption] | Engagement lead + Risk & security partner role. | Engagement lead (Dinesh Naik) | 0B / 25 | No |

### Unknowns

| ID | Unknown | Class | Current evidence | Resolution path | Owner | Resolving stage | Blocking? |
|---|---|---|---|---|---|---|---|
| U-01 | Upstream VCS history / origin repo | [Unknown] | No remote; 2 commits only | Ask engagement sponsor for origin repo | Engagement lead (Dinesh Naik) | 1 | No |
| U-02 | Named owners per component / role | [Unknown] | Only role titles in docs | Stakeholder discovery | Engagement lead (Dinesh Naik) | 2 | No |
| U-03 | Authoritative seed (4100 default vs 4326 documented) | [Unknown] | `app/generate.py` L49 vs README/CI/domain.json | Decision record | Engagement lead (Dinesh Naik) | 4 | No |
| U-04 | Which components are operational vs dormant (Java, JS, SQL report, file-drop import) | [Unknown] | No schedules, no deployment evidence | Stakeholder interviews; Stage 7 characterisation | Engagement lead (Dinesh Naik) | 5 / 7 | No |
| U-05 | Real deployment topology / host | [Unknown] | Only `.env.example` + Compose | Enterprise app owner | Engagement lead (Dinesh Naik) | 5 | No |
| U-06 | Python version in client runtime | [Unknown] | 3.10 / 3.12 both referenced | Enterprise app owner | Engagement lead (Dinesh Naik) | 7 | No |
| U-07 | Whether Java/Node consumers run on any schedule | [Unknown] | No scheduler config | Interviews | Engagement lead (Dinesh Naik) | 5 | No |
| U-08 | The 'obsolete service endpoint' in ADR-007's diagram | [Unknown] | Diagram not in repo | Request diagram | Engagement lead (Dinesh Naik) | 5 / 10 | No |
| U-09 | Whether `docker compose up` works end-to-end | [Unknown] | Docker unavailable on device; PRELOADED_DATA.md L30 says not executed | Run on Docker host in Stage 7 | Engagement lead (Dinesh Naik) | 7 | No |
| U-10 | Consumers of the outbound API | [Unknown] | No client code | Interviews / access logs (none exist) | Engagement lead (Dinesh Naik) | 5 | No |
| U-11 | Whether manual reconciliation of delayed EBR messages (2022 decision) is current practice | [Unknown] | Only historic note | Quality ops lead | Engagement lead (Dinesh Naik) | 5 | No |
| U-12 | Officially supported schema versions (feeds 1.0/1.1/2.0; gateway 0.9/1.0; contract v1) | [Unknown] | Contract file unenforced | Integration lead | Engagement lead (Dinesh Naik) | 5 / 7 | No |
| U-13 | Which dataset is authoritative for the 'before' KPI baseline | [Unknown] | Shipped DB = test residue (125 cases) | Engagement-lead decision (see A-02) | Engagement lead (Dinesh Naik) | 1 → 4 | **Yes for Stage 4**; non-blocking for 0A/0B/0C/1 |
| U-14 | Availability of the original, untouched ZIP / data snapshot | [Unknown] | PRELOADED_DATA.md L34 asks to keep it | Engagement lead to locate and record checksum | Engagement lead (Dinesh Naik) | 0B | No (but urgent) |
| U-15 | Real data classification and retention policy | [Unknown] | Only synthetic `access_level`, `retention_events` | Risk & security partner | Engagement lead (Dinesh Naik) | 24 | No |
| U-16 | Which approval-threshold implementation is authoritative (Python 50,000 / JS archive limits ×1.05 / policy_register 2,500–8,500) | [Unknown] | Three divergent rules | Quality ops lead + Risk partner | Engagement lead (Dinesh Naik) | 5 / 6 | No |
| U-17 | Where batch-disposition decisions are recorded | [Unknown] | Not in code | Quality ops lead | Engagement lead (Dinesh Naik) | 5 | No |
| U-18 | Canonical status model ('closed', completion flag MES vs QA) | [Unknown] | 5+ vocabularies | Cross-team workshop | Engagement lead (Dinesh Naik) | 5 / 9 | No |
| U-19 | Who consumes the JS 'front-end' thresholds | [Unknown] | No front-end in repo | Enterprise app owner | Engagement lead (Dinesh Naik) | 5 | No |
| U-20 | Whether CI has ever run | [Unknown] | No remote / logs | Origin repo CI history | Engagement lead (Dinesh Naik) | 7 | No |
| U-21 | Intended test-data isolation design | [Unknown] | Tests clobber default DB | Stage 7 characterisation | Engagement lead (Dinesh Naik) | 7 | No |
| U-22 | Identity provider / user roles | [Unknown] | No auth anywhere | Risk & security partner | Engagement lead (Dinesh Naik) | 24 | No |
| U-23 | Whether archived RTO 8 h / RPO 24 h / 99.5% are still targets | [Unknown] | Doc says historical, unmeasured | Enterprise app owner | Engagement lead (Dinesh Naik) | 31 | No |
| U-24 | Business KPI values (handling time, backlog ageing, cost per case) for the real estate | [Unknown] | Only synthetic modelled costs | Finance partner + Quality ops lead | Engagement lead (Dinesh Naik) | 4 | No for 0A |

## Evidence References

See the per-artifact citations in `repository-overview.md`, `system-landscape.md`, `technology-inventory.md`, `high-level-architecture.md`, `integration-overview.md`, `data-flow-overview.md`, `workflow-overview.md`, `test-overview.md`, `security-observability-overview.md`.

## Assumptions

All assumptions are listed above; none is presented elsewhere as fact.

## Unknowns

All unknowns are listed above.

## Unresolved Issues

- No stakeholder evidence exists in the repo beyond role descriptions and synthetic correspondence; every stakeholder-dependent item remains Open.
- Due dates: none can be committed without stakeholders; each item is due **before its resolving stage starts**.

## Residual Risks

- Assumptions A-02 and A-07, if wrong, would invalidate the Stage 4 baseline and Stage 5 process map respectively.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
