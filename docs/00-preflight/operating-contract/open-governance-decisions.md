---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "open-governance-decisions.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md", "docs/00-preflight/discovery/assumptions-unknowns.md", "docs/00-preflight/operating-contract/*.md (this folder)"]
supersedes: "none"
---
## Summary

Every unresolved governance item from Stage 0B, each with its confirming stage (2 = stakeholders/decision rights, 23 = human-control rules, 25 = governance, 37 = steady-state ownership; other stages where the item is substantive). Owner of every item: **Engagement lead (Dinesh Naik)** — no other owner exists (OD-04). None is blocking for Stage 0C or Stage 1; GD-03 and GD-14 must be closed before the next stage that executes code.

## Findings

| ID | Open decision | Current provisional position | Class | Owner | Confirming stage | Due | Blocking? |
|---|---|---|---|---|---|---|---|
| GD-01 | Decision rights & approver(s) | Dinesh Naik sole approver — PROVISIONAL | [Assumption] A-0B-06 | Engagement lead (Dinesh Naik) | 2 → 37 | Start of Stage 2 | No |
| GD-02 | Authoritative baseline dataset | Shipped 125-case DB (OD-02 provisional default) | [Unknown] U-13 | Engagement lead (Dinesh Naik) | 1 → 4 | Before Stage 4 | No (Yes for Stage 4) |
| GD-03 | Extend backup checksum manifest to all 1,512 data files (lake JSON/JSONL/CSV + documents) | 6 SQLite only | [Verified Fact] WB-F4 | Engagement lead (Dinesh Naik) / orchestrator | 25 (action now) | Before next code-executing stage | No for 0C/1 |
| GD-04 | Confirm tool/agent permission matrix TP-01…TP-15 | As drafted | PROVISIONAL | Engagement lead (Dinesh Naik) | 23 / 25 | Stage 23 | No |
| GD-05 | Separation of duties for GxP-relevant changes (second approver?) | Single approver | [Unknown] | Engagement lead (Dinesh Naik) | 23 / 25 | Stage 23 | No |
| GD-06 | Environment ownership; availability of an isolated Docker host (E2) | None exists | [Unknown] U-05/U-09 | Engagement lead (Dinesh Naik) | 5 / 7 / 25 | Before Stage 7 runtime checks | No |
| GD-07 | Retention of sandbox execution logs as evidence | Excerpts in stage artifacts only | [Unknown] | Engagement lead (Dinesh Naik) | 25 | Stage 25 | No |
| GD-08 | Tag `a6eb4e8` as `baseline-as-found` | Recommended | Recommendation | Engagement lead (Dinesh Naik) / orchestrator | 25 | Before first BUILD stage | No |
| GD-09 | Create private GitHub remote; accept CI-on-push (runs destructive tests on runner copy only) | OD-05 pending | [Verified Fact] | Engagement lead (Dinesh Naik) | 25 | Before first push | No |
| GD-10 | Scope ambiguities SCOPE-AMB-01…05 (Java/JS/SQL consumers, enterprise estate, AI target outcome, security hardening) | Unresolved | [Unknown] | Engagement lead (Dinesh Naik) | 1 / 2 / 5 / 24 | Per stage | No |
| GD-11 | GxP / Part 11 statements are framing, not a compliance obligation (A-08) | Assumed | [Assumption] | Engagement lead (Dinesh Naik) | 25 | Stage 25 | No |
| GD-12 | Human-control rules for any AI/agent capability introduced into the product (HAR-10/HAR-12) | Always human-approved; no automated GxP decisions | PROVISIONAL | Engagement lead (Dinesh Naik) | 23 | Stage 23 | No |
| GD-13 | Steady-state ownership of the contract, repo, data and runbooks after engagement | None | [Unknown] U-02 | Engagement lead (Dinesh Naik) | 37 | Stage 37 | No |
| GD-14 | Amend OD-03: env-var redirection is insufficient (WB-F1) — require full-repo sandbox copy | This contract mandates full copy | [Verified Fact] | Orchestrator → Engagement lead (Dinesh Naik) | 25 (record now in OD log) | Before next code-executing stage | No for 0C/1 |
| GD-15 | Precedence of instructions (lead > OD log > contract > stage prompt > legacy docs) | As drafted | PROVISIONAL | Engagement lead (Dinesh Naik) | 25 | Stage 25 | No |

## Evidence References

See linked artifacts in this folder and 0A `assumptions-unknowns.md`.

## Assumptions

- All positions above are PROVISIONAL; none is final authority.

## Unknowns

- As listed.

## Unresolved Issues

- All 15 items open.

## Residual Risks

- If GD-03/GD-14 are not closed before code-executing stages, a data-loss incident could be undetectable (lake files) or caused by a non-env-configurable writer.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial open governance decisions. |
