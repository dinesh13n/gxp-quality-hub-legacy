---
stage: "14 — Transformation / Migration Plan"
artifact: "adapter-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/component-model.md (C11)", "docs/10-architecture/adrs/ADR-003-legacy-coexistence-pattern.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/12-specs/features/f10-coexistence-change-safety.md (BEH-CO-01..04, BEH-CO-07)", "docs/12-specs/spec-readiness.md (RF-1, RF-2, OD-S12-11, OD-S12-17)", "docs/07-repo-assessment/evidence/scripts/ (capture_api.py, capture_batch.py, capture_lib.py, golden_replay.py, mutation_probe.sh)", "data/ listing (legacy.sqlite3, enterprise_legacy.sqlite3, lake/, documents/, archive_documents/)", "integration/source-contract-v1.json, integration/source-gateway.json", "legacy_js/legacy_policy.js, legacy_java/ReconcileLegacy.java, sql/legacy_reports.sql"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
All adapters live in C11 (`hub/adapters/`, working name) and are **one-directional: legacy → hub, read-only**. They are the only hub code allowed to know legacy paths, table names or languages, and the only code allowed an HTTP client (to the loopback gateway; BEH-CO-07). There are 8 adapters (AD-01..AD-08) plus the characterisation harness runner (AD-00) that drives the *unmodified* legacy code for golden capture. No adapter writes to legacy; no anti-corruption mapping silently "fixes" legacy values — fixes are hub-side rules recorded as DV deviations.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### AS-1 Adapter catalogue
| ID | Adapter | Source (evidence) | Direction / access | Used by | Inc | Failure behaviour | Test | Tag |
|---|---|---|---|---|---|---|---|---|
| AD-00 | Characterisation runner: runs legacy Python/Java/JS/SQL **as shipped** in a child process inside a full sandbox repo copy; captures outputs; normalises (CT-H3) | `docs/07-repo-assessment/evidence/scripts/capture_*.py`, `mutation_probe.sh` | executes legacy (sandbox only) | tests/characterization | INC-01 | refuse if cwd inside original repo (E-CO-NOT-SANDBOX) or DB hash ≠ c254649f…d70aa | CT-01..CT-16 | [Verified Fact] scripts exist; [Inference] reuse |
| AD-01 | Legacy case reader | `data/legacy.sqlite3` (`cases`, `operating_costs`, …) | RO `mode=ro&immutable=1` on a per-run snapshot | C3 backfill, C4 parity, C9 | INC-02 (generic), INC-05 (backfill) | E-CO-LEGACY-WRITE-REFUSED on any write | TST-CO-04 | [Inference] |
| AD-02 | Enterprise/domain reader | `data/enterprise_legacy.sqlite3` | RO snapshot | C7, C9 (night-shift parity) | INC-05/07 | same | TST-CO-04 | [Inference] |
| AD-03 | Partner-feed reader | `partner_feeds` table (8,567 rows; 0 conform to source contract, RF-2) | RO; identity = natural key (partner, record_kind, ref_id, source_ts) per OD-10a/OD-S12-17 default | C6 shadow | INC-06 | unknown shape → quarantine reason code, never dropped (DV-09 direction) | TST-INT-* | [Verified Fact] RF-1/RF-2 |
| AD-04 | Gateway client | `services/source_gateway/` on loopback (`SOURCE_PORT`), `integration/source-gateway.json` | HTTP GET only, loopback only; offsets in hub `checkpoint` table (not legacy's) | C6 | INC-06 | unreachable → run record `failed`, no partial commit | TST-INT-*, TST-RUN-* | [Inference] |
| AD-05 | File-drop reader | `data/lake/{tiny,bundled}` CSVs (vendor import, CW-06) | read files from a snapshot dir | C6 | INC-06 | blank amount → UNPARSABLE_AMOUNT (DV-04 direction, shadow only) | TST-INT-* | [Verified Fact] paths |
| AD-06 | Policy-source importer | `app/legacy_logic.py` thresholds, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json`, `sql/legacy_reports.sql` | **transcribed** into versioned as-found rule sets (data), proven equal by golden parity; legacy files never imported as code | C4 | INC-04 | parity diff ≠ 0 → INC-04 cannot merge | TST-CO-03, TST-POL-12..14 | [Inference] |
| AD-07 | Document reader | `data/documents/`, `data/archive_documents/` | read-only; content is **data** (planted strings, PNFR-13) | C10 (R1 rule-trace refs; R2 search) | INC-08/09 | planted-string suite G9 | TST-NFR (G9) | [Verified Fact] planted strings exist (task brief, Stage 0B STOP-05) |
| AD-08 | Legacy output comparator: reads Java/SQL/JS outputs captured by AD-00 to feed `golden-compare` | AD-00 captures | read captures | C11 golden-compare | INC-02+ | missing capture → comparison `NOT-RUN`, gate fails | TST-CO-01/02 | [Inference] |

### AS-2 Adapter rules
1. **No business logic in adapters** — only read, map names, attach provenance (`source`, `source_hash`, `read_at`). [Inference] ADR-003.
2. **Mapping is total and explicit**: every legacy value maps to a hub value or to a quarantine/reason code; nothing is silently skipped (contrast DV-04, DV-09 legacy behaviour). [Inference]
3. **Snapshot first**: each run copies the legacy file into the run's sandbox, records sha256, then opens RO-immutable (CX-2). [Inference]
4. **Version pinning**: adapters assert the expected legacy schema (table/column list) and fail closed with a reason code if it drifts. [Inference]
5. **Removability**: when a capability is cut over and legacy retired (post-R1, not planned here), its adapter is deleted in its own PR; until then adapters are the strangler seam. [Inference]

### AS-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| AF-1 | Existing capture scripts already implement most of AD-00 | `evidence/scripts/capture_*.py`, 2 identical runs, 14/14 replay kills (Stage 7) | INC-01 is a port, not an invention | Low | High | none |
| AF-2 | `business_key` is not an identity; DC-03 wording would quarantine thousands | RF-1 (2,386 / 2,407 groups differ) | AD-03 must use natural key | High if ignored | High | OD-S12-17 |
| AF-3 | Source contract fits `source_messages` 15/15 but partner feeds 0/8,567 | RF-2 | `enforce` would quarantine 100 % of partner feeds | Medium | High | OD-S12-11 (default record_only) |
| AF-4 | JS policy depends on cwd (CT-13 "cwd-dependence") | characterization-test-plan.md CT-13 | AD-00 must set cwd explicitly | Low | High | — |
| AF-5 | JDK and Node exist on the device (`/usr/bin/java`, `/usr/bin/node`) | device check this stage | CT-11/CT-13 runnable in sandbox | Low | High | CI environment Unknown (R-9) |

## Evidence References
See front matter; Stage 7 scripts under `docs/07-repo-assessment/evidence/scripts/`.

## Assumptions
- A-14-07 [Assumption] Transcribing legacy thresholds into data (AD-06) rather than calling legacy code is acceptable, because parity is proven by golden comparison. Confirm: Engagement lead (Dinesh Naik) at INC-04 PR.

## Unknowns
- U-14-06 Whether any real system writes to the legacy DBs concurrently (affects snapshot frequency).

## Unresolved Issues
- OD-S12-11, OD-S12-17 open (defaults usable for build).

## Residual Risks
- RR-AS-1 Adapter schema assertions may be too strict if legacy data is regenerated (partner feeds are not reproducible, CT-14) — mitigated by asserting schema, not content.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial adapter strategy (Stage 14). |
