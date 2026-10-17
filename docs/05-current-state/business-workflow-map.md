---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "business-workflow-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "domain.json", "domain-profile.json", "docs/domain-assurance.md", "contracts/decision-policies-archive.json", "app/legacy_logic.py", "app/partner_feeds.py", "app/gateway_bridge.py", "legacy_js/legacy_policy.js", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "sql/legacy_reports.sql", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md"]
supersedes: "none"
---
## Summary

Business workflow = "Batch quality review and deviation processing" (`domain.json` `workflow`, owner "Quality"). This file maps **decision points and rules** that the repository actually encodes, and the decisions that exist only as documentation. Finding: **seven distinct decision points**, of which only three are machine-evaluated, and the three machine-evaluated "approval/priority" rules disagree (Python, JavaScript, night-shift batch). The one decision with GxP significance (`batch_disposition`) has policy data but no workflow.

## Findings

### BW-A. Decision register

| ID | Decision | Where decided | Rule (as found) | Input | Output | Evidence | Class |
|---|---|---|---|---|---|---|---|
| D-01 | Is an inbound gateway event accepted? | `app/gateway_bridge.py` L17-23 | Reject if any of `message_id, business_key, system, event_type, occurred_at` missing, or `business_key` not in `batch_records.batch_id`; duplicate by PK | Event | `accepted/invalid/duplicate` counters; invalid events not persisted | file | [Verified Fact] |
| D-02 | Is a partner feed row accepted/rejected/duplicate? | `app/partner_feeds.py` `reconcile()` | Missing `business_key` or `schema_rev=='unsupported'` → REJECTED; `REPLAY` → DUPLICATE (content not compared); `quantity<0` → REJECTED; else ACCEPTED. `policy_exceptions` and `reference_versions` never consulted | `processing_status IN (NEW,RETRY,REPLAY)`, limit 1000 | Overwrites `processing_status`, `error_reason` | file | [Verified Fact] |
| D-03 | Case priority (`urgent/review/queue/archive`) | `app/legacy_logic.priority()` | CLOSED→archive; CRITICAL or amount>50000→urgent; HIGH or ESCALATED→review; else queue | status, severity, amount | label returned by `/api/cases` | file; header comment says "used by both API and month-end reports"; importers (grep) are `app/server.py`, `app/baseline.py` and `tests/test_workflow.py` only - the Java/SQL month-end paths do not call it | [Verified Fact] |
| D-04 | Manual review required? | `manual_review_required()` | severity HIGH/CRITICAL, or status ESCALATED/REOPENED | status, severity | boolean on `/api/cases/<id>` | file | [Verified Fact] |
| D-05 | Within approval limit? | `legacy_js/legacy_policy.js` | `amount <= regional_yearly_limit * 1.05`; if no (region, year) match → limit 999,999 | amount, region, year | boolean | file; ran in 0A: APAC 2026 limit 25,000 | [Verified Fact] |
| D-06 | Flag for night-shift follow-up | `legacy_batch/shift_reconciliation.py` | status HOLD or REVIEW, or `value > policy_register.threshold` (threshold 2,500-8,500) after LEFT JOIN on region with several active policies | `operational_objects` | flagged list | file | [Verified Fact] |
| D-07 | **Batch disposition** (release/reject a batch) | Not in any code | Policy data only: `contracts/decision-policies-archive.json` — 15 versions, one per region/year 2022-2026; approval roles `['operations_lead']` for 2022-2024, **`['business_owner','risk_control']` for 2025-2026**; limits 15,000 (APAC 2022) to 27,200 (AMER 2026), USD | — | — | file; `docs/domain-assurance.md` L4 | [Verified Fact] |
| D-08 | Is a case "closed / resolved / within 48 h"? | Nowhere | Ops: 48 h; Compliance: verifiable evidence needed; Finance: no definition; sites differ on "closed" | — | — | `operations-vs-risk-2024.md`; `business-context.md` L19 | [Verified Fact] (docs say so); definition [Unknown] |

### BW-B. Rule disagreement matrix (same business question, three answers)

| Case | Python D-03 | JS D-05 | Night batch D-06 |
|---|---|---|---|
| Amount 40,000, APAC, 2026 | not urgent by amount | disallowed (limit 25,000×1.05 = 26,250) | depends on policy threshold 2,500-8,500 → flagged |
| Amount 60,000, region/year not in archive | urgent | allowed (999,999 default) | flagged if over threshold |
| Status HOLD, tiny amount | queue/review depends on severity | allowed | flagged (HOLD) |

[Verified Fact] for the rule texts; the table cells are [Inference] derived by reading the formulas (no execution in this stage). Units: `cases.amount` has no currency; policy limits are labelled USD [Verified Fact] — the comparison basis is therefore [Unknown].

### BW-C. Status model fragmentation

Four vocabularies coexist [Verified Fact, confirmed again by query]: `cases` `{OPEN 42, UNDER_REVIEW 30, CLOSED 36, ESCALATED 9, REOPENED 8}`; `batch_records.qa_status` `{REVIEW 50, QA_HOLD 42, CLOSED 33}`; `deviations.status` `{OPEN 14, INVESTIGATION 16, CLOSED 12}`; `capa_actions.state` `{OPEN 7, OVERDUE 6, VERIFIED 8}`; enterprise `{OPEN, REVIEW, HOLD, CLOSED, REOPENED, ESCALATED}`. There is no cross-reference between `cases` (C…) and `batch_records`/`deviations` (BT…/deviation ids): no column in `cases` carries a batch or deviation id [Verified Fact, schema `app/store.py`]. Consequence [Inference]: the "case" the API prioritises is not the same object as the batch/deviation/CAPA records the business description talks about.

### BW-D. Decision timeline implied by documents (not by code)

2018 spreadsheet approvals → service; 2020 partner ingestion added; 2022 manual reconciliation of delayed EBR messages agreed; 2024 stricter approvals requested and parallel workflow retained; approval roles in the policy archive change at 2025 (consistent with, but not proof of, the 2024 request) [Inference]; 2025 rollout rolled back after replay; 2026 modernisation proposal awaiting baseline (`docs/legacy-operations-history.md`, `docs/historic-decisions.md`).

## Evidence References

`app/legacy_logic.py`; `app/gateway_bridge.py` L13-34; `app/partner_feeds.py` L60-71; `legacy_js/legacy_policy.js`; `legacy_batch/shift_reconciliation.py` L9-14; `contracts/decision-policies-archive.json` (parsed: 15 versions); `docs/domain-assurance.md`; read-only counts on `data/legacy.sqlite3`.

## Assumptions

- A-05-03: `cases` is an operational "work item" abstraction for the batch-quality domain; its mapping to batch/deviation/CAPA is not defined anywhere. Confirm: Engagement lead (Dinesh Naik) — Stage 6/7.
- A-05-04: The 2025 change of approval roles reflects a real governance change (inference from dates only). Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-05 Which of D-03/D-05/D-06 (if any) is authoritative (carries 0A U-16). U-05-06 Currency/unit of `cases.amount`. U-05-07 Whether `okstatus: released` is the target state of D-07.

## Unresolved Issues

- D-07 and D-08 cannot be mapped to a system or owner from repository evidence.

## Residual Risks

- Divergent rules (R-06) and absent disposition workflow (R-12) remain; any AI-assisted decisioning in later stages inherits an undefined "ground truth".

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
