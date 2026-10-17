---
stage: "1 — Engage & Qualify"
artifact: "engagement-canvas.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/decisions/ADR-archived-007.md", "docs/baseline-measurement-notes.md", "docs/operations-service-levels.md", "README.md", "docs/00-preflight/discovery/discovery-summary.md", "docs/00-preflight/operating-contract/scope-boundaries.md", ".fde/engagement-context.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

One-page canvas of the engagement. The "client" is **Gxp Group**, a *fictional* multi-region pharma organisation (`docs/business-context.md` L3: "All people and company records are synthetic"). The engagement is **GxP Quality Hub Modernisation** (FDE capstone). All client-side statements below are **claims from synthetic repo documents**, not validated evidence; no real sponsor, interview, or production telemetry exists (OD-04). Every owner is therefore PROVISIONAL and defaults to Engagement lead (Dinesh Naik).

## Findings

### Canvas

| Block | Content | Class | Source |
|---|---|---|---|
| Client / BU | Gxp Group (fictional), Pharma Quality Intelligence; engagement label "GxP Quality (FDE Capstone)" | [Verified Fact] (as stated in docs) | `docs/business-context.md`; `.fde/engagement-context.md` |
| Stated problem (claim) | "Rising exception-handling effort and inconsistent information between external feeds and the core system" in batch quality review and deviation processing | [Verified Fact] that the claim is written; truth of the claim is [Unknown] | `docs/business-context.md` "Operating concern" |
| Corroborating signals (claims) | 2022 manual reconciliation of delayed ElectronicBatchRecord messages; 2025 rollback after replayed partner delivery inflated exception queue; 2024 competing finance (faster month-end) vs risk (more evidence) requests "both remain active" | [Verified Fact] documented; unverified by any ticket ("original change ticket has not been archived") | `docs/historic-decisions.md` |
| Current system | Python-stdlib + SQLite hub: read-only API :8080, source gateway :8090, ingestion bridge, partner-feed reconciliation, CSV file-drop, night-shift batch, month-end scripts; zero AI calls; no auth; no telemetry; no deployment evidence | [Verified Fact] | `discovery-summary.md`; `security-observability-overview.md` |
| Desired outcome (stated) | "Determine and justify any modernization or AI intervention through business and technical evidence, preserving legitimate workflows." Pending item 2026: "modernization proposal awaiting business baseline measurements and architecture review" | [Verified Fact] (stated) | `docs/business-context.md` "Transformation scope"; `docs/historic-decisions.md` |
| Outcome measures (candidate, not agreed) | Handling time, throughput, case quality, case cost / avoidable rework, uptime/interfaces, reconciliation correctness; archived targets 99.5 % availability, 06:00 reconciliation, 4 h feed acceptance, 24 h stale-signal, RTO 8 h / RPO 24 h | Targets are [Assumption] ("historical working targets, not measured guarantees") | `docs/operations-service-levels.md`; `docs/baseline-measurement-notes.md` |
| Role-based stakeholders (no named people) | Quality operations lead; Enterprise application owner; Finance partner; Risk and security partner; Integration lead | [Verified Fact] role titles only | `docs/business-context.md` |
| Sponsor / business owner / technical owner | **None evidenced.** PROVISIONAL: Dinesh Naik (engagement lead) as sole decision-maker (GD-01). ADR-007 "owner transferred 2024" with no named owner | [Unknown] / [Assumption] | `open-governance-decisions.md` GD-01; `docs/decisions/ADR-archived-007.md` |
| Urgency | No dated deadline, SOW or budget in repo. Only urgency signal is the unresolved 2024 finance-vs-risk conflict and the 2026 proposal "awaiting" baselines | [Unknown] | absence of brief; `docs/historic-decisions.md` |
| Constraints | Stage 0B contract: DESIGN-only writes to own docs folder; `data/` write-prohibited; code only runs in full repo copy outside tree (OD-03a); no production/real-system contact; instruction-like strings in data are data; no automated GxP decisions (HAR-12/STOP-07) | [Verified Fact] | `docs/00-preflight/operating-contract/*`; `.fde/orchestrator-decisions.md` |
| Dependencies | Stakeholder access (none today); baseline dataset decision (OD-02 provisional, U-13); agreement on definitions of "closed"/"resolved"; location of batch disposition (A-07); price/volume inputs for economics (0C C-1..C-5) | [Verified Fact] list of open items | `assumptions-unknowns.md`; `economics-readiness.md` |
| Unresolved definitional conflict | Operations: close deviation/CAPA in 48 h; Compliance: no automatic closure without verifiable evidence; Finance: no agreed "successfully resolved". "Never formalized in the shared policy repository" | [Verified Fact] (as documented) | `docs/correspondence/operations-vs-risk-2024.md` |
| AI posture | Zero AI today; whether AI is a target outcome is an open scope ambiguity; **no AI commitment before Stage 8** | [Verified Fact] / [Unknown] | SCOPE-AMB-04; `solution-scenarios.md` (0C) |

### Claims vs. validated evidence (separation)

| Stakeholder claim (source) | Validated by repo evidence? | Status |
|---|---|---|
| "Rising exception-handling effort" (`business-context.md`) | No trend data; only synthetic modelled costs and a 125-case test-residue DB | Unvalidated claim |
| "Inconsistent information between external feeds and core system" | Yes, structurally: 8,394 orphan `partner_feeds` refs, 3 divergent approval rules, ingestion drops (DF-03, WF-06, IO-01..03) — but on synthetic data | Partly validated (synthetic) |
| "Local interpretations of 'closed' differ" | Yes, 5+ status vocabularies in code/data (WF-11, U-18) | Validated structurally |
| Operations/Compliance/Finance conflict (2024) | Document only; no minutes, no owners | Unvalidated claim |
| 2025 rollback due to replay | Document only; no ticket/log | Unvalidated claim |
| Archived SLOs | Doc states unmeasured | Not evidence |

## Evidence References

See `evidence_sources`; Stage 0A finding IDs (DF-*, WF-*, IO-*, SO-*) in `docs/00-preflight/discovery/`.

## Assumptions

- A-ENG-01: The fictional Gxp Group documents are the intended stand-in for client context for this capstone (confirm: Engagement lead).
- A-ENG-02: Engagement lead is acting as sponsor, business owner and technical owner until Stage 2 confirms otherwise (GD-01).
- A-08 (carried from 0A): GxP / Part 11 references are framing for a training simulator, not an obligation on this code.

## Unknowns

- U-E01 Real sponsor, budget, deadline, success definition. U-E02 Whether the real objective is modernisation, AI, or both. U-E03 Any live production counterpart to this simulator.

## Unresolved Issues

- See `open-qualification-questions.md` (OQ-01..OQ-14).

## Residual Risks

- Treating synthetic documentation as validated client evidence would overstate the business case (ER-01).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial canvas. |
