---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "agent-security-controls.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "hub/web/*.py", "hub/gate/", "hub/r2/protection.py", "hub/core/untrusted.py", "hub/guards/", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", "docs/12-specs/security-spec.md", "docs/16-repo-validation/security-scan-summary.md", ".fde/orchestrator-decisions.md", "docs/22-agentic-engineering/", "docs/19-intelligence/", "docs/23-human-control/", "docs/25-governance/ai-system-register.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Agent security. The product has no agent, no model and no tool runtime: Stage 19 is Not Applicable and Stage 22 was not triggered (OD-08, OD-25..OD-27). The non-human actors that do exist are service principals (role `integration`) and the run scheduler (switched OFF). Their agency is bounded by design: they can ingest and trigger runs, never act in Zone H, never log in, never re-authenticate. The AI coding assistant that builds the system is development tooling (CP-10) and is controlled by repository rules, not by product code.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AC-1 Non-human actors and their limits [Verified Fact]
| Actor | Can | Cannot | Control | Test |
|---|---|---|---|---|
| service principal (`svc_` token) | ingest items, trigger runs, read allowed endpoints | any Zone H action, login, fresh re-auth, human-only route | role `integration`; `reauth_at` = issue time; role matrix; audited denial | TST-SEC-08, TST-GATE-09, I8 |
| scheduler | nothing: OFF (OPD-11 open) | n/a | config default `off`; no job without a flag | TST-RUN |
| decision flags / capability_authority | default OFF / `shadow` | become authoritative without `approval_ref` | FF-2 rule, CLI + `approval_ref` (OD-31), CONFIG_CHANGED audit, L3 flip | Stage 23 S10..S16 |
| gateway / adapters | read loopback sources | write to legacy, call out | read-only adapters, egress guard | TST-CO-04, TST-CO-12 |
### AC-2 Excessive agency [Verified Fact]
Zone H is one function (`GateService.execute` / `ZoneHActions.execute`), the holder rule is written once, the DB trigger refuses Zone H event types from anywhere else, and `zone_h.holders` is empty in the shipped config. `approval_ref` is only a pointer: the hub cannot verify that a human decision exists behind it (Unknown; recorded since Stage 23).
### AC-3 Insecure tool use [Verified Fact]
No tool interface exists. Imports of HTTP clients are denied outside `hub/adapters/`; `subprocess`, `eval`, `exec`, `pickle`, `ctypes` and `shell=True` do not occur in `hub/` (S31); only 3 constant `__import__` calls exist.
### AC-4 AI coding assistant (build-time) [Assumption]
Controls today: work in a sandbox copy; legacy paths byte-identical (TST-CO-05); non-add edits must be listed with a work item (`tests/hub/non_add_edits.json`); commits carry the assistant attribution; no push without the orchestrator; data checksums verified before and after. Not controlled: the assistant's own tool permissions and prompt handling (outside the repo).

## Evidence References
`hub/web/tokens.py`, `hub/gate/`, `hub/control/`, `docs/23-human-control/autonomy-matrix.md`, `docs/25-governance/ai-system-register.md`, tests above, S31.

## Assumptions
- A-S24-AC-1 The AI coding assistant stays in the AI register (OD-31) and is not part of the product's attack surface.

## Unknowns
- U-S24-AC-1 Whether `approval_ref` values map to real recorded decisions (the hub cannot check).

## Unresolved Issues
- Single approver (DQ-17, accepted as a risk by Dinesh in OD-30).

## Residual Risks
RS-16 (single approver), RS-13.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
