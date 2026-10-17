---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "workflow-overview.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/domain-assurance.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "app/legacy_logic.py", "app/server.py", "app/partner_feeds.py", "legacy_batch/shift_reconciliation.py", "legacy_js/legacy_policy.js", "contracts/decision-policies-archive.json", "legacy_java/ReconcileLegacy.java", "sql/legacy_reports.sql", "domain.json", "domain-profile.json"]
supersedes: "none"
---
## Summary

The documented business workflow is **batch quality review and deviation processing** (`domain.json` `workflow`), owned by Quality. The documented 5-step journey (`docs/business-context.md` L21-27) is: external sources produce messages → integration reconciles/imports → operations review & prioritise → decisions recorded in local systems → monthly measures reviewed. In code, steps 1, 2, 3 (prioritisation only) and 5 exist; **step 4 (recording a decision, including `batch_disposition`) has no implementation** — the API is read-only and no CLI writes decisions. The same decision rule is implemented three different ways.

## Findings

| ID | Workflow | Implemented by | Class | Evidence | Notes / risk | Confidence |
|---|---|---|---|---|---|---|
| WF-01 | Intake of upstream batch-quality events (MES/LIMS/QMS) | Source gateway + bridge | [Verified Fact] | `app/gateway_bridge.py`; gateway | Events with unknown `business_key` dropped silently (counted only). | High |
| WF-02 | Partner feed staging & reconciliation | `app.partner_feeds --reconcile` | [Verified Fact] | `app/partner_feeds.py` L60-71 | 4 outcome rules; `policy_exceptions` tracked separately and never consulted during reconciliation. | High |
| WF-03 | Case triage / prioritisation | `app/legacy_logic.priority()` used by `/api/cases` and `app.baseline`; `manual_review_required()` used by `/api/cases/<id>` | [Verified Fact] | `app/legacy_logic.py` L2-8; `app/server.py` L50, L58 | `urgent` if CRITICAL or amount > 50,000; `review` if HIGH or ESCALATED; manual review if HIGH/CRITICAL or ESCALATED/REOPENED. Header comment: "used by both API and month-end reports". | High |
| WF-04 | Batch quality records: lab results (VALID/OOS/PENDING/INVALID), deviations (MINOR/MAJOR/CRITICAL), CAPA (OPEN/OVERDUE/VERIFIED), SOP versions | Data + read endpoints `/api/domain/*` only | [Verified Fact] | `app/enterprise_data.py`; `docs/domain-contracts.md` | No state-transition logic exists for these entities. | High |
| WF-05 | **Batch disposition** — "Decision requiring authorized human review: `batch_disposition`" | **Not implemented**; appears only in `docs/domain-assurance.md` L4 and `contracts/decision-policies-archive.json` (`rule: batch_disposition`) | [Verified Fact] (absence by grep) | as cited | The core GxP decision and its human approval gate exist only as documentation and policy data. | High |
| WF-06 | Approval / threshold rules — **three divergent implementations** | (a) Python `priority`: amount > 50,000 → urgent. (b) JS `legacyAllows`: amount ≤ regional-yearly limit × 1.05 (APAC 2026 limit 25,000), and returns limit 999,999 when no region/year match (e.g. year 2021, regions like `IN`). (c) Night-shift batch: flag if status HOLD/REVIEW or value > `policy_register.threshold` (2,500–8,500). | [Verified Fact] | `app/legacy_logic.py` L4; `legacy_js/legacy_policy.js` L4-5 (ran: threshold 25000, example false); `legacy_batch/shift_reconciliation.py` L9-14 | Inconsistent decisions for the same record; JS default is permissive. Policy archive approval roles change in 2025 from `operations_lead` to `business_owner`+`risk_control` — no code reads roles. | High |
| WF-07 | Night-shift reconciliation | `legacy_batch/shift_reconciliation.py` | [Verified Fact] | L9 LEFT JOIN on region with 4–5 active policies per region | In isolated copy, `--limit 500` processed 500 joined rows covering only **118 distinct objects** (row multiplication), so per-tenant totals over-count. | High |
| WF-08 | Month-end reconciliation | `legacy_java/ReconcileLegacy.java` (floating-point totals; silently skips unparsable amounts — 2,390 of 2,400 counted on tiny export); `sql/legacy_reports.sql` (join without date restriction; float amounts; also sums amount after LEFT JOIN to events, which [Inference] multiplies amounts for cases with >1 event) | [Verified Fact] / [Inference] | cited files; isolated run | Finance vs operations cut-off disputes are documented (`docs/legacy-operations-history.md` L17). | Medium |
| WF-09 | Monthly operating measures | `GET /api/metrics`; `python -m app.baseline` | [Verified Fact] | `app/server.py` L16-21; `app/baseline.py` | Business measure named "batch quality cases reviewed" (`domain.json`) is not computed by any code. | High |
| WF-10 | Incident handling | Manual (runbook, INC-2025-014); `/api/incidents` returns a hard-coded single incident `INC-2019-0082` | [Verified Fact] | `app/server.py` L15; `operations/incidents/INC-2025-014.md` | Incident endpoint is static, not data-driven. | High |
| WF-11 | Process tensions recorded in correspondence: Operations wants 48-hour closure; compliance refuses automatic closure without verifiable evidence; Finance has no agreed "resolved" definition; "closed" interpreted differently across sites; completion flag interpreted differently in MES vs QA. | [Verified Fact] (that the documents say this) | `docs/correspondence/operations-vs-risk-2024.md`; `docs/business-context.md` L19; `domain-profile.json` `legacy` | Unresolved definitional conflicts will block KPI definition. | High |

Status vocabularies are inconsistent across stores [Verified Fact]: cases `OPEN/UNDER_REVIEW/CLOSED/ESCALATED/REOPENED`; human queues in docs `OPEN/INVESTIGATING/QA_REVIEW/DISPOSITIONED/REOPENED`; enterprise `OPEN/REVIEW/HOLD/CLOSED/REOPENED/ESCALATED`; batch `REVIEW/QA_HOLD/CLOSED`; `domain.json` `okstatus: released` (not present in any data).

## Evidence References

As cited per row; isolated-copy runs of `node legacy_js/legacy_policy.js`, `java ReconcileLegacy.java data/lake/tiny/partner_export.csv`, `shift_reconciliation --limit 500` plus a distinct-object count query.

## Assumptions

- A-07: `batch_disposition` is performed outside this system (in "local systems", step 4). Confirm with Quality operations lead — owner: Engagement lead (Dinesh Naik).

## Unknowns

- U-16 which threshold implementation is authoritative; U-17 where disposition decisions are recorded; U-18 canonical status model; U-19 who consumes JS "front-end" thresholds.

## Unresolved Issues

- The documented journey cannot be traced end-to-end in code (gap at step 4). Stage 5 (process discovery) must obtain this from stakeholders.

## Residual Risks

- R-06 divergent decision rules; R-12 missing human-approval implementation for a GxP decision. See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
