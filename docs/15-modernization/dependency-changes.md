---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "dependency-changes.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "pyproject.toml (unchanged)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
**No dependency was added, removed or upgraded in INC-01** (HAR-07/HAR-08 not triggered; CG-7). The harness uses the Python standard library only (`unittest`, `subprocess`, `sqlite3`, `json`, `hashlib`, `shutil`, `urllib`, `concurrent.futures`). It invokes the JDK and Node that are already installed on the device, exactly as Stage 7 did. No network install was made.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| Item | Before | After | Change | Tag |
|---|---|---|---|---|
| Python packages | none beyond stdlib (pyproject `>=3.10`) | same | none | [Verified Fact] |
| Interpreter used | 3.10.12 (device) | 3.10.12 | none (E-4) | [Verified Fact] |
| JDK (CT-11) | OpenJDK 11.0.32.1 present | used, not changed | none | [Verified Fact] |
| Node (CT-13) | v22.23.2 present | used, not changed | none | [Verified Fact] |
| SQLite | 3.37.2 | same | none | [Verified Fact] |
| Network egress | — | servers bound to 127.0.0.1 only; no outbound call | none | [Verified Fact] |
[Verified Fact] No AI/LLM/ML import or call was added (OD-08); the No-AI deny-list guard itself is INC-02 (TB-07).

### INC-02
| Item | Before | After | Change | Tag |
|---|---|---|---|---|
| Python packages | stdlib only | stdlib only (`hub/` imports: argparse, ast, hashlib, html, ipaddress, json, os, re, shutil, socket, sqlite3, sys, threading, urllib.parse, datetime, functools, copy) | none | [Verified Fact] |
| `pyproject.toml` | `requires-python >=3.10`, no deps | unchanged (OD-14 / OD-S12-12: run as `python -m hub`) | none | [Verified Fact] |
| Runtime floor | undecided (OD-S12-12) | enforced at start-up: Python >= 3.10, SQLite >= 3.37 (default); 3.12 selectable | new guard, no dependency | [Verified Fact] |
| No-AI deny-list | none | `hub/guards/no_ai.py` (R1 AI/ML imports, R2 HTTP clients outside `adapters/`, R3 manifests); `python -m hub no-ai-check` clean on hub/, tests/hub/, pyproject.toml | new guard | [Verified Fact] |
| Network egress | none | `python -m hub` installs a loopback-only egress guard; tripwires 0 | new guard | [Verified Fact] |
| CI | `.github/workflows/verify.yml` | unchanged (OD-14) | none | [Verified Fact] |

### DC-INC03 INC-03
[Verified Fact] No dependency added, removed or upgraded; `pyproject.toml`, `compose.yaml`, `Dockerfile`, `.github/` unchanged. New stdlib modules used: `hashlib` (PBKDF2, sha256), `hmac` (compare_digest), `os.urandom`, `ipaddress`, `logging`, `contextlib`, `getpass`, `shutil`, `sqlite3` (via `hub.store.db` only). No-AI deny-list scan of hub/ + tests/hub: 0 findings (TST-CO-11 d, gate G5).
[Verified Fact] New runtime requirement inside the existing floor: `VACUUM INTO` needs SQLite >= 3.27 (floor 3.37, device 3.37.2).

### DC-INC04 INC-04
[Verified Fact] No dependency added, removed or upgraded; `pyproject.toml`, `compose.yaml`, `Dockerfile`, `.github/` unchanged (OD-14). New stdlib modules used: `decimal`, `ast`, `re`, `hashlib`, `json`, `sqlite3` only through `hub.store.db` (TST-CO-04 d). No-AI deny-list scan of hub/ + tests/hub: 0 findings (TST-CO-11 d); full suite under the egress guard: 0 attempts, `model_calls_total` 0.
[Verified Fact] Node (already required by the INC-01 harness, v22 on the device) is used by TST-CO-03 c and S05 to run the legacy JS in the sandbox copy; the product code does not use it. Floor unchanged: Python 3.10, SQLite 3.37.

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `evidence/inc01/final-A_report.json` `tools`; `pyproject.toml`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-02 3.12 behaviour (CT-H5).

## Unresolved Issues
- OD-S12-12 runtime decision (INC-02).

## INC-05
None. Standard library only; no `random`/`secrets` in `hub/`; no network, model or fuzzy-matching import in INC-05 packages (TST-ID-05, S12). TST-CO-11 and TST-CO-13 pass. Verified Fact.

## INC-06
None. Standard library only (the gateway client uses `urllib` under `hub/adapters/`, loopback only); no `random`/`secrets`/`time` in the disallowed places; no model import. TST-CO-11 and TST-CO-13 pass; pyproject and CI unchanged. Verified Fact.

## INC-07
None. Standard library only; no `time`/`random`/`secrets`/network/model import in `hub/runs`, `hub/metrics`, `hub/obs` (S14); no scheduling library or thread (S09). TST-CO-11 and TST-CO-13 pass; pyproject and CI unchanged. Verified Fact.

## INC-08
None. Standard library only (`http.server` / `socketserver` for the loopback listener in `hub/web/server.py`; no `http.client`, `urllib.request`, `ssl`, `socket` client or model import anywhere in `hub/web`, checked by TST-NFR-18); no `time`/`random`/`secrets` in the core modules (`os.urandom` for ids and tokens); the tests use a raw `socket` client on 127.0.0.1 only. TST-CO-11 and TST-CO-13 pass; pyproject and CI unchanged. Verified Fact.

## INC-09
None. Standard library only: `email` / `email.policy` and `html.parser` (archive item text), `unicodedata`, `math`, `decimal`, `hashlib`, `sqlite3`. SQLite FTS5 and the trigram tokenizer are runtime features detected at run time (`hub/search/fts.py`), never required: without them the fallback engine serves the same results. No `time`, `random`, `secrets`, socket, HTTP client or AI import in hub/search or hub/r2 (S08, TST-CO-11). No pyproject.toml or CI workflow change.

## Residual Risks
- RR-DC-1 CI pins Python 3.12 while INC-01 evidence is 3.10.12 only.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-05 (branch `stage-15-inc05-decision-record`): sections added; earlier content unchanged. |
| v0.6 | 2026-10-19 | claude-fde-agent | INC-06 (branch `stage-15-inc06-intake`): sections added; earlier content unchanged. |
| v0.7 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.8 | 2026-10-19 | claude-fde-agent | INC-08 (branch `stage-15-inc08-http-reviewer`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
