---
stage: "1 — Engage & Qualify"
artifact: "engagement-risks.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/initial-risk-register.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/00-preflight/operating-contract/open-governance-decisions.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Engagement-level risks (delivery, mandate, evidence, governance). Technical/system risks R-01..R-15 stay in `docs/00-preflight/discovery/initial-risk-register.md` and are referenced, not duplicated. Ratings (L/I = Low/Medium/High) are the agent's judgement [Inference] for validation by the engagement lead. All owners: Engagement lead (Dinesh Naik). No containment here proposes a technology or AI solution.

## Findings

| ID | Risk | L | I | Conf. | Evidence | Mitigation / containment | Resolving stage | Status |
|---|---|---|---|---|---|---|---|---|
| ER-01 | Synthetic claims and a simulator are mistaken for validated client evidence; value case overstated | High | High | High | `business-context.md` L3 (synthetic); OD-04 | Tag every client statement as claim; state "synthetic" in all value artifacts | 3, 4, 36, 42 | Open |
| ER-02 | No sponsor/business owner: no one can validate problem, definitions or accept outcomes | High | High | High | Q-04/05/06; GD-01 | Stage 2 either names owners or records a signed waiver by engagement lead; never invent approvals | 2 | Open |
| ER-03 | Baseline dataset unresolved/incoherent → before/after KPIs invalid | High | High | High | R-03; OD-02; U-13 | Confirm or change OD-02 before Stage 4 | 4 | Open |
| ER-04 | Single approver, no independent review of GxP-relevant design | Medium | High | Medium | GD-05; HAR rules | Record as accepted risk or add reviewer | 23, 25 | Open |
| ER-05 | AI anchoring: downstream stages presuppose AI before Stage 8 | Medium | High | Medium | SCOPE-AMB-04; 0C scenarios S3/S4 | Keep AI as hypothesis H6; non-AI scenarios S0–S2 retained | 8 | Open |
| ER-06 | Definitional conflict (48 h closure vs verifiable evidence vs finance "resolved") cannot be settled by engineering | High | High | High | `operations-vs-risk-2024.md`; `historic-decisions.md` 2024 | Escalate as policy decision; do not encode a rule without owner | 2, 3, 6 | Open |
| ER-07 | Baseline loss/corruption during execution stages (test suite overwrites DB; 4+ repo-relative writers; 1,084 lake files un-checksummed) | Medium (controls exist) | High | High | R-01/R-02; WB-F1/F4; OD-03a; GD-03 | Full-copy sandbox only; extend SHA256SUMS before the next code-executing stage | 7 | Open (GD-03) |
| ER-08 | Prompt-injection content in data/docs steers an agent (≥286 strings) | Medium | High | High | DF-08; STOP-05; R-09 | Content-as-data rule in every stage; self-check | all | Controlled, Open |
| ER-09 | Compliance overreach/underreach: Part 11/GxP language treated as obligation (or ignored) without confirmation | Medium | Medium | Medium | A-08; GD-11 | Keep as framing; confirm with risk partner role | 25 | Open |
| ER-10 | Scope drift: Java/JS/SQL consumers, enterprise estate, security hardening undecided | Medium | Medium | High | SCOPE-AMB-01..05; GD-10 | Decide per stage; record in OD log | 2, 5, 24 | Open |
| ER-11 | Timeline/budget unknown; 46-stage plan may be unrealistic vs. capacity of one human approver | Medium | Medium | Low | no SOW; OD-01 | Engagement lead sets pace; BLOCKED-only stop is already approved | 2 | Open |
| ER-12 | Economics envelope (0C) quoted as a business case; all inputs Assumed | Medium | Medium | High | `economics-readiness.md` C-1..C-5 | Always cite "gross, benefits unmodelled" | 8, 32, 36 | Open |
| ER-13 | Remote publication (OD-05) moves repo content off-device; CI-on-push would run destructive tests on runner copy | Low | Medium | Medium | SCOPE-AMB-06; GD-09 | Private repo only; confirm before first push | 25 | Pending |
| ER-14 | Provenance of the baseline archive unproven (no origin repo, ZIP checksum) | Medium | Medium | Medium | A-01; U-01; U-14 | Engagement lead locates original ZIP / records checksum | 2 | Open |

## Evidence References

See `evidence_sources` and per-row citations.

## Assumptions

- Likelihood/impact ratings are judgement. Mitigations are procedural, not technically enforced.

## Unknowns

- Real timeline, budget, sponsor appetite (OQ-07, OQ-08).

## Unresolved Issues

- ER-02, ER-03, ER-06, ER-07 shape Conditional Go conditions (see Go/No-Go).

## Residual Risks

- Even with mitigations, ER-01 and ER-02 remain until real stakeholders exist; the engagement can at most produce a well-evidenced, clearly-labelled synthetic case.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial engagement risk register. |
