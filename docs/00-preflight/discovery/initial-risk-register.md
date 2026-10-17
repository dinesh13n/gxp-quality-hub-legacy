---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "initial-risk-register.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["all Stage 0A discovery artifacts"]
supersedes: "none"
---
## Summary

15 early risks identified from read-only discovery. Five are rated High likelihood × High impact: R-01 (test suite destroys baseline), R-02 (baseline data unversioned), R-03 (shipped DB incoherent), R-06 (divergent decision rules), R-12 (GxP disposition gate unimplemented) — plus R-09/R-15 which become High once later stages start. "Next discovery action" entries are containment or investigation actions only — **no transformation, technology or AI recommendations are made**.

## Findings

| ID | Risk | Likelihood | Impact | Confidence | Evidence (artifact finding IDs) | Next discovery / containment action | Owner | Resolving stage | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Baseline destroyed/altered by running the documented test/preflight commands (tests write to the real `data/legacy.sqlite3`; reproduced 6,000 → 125 cases). | High | High | High | TO-03, DF-02 | Treat `data/` as read-only; run any command only in a disposable copy; record checksums (pre-inspection SHA-256 `legacy.sqlite3` = c254649f…d70aa). | Engagement lead (Dinesh Naik) | 0B (boundary) / 7 (characterise) | Open |
| R-02 | Baseline data is git-ignored (`data/*.sqlite3`, `data/lake/`) — not versioned, easily lost; fresh clones lack it. | High | High | High | RO-05 | Locate original ZIP; snapshot + checksum outside working tree (U-14). | Engagement lead (Dinesh Naik) | 0B | Open |
| R-03 | Shipped DB is internally incoherent (125 cases vs 8,394 orphan partner_feeds refs, 222 orphan policy_exceptions; cost table 108 cases) — KPIs computed from it would be misleading. | High (already present) | High | High | DF-01, DF-03, IO-10 | Decide baseline dataset (A-02/U-13) before any KPI capture. | Engagement lead (Dinesh Naik) | 1 → 4 | Open |
| R-04 | No authentication/authorisation/TLS on any endpoint; all tenants' data returned to any caller; bind 0.0.0.0 in container configs. | Medium (simulator)  | High (if exposed) | High | SO-01–SO-03 | Keep services on isolated/local networks only during the engagement. | Engagement lead (Dinesh Naik) | 0B / 24 | Open |
| R-05 | Shared-SQLite integration DB couples API, gateway, bridge, feeds and reports (single writer, schema DDL from GET). | Medium | Medium | High | HA-01–HA-04, SL relationships | Deep coupling analysis. | Engagement lead (Dinesh Naik) | 7 | Open |
| R-06 | Same approval/priority decision implemented 3 ways with different thresholds (50,000 / regional limit×1.05 with permissive 999,999 default / 2,500–8,500); approval roles in policy archive not used by code. | High | High | High | WF-06 | Establish authoritative rule with stakeholders before any behaviour change. | Engagement lead (Dinesh Naik) | 5 / 6 | Open |
| R-07 | Compose runtime may diverge: gateway reads image DB copy while API/bridge use volume; fresh-clone build lacks DB → empty API. | Medium | Medium | Medium | HA-05, HA-06 | Verify on Docker host. | Engagement lead (Dinesh Naik) | 7 | Open |
| R-08 | Ingestion has no retry/backoff; unknown-key events dropped without persistence; partner status overwritten in place (no history). | Medium | Medium | High | IO-01–IO-03 | Characterise failure behaviour. | Engagement lead (Dinesh Naik) | 7 | Open |
| R-09 | Instruction-like untrusted text embedded in feeds, documents, events and archives (≥ 286 occurrences across corpora: 22 + 4 + 86 + 9 + 15 + 150). | High (if any automated/AI consumer is added) | High | High | DF-08, SO-06 | Carry as explicit constraint into 0B, 11, 24, 26. | Engagement lead (Dinesh Naik) | 0B / 24 / 26 | Open |
| R-10 | Documentation drift and contradictions (README triplicated section, seed mismatch, claimed 6,000 cases, historic SQL Server/Oracle, obsolete ADR diagram). | High | Medium | High | RO-07, HA-10 | Treat docs as claims; verify against code/data. | Engagement lead (Dinesh Naik) | 5 / 7 | Open |
| R-11 | Runtime currency: minimum Python 3.10 at/after upstream EOL (assumption A-04); unpinned base image and CI runner. | Medium | Medium | Medium | TI-01, TI-07 | Confirm EOL and runtime versions. | Engagement lead (Dinesh Naik) | 7 | Open |
| R-12 | GxP-critical `batch_disposition` human-approval gate exists only in documents/policy data; no implementation or audit trail. | High | High | High | WF-05, SO-09, SO-10 | Locate where disposition is actually performed (A-07/U-17). | Engagement lead (Dinesh Naik) | 2 / 5 | Open |
| R-13 | Thin, order-dependent test suite — behavioural regressions would go undetected. | High | Medium | High | TO-01, TO-03, TO-07 | Characterisation baseline. | Engagement lead (Dinesh Naik) | 7 | Open |
| R-14 | No operational telemetry (gateway logs disabled, no metrics/tracing/alerts); historic SLOs unmeasured. | High | Medium | High | SO-12–SO-17 | Observability baseline. | Engagement lead (Dinesh Naik) | 7 / 31 | Open |
| R-15 | Unresolved definitional conflicts ('closed', completion flag, 48 h closure vs compliance, finance 'resolved') block KPI definition; no real stakeholders available to this run. | High | High | High | WF-11 | Stakeholder discovery; record as open decisions. | Engagement lead (Dinesh Naik) | 2 / 3 / 4 | Open |

All risk statements are [Inference] grounded in the cited [Verified Fact] findings; likelihood/impact ratings are the agent's judgement and need validation by the engagement lead.

## Evidence References

Finding IDs refer to: RO-* `repository-overview.md`; SL-* `system-landscape.md`; TI-* `technology-inventory.md`; HA-* `high-level-architecture.md`; IO-* `integration-overview.md`; DF-* `data-flow-overview.md`; WF-* `workflow-overview.md`; TO-* `test-overview.md`; SO-* `security-observability-overview.md`.

## Assumptions

- Ratings assume the repository is a training simulator on isolated networks (README "Boundary"); exposure on a shared network would raise R-04.

## Unknowns

- See `assumptions-unknowns.md` (notably U-13, U-14, U-16, U-17).

## Unresolved Issues

- No due dates can be committed without stakeholders; each risk is due for review at the start of its resolving stage.

## Residual Risks

- Risk ratings themselves are unvalidated (no stakeholder input).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
