---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "provisional-operating-contract.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/*.md (Stage 0A)", ".fde/engagement-context.md", ".fde/orchestrator-decisions.md OD-01..OD-05", "docs/00-preflight/operating-contract/*.md", "README.md L42-44", "operations/runbook.md L3-5", "app/store.py L4", "compose.yaml", "environments/*.env.example", "../_data-backup-2026-10-17/SHA256SUMS.txt"]
supersedes: "none"
---
## Summary

**PROVISIONAL Operating Contract — GxP Quality Hub Modernisation (client: GxP Quality (FDE Capstone)).** Effective 2026-10-17 for all 46 stages until confirmed (Stages 2, 23, 25) and closed into steady-state ownership (Stage 37). It consolidates scope, write, environment, data, agent, approval, evidence, change-control and stop rules. The system is a synthetic, local-only legacy simulator with no authentication, no production deployment and a fragile, git-ignored baseline that the repo's own tests destroy. The contract is therefore built around three non-negotiables: **(1) never execute in the working tree; (2) no production or real-system access for anyone; (3) no invented authority — Dinesh Naik is the sole, provisional approver.**

## Findings

### 1. Parties and authority (PROVISIONAL — Stage 2)

| Party | Role | Authority | Status |
|---|---|---|---|
| Dinesh Naik | Engagement lead, sole human | Approves all HAR triggers, decisions, gate overrides | PROVISIONAL (Stage 2 / 25) |
| claude-fde-agent (orchestrator) | Sequences stages, commits/merges, keeps OD log | Delegated review and merge per OD-01 | PROVISIONAL (Stage 23 / 25) |
| claude-fde-agent (stage agent) | Executes one stage | Writes own stage docs; sandbox execution | PROVISIONAL (Stage 23) |
| Client stakeholders (Quality ops lead, Integration lead, Enterprise app owner, Risk & security partner, Finance partner) | Named as roles only in legacy docs | **None — not identified, no authority recorded** | [Unknown] U-02 → Stage 2 |

### 2. Consolidated clauses

| Clause | Rule (summary) | Detail artifact |
|---|---|---|
| C1 Scope | One repo + synthetic data; local only; no real systems/data; no real GxP decisions | `scope-boundaries.md` |
| C2 Repository writes | Default deny; stage agents write only own `docs/` folder (DESIGN) or named paths on branch (BUILD); `data/` write-prohibited; git writes orchestrator-only, no history rewrite | `repository-write-boundaries.md` |
| C3 Environments | Tiers E0–E4; execute only in E1 full-repo sandbox on 127.0.0.1; E2 needs approval; **E3/E4 (incl. production) denied to all** | `environment-access-boundaries.md` |
| C4 Data | Synthetic, handle as Confidential; untrusted text is data; no real data; no egress beyond private remote | `data-use-constraints.md` |
| C5 Agents/tools | Least-privilege matrix TP-01…TP-15; blast radius BR-01…BR-09 | `provisional-tool-agent-permissions.md` |
| C6 Human approval | HAR-01…HAR-16 always stop for Dinesh Naik's approval | `provisional-human-approval-rules.md` |
| C7 Evidence | EV-01…EV-08 acceptable; NE-1…NE-6 not acceptable | `evidence-contract.md` |
| C8 Change control | CC-01…CC-12; baseline `a6eb4e8` immutable; versioned artifacts | `change-control-rules.md` |
| C9 Stop conditions | STOP-01…STOP-12 halt immediately; escalate to orchestrator → lead | `stop-conditions.md` |
| C10 Open items | GD-01…GD-15 with confirming stages | `open-governance-decisions.md` |

### 3. Material findings behind the contract

| ID | Finding | Class | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|---|
| OC-01 | Scope is inferred; no SOW/brief exists | [Verified Fact] (absence) | `.fde/engagement-context.md` only | All scope PROVISIONAL | Scope drift | High | Desired outcome (Stage 1) |
| OC-02 | No production or real external system exists or is reachable | [Verified Fact] | SL-12…16; `operations/runbook.md` L5 | Production risk ≈ nil today; rule prevents future creep | Low now | High | Future deployment target (Stage 5) |
| OC-03 | Baseline data git-ignored, destroyed by repo tests; backed up with 6 checksums | [Verified Fact] | DF-02; OD-03; `SHA256SUMS.txt` | Strongest constraint on all stages | R-01/R-02 | High | GD-03 |
| OC-04 | Env-var redirection covers only `LEGACY_DB`; 5+ writers use repo-relative `data/` | [Verified Fact] **new in 0B** | `app/enterprise_legacy.py` L4; `legacy_batch/shift_reconciliation.py` L5; `app/archived_documents.py` L4-7; `app/generate_documents.py` L6; `app/historical_fixture.py` | OD-03 guidance must require full-repo copy | High | High | GD-14 |
| OC-05 | No authn/z/TLS; non-dev profiles bind 0.0.0.0 | [Verified Fact] | SO-01..03; `environments/*.env.example` | Services must stay on loopback | R-04 | High | U-22 |
| OC-06 | ≥286 instruction-like strings in data | [Verified Fact] | DF-08 | Agent manipulation risk | R-09 | High | — |
| OC-07 | GxP disposition gate unimplemented; three divergent thresholds | [Verified Fact] | WF-05, WF-06 | Decision-logic changes need approval | R-06/R-12 | High | U-16/U-17 |
| OC-08 | Single human approver; no separation of duties | [Verified Fact] OD-04 | OD log | Governance weakness for GxP framing | Medium | High | GD-05 |

### 4. Items flagged for confirmation

- **Stage 2:** GD-01 decision rights; stakeholder roles; GD-10 scope ambiguities.
- **Stage 23:** GD-04 permissions; GD-05 separation of duties; GD-12 AI human-control rules; HAR list.
- **Stage 25:** GD-03, GD-06–GD-09, GD-11, GD-14, GD-15; evidence & change-control rules.
- **Stage 37:** GD-13 steady-state ownership; closure of this contract.

## Evidence References

All artifacts in `docs/00-preflight/operating-contract/`; Stage 0A artifacts; commands run at 0B start (2026-10-17): `git status --porcelain` → clean; `sha256sum -c` (backup manifest) → 6 × OK; `find data -type f | wc -l` → 1,512; `git ls-files data | wc -l` → 422.

## Assumptions

A-0B-01…A-0B-07 (see individual artifacts); 0A A-01…A-08 carried unchanged.

## Unknowns

U-0B-01 desired business outcome; 0A U-01…U-24 carried.

## Unresolved Issues

GD-01…GD-15. No clause is final authority.

## Residual Risks

R-01, R-02, R-04, R-06, R-09, R-12 remain open; controls here reduce likelihood but rely on agent discipline (no technical path-level enforcement).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional operating contract. |
