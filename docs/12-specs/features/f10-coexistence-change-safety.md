---
stage: "12 — Spec-Driven Design"
artifact: "features/f10-coexistence-change-safety.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/baseline-behaviour.md", "docs/07-repo-assessment/technical-debt-register.md (TD-02)", "docs/10-architecture/adrs/ADR-003-legacy-coexistence-pattern.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/10-architecture/adrs/ADR-018-runtime-stack.md", ".fde/orchestrator-decisions.md (OD-03a)", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for coexistence and change safety (CAP-10): golden harness with an explicit preserve-vs-fix register (DV-01..DV-09, all proposed, none approved), read-only legacy adapters, ten release gates, rollback, protected parallel workflow, structural No-AI enforcement. 9 behaviours, 15 acceptance criteria for FR-CO-01..04.

## Findings
### F10-1 Scope and traceability [Verified Fact: requirement text and legacy state; Inference: design]
Feature **F10 Coexistence & Change Safety** = CAP-10, component C11 (legacy adapters + golden harness), ADR-003 (read-only adapters, shadow comparison, no dual-write), ADR-002 (structural No-AI enforcement), ADR-015/018 (single-host, stdlib), OD-03a (execution only in a full repo copy outside the working tree).

| Implements | FR-CO-01, FR-CO-02, FR-CO-04 (R1 Must); FR-CO-03 (R1 Should) |
|---|---|
| Also constrained by | PNFR-17, PNFR-18, PNFR-19, PNFR-05, PNFR-11, PNFR-13; BR-11, BR-13; RC-4, RC-6, RC-8; CT-01..CT-18; HAR-06, HAR-08, HAR-10 |
| Open decisions | OD-S12-13 (preserve vs fix per golden), OD-S12-12 (target runtime), OPD-15 (owner of the parallel workflow), OPD-10 (buy vs build, ADR-017 not evaluated) |
| Legacy evidence | Stage 7 goldens exist as captures and regenerate byte-for-byte on two runs (characterization-test-plan.md); 14/15 mutants survive the shipped suite (TD-02); ≥5 modules write repo-relative `data/` paths (OD-03a); legacy `data/legacy.sqlite3` sha256 prefix c254649f57e2 (OD-02/09) |

### F10-2 Preserve-vs-fix register (proposed; none approved) [Inference]
| ID | Legacy golden (Stage 7) | New-module behaviour | Nature | Needs |
|---|---|---|---|---|
| DV-01 | SQL report total 742,956.61 (join fan-out, BB-08) | `month_end_total` = 622,826.44 | fix | HAR-06 approval; listed in golden diff |
| DV-02 | REPLAY always marked DUPLICATE (BB-05) | identical content -> NOOP_DUPLICATE, changed content -> REVISED_CONFLICT | fix | HAR-06 |
| DV-03 | quantity < 0 -> REJECTED 'quantity out of range' | NEGATIVE_VALUE flag, kept, reviewer queue | change of class | HAR-06 |
| DV-04 | blank amounts silently skipped (Java) | UNPARSABLE_AMOUNT error / quarantine | fix | HAR-06 |
| DV-05 | JS tolerance with 'abc'/null undefined | E-POL-INPUT-INVALID | fix | HAR-06 |
| DV-06 | unknown region/year -> 999999 unmarked | same value **marked** `defaulted` | additive | none for value; marker only |
| DV-07 | reconcile overwrites `processing_status` in place | append-only outcomes; legacy table untouched | fix | HAR-06 |
| DV-08 | night shift row multiplication (118 distinct in first 500) | rule evaluation per entity, no fan-out | fix | HAR-06 |
| DV-09 | invalid gateway events counted not stored | stored in quarantine | fix | HAR-06 |
Any item not listed that changes a golden is an unapproved deviation and fails the gate.

### F10-3 Release gates (checklist, machine-checkable where noted)
| Gate | Check | Source |
|---|---|---|
| G1 | golden diff: unapproved differences = 0 | FR-CO-01 |
| G2 | replay-safety suite (AC-INT-04/05) passes | FR-CO-03, FR-INT-02 |
| G3 | `verify-audit` ok | FR-SEC-02 |
| G4 | `verify-projection` 0 mismatches | FR-DEC-02 |
| G5 | No-AI tripwire: dependency deny-list clean, no egress, `model_calls_total = 0` | FR-CO-04 |
| G6 | secret scan 0; deletion-path grep 0 | PNFR-08, PNFR-10 |
| G7 | backup/restore rehearsal checksum match | PNFR-05, FR-CO-03 |
| G8 | Zone H negative tests (AC-GATE-09/11/12) pass | FR-GATE-01/03 |
| G9 | planted-string fixture suite (86/22/44) 0 effects | PNFR-13 |
| G10 | determinism: bit-identical across PYTHONHASHSEED/TZ/locale | PNFR-17 |

### F10-4 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-CO-01 | **Golden harness.** `hub golden-compare` replays the Stage 7 capture scenarios (CT-01..CT-16) against the new modules' preserved functions and the legacy code through read-only adapters, and prints every difference as `{golden_ref, legacy, new, disposition}` where disposition is `identical`, `approved_deviation(<dev_id>, <HAR-06 reference>)` or `UNAPPROVED`. Exit code non-zero if any `UNAPPROVED`. | FR-CO-01 |
| BEH-CO-02 | **Deviation register.** `deviation_register` rows `{dev_id, golden_ref, legacy_value, new_value, justification, approval_ref, status}`; `status` in {proposed, approved, rejected}. Only `approved` with a non-empty `approval_ref` counts as approved; DV-01..DV-09 ship `proposed`. Approval is recorded by Dinesh Naik outside the product and referenced. | FR-CO-01 |
| BEH-CO-03 | **Read-only legacy.** C11 opens legacy databases only with `file:<path>?mode=ro` (immutable where the file is a baseline); no new-module code writes under legacy paths; legacy source files (`app/`, `legacy_js/`, `legacy_batch/`, `legacy_java/`, `sql/`, `contracts/`) are unmodified in R1 (git diff on those paths is empty). | FR-CO-01, ADR-003 |
| BEH-CO-04 | **Sandbox guard.** The harness and acceptance suite refuse to run when the working data directory resolves inside the original repository root (E-CO-NOT-SANDBOX) and verify the backup manifest before and after (`sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt`). | OD-03a, FR-CO-01 |
| BEH-CO-05 | **Protected parallel workflow.** `coexistence_inventory` lists protected workflows `{item_id, description, owner, status}`; the older-customer parallel workflow is item CO-WF-01 with `owner = Unknown`. The product exposes it read-only; no endpoint, job or rule can alter, disable or retire it. | FR-CO-02 |
| BEH-CO-06 | **Rollback.** Each release has a rollback procedure document and a rehearsal record: stop process, restore `hub.sqlite3` + anchor file from the pre-release backup, verify checksum and audit chain, restart. Replay-safety (G2) must pass before the release is marked ready. | FR-CO-03, PNFR-19 |
| BEH-CO-07 | **No-AI enforcement.** CI blocks any dependency or import from the deny-list (openai, anthropic, transformers, torch, langchain, llama, sklearn and any HTTP client outside `adapters/`); the process makes no outbound connection except the loopback gateway (egress test with sockets patched); `model_calls_total` metric is emitted and equals 0. Adding any AI element requires a new Stage 8 qualification and Dinesh's decision. AI coding assistants used to build the product are out of scope of this rule (BR-AI-7). | FR-CO-04, PNFR-18 |
| BEH-CO-08 | **Determinism.** Core paths (decision fold, rule evaluation, intake classification, metrics) use no `random`, no wall-clock inside pure functions (time injected), stable ordering, and produce bit-identical output across `PYTHONHASHSEED`, timezone and locale. | PNFR-17 |
| BEH-CO-09 | **Runtime floor.** New code uses only features available in Python 3.10 and SQLite 3.37 until the target runtime is confirmed (ADR-018 says 3.12; `pyproject.toml` declares `requires-python >= 3.10` and no dependencies; dev device is 3.10.12); the start-up self-check prints Python, SQLite and FTS5 versions. | OD-S12-12 |

### F10-5 Error cases
E-CO-NOT-SANDBOX, E-CO-UNAPPROVED-DEVIATION, E-CO-LEGACY-WRITE-REFUSED, E-CO-DENYLIST-IMPORT, E-CO-EGRESS-ATTEMPT, E-CO-RUNTIME-UNSUPPORTED (error-handling-spec.md).

### F10-6 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-CO-01 | all deviation_register rows `proposed` | `golden-compare` runs on the 125-case baseline (sandbox copy) | every difference from DV-01..DV-09 is listed as UNAPPROVED and the exit code is non-zero; with matching approved rows the exit code is 0 | FR-CO-01 | positive |
| AC-CO-02 | a change that alters an unlisted golden (e.g. priority of one case) | the harness runs | reports UNAPPROVED for that golden and fails | FR-CO-01 | negative |
| AC-CO-03 | the Stage 7 goldens CT-01..CT-03 | run through `as-found-*` rule sets | zero differences (cross-reference AC-POL-12..14) | FR-CO-01, FR-POL-04 | positive |
| AC-CO-04 | the new code | a test opens each legacy DB path | only via `mode=ro`; a write attempt raises E-CO-LEGACY-WRITE-REFUSED | FR-CO-01 | negative |
| AC-CO-05 | the repo after an R1 build | `git diff` on legacy source paths | empty | FR-CO-01, ADR-003 | negative |
| AC-CO-06 | a working data directory inside the original repo root | the harness starts | E-CO-NOT-SANDBOX, no run | OD-03a | negative |
| AC-CO-07 | a sandbox run completes | `sha256sum -c --quiet` on the backup manifest is executed from the repo root | exit 0 (all 1,512 files match) | OD-03a, FR-CO-01 | positive |
| AC-CO-08 | the coexistence inventory | read | CO-WF-01 present with owner 'Unknown'; no API route or job named update/retire/disable for it exists | FR-CO-02 | negative |
| AC-CO-09 | a rollback rehearsal in the sandbox | executed from the written procedure | store restored, checksum matches, audit chain verifies, replay-safety suite passes | FR-CO-03, PNFR-19 | positive |
| AC-CO-10 | the release checklist | a release is attempted with G2 failing | release record cannot be marked ready | FR-CO-03 | negative |
| AC-CO-11 | a dependency `openai` added to the project | CI deny-list check runs | build fails E-CO-DENYLIST-IMPORT | FR-CO-04, PNFR-18 | negative |
| AC-CO-12 | the process runs the full acceptance suite with `socket.connect` patched to record attempts | the suite finishes | zero non-loopback connection attempts; `model_calls_total = 0` | FR-CO-04, PNFR-18 | negative |
| AC-CO-13 | core functions run under PYTHONHASHSEED 0/1/random, TZ UTC/Asia/Kolkata/America/Los_Angeles, locale C/en_IN | outputs hashed | all hashes equal; no `random` import in core modules | PNFR-17 | positive |
| AC-CO-14 | a runtime older than the floor (Python 3.9) | the product starts | E-CO-RUNTIME-UNSUPPORTED; on 3.10.12 / SQLite 3.37.2 it starts and prints versions | OD-S12-12 | edge |
| AC-CO-15 | G1-G10 | the pre-release checklist is generated | every gate has a recorded pass/fail with evidence path; any fail blocks | FR-CO-03, PNFR-19 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F10-1 DV-01..DV-09 are the complete set of intended deviations known at Stage 12; Stage 14/15 may add more. Each needs HAR-06 approval.
- A-12-F10-2 Deny-list contents are heuristic (ADR-002).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F10-1 Owner and nature of the parallel workflow for older customers (OPD-15).
- U-12-F10-2 Whether the mutation-kill gate required by ADR-003 (R-1) can be met before cut-over.

## Unresolved Issues
- OD-S12-13 requires Dinesh's per-item preserve/fix decision before Stage 15 code change.
- ADR-018 (Python 3.12) vs device 3.10.12 conflict is open (OD-S12-12).

## Residual Risks
- Golden outputs encode defects; blindly preserving them carries known-wrong numbers (R-07-02).
- Goldens exist for the shipped dataset only; behaviour on real data is Unknown.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
