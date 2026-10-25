---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "service-ownership-map.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["hub/ (directory listing)", "services/source_gateway", "app/, legacy_batch/, legacy_java/, legacy_js/", "Dockerfile, compose.yaml, environments/*.env.example, .github/workflows/verify.yml", "data/ and ../_data-backup-2026-10-17/SHA256SUMS.txt (OD-03, OD-03a)", "operations/runbook.md, operations/incidents/INC-2025-014.md", "docs/33-vendor-risk/vendor-inventory.md V-01..V-11", "docs/25-governance/accountability-map.md", "docs/18-delivery/ownership-map.md OM-3", "docs/14-transformation/cutover-plan.md", "docs/17-implementation-prd/release-boundaries.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Inventory of **28 production-relevant assets (PA-01..PA-28)** and who owns each. "Production asset" here means anything a steady-state operator would have to keep working, or whose loss/change would matter, including toolchain and evidence assets. The product is not in production (no deployment, no real data, loopback only: ADR-015, OD-28), so "production" is read as "what a handover would transfer".

Result: **25 assets have Dinesh Naik as INTERIM owner of record, 1 is N/A (PA-28, No-AI), and 2 are VACANT with no owner at all (PA-25, PA-26). 0 of 28 has an ACCEPTED steady-state owner.** A further 6 INTERIM assets (PA-02, 04, 05, 11, 12, 20) also depend on a client-side role that is VACANT. This is the central gap behind the CONDITIONAL PASS.

## Findings
### SO-1 Asset inventory and ownership
Legend: State = INTERIM / VACANT / N/A (see `target-operating-model.md` TOM-2). "Needed role" = the role that should own it in steady state (from TOM-4). Evidence tag applies to the existence of the asset.

| ID | Asset | Evidence (path) | Owner of record | State | Needed steady-state role | Tag |
|---|---|---|---|---|---|---|
| PA-01 | Hub application: core, store, CLI, loopback HTTP | `hub/__init__.py`, `hub/cli.py`, `hub/web/`, `hub/core/`, `hub/store/` | Dinesh Naik | INTERIM | RL-02 Service owner | [Verified Fact] |
| PA-02 | Zone H gate and holder list | `hub/security/zone_h.py`, `hub/gate/`, `hub/security/settings.py` (`zone_h.holders` empty) | Dinesh Naik (for the control code and the holder-list decision only) | INTERIM; **holder role VACANT** | RL-04 dispositioner (outside any engagement) | [Verified Fact] |
| PA-03 | Audit trail, hash chain, anchor | `hub/security/audit.py`, `hub/security/anchor_seal.py`, `hub/decision/` chain | Dinesh Naik | INTERIM | RL-05 / RL-06 (oversight), RL-02 (operation) | [Verified Fact] |
| PA-04 | Rule service and the three inactive candidate rule sets | `hub/decision/service.py`, `hub/policy/` | Dinesh Naik | INTERIM; **rule authority role VACANT** (DR-23, OD-S12-04) | RL-03 process owner + RL-04 for activation | [Verified Fact] |
| PA-05 | Intake, source gateway, adapters, crosswalk | `hub/intake/`, `hub/adapters/`, `hub/crosswalk/`, `services/source_gateway/` | Dinesh Naik | INTERIM; **source-contract owner VACANT** (U-17-IP-2) | RL-08 | [Verified Fact] |
| PA-06 | Reviewer queue, disposition gate UI/API | `hub/review/`, `hub/gate/`, `hub/web/` | Dinesh Naik | INTERIM | RL-02; users RL-11 | [Verified Fact] |
| PA-07 | Runs, metrics, observability | `hub/runs/`, `hub/metrics/`, `hub/obs/` | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-08 | Search and R2 corpus | `hub/search/`, `hub/r2/` | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-09 | Release checklist, backup, gates | `hub/ops/release.py`, `hub/ops/backup.py`, `hub/ops/gates.py` | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-10 | No-AI and egress guards (tripwires) | `hub/guards/no_ai.py`, `hub/guards/egress.py`; TST-CO-11/12 | Dinesh Naik | INTERIM | RL-02 (run), RL-05 (policy) | [Verified Fact] |
| PA-11 | Hub datastores (SQLite) and audit store | hub store modules; files under git-ignored `data/` | Dinesh Naik | INTERIM; **data-owner role VACANT** | RL-07 | [Verified Fact] |
| PA-12 | Legacy estate (read-only adapters, batch, Java, JS) | `app/`, `legacy_batch/`, `legacy_java/`, `legacy_js/` | Dinesh Naik | INTERIM; **legacy technical owner VACANT** (SH-08) | RL-10 | [Verified Fact] |
| PA-13 | Baseline data and backup | `data/legacy.sqlite3` (125 cases, seed 4100, OD-09); `../_data-backup-2026-10-17/` + `SHA256SUMS.txt` | Dinesh Naik | INTERIM | RL-07 | [Verified Fact] |
| PA-14 | Synthetic fixtures (86 feed rows, 22 injection docs, 10 variants) | `tests/`, PCH-31 (OD-25) | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-15 | Source repository, history, tag `baseline-as-found` (a6eb4e8), GitHub remote | `git remote -v`; OD-05, OD-06; V-03 | Dinesh Naik (holds the account in effect) | INTERIM; terms Unknown | RL-12 | [Verified Fact] usage; [Unknown] terms |
| PA-16 | CI workflow (never run; does not cover `hub/`) | `.github/workflows/verify.yml`; V-06 | Dinesh Naik | INTERIM | RL-12 / RL-02 | [Verified Fact] |
| PA-17 | Characterization harness and goldens (Python 3.10.12, laptop) | OD-23; `tests/characterization/` | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-18 | Full-regression cloud workspace (Python 3.13; provider Unknown) | OD-23, OD-27, OD-30; V-05 | Dinesh Naik | INTERIM | RL-12 | [Verified Fact] usage; [Unknown] provider |
| PA-19 | Engagement documentation corpus and OD log | `docs/00-*..37-*`, `.fde/orchestrator-decisions.md` | Dinesh Naik | INTERIM | RL-01 until closure; then RL-02 | [Verified Fact] |
| PA-20 | Runbook and incident records | `operations/runbook.md`, `operations/incidents/INC-2025-014.md` (follow-up owner unknown, DR-27) | Dinesh Naik | INTERIM; **incident owner VACANT** | RL-02 + incident role (Stage 29) | [Verified Fact] |
| PA-21 | Container artifacts (not authorised for use, HAR-05) | `Dockerfile`, `compose.yaml` | Dinesh Naik | INTERIM | RL-02 | [Verified Fact] |
| PA-22 | Configuration, decision flags, environment templates | `hub/config.py`, `environments/{dev,staging,production-like}.env.example`, `docs/14-transformation/feature-flag-plan.md` | Dinesh Naik | INTERIM (flag moves need `approval_ref`) | RL-02 with RL-03 for decision flags | [Verified Fact] |
| PA-23 | Credentials and tokens (local password hashes, service tokens) | `hub/security/auth.py`; no real credentials exist (OD-28) | Dinesh Naik | INTERIM | RL-05 | [Verified Fact] none real |
| PA-24 | Registers: deviation (DV-xx), risk acceptance (RA/RP/RS), vendor acceptance (VA-01..07 PROPOSED) | `docs/16-repo-validation/`, `docs/25-governance/risk-acceptance-register.md`, `docs/24-security-privacy/residual-security-risks.md`, `docs/33-vendor-risk/vendor-risk-acceptance.md` | Dinesh Naik (only person who may accept) | INTERIM | RL-01 / RL-05 / RL-06 | [Verified Fact] |
| PA-25 | Nightly file exchange (ADR-007) | `docs/decisions/ADR-archived-007.md` ("owner transferred 2024", unnamed) | **none** | **VACANT** | RL-10 / RL-08 | [Verified Fact] gap |
| PA-26 | Parallel legacy-customer workflow (OPD-15) | `docs/09-initial-prd/capability-map.md` U-09-05 | **none** | **VACANT** | RL-03 | [Verified Fact] gap |
| PA-27 | AI coding assistant used to build (dev tooling, not product AI) | V-04; OD-08; all 51 of 51 commits carry the co-author trailer (Stage 33 count) | Dinesh Naik | INTERIM; terms Unknown | RL-12 | [Verified Fact] |
| PA-28 | Models, prompts, retrieval indexes, agent tools (product) | none exist; OD-08; 0 model calls | n/a | **N/A** | none while No-AI; owner required before any RQ-1..RQ-3 re-qualification | [Verified Fact] |

PA-25 and PA-26 are the only two assets with no interim owner of record; they belong to the legacy estate and the business, not to the hub, and Dinesh has not taken them on. They are shown as VACANT, not assigned, in line with the Stage 37 exclusion rule.

### SO-2 Service-level ownership (what a "service" is here)
| Service | Components | Interim owner of record | Operating status | Tag |
|---|---|---|---|---|
| S-HUB core service | PA-01, 03, 04, 05, 06, 07, 08, 11 | Dinesh Naik | not deployed; loopback only; scheduler off | [Verified Fact] |
| S-CONTROL human-control service | PA-02, PA-10 | Dinesh Naik (code); holder role VACANT | gate refuses every request on a fresh install (AC-GATE-02) | [Verified Fact] |
| S-RELEASE release and evidence service | PA-09, 15, 16, 17, 18 | Dinesh Naik | manual; no CI over `hub/` | [Verified Fact] |
| S-LEGACY legacy-parallel estate | PA-12, 13, 25, 26 | Dinesh Naik for code in repo; exchange and workflow VACANT | unchanged since `baseline-as-found` | [Verified Fact] |

### SO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SF-01 | [Verified Fact] Every asset is shown as INTERIM (25), N/A (1) or VACANT (2); none is silently unowned and none is shown as accepted | SO-1 | Ownership completeness is documented, not achieved | High (real use) | High | Who accepts? |
| SF-02 | [Inference] Assets whose steady-state owner must be a client role (PA-02, 04, 05, 11, 12, 20, 25, 26) cannot be satisfied by any amount of engagement work | OD-04; `stakeholder-map.md` | Handover to nobody | High | High | Does a receiving team exist? (U-37-TOM-1) |
| SF-03 | [Inference] Concentration: one person is owner of record of 25 of 28 assets and the accountable party for all decisions | SO-1 | Bus factor 1; no separation of duties | Medium-High | High | DQ-17 follow-up |
| SF-04 | [Verified Fact] PA-18 and PA-27 sit in third-party environments with unknown terms | V-04, V-05, U-33-01, U-33-02 | Evidence continuity depends on accounts nobody else controls | Medium | High | VA-02..VA-04 decision |

## Evidence References
See `evidence_sources`. Cross-checks: `docs/18-delivery/ownership-map.md` OM-3 (gaps carried: Zone H holders, rule authority, definitions, source contract owner, consumers, steady-state repo/data/runbooks, parallel workflow); `docs/33-vendor-risk/vendor-inventory.md` V-01..V-11.

## Assumptions
- A-37-SO-1 [Assumption] The asset list is complete as far as the repo shows; assets outside the repo are not visible (consistent with A-33-02). Confirm: Engagement lead (Dinesh Naik).
- A-37-SO-2 [Assumption] Placing Dinesh as interim owner of record reflects A-18-OM-1, not a statement by him that he will operate the service. Confirm: Engagement lead (Dinesh Naik).
- A-37-SO-3 [Assumption] Directory-level paths for PA-04/07/08 are taken from the `hub/` listing; file-level responsibility was not re-read for this stage. Confirm: Build agent at next build stage.

## Unknowns
- U-37-SO-1 Consumers of the 13 legacy outputs outside the repo (OD-28).
- U-37-SO-2 Whether any asset (hosting, DNS, certificates, secrets store) exists outside the repo.

## Unresolved Issues
- Steady-state acceptance for PA-01..PA-24, PA-27; owners for PA-25, PA-26; holder roles for PA-02/04/05/11/12/20.

## Residual Risks
- RR-37-SO-1 Handover without an accepting owner (High for real adoption). Not accepted.
- RR-37-SO-2 Evidence held on accounts with Unknown terms (Medium). VA-02..VA-04 PROPOSED, not decided.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
