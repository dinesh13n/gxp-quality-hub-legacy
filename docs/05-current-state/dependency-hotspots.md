---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "dependency-hotspots.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/store.py", "app/server.py", "app/partner_feeds.py", "app/enterprise_legacy.py", "app/generate.py", "legacy_batch/shift_reconciliation.py", "legacy_js/legacy_policy.js", "legacy_java/ReconcileLegacy.java", "services/source_gateway/server.py", "compose.yaml", "Dockerfile", "scripts/smoke.py", "scripts/rehearse_local.py", "docs/00-preflight/discovery/initial-risk-register.md", "docs/00-preflight/operating-contract/environment-access-boundaries.md"]
supersedes: "none"
---
## Summary

Fragile dependencies, ranked by how many process steps they touch and how silently they fail. Ten hotspots (DH-01..DH-10). Highest: the single shared SQLite file whose location is resolved in four different ways, the generator as sole data origin, the human decision step outside the repo, and three unsynchronised copies of the approval rule. Nothing here is a runtime-measured failure; failures are read from code and tested in isolated copies in Stage 0A.

## Findings

| ID | Hotspot | Dependents | Why fragile (evidence) | Failure mode | Detectability | Impact | Confidence | Class |
|---|---|---|---|---|---|---|---|---|
| DH-01 | **Shared `legacy.sqlite3` as integration bus** | API, bridge, partner reconcile, file import, baseline, reports, smoke test, gateway (ro) | Path from `LEGACY_DB` env or `ROOT/data/...` (`app/store.py` L4; gateway L7); DDL on read routes; `busy_timeout` 15 s; Compose runs two *different physical copies* (volume vs image) | Lock errors; gateway never sees bridge writes; wrong DB used by a job started without env | Low (no alerts; gateway log off) | Every step 1-5 | High | [Verified Fact] / [Inference] on failure |
| DH-02 | **Hard-coded repo-relative `data/` paths in ≥6 modules** | `enterprise_legacy.py`, `archived_documents.py`, `generate_documents.py`, `historical_fixture.py`, `shift_reconciliation.py`, `scripts/smoke.py`, `rehearse_local.py`, `offline_inventory.py` | `LEGACY_DB` override does not reach them (OD-03a) | A "test" or "report" run writes/reads the live data folder; `smoke.py` opens `ROOT/data/legacy.sqlite3` regardless of env | Low | Evidence integrity of this engagement and any ops use | High | [Verified Fact] |
| DH-03 | **Generator is the only data origin** | All Stage 3-5 conclusions; tests; `run.sh`; CI | `app/generate.py` seeds cases/events/messages/costs; `--reset` drops enterprise tables; shipped (125) vs CI/run.sh (6,000, seed 4326) vs partner feeds (default 8,500, seed 20261017) are three different data builds | Different environments produce different "facts"; real data never enters | High (visible) | Validity of all quantitative baselines (OD-02) | High | [Verified Fact] |
| DH-04 | **Human decision step outside system** (BN-02, CG-01) | Closure, disposition, KPIs K-04/K-05 | No write path | Unmeasurable and unauditable | Low | Core outcome | High | [Verified Fact] (absence) |
| DH-05 | **Three approval-rule implementations** (Python 50,000; JS regional limit ×1.05 or 999,999; SQL-batch threshold 2,500-8,500) | Step 3, step 5, night shift, any front-end | No shared source; JS banner comment: "do not consistently agree with server policy" | Divergent outcomes for same input | Low (no test compares) | Decision consistency | High | [Verified Fact] |
| DH-06 | **Cross-language month-end reconciliation** (Java double, SQL join, Python counts) | Finance, Operations | Different numeric types and cut-off rules; blank amounts silently skipped (200 of 50,000 rows in bundled CSV) | Totals differ by method, not by business | Medium (K-10 shows the divergence) | Month-end trust | High | [Verified Fact] |
| DH-07 | **Unvalidated external contracts**: schema revs 1.0/1.1/2.0/unsupported (224 unsupported feed rows), gateway `0.9` every 19th event, `source-contract-v1.json` unenforced | Bridge, reconcile, adapter | Contracts documented, not validated; `json.loads(raw_json)` unguarded | Parser exception halts a run [Inference]; silent drops | Medium | Intake reliability | High (code) | [Verified Fact] |
| DH-08 | **Policy archive coupling**: `contracts/decision-policies-archive.json` read by JS via cwd-relative path, versions keyed to `startsWith(String(year))` | JS consumer only | Run from another directory fails; year/region without a row silently gets 999,999 | Approval limit effectively removed for unknown region/year | Low | Approval correctness | High | [Verified Fact] |
| DH-09 | **Environment/tooling absent or unpinned**: no dependency lock; Java and Node ad-hoc launches; Docker not installed on inspection device; Compose never executed | Operators, CI | Runtime parity unknown | "Works on my machine" | n/a | Reproducibility | High | [Verified Fact] |
| DH-10 | **Undocumented tribal procedures**: manual reconciliation (2022), parallel workflow (2024), "resolved operationally" (2025), follow-up owner unknown | Operations, Integration | Recorded in 1-2 sentences each | Knowledge loss; re-creation of rolled-back behaviour | n/a | Continuity | Medium | [Verified Fact] (claims) |

### DH-B. Dependency matrix (process step × hotspot, "●" = depends)

| Step | DH-01 | DH-02 | DH-03 | DH-04 | DH-05 | DH-06 | DH-07 | DH-08 |
|---|---|---|---|---|---|---|---|---|
| 1 Source production | ● | | ● | | | | ● | |
| 2 Integration | ● | ● | ● | | | | ● | |
| 3 Review & prioritise | ● | | ● | ● | ● | | | |
| 4 Decision | | | | ● | ● | | | ● |
| 5 Monthly measures | ● | ● | ● | | ● | ● | | |

[Inference] from the cited files; not machine-derived.

## Evidence References

`app/store.py` L4-12; `services/source_gateway/server.py` L7; `compose.yaml` L6-22; `grep` of `data` path literals across `app/ scripts/ services/ legacy_batch/`; `legacy_js/legacy_policy.js` L1-5; `app/partner_feeds.py` L58-63; CSV blank-amount count; `app/generate.py`; `docs/00-preflight/operating-contract/environment-access-boundaries.md`.

## Assumptions

- A-05-12: Dependency ranking is by breadth of process impact and silent failure, a qualitative judgement. Confirm: Engagement lead (Dinesh Naik) - may be re-ranked in Stage 6/7.

## Unknowns

- U-05-22 Whether any consumer reads the API or the JS thresholds (carries 0A U-10, U-19). U-05-23 Real runtime versions of Java and Node.

## Unresolved Issues

- No runtime failure telemetry exists to validate the "failure mode" column.

## Residual Risks

- DH-02 remains an active risk to the engagement: any non-sandboxed run mutates `data/`. Mitigation in force: OD-03a plus checksum verification.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
