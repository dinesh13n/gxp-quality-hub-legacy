---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "control-points.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/domain-assurance.md", "contracts/decision-policies-archive.json", "app/store.py", "app/server.py", "app/gateway_bridge.py", "app/partner_feeds.py", "app/historical_estate.py", "app/integration.py", "app/enterprise_legacy.py", "legacy_js/legacy_policy.js", "tests/*.py", ".github/workflows/verify.yml", "scripts/smoke.py", "operations/runbook.md", "data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)"]
supersedes: "none"
---
## Summary

Controls found (preventive, detective, corrective) and the controls the documents say must exist but do not. Reference requirements come from the repo's own text: `docs/domain-assurance.md` (preserve the human approval gate for `batch_disposition`; no silent cross-tenant action; source attribution for each decision; "21 CFR Part 11 and GMP data integrity principles" cited as background, "not compliance certification"). Control gaps are stated against these repo-internal requirements; **no regulatory assessment is made here** (not authorised evidence; deferred). All data findings are on synthetic data and show what the system *permits*, not what users did.

## Findings

### CP-A. Controls present

| ID | Control | Type | Where | Strength | Class |
|---|---|---|---|---|---|
| CP-01 | Primary keys on all tables; `PRAGMA foreign_keys=ON` and FKs on `events.case_id`, domain tables | Preventive (data integrity) | `app/store.py` L11, DDL; domain DDL | Medium - but no FK from `cases` to batch/deviation, and `partner_feeds.ref_id` has no FK (8,394 orphans) | [Verified Fact] |
| CP-02 | Gateway event validation (required fields; parent key must exist) | Preventive | `app/gateway_bridge.py` L17-23 | Medium - rejects silently, no quarantine | [Verified Fact] |
| CP-03 | Message-id idempotency (PK) and file-hash idempotency | Preventive | bridge; `historical_estate.py` | Medium | [Verified Fact] |
| CP-04 | Partner reconcile rules (missing key, unsupported schema, negative quantity, replay) | Preventive/detective | `app/partner_feeds.py` L60-71 | Low-Medium - overwrites state, no audit | [Verified Fact] |
| CP-05 | Manual-review flag (`manual_review_required`) | Detective (advisory) | `app/legacy_logic.py` L7-8, `/api/cases/<id>` | Low - advisory boolean; nothing enforces it | [Verified Fact] |
| CP-06 | Approval limits per region/year with role lists | Preventive (policy data) | `contracts/decision-policies-archive.json` | **Not enforced by any workflow**; consumed only by `legacy_policy.js` (advisory boolean, +5% tolerance, 999,999 default) | [Verified Fact] |
| CP-07 | Read-only API (GET only) and read-only gateway DB (`mode=ro`) | Preventive | `app/server.py`; gateway | Medium; contradicted by DDL on read path (DO-01) | [Verified Fact] |
| CP-08 | Pagination bounds (limit 1-100), allow-listed table names | Preventive | `app/server.py` | Medium | [Verified Fact] |
| CP-09 | Automated tests + smoke + CI | Detective (release) | `tests/`, `scripts/verify.sh`, `.github/workflows/verify.yml` | Low - behaviour coverage thin (BI-B); no gate on deploy | [Verified Fact] |
| CP-10 | Backup + checksum (engagement-level, not product) | Detective | `../_data-backup-2026-10-17/SHA256SUMS.txt` (OD-03) | Outside the product | [Verified Fact] |

### CP-B. Control gaps (required by repo text or inherent to GxP-style process, but absent)

| ID | Gap | Evidence | Impact | Risk | Confidence | Class |
|---|---|---|---|---|---|---|
| CG-01 | **No enforced human approval gate for `batch_disposition`**; decision and approver not captured by any component | `domain-assurance.md` L4 vs absence of write path; policy roles unused | Required gate exists only on paper | Disposition outside traceable system; cannot attribute decision to a role | High | [Verified Fact] |
| CG-02 | **No audit trail of state change**: `cases.status` is a snapshot; `cases.version` is 1 for all 125 and no code increments it; `events` has no reopen/close type (8 REOPENED cases, 0 reopen events); `CASE_CREATED.payload.status` equals the *current* status for 125 of 125 cases (it is a copy, not the status at creation) | SQL; `app/generate.py` | History of who changed what/when cannot be reconstructed | Data-integrity (attributable, contemporaneous) exposure | High | [Verified Fact] |
| CG-03 | **Closure without recorded review**: 30 of 36 CLOSED cases (83%) have no `STATUS_REVIEWED` event, incl. 3 of 4 CLOSED HIGH/CRITICAL cases | SQL | Closed state does not imply any recorded verification step | Premature closure (the compliance concern in `operations-vs-risk-2024.md`) | Medium (synthetic; only 17% of any case has a review event) | [Verified Fact] |
| CG-04 | **No cross-record consistency**: 10 CLOSED deviations sit on batches not CLOSED; 7 CLOSED batches have unclosed deviations; 4 CLOSED deviations have CAPA not VERIFIED; 4 open deviations have VERIFIED CAPA; **25 of 33 CLOSED batches carry a lab result that is OOS/PENDING/INVALID**; 8 of 12 CLOSED deviations have no root cause | SQL across `batch_records`, `lab_results`, `deviations`, `capa_actions` | Nothing prevents contradictory states (a GxP closure rule) | Release/closure of questionable batches | Medium (random synthetic assignment; still proves absence of constraints) | [Verified Fact] |
| CG-05 | **Overdue not computed** (BN-06) | SQL | Deadline control is manual | Missed CAPA | Medium | [Verified Fact] |
| CG-06 | **Silent data loss / skip**: invalid gateway events not persisted; Java skips unparsable rows; partner row statuses overwritten; no error queue | code (IL-01, IL-07, IL-04) | Evidence vanishes | Data-integrity | High | [Verified Fact] |
| CG-07 | **No authentication/authorisation/tenant control** on API; `access_audit` holds only `read` actions (no `update`/`approve`), 220 reads lack a reason; cross-tenant "no silent action" requirement untestable | `app/server.py`; `app/enterprise_legacy.py` L50 | Required safety property cannot be demonstrated | Unauthorised access | High | [Verified Fact] |
| CG-08 | **Untrusted text reaches decision-adjacent data** with no sanitisation boundary: instruction-like strings in 86 feed rows, enterprise notes, lake events | 0A IO-15; lake events `source_claim` | If later AI components read these fields, injection reaches decisions | Prompt-injection / unsafe action | High (presence) | [Verified Fact] |
| CG-09 | **Duplicate unreconciled rules** (D-03, D-05, D-06) - no single policy control | `business-workflow-map.md` BW-B | Same case gets different outcomes | Control inconsistency | High | [Verified Fact] |
| CG-10 | **Source attribution for decisions absent**: no field records which rule, version or person led to `priority`/flag; policy versions unused at runtime | code | "Source attribution for each decision" requirement unmet | Un-auditable | High | [Verified Fact] |
| CG-11 | **Retention/legal hold not acted on**: `retention_events` (2,084 rows, expiry +7 years, legal_hold flag) read by nothing | grep | Retention is data only | Retention breach/hold ignored | Medium | [Verified Fact] |
| CG-12 | **Controls on this engagement itself**: single human owns, measures and approves (ER-11, Stage 4 sign-off) | `docs/04-baseline-kpis/kpi-baseline-signoff.md` | Self-approval | Independence gap for the programme (not the product) | High | [Verified Fact] |

## Evidence References

`app/store.py`; `app/gateway_bridge.py` L17-23; `app/partner_feeds.py` L60-71; `app/legacy_logic.py`; `contracts/decision-policies-archive.json`; `docs/domain-assurance.md` L4-7; SQL on `cases`, `events`, `batch_records`, `lab_results`, `deviations`, `capa_actions`, `access_audit`, `retention_events` (read-only, immutable); grep for `retention_events` consumers (none).

## Assumptions

- A-05-11: The requirements in `docs/domain-assurance.md` are the applicable control baseline for this engagement; it explicitly disclaims compliance certification. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-20 Controls operating outside the repo (QA review, e-signature, ECM audit trail). U-05-21 Whether Part 11 applies to the (fictional) client's systems.

## Unresolved Issues

- Control effectiveness in the real process cannot be tested; the findings are "system permits" findings.

## Residual Risks

- Highest: CG-01/CG-02 (no gate, no trail). Any intervention in Stage 14+ that touches closure must not weaken or bypass the (unknown) external gate.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
