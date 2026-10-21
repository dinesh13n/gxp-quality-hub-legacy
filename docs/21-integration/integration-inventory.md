---
stage: "21 — Enterprise Integration"
artifact: "integration-inventory.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/05-current-state/integration-landscape.md (IL-01..IL-13, IL-C)", "docs/14-transformation/adapter-strategy.md (AD-01..AD-08)", "docs/14-transformation/cutover-plan.md (CUT-2..CUT-4, CO-2 step 4, CF-1)", "docs/12-specs/interface-contracts.md (IF-4, IF-7)", "hub/adapters/*.py", "hub/intake/cli.py", "services/source_gateway/server.py", "app/*.py, legacy_*/, sql/legacy_reports.sql, scripts/smoke.py, .github/workflows/verify.yml", "docs/21-integration/evidence/consumer-scan.json (STG21 S05)", "docs/21-integration/evidence/contract-pack.json (STG21 S01)", "docs/21-integration/evidence/gateway-stub-conformance.json (STG21 S02)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. There are no real enterprise systems in this engagement: every "system" below is a file, a table or a loopback stub shipped in the repository. No partner agreement, endpoint, credential or SLA exists or is implied (OD-04).**

## Summary
The hub has **10 integration points** (INT-01..INT-10, all inbound and read-only: 8 adapters AD-01..AD-08, of which AD-04 is the only network client and talks to the repo's loopback source-gateway stub) and **2 provided surfaces** (INT-11 hub HTTP API on loopback, INT-12 host-operator CLI). It publishes nothing to any other system: no event bus, queue, webhook, file drop or scheduler exists in the estate (Stage 5 IL-C). On the legacy side, **13 legacy outputs (LO-01..LO-13)** are produced by the CUT-2..CUT-4 counterparts; the DW-11 repository scan finds **no system consumer outside the repository** for any of them and only repository-internal readers (API handlers, a smoke check, a CI step, legacy tests, the characterisation harness, hub transcriptions). External consumers stay **Unknown** until Dinesh confirms them (DQ-15).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### II-1 Integration points of the hub
| ID | Integration | Direction / style | Counterpart (shipped) | Hub component | Contract (see) | Failure semantics (see) | Tag |
|---|---|---|---|---|---|---|---|
| INT-01 | Legacy case DB reader AD-01 | inbound, batch read | `data/legacy.sqlite3` (`cases`, `events`, `operating_costs`; 125 cases, sha256 c254649f…) | `hub/adapters/legacy_sqlite.py` | data-contracts DC-S21-05 | FS-DB-* | [Verified Fact] |
| INT-02 | Enterprise DB reader AD-02 | inbound, batch read | `data/enterprise_legacy.sqlite3` | `hub/adapters/legacy_sqlite.py` | data-contracts DC-S21-05 | FS-DB-* | [Verified Fact] |
| INT-03 | Partner-feed reader AD-03 | inbound, batch read -> shadow intake | `partner_feeds` (8,567 rows) | `hub/adapters/intake_sources.py` -> `hub/intake/service.py` | data-contracts DC-S21-01 | FS-ITEM-*, FS-DB-* | [Verified Fact] |
| INT-04 | Source-message reader (DM-4) | inbound, batch read -> shadow intake | `source_messages` (15 rows) | as INT-03 | DC-S21-02 | FS-ITEM-* | [Verified Fact] |
| INT-05 | Gateway-inbox reader | inbound, batch read -> shadow intake | `gateway_inbox` (1 row, the legacy bridge's store) | as INT-03 | DC-S21-03 | FS-ITEM-* | [Verified Fact] |
| INT-06 | Gateway client AD-04 | inbound, HTTP GET pull with offset checkpoint | `services/source_gateway/server.py` on loopback (`/api/events`) | `hub/adapters/gateway_client.py`, `python -m hub.intake gateway-pull` | api-contracts AC-S21-02 | FS-NET-* | [Verified Fact] |
| INT-07 | Vendor CSV file-drop reader AD-05 | inbound, file read | `data/lake/tiny/partner_export.csv` (2,400 rows) | `hub/adapters/intake_sources.py` | DC-S21-04 | FS-FILE-*, FS-ITEM-* | [Verified Fact] |
| INT-08 | Policy-source importer AD-06 | design-time transcription (no runtime read of legacy code) | `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json`, `legacy_batch/shift_reconciliation.py` | `hub/policy/asfound.py`, `as_found_pins.json` | TST-CO-03 goldens | n/a (static data) | [Verified Fact] |
| INT-09 | Document reader AD-07 | inbound, file read (R1 refs / R2 search) | `data/documents/`, `data/archive_documents/` | `hub/search/*` | PNFR-13 planted strings | content treated as data | [Verified Fact] |
| INT-10 | Legacy output comparator AD-08 | inbound, read of captured goldens | `tests/characterization/golden/*` (INC-01 captures) | `hub/adapters/legacy_captures.py`, `hub/golden/*` | TST-CO-01/02 | missing capture -> NOT-RUN, exit 6 | [Verified Fact] |
| INT-11 | Hub HTTP API (provided) | outbound-facing, request/response, loopback only | consumers: reviewers / UI (synthetic users); no external system | `hub/web/*`, `hub/security/route_registry.json` (48 routes) | api-contracts AC-S21-01 | error envelope; FS-API | [Verified Fact] |
| INT-12 | Hub CLI (provided) | host operator | operator shell | `python -m hub`, `hub.intake`, `hub.web`, ... | `docs/20-application/spec-addendum-cli-error-shape.md` | exit codes | [Verified Fact] |

- [Verified Fact] No hub module writes to any legacy store or file: AD-01..AD-03 open `mode=ro&immutable=1` snapshots behind a write-refusing authorizer (TST-CO-04 a-f), the CSV is opened `rb`, the gateway client only issues GET (STG21 S03, S06).
- [Verified Fact] No event bus, broker, webhook, SFTP or scheduler exists in the estate (Stage 5 IL-C); the hub scheduler ships OFF (OD-19 / OPD-11).
- [Unknown] Real enterprise systems (MES / LIMS / QMS / ERP, partner portals) and their endpoints, credentials and agreements: none exist in the repository. Owner: Engagement lead (Dinesh Naik). Resolution: only if a real system is named (out of scope for this synthetic engagement).

### II-2 Legacy-output consumer inventory (DW-11; decision support for CUT-2..CUT-4 step 4, DQ-15 / U-14-01)
Scan: `tests/hub/_stg21.py consumer_scan()` over every text file of the repository except `.git`, `data/`, `.fde/`, `docs/NN-*` stage documents and `tests/hub/` (285 files); result `evidence/consumer-scan.json`; the part found under frozen legacy paths is pinned by STG21 S05. "Reader" = a file that names the output; it is not necessarily a consumer that depends on the value.

| LO | CUT | Legacy output (producer) | Readers inside the repository (by class) | Consumer outside the repository | Tag |
|---|---|---|---|---|---|
| LO-01 | CUT-2 | `priority()` / `manual_review_required()` (`app/legacy_logic.py`) | runtime: `app/server.py` (API fields), `app/baseline.py` (`urgent_cases`); test: `tests/test_workflow.py`; hub: as-found rule set (transcribed); harness | Unknown (code comment: "used by both API and month-end reports") | [Verified Fact] scan / [Unknown] external |
| LO-02 | CUT-2 | `/api/cases`, `/api/cases/{id}` (`app/server.py`) | docs: `README.md`, `docs/interface-notes.md`; harness captures | Unknown HTTP clients (IL-13 "pull by unknown consumers") | [Verified Fact] / [Unknown] |
| LO-03 | CUT-2 | JS `threshold()` / `legacyAllows()` (`legacy_js/legacy_policy.js`) | docs: `docs/historical-fixtures.md`; hub: as-found rule set; harness | Unknown ("JavaScript policy consumer", `docs/service-boundaries.md`) | [Verified Fact] / [Unknown] |
| LO-04 | CUT-3 | `partner_feeds.processing_status` after in-place reconcile (`app/partner_feeds.py`) | runtime: `app/server.py` (`/api/partners/partner_feeds`); docs: `README.md`; hub: pins / DV seeds; harness | Unknown (call chain "reconciliation -> operational case and quality decision", `docs/partner-feed-operations.md`) | [Verified Fact] / [Unknown] |
| LO-05 | CUT-3 | `gateway_inbox` / `gateway_checkpoints` (`app/gateway_bridge.py`) | runtime: `app/operational_report.py` (COUNT only); hub: AD-03-style reader `gateway_inbox_deliveries`, gateway profile; docs: `docs/source-gateway.md`; harness | none found; no step turns an inbox row into a case change (IL-03) | [Verified Fact] |
| LO-06 | CUT-3 | `vendor_file_rows` / `vendor_file_imports` (`app/historical_estate.py`) | runtime: `sql/legacy_reports.sql` (2nd query; itself referenced by no code); hub: pins; harness | Unknown | [Verified Fact] / [Unknown] |
| LO-07 | CUT-3 | `consume_source_messages()` output (`app/integration.py`) | test: `tests/test_workflow.py`; docs: `operations/runbook.md` ("can be inspected"); harness | none found (inspection only) | [Verified Fact] |
| LO-08 | CUT-4 | `app.baseline` metrics JSON | CI: `.github/workflows/verify.yml` (runs it, no assertion on values); test: `tests/test_workflow.py`; docs: `README.md`, `PRELOADED_DATA.md`; harness | Unknown (role hint: "Finance requested a faster month-end reconciliation", `docs/historic-decisions.md`) | [Verified Fact] / [Unknown] |
| LO-09 | CUT-4 | Java month-end total, stdout (`legacy_java/ReconcileLegacy.java`) | docs: `docs/historical-fixtures.md` (how to run); harness | Unknown (finance role hint as LO-08) | [Verified Fact] / [Unknown] |
| LO-10 | CUT-4 | SQL month-end report (`sql/legacy_reports.sql`) | harness only | Unknown (IL-08: referenced by no code) | [Verified Fact] / [Unknown] |
| LO-11 | CUT-4 | night-shift reconciliation output (`legacy_batch/shift_reconciliation.py`) | test: `tests/test_enterprise_legacy_v6.py`; docs: `README.md`; hub: as-found rule set; harness | Unknown (role hint: "overnight reconciliation before 06:00", `docs/operations-service-levels.md`, archived target, not a measured guarantee) | [Verified Fact] / [Unknown] |
| LO-12 | CUT-4 | `/api/metrics` (`app/server.py`) | runtime: `scripts/smoke.py` (asserts `total_cases > 0`); docs: `README.md`, `PRELOADED_DATA.md`, `docs/interface-notes.md` ("2025: reporting team implemented new monthly operating metrics"); harness | Unknown (reporting team named by role only) | [Verified Fact] / [Unknown] |
| LO-13 | CUT-3/4 | operational correlation report (`app/operational_report.py`) | test: `tests/test_source_gateway.py`; docs: `docs/source-gateway.md`; harness | Unknown | [Verified Fact] / [Unknown] |

- [Verified Fact] Every CUT-2..CUT-4 output has a row (STG21 S05); none of LO-09..LO-11 is read by a CI job; the only CI reader of any output is `verify.yml` running `python -m app.baseline` without checking values.
- [Inference] Inside the repository no output has a consumer whose behaviour depends on the value except the legacy API handlers that re-expose LO-01 / LO-04 and the smoke check on LO-12. The consumers that matter for cutover step 4 are therefore outside the repository (people or systems named only by role: finance, reporting team, operations, "JavaScript policy consumer") and cannot be identified from evidence. CUT-2..CUT-4 step 4 stays unplannable until Dinesh names them (CF-1 unchanged in substance, now evidenced per output).
- **Confirmation line (DW-11 acceptance):** `Consumer inventory II-2 confirmed by: ______ (Engagement lead, Dinesh Naik) on ______; external consumers: ______` - **PENDING** (DQ-S21-02).

## Evidence References
- `docs/21-integration/evidence/consumer-scan.json` (reproduce: `python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-scan --label scan -k TST_HUB_STG21_S05`).
- `hub/adapters/*.py`; `tests/hub/test_tst_co_04_readonly_adapters.py`; STG21 S03 / S06.
- Stage 5 `integration-landscape.md` IL-01..IL-13, IL-C; Stage 14 `adapter-strategy.md`, `cutover-plan.md`.

## Assumptions
- A-21-II-1 [Assumption] A file that names an output is a candidate reader; a consumer that reads an output without naming it (e.g. a person reading stdout) cannot be found by a repository scan. Confirm: Engagement lead (Dinesh Naik).
- A-21-II-2 [Assumption] Role names in the legacy docs (finance, reporting team, operations) are historical narrative of the synthetic estate, not named stakeholders. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-II-1 External consumers of LO-01..LO-13 (DQ-15 / U-14-01) - Engagement lead (Dinesh Naik); resolves CUT-2..CUT-4 step 4 at Stage 30.
- U-21-II-2 Real enterprise systems, endpoints, credentials, partner agreements, SLAs - none exist; Engagement lead (Dinesh Naik).

## Unresolved Issues
- DW-11 confirmation line pending.

## Residual Risks
- RR-21-II-1 A cutover (Stage 30) that re-points nobody leaves an unknown human consumer on the legacy figures (Medium; mitigated: legacy keeps running as comparator, CO-2 step 6).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue (Stage 21, DW-11 inventory included). |
