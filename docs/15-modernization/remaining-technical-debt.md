---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "remaining-technical-debt.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "docs/07-repo-assessment/technical-debt-register.md", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Debt that remains after INC-01 (legacy debt itself is untouched by design and stays in the Stage 7 register). Items below are about the change-safety net and the open INC-01 conditions.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Debt / open item | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-01 | Harness cannot run in GitHub CI as-is: FX-BASE125 data (`data/*.sqlite3`, `data/lake/`) is git-ignored and absent on the runner; partner tables are not regenerable | CT gate not enforced on PRs | Engagement lead (Dinesh Naik) | before INC-02 merge (fixture provisioning decision, e.g. private artifact) | [Verified Fact] |
| RTD-02 | Harness and mutation gate not wired into `.github/workflows/verify.yml` (existing file, out of INC-01 scope) | manual gate only | orchestrator | later increment / Stage 23 | [Verified Fact] |
| RTD-03 | CT-H5: no Python 3.12 parity run (CI uses 3.12, device has 3.10.12 only). INC-02: floor 3.10/3.37 adopted as default (OD-14) and enforced; 3.12 mode tested only by refusal on 3.10 | runtime-dependent diffs unknown | Engagement lead (Dinesh Naik) | before CUT / Stage 27 | [Verified Fact] |
| RTD-04 | CT-H7 coverage.py unavailable (no installs); kill rate used instead | branch coverage unknown | — | when HAR-08 allows | [Verified Fact] |
| RTD-05 | CT-17 (concurrency) and CT-18 (docker) NOT-RUN | no lock-timeout / container evidence | — | Stage 26/31 | [Verified Fact] |
| RTD-06 | AC-CO-L04..L16 proposed in test metadata only; Stage 12 acceptance criteria not updated (GAP-13-06 partially closed) | traceability partial | Engagement lead (Dinesh Naik) | Stage 16/17 addendum | [Inference] |
| RTD-07 | TB-22 (correct unsafe legacy quick-start docs) not done — would edit an existing file | users may still run destructive tests in the working tree | orchestrator | separate approved docs increment | [Verified Fact] |
| RTD-08 | Supplement golden v1 reviewed only by its authoring agent | weak four-eyes on 7 checks | orchestrator / Dinesh (PR review) | INC-01 PR | [Verified Fact] |
| RTD-09 | Full mutation gate (~5-6 min) had to be run in 4 chunks because device calls are capped at 180 s; a single uninterrupted run was not observed | none functionally (same code path) | — | CI wiring | [Verified Fact] |
| RTD-10 | Negative test of the INC-01 runner golden-manifest check (E-GOLDEN-HASH) not executed. INC-02: the equivalent hub AD-08 check is negatively tested on a synthetic golden dir (TST-CO-02 f, E-FX-HASH); the INC-01 runner path itself is still untested | check partly untested | — | later increment | [Verified Fact] |
| RTD-11 | Shipped tests still overwrite the DB copy they run on (TQ-01): post-run sha 750336f3… — pinned as-found, not fixed | unchanged legacy hazard (sandbox-contained) | — | Stage 30 decision | [Verified Fact] |
| RTD-12 | N4 tail compare tolerates a change only in the clipped start of one stderr tail (`node_cwd_other`) | small blind spot | — | review with CT-H3 list | [Inference] |

### INC-02 additions
| ID | Debt / open item | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-13 | Stage 12 addenda needed: DDL (M000 tables), hub-config schema (4 INC-02 keys), error-handling spec (new codes + exit codes 2-15, RD-19) | specs lag the code | Engagement lead (Dinesh Naik) | Stage 16/17 addendum (HAR-13) | [Verified Fact] |
| RTD-14 | `no-ai-check` and hub tests not wired into CI; BEH-CO-07 says "CI blocks" | No-AI gate is manual | orchestrator | Stage 27/30 (OD-14) | [Verified Fact] |
| RTD-15 | 7 of 9 DV probes use declared target values (DEV-08) | golden-compare proves machinery, not modules | owning increments | INC-04..INC-08 | [Verified Fact] |
| RTD-16 | Untrusted: runtime guard only; AC-INT-23 static check not built | a typed misuse is caught only at run time | — | INC-06 | [Verified Fact] |
| RTD-17 | Deny-list is heuristic and scoped to hub/ + tests/hub + manifests; legacy estate excluded (`app/gateway_bridge.py` uses `urllib.request`) | transitive or renamed packages could slip | — | Stage 24 review | [Inference] |
| RTD-18 | No python3.9 and no `en_IN` locale on the device: AC-CO-14 old runtime simulated; AC-CO-13 locale relies on libc fallback | partial environment coverage | Engagement lead (Dinesh Naik) | CI matrix (Stage 27) | [Verified Fact] |
| RTD-19 | Hub suite takes 110-130 s (TST-CO-12 e re-runs the suite); device calls are capped at 180 s | suite will need chunking (`-k`) as it grows | — | INC-03+ | [Verified Fact] |
| RTD-20 | Gate G1 red by design until DV-01..DV-09 are decided (OD-S12-13 / HAR-06) | merge criterion must accept "UNAPPROVED = DV-01..09 only" | Engagement lead (Dinesh Naik) | before INC-04 | [Verified Fact] |
| RTD-21 | Exit code 2 shared by usage error, E-FX-HASH and E-CFG-INVALID | ambiguous in scripts | — | with RTD-13 | [Verified Fact] |
| RTD-22 | `coexistence_inventory` triggers block all updates, including a future legitimate owner assignment for CO-WF-01 (OPD-15) | needs a migration when the owner is known | — | when OPD-15 answered | [Inference] |

## Evidence References
- `transformation-log.md` TL-3; `behavior-preservation-evidence.md` residual risks.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 CI fixture provisioning approach.

## Unresolved Issues
- RTD-01, RTD-03, RTD-06 need decisions by Dinesh (owner) before or during INC-02.

## Residual Risks
- RR-RTD-1 Until RTD-01/02 are closed, behaviour preservation depends on someone running the harness manually before each merge (OD-13 orchestrator check).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
