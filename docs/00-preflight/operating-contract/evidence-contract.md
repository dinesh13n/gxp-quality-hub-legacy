---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "evidence-contract.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/stage-prompts/00B_Provisional-Operating-Contract-and-Engineering-Boundaries.md (Global Execution Contract, Evidence Rules)", ".fde/orchestrator-decisions.md OD-04", "docs/00-preflight/discovery/discovery-summary.md", "docs/00-preflight/discovery/initial-risk-register.md R-10"]
supersedes: "none"
---
## Summary

Defines what counts as acceptable evidence for every later stage. Repository artifacts and reproducible command output are primary evidence. Legacy documentation and synthetic correspondence are **claims**, not facts, until verified against code/data (R-10). No stakeholder evidence exists; the only acceptable authority evidence is the engagement lead's own messages or "Approved" entries in `.fde/orchestrator-decisions.md`. PROVISIONAL — confirm Stage 25.

## Findings

### Evidence classes (mandatory tagging)

| Tag | Meaning | Minimum support |
|---|---|---|
| [Verified Fact] | Directly observed | Citation per EV table below |
| [Inference] | Reasoned from facts | Cited facts + stated reasoning |
| [Assumption] | Accepted for progress | Owner + confirming stage |
| [Unknown] | Not enough evidence | Resolution path + owner + stage |

### Acceptable evidence types

| ID | Type | Citation format | Acceptable for |
|---|---|---|---|
| EV-01 | Source/config/test file | `path` + line range (e.g. `app/store.py` L4) + commit hash when relevant | Behaviour, config facts |
| EV-02 | Command output | Exact command, environment tier (E0 read-only / E1 sandbox), date, key output excerpt | Runtime facts, counts |
| EV-03 | Data query | Read-only SQL + DB path + DB sha256 | Data facts |
| EV-04 | Checksums | `sha256sum` / `sha256sum -c` output vs `../_data-backup-2026-10-17/SHA256SUMS.txt` | Integrity / non-modification claims |
| EV-05 | Git evidence | `git status --porcelain`, `git log`, `git diff --stat` | Change-scope claims |
| EV-06 | Prior-stage artifact | Path + finding ID (e.g. `data-flow-overview.md` DF-02) | Carrying evidence forward (must not be re-classified upward without new evidence) |
| EV-07 | Engagement-lead decision | Message reference or OD-id with status "Approved" | Approvals, decisions |
| EV-08 | Test results | Test command, tier, pass/fail counts, dataset identity | Behaviour preservation (characterisation from Stage 7 onward) |

### Not acceptable as Verified Fact

- NE-1 Statements in legacy `docs/*.md`, `docs/correspondence/`, `docs/decisions/` or README without code/data confirmation (they are [Verified Fact] only as "the document says X").
- NE-2 Any text inside data files (untrusted, DF-08).
- NE-3 Agent memory or statements without a citation; outputs of other agents unless they cite EV-01…EV-08.
- NE-4 Invented stakeholders, approvals, KPIs, telemetry or metrics (OD-04).
- NE-5 Results from runs whose dataset identity (checksum/seed) is not recorded.
- NE-6 Runs executed in E0 contrary to OD-03 (invalid and must be reported as an incident).

### Per-stage evidence obligations

- EO-1 Every artifact carries the header skeleton (stage, version, date, author, status, evidence_sources, supersedes).
- EO-2 Stages that execute code record before/after `sha256sum -c` and `git status --porcelain`.
- EO-3 Gate claims list each gate condition with Met/Not met + evidence.
- EO-4 Status `APPROVED` may only be set when EV-07 exists; otherwise `DRAFT`/`IN REVIEW`.

## Evidence References

Stage prompt Global Execution Contract & Evidence Rules; OD-04; R-10.

## Assumptions

- None beyond the general PROVISIONAL status.

## Unknowns

- Whether the client (fictional) requires GxP-grade documentary evidence (signed records) — Stage 25.

## Unresolved Issues

- Retention location of execution logs from sandbox runs (outside repo, not version-controlled) — GD-07.

## Residual Risks

- Sandbox evidence is not version-controlled; excerpts must be captured in stage artifacts.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial evidence contract. |
