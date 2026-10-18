---
stage: "14 — Transformation / Migration Plan"
artifact: "coexistence-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/adrs/ADR-003-legacy-coexistence-pattern.md", "docs/10-architecture/adrs/ADR-001-architecture-style.md", "docs/10-architecture/adrs/ADR-015-deployment-topology.md", "docs/12-specs/features/f10-coexistence-change-safety.md (BEH-CO-03..05, AC-CO-04/05/08)", "docs/07-repo-assessment/critical-workflow-inventory.md (CW-01..CW-14)", "docs/00-preflight/operating-contract/repository-write-boundaries.md (WB-01..WB-11, WB-F1/F2)", "app/server.py L63 (PORT default 8080, HOST 127.0.0.1)", "repository listing (app/, legacy_*/, sql/, services/, scripts/, ops/, integration/, contracts/, environments/, operations/)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
Coexistence model (ADR-003 option B, PROPOSED): **legacy runs unchanged and remains the system of record for every output it produces today; the hub runs beside it, reads legacy data only through read-only adapters, writes only its own `hub.sqlite3`, and publishes shadow comparisons.** There is **no dual-write** and no write-back into legacy tables in R1. A hub output becomes authoritative only through a per-capability cutover step (cutover-plan.md) after the relevant preserve-vs-fix item is decided. This keeps every Stage 15 increment reversible by "stop the hub / revert the PR".

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### CS-1 Coexistence rules (binding for Stage 15 once Dinesh accepts the plan)
| # | Rule | Enforced by | Test | Tag |
|---|---|---|---|---|
| CR-1 | Legacy source files are byte-identical at every Stage 15 merge | `git diff --stat baseline-as-found..HEAD -- <legacy paths>` empty | TST-CO-05 (AC-CO-05) | [Inference] from BEH-CO-03 |
| CR-2 | Hub opens legacy DBs only `file:<path>?mode=ro` (immutable for baselines) | C11 adapter | TST-CO-04 (AC-CO-04) | [Inference] |
| CR-3 | Hub never writes under the repo's `data/`; `hub.sqlite3` path via env, never repo-relative | config + guard | TST-CO-06 (AC-CO-06) | [Verified Fact] deployment-architecture.md L23 |
| CR-4 | Every executable step runs in a full repo copy outside the working tree (OD-03a); backup manifest verified after | BEH-CO-04 | TST-CO-07 (AC-CO-07) | [Verified Fact] OD-03a |
| CR-5 | Hub binds 127.0.0.1 only, on a port distinct from legacy (legacy default 8080, `app/server.py` L63) and gateway | start-up refusal | security tests (HAR-05) | [Verified Fact] L63; [Inference] rule |
| CR-6 | No dual-write: legacy and hub never both write the same business fact | design review + CR-1/CR-2 | — | [Inference] ADR-003 |
| CR-7 | Protected parallel workflow CO-WF-01 is read-only to the hub; no route/job can alter it | C11 inventory | TST-CO-08 (AC-CO-08) | [Verified Fact] BEH-CO-05 |
| CR-8 | No product AI (OD-08) | deny-list + egress test | TST-CO-11/12 | [Verified Fact] OD-08 |

### CS-2 Components that remain UNCHANGED (Completion Gate item) [Verified Fact: paths exist in the repo listing; Inference: decision]
| Path | Role today | Unchanged through | Why | Changed only by |
|---|---|---|---|---|
| `app/legacy_logic.py` | priority / manual-review rules (CW-01/02) | all of Stage 15 R1 | HAR-06; CT-01..03 baseline | Stage 30 cutover decision + HAR-06, if ever |
| `app/server.py` | legacy read API (CW-02/10/13) | R1 | untested god handler (heat map High) | never in R1 |
| `app/store.py` | import-time DB binding used by 11 modules (WB-F2) | R1 | ripple risk; HD-1 avoids refactor | never in R1 |
| `app/partner_feeds.py`, `app/gateway_bridge.py`, `app/integration.py` | intake (CW-04/05) | R1 | DV-02/03/07/09 undecided | cutover CUT-3 |
| `app/baseline.py`, `app/operational_report.py`, `app/workshop_check.py` | reports/readiness (CW-03/11/12) | R1 | baseline KPIs (OD-07) | — |
| `app/generate*.py`, `app/enterprise_*.py`, `app/domain_data.py`, `app/historical_*.py`, `app/archived_documents.py` | data provisioning (CW-12) | R1 | regeneration equivalence (CT-14) | — |
| `legacy_batch/shift_reconciliation.py` | night shift (CW-07) | R1 | DV-08 undecided | CUT-4 |
| `legacy_java/ReconcileLegacy.java`, `sql/legacy_reports.sql` | month-end (CW-08) | R1 | DV-01/DV-04 undecided; consumers Unknown | CUT-4 |
| `legacy_js/legacy_policy.js` | front-end threshold (CW-09) | R1 | DV-05; HAR-06 | CUT-2 |
| `services/source_gateway/` | upstream simulator (CW-04) | R1 | comparator for C6 | — |
| `contracts/decision-policies-archive.json`, `integration/source-contract-v1.json`, `integration/source-gateway.json` | contracts | R1 | read by C4/C6 as data | OD-S12-11 amend-contract option |
| `scripts/`, `ops/`, `operations/` | readiness/ops | R1 | CT-15 | — |
| `tests/test_*.py` (7 files) | shipped suite (destructive, TQ-01) | R1 — kept, **run only in sandbox** | evidence of as-found behaviour | — |
| `data/` (1,512 files) | baseline dataset (OD-09) | always (HAR-01) | golden source | never by Stage 15 |
| `Dockerfile`, `compose.yaml`, `environments/`, `pyproject.toml`, `run.sh`, `domain.json`, `.github/` | build/env (WB-05) | INC-01..INC-07; possibly INC-08 if a `hub` entry point is added to `pyproject.toml` (HAR-07) | HAR-07 | HAR-07 approval |
| `docs/*.md` legacy docs | as-found documentation | R1 except TB-22 (optional, WB-03) | TD-04 | branch PR |
| `docs/00-…13-*/`, `.fde/` | prior evidence | always (HAR-13) | before/after comparison | addenda only |

### CS-3 Coexistence modes per capability
| Capability | Legacy (authoritative in R1) | Hub mode in R1 | Comparison | Tag |
|---|---|---|---|---|
| Priority/manual review (CW-01/02) | `app/legacy_logic.py` | shadow: as-found rule set evaluation | TST-CO-03 must show 0 diffs | [Inference] |
| Decision recording (CW-14) | **none exists** | net-new, but Zone H mode `none` → no disposition recorded | n/a (no legacy) | [Verified Fact] CW-14 |
| Intake (CW-04/05/06) | gateway bridge, reconcile, file import | shadow over **sandbox copies** of feeds | golden-compare lists DV-02/03/07/09 as UNAPPROVED | [Inference] |
| Metrics/month-end (CW-03/07/08) | baseline, Java, SQL, night shift | shadow metrics with definition tags | DV-01/04/08 listed | [Inference] |
| Threshold UI (CW-09) | JS | rule service exposes as-found JS set | DV-05 listed | [Inference] |

### CS-4 Coexistence risks
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| CX-1 | SQLite lock contention if hub reads a live legacy DB while legacy writes | `busy_timeout` 15 s; CT-17 not captured (U-07-05) | read stalls / SQLITE_BUSY | Medium | Medium | Is any legacy writer live in a real deployment? Unknown |
| CX-2 | Hub reading a moving legacy file gives non-reproducible shadow results | WB-F1 writers | flaky comparisons | Medium | High | Mitigation: hub reads snapshot copies (`immutable=1`) taken per run, hash recorded |
| CX-3 | Two "truths" visible to users during shadow period | CS-3 | confusion | Medium | Medium | Hub pages label all outputs "SHADOW — not authoritative" until cutover |
| CX-4 | Port collision with legacy 8080 / gateway | `app/server.py` L63 | start failure | Low | High | distinct env-configured ports |

## Evidence References
ADR-003, ADR-001, ADR-015; `features/f10-coexistence-change-safety.md`; `critical-workflow-inventory.md` L19-32; `repository-write-boundaries.md`; `app/server.py` L63.

## Assumptions
- A-14-05 [Assumption] Legacy stays the system of record for all existing outputs until a CUT step; confirm: Engagement lead (Dinesh Naik) (Stage 30).
- A-14-06 [Assumption] Snapshot-read (CX-2 mitigation) is acceptable to ADR-003 "read-only adapters". Confirm at Stage 15 review.

## Unknowns
- U-14-04 Real-world consumers of legacy outputs (none identifiable in repo).
- U-14-05 Owner of CO-WF-01 (OPD-15; `owner = Unknown`).

## Unresolved Issues
- ADR-003 PROPOSED, not ACCEPTED (HAR-11).

## Residual Risks
- RR-CS-1 Extended coexistence becomes permanent (two systems maintained indefinitely). Mitigation: cutover criteria per capability in cutover-plan.md; decommission is an explicit later decision.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial coexistence strategy (Stage 14). |
