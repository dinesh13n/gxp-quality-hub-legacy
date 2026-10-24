---
stage: "33 — Vendor / Third-Party / Concentration Risk"
artifact: "vendor-inventory.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-14, OD-23, OD-28, OD-30, OD-31, OD-32)", "docs/07-repo-assessment/dependency-map.md (DM-01..DM-08)", "docs/10-architecture/{deployment-architecture,model-service-scorecard,architecture-options}.md; adrs/ADR-015", "docs/16-repo-validation/security-scan-summary.md (SS-01)", "docs/24-security-privacy/{threat-model,residual-security-risks}.md (T-21, RS-10, RS-15)", "docs/25-governance/{risk-acceptance-register,operating-contract-governance-updates,accountability-map,ai-system-register}.md", "pyproject.toml; Dockerfile; compose.yaml; .github/workflows/verify.yml; git log (read-only)", "git remote -v / git log (read-only)", "tests/hub/test_tst_co_11_no_ai_denylist.py (read only; not executed)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: nothing here is an approval, a legal interpretation or a vendor assessment from vendor-supplied evidence. Only the Engagement lead (Dinesh Naik) can accept a risk (HAR-11, TP-14); this stage accepts nothing. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04).**

The honest result is **few third parties, and almost all are runtimes, tooling or code hosting rather than service vendors**. The product (the `hub/` package) has **zero third-party libraries, no cloud service, no managed database, no model/AI provider, no SaaS, no telemetry sink and no network egress beyond loopback** (SS-01; DM-08; ADR-015; OD-08). Inventory: **11 entries (V-01..V-11)**; **5 are rated critical** to build or run and receive full scorecards (V-01 CPython, V-02 SQLite, V-03 GitHub, V-04 AI coding assistant, V-05 orchestrator cloud workspace); 6 are non-critical or legacy-only and receive compact scorecards. **No contract terms exist for any entry** (all Unknown). Stage 27 (SBOM) and Stage 32 (cost) are not yet produced; this stage derives the dependency list from Stage 7 DM-01..DM-08 and flags both as upstream gaps.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Criteria
- Critical = failure, change of terms or withdrawal stops the build, the test evidence or the running hub within the engagement (agent judgement, [Inference]).
- "Vendor" is used loosely: open-source runtimes have a steward (not a contracting party); services have a provider.

### Inventory
| ID | Third party / dependency | What it supplies | Where used (evidence) | Contract / terms in repo | Critical? | Tag |
|---|---|---|---|---|---|---|
| V-01 | CPython runtime and standard library (steward: Python Software Foundation; distribution on each host Unknown) | language runtime for every `.py` file; stdlib `sqlite3`, `http.server`, `urllib`, `csv`, `hashlib` | `pyproject.toml` `requires-python >=3.10`; Dockerfile `python:3.12-slim`; CI 3.12; reference laptop 3.10.12; cloud workspace 3.13 (OD-23); DM-01; SS-01 | none (licence not examined: Unknown) | **Yes** | [Verified Fact] usage; [Unknown] terms |
| V-02 | SQLite library (bundled with CPython; version not pinned; RS-10 names 3.37) | the only datastore: hub DB, audit store, legacy DBs; optional FTS5 for R2 search | `hub/store/`, `app/store.py`; `hub/runtime.py` reports FTS5 availability, does not require it; DM-02; ADR-004, ADR-012 | none (licence not examined: Unknown) | **Yes** | [Verified Fact] usage; [Unknown] terms |
| V-03 | GitHub (code hosting, pull requests, private remote) | `origin` = `https://github.com/dinesh13n/gxp-quality-hub-legacy.git` (private, OD-05); PR + squash-merge workflow (OD-13); 11 commits carry committer "GitHub" | `git remote -v`; `git log`; OD-05, OD-13; HAR-09 | none in repo; plan tier, data residency, retention Unknown | **Yes** (only remote copy of history; review workflow) | [Verified Fact] usage; [Unknown] terms |
| V-04 | AI coding assistant used to BUILD (Anthropic model family via Claude Code; dev tooling, not product AI) | authored/co-authored code and docs: **all 51 of 51 commits** on main carry a `Co-Authored-By: Claude ... <noreply@anthropic.com>` trailer | `git log` (read-only count); CP-10; AI register (OD-31: stays in the register); OD-08 ("dev tooling, not product AI") | none in repo; commercial terms, data use and retention Unknown | **Yes** to the engagement; **not** to the product at runtime | [Verified Fact] usage; [Unknown] terms |
| V-05 | Orchestrator cloud workspace (provider Unknown), Python 3.13 | runs the full hub regression (419 methods, 19 groups) on checksum-gated copies of git-ignored data | OD-23, OD-27, OD-30; AEF-3 (audit-evidence-index) | none; provider, region, retention Unknown | **Yes** (single environment for the full-regression evidence) | [Verified Fact] usage; [Unknown] provider |
| V-06 | GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`) | CI workflow `verify.yml` | `.github/workflows/verify.yml`; DM-06 | none; actions pinned by major tag, not commit SHA | No (never run; does not cover `hub/`) | [Verified Fact] |
| V-07 | Docker / base image `python:3.12-slim` (publisher and registry not examined) | optional container build | `Dockerfile`, `compose.yaml`; DM-05; never executed (U-09) | none | No (HAR-05: not authorised for use) | [Verified Fact] |
| V-08 | JDK (OpenJDK 11.0.32 observed; distributor Unknown) | `legacy_java/ReconcileLegacy.java` source-launcher run | DM-03; not in CI or Docker | none | No (legacy estate only) | [Verified Fact] |
| V-09 | Node.js (v22.23.2 observed) | `legacy_js/legacy_policy.js` | DM-04; no `package.json`; `require('fs')` only | none | No (legacy estate only) | [Verified Fact] |
| V-10 | Reference laptop OS / hardware and device VM | runs goldens (Python 3.10.12), characterization harness, git | OD-23, OD-03a; ~9.8 GB VM disk (OD-16) | none; OS vendor and version Unknown | Yes in practice (only host of the 3.10.12 goldens); no full scorecard, covered under V-01/V-05 concentration | [Verified Fact] usage; [Unknown] vendor |
| V-11 | Data suppliers / partners / integration counterparties | partner feed, vendor CSV, source gateway | all **synthetic, generated in-repo** (`app.generate`, seed 4100); OD-28 (a): no real enterprise systems, endpoints, credentials or SLAs exist | none | No (none real) | [Verified Fact] |

### Absences (each is a finding, not an omission)
- No model/AI provider and no model calls: OD-08; `model-service-scorecard.md` MS-1 (N/A); TST-CO-11/12 tripwires. [Verified Fact]
- No cloud, hosting vendor or managed database chosen: ADR-015 ("No vendor chosen"); `deployment-architecture.md` DA-4. [Verified Fact]
- No third-party Python/JS/Java library, no package manifest, no lock file: DM-08; SS-01; a search of the tree (excluding `data/` and `.git`) for `package.json`, `pom.xml`, `build.gradle`, `requirements*.txt`, `*.lock`, `setup.py`, `Pipfile` found none. [Verified Fact]
- No identity provider, email/SMS, payment, analytics, APM or logging SaaS: ADR-013/016 (local authn, stdlib logs); privacy-impact-assessment ("no telemetry leaves the host"). [Verified Fact]
- `urllib.request` is used in `hub/adapters/` (the one place an HTTP client may be imported) and in legacy `app/gateway_bridge.py` and `scripts/smoke.py`, which target loopback gateway URLs; egress tripwires E05..E09, E20EGRESS, E21, E23 exist. [Verified Fact] (tests not re-run in this docs-only stage)

### Inference
- [Inference] Because the only runtime dependencies are language runtimes, the effective "vendor" risk sits in the **toolchain around the product** (code host, AI coding assistant, test workspace) rather than in the product. Reasoning: SS-01 plus the absences above.

## Evidence References
docs/07-repo-assessment/dependency-map.md DM-01..DM-08; docs/16-repo-validation/security-scan-summary.md SS-01; docs/10-architecture/deployment-architecture.md; docs/10-architecture/adrs/ADR-015-deployment-topology.md; .github/workflows/verify.yml; Dockerfile; compose.yaml; `git remote -v`; `git log` (51 commits, 51 with Claude co-author trailer); .fde/orchestrator-decisions.md OD-05, OD-08, OD-13, OD-23; docs/24-security-privacy/threat-model.md CP-09, CP-10, T-21.

## Assumptions
A-33-01 "Critical" thresholds are agent judgement; confirm: Engagement lead (Dinesh Naik).
A-33-02 The inventory is complete as far as the repository and OD log show; any vendor used outside the repository (real hosting, email, ticketing) is not visible. Confirm: Engagement lead (Dinesh Naik).
A-33-03 The AI coding assistant entry names the model family only as recorded in commit trailers; no product-level contract is implied.

## Unknowns
U-33-01 Contract terms, plan tier, data-use and retention terms for V-03, V-04, V-05 (no document in repo). Resolve: Dinesh supplies them or marks "not applicable".
U-33-02 Provider and region of the orchestrator cloud workspace (V-05).
U-33-03 Python/SQLite distribution on any future production host (V-01/V-02).
U-33-04 Stage 27 SBOM and Stage 32 cost/TCO are not yet produced (upstream gap).
U-33-05 Whether any real vendor exists beyond the repository (A-33-02).

## Unresolved Issues
UI-33-01 Reconcile with the Stage 27 SBOM when produced (expected: runtimes only). Owner: Stage 27 author / Dinesh.
UI-33-02 Stage 32 cost lines for V-03..V-05 are unavailable; none are invented here.

## Residual Risks
RR-33-01 A vendor used outside the repository stays invisible. RR-33-02 Point-in-time view at main 7c60c09.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial draft (Stage 33). |
