---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "manual-handoffs.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["operations/incidents/INC-2025-014.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "docs/correspondence/operations-vs-risk-2024.md", "operations/runbook.md", "operations/baseline-evidence.md", "app/partner_feeds.py", "app/gateway_bridge.py", "compose.yaml", "data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)", "docs/business-context.md"]
supersedes: "none"
---
## Summary

Manual steps, handoffs and workarounds found. **Two evidence tiers**: (a) *documented* manual work (INC-2025-014, 2022 decision, history notes) - real statements but no procedure, owner or timing; (b) *structural* manual work implied by the code (every job is human-started; nothing writes a decision). Data rows that "show" manual recovery are generator output and are labelled so. No handoff has a recorded owner, SLA or queue in the repository. Counts below are on the synthetic baseline (OD-02) and describe the *data model's* behaviour, not a real workforce.

## Findings

| ID | Manual step / handoff | From → To | Evidence | Frequency / duration | Rework or duplication? | Confidence | Class |
|---|---|---|---|---|---|---|---|
| MH-01 | Start every batch job by hand (bridge, reconcile, file import, night-shift, Java, SQL, baseline) | Operator → job | No scheduler/cron/orchestrator in code, Compose or CI (grep); Compose `bridge` runs once, `restart: "no"` | Unknown / unknown | Backlog drains only on demand: 8,567 feed rows vs 1,000 per `--reconcile` run | High | [Verified Fact] (absence) |
| MH-02 | Manual spreadsheet reconciliation of diverged totals | Integration/application teams → (unnamed) | `operations/incidents/INC-2025-014.md` ("04:00 UTC: manual spreadsheet reconciliation used"); `docs/historic-decisions.md` 2022 ("agreed to manually reconcile delayed ElectronicBatchRecord source messages; original change ticket not archived"); `docs/legacy-operations-history.md` ("Several reconciliations remain manual") | 1 incident dated; others unknown; duration unknown | Yes - same totals re-derived outside the system; spreadsheet itself not in repo | Medium | [Verified Fact] (claims) / [Unknown] (frequency) |
| MH-03 | Recovery actions chosen by hand per outage: rerun import 20, restart bridge 19, leave queued 17, manual reconciliation 16 of 72 `upstream_outages` rows | Operator → system | `upstream_outages.recovery_action`, `resolved IS NULL` for 8 | Generated rows (`app/partner_feeds.py`) | Reruns re-import (idempotent for files by hash, see IL-06) | Low (generator) | [Verified Fact] on rows; [Inference] intent |
| MH-04 | Operations review & prioritisation | Integration → Operations users | `docs/business-context.md` step 3; only code trace = `priority()` label on API; 20 STATUS_REVIEWED events (all `reviewer:"operations"`, written by the generator) | 17% of cases have a review event (20/125) | Unknown | Low | [Unknown] who/when |
| MH-05 | Case decision recorded in "local systems" | Operations → local system | `docs/business-context.md` step 4; no write path in repo | Unknown | Unknown; parallel workflow retained for older customers (2024) | Low | [Unknown] |
| MH-06 | Batch disposition by authorised human | Quality → release | `docs/domain-assurance.md` L4; policy archive roles: `operations_lead` (2022-2024), `business_owner`+`risk_control` (2025-2026) | Unknown | Unknown | Low | [Verified Fact] roles in data; process [Unknown] |
| MH-07 | Evidence gathering before closure | Operations ↔ Compliance | `operations-vs-risk-2024.md` ("verifiable evidence"); no evidence store linked to cases: `document_links` exist only in the enterprise DB (12,500, one per object), `cases` has none | Unknown | Unknown | Low | [Unknown] where evidence lives |
| MH-08 | Month-end cut-off alignment | Finance ↔ Operations | `legacy-operations-history.md` ("reports may disagree in monthly cut-offs"); K-10 in Stage 4: totals 125 vs 108 | Monthly (documented) | Yes - two parallel computations (Java/SQL vs API) | Medium | [Verified Fact] (claim) |
| MH-09 | Cross-identifier lookup (case id vs domain id) | Support → data | `legacy-operations-history.md` ("Support requests can refer to either case identifiers or domain-specific identifiers"); schema: `cases` (C…) has no link to `batch_records` (BT…); `partner_feeds.ref_id` points to case ids but 8,394 of 8,567 rows are orphans (0A IO-10) | Unknown | Yes - manual mapping | Medium | [Verified Fact] schema / [Inference] manual mapping |
| MH-10 | Unassigned workflow tasks | Queue → nobody | `workflow_tasks.assigned_to IS NULL`: 695 of 6,250 (11%) | snapshot | Tasks wait without owner | Medium (synthetic rule `i%9==0` in generator, `app/enterprise_legacy.py` L47) | [Verified Fact] on data; generator-driven |
| MH-11 | Read access without recorded reason | User → data | `access_audit` 4,167 rows, all action `read`; `access_reason` empty on 220; **zero `approve` or `update` rows** (generator indexing bug: filter `i%3==0` selects action index 0 only, `app/enterprise_legacy.py` L50) | — | — | High | [Verified Fact] |
| MH-12 | Baseline evidence capture by hand | Engineer → note | `operations/baseline-evidence.md` ("record dataset seed, command, exit status, and timestamp before modifying workflows") | Per change | Manual record | High | [Verified Fact] |
| MH-13 | Regenerate-or-restore the dataset to "fix" state | Engineer → DB | `operations/runbook.md` ("To regenerate synthetic data, run `python -m app.generate --reset`"); `--reset` deletes `events/source_messages/cases/operating_costs` and drops enterprise tables | On demand | Destroys history | High | [Verified Fact] |

## Evidence References

`operations/incidents/INC-2025-014.md`; `docs/historic-decisions.md`; `docs/legacy-operations-history.md`; `operations/runbook.md`; `operations/baseline-evidence.md`; `app/enterprise_legacy.py` L43-50; `app/generate.py` (`--reset` branch); SQL on both SQLite DBs (`mode=ro&immutable=1`): `upstream_outages`, `workflow_tasks`, `access_audit`, `events`.

## Assumptions

- A-05-08: Documented manual reconciliation (2022 decision, INC-2025-014) is still practised (carries 0A U-11). Confirm: Engagement lead (Dinesh Naik) - Stage 6 interviews or explicit ruling.
- A-05-09: The 20 `STATUS_REVIEWED` events stand for "operations review" (this closes Stage 4 A-04-05 only as a label - see `current-state-summary.md` §CS-C).

## Unknowns

- U-05-15 Time, headcount and cadence of every manual step above. U-05-16 Where the reconciliation spreadsheet lives and who owns it. U-05-17 Whether the "parallel workflow" for older customers is manual or a second system.

## Unresolved Issues

- Not one handoff in the repository names an owner, queue, SLA or tool.

## Residual Risks

- Key-person and undocumented-knowledge risk: manual reconciliation depends on practices recorded in two sentences. Any automation (Stage 14+) would encode an unverified procedure.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
