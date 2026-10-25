---
stage: "38 — Handover + Knowledge Transfer"
artifact: "architecture-handover.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/target-architecture.md", "docs/10-architecture/component-model.md", "docs/10-architecture/adrs/ADR-001..018", "docs/10-architecture/deployment-architecture.md", "docs/21-integration/", "docs/12-specs/", "hub/ (package listing)", "docs/37-operating-model/service-ownership-map.md", "docs/30-release/deployment-strategy.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. This is the handover of a PREPARED-BUT-UNRELEASED system: Stage 30 is BLOCKED (0 of 40 approvals), no cutover, authority flip, tag or release happened, and the hub is not deployed beyond loopback. The only human is Dinesh Naik, Engagement lead (OD-04). No receiving team, trainee, walkthrough audience, exercise result, sign-off or approval is invented here; vacant roles stay vacant (Stage 37). Nothing here accepts a risk (HAR-11). The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
What a receiver must understand about the architecture, and where it is *proposed* rather than accepted. The target is a **No-AI modular monolith** (the "hub", Python package `hub/`) with its own SQLite store, an append-only event store and a hash-chained audit log, running **beside** the untouched legacy estate and reading legacy stores only through read-only adapters (`target-architecture.md` Summary, TA-1). It ships inert: loopback only, scheduler off, no active rule set, empty Zone H holders. Status of the architecture decisions: ADR-001..018 exist; per the Stage 10 label they are PROPOSED unless an OD entry says otherwise (OD-14: build proceeded on PROPOSED ADRs at risk). This document does not upgrade any ADR to ACCEPTED.

## Findings
### AH-1 Shape [Verified Fact: target-architecture.md TA-1]
HTTP layer (API and server-rendered pages, no business logic) over a service layer (Gate/Zone H, Decision Record, Policy/Rules, Intake, Crosswalk, Runs, Metrics, Reviewer support, Audit) over repositories (SQLite; a Postgres swap is described as possible, ADR-004). Adapters (`hub/adapters/`) read `data/legacy.sqlite3`, the enterprise legacy database, the loopback gateway (`services/source_gateway`), partner CSV and the docs archive. CLI jobs write run records; external triggering is disabled until OPD-11 is decided.

### AH-2 Zones [Verified Fact: TA-2]
Zone H = disposition, QA release, e-signature, closure failing the evidence rule, adoption of definitions/rules/active rule set; enforced in the gate; non-human actors rejected (FR-GATE-03). Zone D = everything else. Zone A (AI) = empty, no component admitted (OD-08).

### AH-3 Package map (directory level) [Verified Fact: `hub/` listing; file-level responsibility not re-read, A-37-SO-3]
`hub/core` (errors, untrusted-text), `hub/store` (db, migrations), `hub/security` (auth, authz, zone_h, audit, anchor_seal, settings), `hub/decision` (decision record, projections), `hub/policy` (rule sets, clocks, withdrawal), `hub/gate` (disposition gate), `hub/intake`, `hub/crosswalk`, `hub/adapters`, `hub/review` (reviewer queue), `hub/search` and `hub/r2` (keyword/FTS and R2 corpus), `hub/runs`, `hub/metrics`, `hub/obs` (observability), `hub/resilience` (built, not wired), `hub/control` (flags, authority switch), `hub/ops` (backup, release checklist, gates), `hub/release` (go/no-go evaluator, not wired), `hub/golden` (golden-compare), `hub/guards` (no-AI, egress), `hub/web` (loopback HTTP), `hub/admin` (host-operator CLI), `hub/coexistence` (deviation register).

### AH-4 What is NOT in place and a receiver must not assume [Verified Fact]
| Item | State | Evidence |
|---|---|---|
| Deployment beyond the laptop and sandboxes | none; no host, no consumer | OD-28 (a), U-30-12 |
| TLS / exposure | loopback only; bind refusal for non-loopback (E-SEC-EXPOSURE-NOT-APPROVED, exit 9) | `security-readiness.md`; DS-6 |
| Resilience mechanisms (GuardedGateway, BoundedLoopbackServer) | built, **not wired** into `gateway-pull` / `hub web serve` | OD-35, DS-4 |
| Observability modules | built, **not wired** to a live source; no telemetry sink | S31-DEV-01, D-31-01/02 |
| Rule sets | three as-found sets loaded INACTIVE; activation needs a recorded human decision | OD-16, OD-17 |
| Authority switch | CLI + `approval_ref`, ships off (DW-17); never flipped outside a sandbox | OD-26, OD-31, OD-37 |
| Scheduler | OFF (HAR-10) | OD-19 |
| CI over `hub/` | none; `.github/workflows/verify.yml` covers legacy only; `ci/hub-hardening.yml` exists but is **not installed** (HAR-07) | OD-34, PA-16 |

### AH-5 Architecture decisions that are still open (carry to the receiver) [Verified Fact: OD entries]
- Runtime: code floor Python 3.10 (pyproject `requires-python >=3.10`), production target 3.12+ (OD-24); ADR-018 says 3.12; no Python 3.12+ evidence exists (OD-33); D-27-02 open.
- Source-contract mode `record_only` everywhere; per-source contracts and allowed schema_version list open (OD-28).
- Scheduler vs HAR-10 / OPD-11; retention (hold-all, OD-30); privacy regime (RS-06); legacy Dockerfile/compose hardening (D-27-06, not authorised for use, HAR-05).
- DV-01..DV-11 preserve-or-fix (OD-S12-13) decide whether the hub's observed behaviour matches legacy; **`golden-compare` exits 6 until decided**.

### AH-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| AHF-01 | [Verified Fact] The architecture is documented end to end (ADR-001..018, component model, deployment architecture, specs, integration docs) but not operated | `docs/10-architecture/`, `docs/12-specs/`, `docs/21-integration/` | A receiver can read it; no live behaviour to observe | Medium | High | Who validates against a real organisation? |
| AHF-02 | [Verified Fact] Baseline `data/*.sqlite3` and `data/lake/` are **git-ignored**; the repo clone alone does not contain the baseline. The verified copy is `../_data-backup-2026-10-17/` (SHA256SUMS.txt) on the same device | `.gitignore`; OD-03; PA-13 | A receiver cloning from the remote has no baseline | High (handover) | High | Where does a durable, off-device copy live? (F-29-02, AP-OPS-04) |
| AHF-03 | [Verified Fact] Regenerating the baseline is not equivalent: `app.generate --count 125 --seed 4100 --reset` gave sha256 5068c2b4... vs shipped c254649f... | `s30-log-32-regenerate-125.txt`, rollback-plan RB-4 | Goldens and checksums bound to the shipped file | Medium | High | Is the 125-case file the permanent baseline? (OD-09 says yes) |
| AHF-04 | [Verified Fact] Characterization goldens are environment-specific (Python 3.10.12, the reference laptop); CT-13 fails on Node patch drift only (S24-DEV-04) | OD-23, OD-32 | A new environment will show harness differences that are not regressions | Medium | High | Who re-baselines goldens? |
| AHF-05 | [Inference] Loopback-only plus inert defaults means the architecture is safe to leave unattended only while nothing is switched on (TF-03) | `release-boundaries.md`, OD-16..OD-20 | Owner acceptance is a precondition to any activation | Medium | High | Make owner acceptance an entry condition for CUT-1 (Stage 37 question) |
| AHF-06 | [Inference] Reading order for a newcomer is not obvious from `docs/` alone (40 stage folders plus legacy notes at the top level) | `docs/` listing | Slow onboarding | Low | Medium | See `handover-index.md` |

## Evidence References
`docs/10-architecture/target-architecture.md` TA-1..TA-3; `docs/30-release/deployment-strategy.md` DS-1..DS-6; `docs/37-operating-model/service-ownership-map.md` PA-01..PA-28; ADR files listed.

## Assumptions
- A-38-AH-1 Directory-level package responsibilities are inferred from names plus the Stage 37 map; file-level reading was not done in this stage. Confirm: Build agent / first receiving engineer.
- A-38-AH-2 ADR statuses remain PROPOSED unless stated; no ADR acceptance is claimed. Confirm: Dinesh.

## Unknowns
- U-38-AH-1 Behaviour on real data, load, or an organisation's identity provider (none exists).
- U-38-AH-2 Consumers of the 13 legacy outputs outside the repo (OD-28).

## Unresolved Issues
- AH-5 list; AHF-02 durable baseline copy.

## Residual Risks
- RR-38-AH-1 Receiver mistakes built-but-unwired modules for operating protection (breaker, cap, telemetry). Medium; mitigated by AH-4.
- RR-38-AH-2 Single-device baseline (F-29-02). High if device lost.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 38). |
