---
stage: "27 — Production Hardening"
artifact: "dependency-hardening.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["pyproject.toml", "Dockerfile", "hub/security/sbom.py", "docs/27-hardening/evidence/sbom.cdx.json", "hub/guards/no_ai.py", "tests/hub/test_tst_gate_01_22_disposition_gate.py", "docs/27-hardening/evidence/no-ai-check.json", "legacy_js/legacy_policy.js", "legacy_java/ReconcileLegacy.java"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
The product has no third-party dependency to harden: an AST scan of `hub/` and `app/` finds 36 imported top-level modules and every one is part of the Python standard library (`third_party() == []`, test `STG27_B01`). There is no `requirements*.txt`, lockfile, `package.json` or `pom.xml` in the repository. The dependency risk is therefore the **runtime**: Python 3.10.12 (end of life since 2026-10-01 according to the Python developer guide), SQLite 3.37.2, the Node and Java versions the legacy characterization uses, and the container base image. Stage 27 keeps the deny-list gate, adds a CI job for Python 3.12 and 3.13 as a file, and leaves the floor decision (3.10 vs 3.12) to Dinesh.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DH-1 Dependency inventory [Verified Fact]
| Kind | Items | Source |
|---|---|---|
| third-party Python packages | **0** | `sbom.cdx.json`, `hub.security.sbom.third_party()` |
| Python standard-library modules imported by `hub/` and `app/` | 36 (argparse, ast, collections, contextlib, copy, csv, datetime, decimal, email, functools, getpass, hashlib, hmac, html, http, importlib, inspect, io, ipaddress, json, logging, math, os, pathlib, random, re, shutil, socket, socketserver, sqlite3, statistics, sys, tempfile, threading, unicodedata, urllib) | `sbom.cdx.json` |
| JavaScript (legacy golden) | one file, imports only Node's `fs` | `legacy_js/legacy_policy.js` |
| Java (legacy golden) | one file, imports only `java.nio.file`, `java.util` | `legacy_java/ReconcileLegacy.java` |
| container base image | `python:3.12-slim` by tag (not by digest) | `Dockerfile` (legacy) |
| runtime on the laptop | Python 3.10.12, SQLite 3.37.2 (FTS5 available) | `evidence/runtime-selfcheck.json` |

### DH-2 Controls [Verified Fact]
- **No-AI / dependency deny-list** (`hub.guards.no_ai`, TST_CO_11, `python -m hub no-ai-check`, exit 9 on findings): rc 0, 0 findings over `hub`, `tests/hub`, `pyproject.toml` (`evidence/no-ai-check.json`). It covers AI / ML / network client imports; a general new dependency is caught by this gate only if it is on the deny-list, otherwise by the SBOM check below (HAR-08).
- **SBOM gate** (new): `hub.security.sbom.third_party(root)` must be empty; `STG27_B01` fails if a third-party import appears and labels it `third-party-UNREVIEWED`; the CI file runs the same check.
- **Egress guard**: tests run with non-loopback connects refused; E27 repeats the 25 Stage 27 tests under the guard (0 attempts).
- `pyproject.toml` `requires-python = ">=3.10"` and `hub.runtime` floor `3.10` (default) or `3.12` (selectable, `python -m hub --floor 3.12 selfcheck`).

### DH-3 Findings [Inference unless marked]
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved |
|---|---|---|---|---|---|---|
| DEP-01 | Python 3.10 is past end of life (the developer guide lists 2026-10-01; the page itself marks scheduled dates as adjustable and was last dated 2026-05-27, so re-check at adoption) [Verified Fact: the page text; the date reading is an Inference] | `evidence` note in `vulnerability-register.md` VR-02; `Dockerfile` already uses 3.12 | no upstream security fixes for the interpreter | High for any exposure, Medium on a closed laptop | Medium | D-27-02 |
| DEP-02 | SQLite 3.37.2 (Ubuntu 22.04 packaging) has had later upstream releases; distribution back-ports are not visible from here | `selfcheck` | unknown CVE exposure | Unknown | Low | U-27-03 |
| DEP-03 | no hosted 3.12 / 3.13 run of the hub exists | Stage 26 A-26-02 | a version-specific defect would be found late | Medium | Medium | CI file, orchestrator cloud run |
| DEP-04 | GitHub Actions in `verify.yml` and in `ci/hub-hardening.yml` are referenced by tag (`@v4`, `@v5`), not by commit SHA | both files | a moved tag changes what runs | Low-Medium | High | D-27-03; a SHA can not be looked up offline and is not invented |
| DEP-05 | Node patch drift fails characterization CT-13 (golden v22.23.2, laptop v22.23.4) | S24-DEV-04, run in this stage: only CT-13 fails | none on the product | Low | High | refresh the golden under approval (Stage 30) |
| DEP-06 | no lockfile or hash pinning exists because there is nothing to pin | repo scan | none today; the control is the SBOM gate | Low | High | - |

### DH-4 What would change this [Assumption]
Adding any package (HAR-08) would first need a Dinesh decision; after it, `third_party()` lists the package, the SBOM marks it UNREVIEWED, the CI file fails, and a lock or hash-pinning policy, a licence check and a vulnerability scan would have to be added. None of these exists because none is needed.

## Evidence References
- `docs/27-hardening/evidence/sbom.cdx.json`, `no-ai-check.json`, `runtime-selfcheck.json`
- `tests/hub/test_tst_hub_stg27_supply.py` B01 / B02 / C01
- Python developer guide, versions table (fetched 2026-10-25): 3.10 end-of-life 2026-10-01; 3.11 2027-10; 3.12 2028-10; 3.13 2029-10 (scheduled dates in italics on that page)

## Assumptions
- A-27-10 The Python developer guide is read as the authority for end-of-life dates; Dinesh confirms at adoption.
- Stage 12 ADR-018 (3.12 floor) is PROPOSED, not adopted.

## Unknowns
- U-27-01 behaviour on 3.12 / 3.13.
- U-27-03 CVE status of the interpreter and SQLite on the target host.
- U-27-11 Node and Java versions used by the characterization on the orchestrator's machine.

## Unresolved Issues
- D-27-02 floor decision; D-27-03 CI wiring and SHA pinning.

## Residual Risks
- Running on an end-of-life interpreter (VR-02).
- The deny-list is a heuristic list of names; a malicious pure-Python module copied into the tree would be caught by review, not by a tool.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
