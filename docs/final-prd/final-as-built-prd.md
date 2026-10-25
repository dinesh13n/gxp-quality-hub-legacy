---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-as-built-prd.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/", "docs/17-implementation-prd/", "docs/13-traceability/", "docs/20-application/", "docs/26-tevv/", "docs/30-release/", "docs/37-operating-model/", "docs/38-handover/", "docs/41-retirement/", "docs/42-executive-defence/", ".fde/orchestrator-decisions.md", "hub/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
The as-built PRD for the GxP Quality Hub. What exists: a tested, stdlib-only, No-AI shadow hub with every consequential switch off. What does not exist: a release, a user, a measured benefit, an accepted owner, an approval or a sign-off. Gate BLOCKED. Authoritative only as 'as-built, NOT released'; acceptance is left to Dinesh Naik (OPEN).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### 0. Gate and authority statement
| Item | Value |
|---|---|
| Stage gate | **BLOCKED** (documents complete; four blocking conditions B-1..B-4 in `final-product-baseline-signoff.md`) |
| Authority of this PRD | **Authoritative only as: 'as-built, NOT released'.** It is the best evidence-based record of what exists in `main` 08add05. It is not a release record, an acceptance record, a value record or a compliance record |
| Release | **NOT executed.** Stage 30 gate BLOCKED; 0 of 40 approvals; evaluator NO-GO |
| Handover / retirement | Stage 38 BLOCKED; Stage 41 BLOCKED; nothing retired; legacy authoritative |
| Executive defence | Stage 42 CONDITIONAL PASS for documents; value NOT COMPUTABLE |
| Acceptance of this PRD | **OPEN - left to Dinesh Naik** |
| Baselines preserved | Stage 9 (`docs/09-initial-prd/`) and Stage 17 (`docs/17-implementation-prd/`) unchanged |
| Folder | `docs/final-prd/` (named by the stage prompt); see S43-DEV-01 |

**Required final-response elements.** (1) Status BLOCKED. (2) Disposition: Delivered 44, Delivered + Deferred part 3, Changed 4, Deferred 1, Rejected 0, Superseded 0 (52 FR); 'Delivered' = built in shadow, not released. (3) Key findings: section 3. (4) Major risks: `residual-risk-register.md` R1-R18. (5) Assumptions / unknowns: section 4. (6) Artifacts: section 1. (7) Blocking issues: B-1..B-4. (8) Next action: Dinesh decides release/stop question and records sign-off or rejection (section 9).

### 1. Document set (20 files in `docs/final-prd/`)
| # | File | Purpose |
|---|---|---|
| 1 | `final-as-built-prd.md` | This PRD |
| 2 | `requirement-disposition-matrix.md` | 52 FR + 20 PNFR dispositions |
| 3 | `final-capability-map.md` | CAP-01..CAP-10 and switch state |
| 4 | `as-built-architecture.md` | Architecture, not-wired list, ADR status |
| 5 | `final-api-interface-baseline.md` | HTTP, CLI, inbound integrations, error codes |
| 6 | `final-data-knowledge-baseline.md` | Data, retention, backup |
| 7 | `final-ai-agent-baseline.md` | N/A: No-AI |
| 8 | `final-security-governance-baseline.md` | Security, Zone H, governance |
| 9 | `final-nfr-baseline.md` | NFR baseline and proof class |
| 10 | `final-acceptance-evidence-map.md` | Technical and human acceptance state |
| 11 | `implemented-vs-deferred.md` | Built, deferred, not executed; switch state |
| 12 | `known-limitations.md` | KL-01..KL-24 |
| 13 | `residual-risk-register.md` | Index of risk registers; R1-R18 |
| 14 | `production-kpi-baseline.md` | No production baseline; synthetic position |
| 15 | `final-economics-baseline.md` | No value; ROI not computable |
| 16 | `final-operating-boundaries.md` | Hard limits and gates |
| 17 | `final-ownership-map.md` | Roles and owners (mostly vacant) |
| 18 | `approved-roadmap.md` | Proposed (NOT approved) gated roadmap |
| 19 | `final-product-baseline-signoff.md` | Sign-off form, blank |
| 20 | `open-items-and-decision-register.md` | Consolidated open items and decisions (extra) |

### 2. The product as built (PRD body)
**2.1 Problem and intent (unchanged from Stage 9).** [Verified Fact] A synthetic GxP quality-operations repository (batch-deviation / CAPA cases) shows eight confirmed repo-level structural root causes RC-1..RC-8 (e.g. case state is a mutable snapshot, three divergent rule implementations, non-idempotent intake, month-end figures with join fan-out). [Verified Fact] The intent is one attributable record of each case and its decisions, safe handling of external case information, and figures that declare their definitions, with batch disposition staying human and the product No-AI. [Unknown] Whether the problem exists in a real organisation, its size or its cost (C-01, C-02).

**2.2 Users and personas.** [Verified Fact] PER-01..PER-08 are documentary personas; no real user, interview, ticket, volume or cost exists. Dinesh Naik is the only human.

**2.3 What was built.** [Verified Fact] A shadow `hub/` (204 Python files, 17,247 lines counted at 08add05; stdlib only) implementing CAP-01..CAP-10, beside untouched legacy code and data. It is loopback-only, uses a single SQLite file with insert-only tables and a hash-chained audit trail, and contains no AI. See `as-built-architecture.md`.

**2.4 How it ships.** [Verified Fact] Every consequential switch is off: no Zone H holder, disposition mode `none`, no adopted policy, no active rule set, schedule off, authority switch unset, case creation disabled, search/templates off, contracts `record_only`, loopback only, synthetic data only (T-07 pass on shipped defaults). Legacy remains authoritative for every output.

**2.5 Requirement disposition.** See `requirement-disposition-matrix.md`. Counts: 52 FR = Delivered 44 + Delivered with a Deferred part 3 + Changed 4 + Deferred 1 + Rejected 0 + Superseded 0. 20 PNFR: dispositions in DM-4. [Inference] 'Delivered' is a statement about code and sandbox tests, not about use.

**2.6 What was added beyond the PRD.** BX-01..BX-05 (authority switch, resilience, observability, release evaluator, hardening behaviours). None was approved as a requirement.

### 3. Key findings
| # | Finding | Class | Evidence | Confidence |
|---|---|---|---|---|
| F1 | 51 of 52 FRs are built at least in part in the shadow hub (44 Delivered, 3 Delivered with a Deferred part, 4 Changed); 1 (FR-MET-08) is Deferred; none is in use | Verified Fact (Stage 17 state + Stage 20 deltas) | disposition matrix | High (Stage 17) / Medium (HEAD) |
| F2 | Release was not executed; gate BLOCKED; 0 of 40 approvals; evaluator NO-GO (G1, T-09, T-10 fail; T-05 not run) | Verified Fact | release-outcome; approvals-register.json; gate-results.json | High |
| F3 | No production, no users, no after-window; K-21 = 0 of 125 | Verified Fact | after-intervention-kpi-sheet | High |
| F4 | ROI, NPV, payback NOT COMPUTABLE; no value realised | Verified Fact | Stage 36 | High |
| F5 | The human gate has never been exercised by a real person (no holders) | Verified Fact | OD-17, OD-31 | High |
| F6 | The only parity KPIs show imported snapshots, not improvement | Verified Fact | Stage 34/35 | High |
| F7 | Security adequate only for synthetic loopback shadow; no TLS, no 2FA, no pen test | Verified Fact | Stage 24, 27 | High |
| F8 | Resilience, observability, release evaluator, CI built or written but not wired / installed | Verified Fact | OD-34..OD-36 | High |
| F9 | All roles but Dinesh vacant; 0 of 28 assets with accepted owner; no receiver | Verified Fact | Stage 37, 38 | High |
| F10 | Many numeric defaults are agent assumptions, not approvals | Verified Fact | OD-32..OD-36 | High |
| F11 | The build process needed the orchestrator's full regression to catch defects four times | Verified Fact | OD-28, 32, 35, 36 | High |
| F12 | Documents drift: 16 reconciliation items AB-1..AB-16 (section 6) | Verified Fact | this stage | High |

(Reconciliation with earlier counts: Stage 17 and Stage 42 say '49 built, 2 partial, 1 not built' = 51 built at least in part + 1 not built. Same total here; the split differs because FR-POL-01 withdrawal was completed at Stage 20 (AB-4) and the Changed/Deferred-part vocabulary is finer.)

### 4. Evidence classes: separation of Verified Fact / Inference / Assumption / Unknown
**Verified Fact (examples; each cited in the companion files).** 125-case synthetic baseline sha256 `c254649f…d70aa`; 48 operations in openapi.yaml; hub = 204 files / 17,247 lines (my count); 40 approvals all OPEN; 18 ADR files DRAFT; harness 134/134 at Stage 16/20; Stage 30 criteria results; all consequential switches off at shipped defaults.
**Inference (reasoning stated where used).** 'Delivered' totals overstate user-visible capability (no FR is in use); 90 days reaches at most a limited-entry decision; a 30-day pilot may be too short for a month-end; no operating boundary an on-call person could rely on exists; single-device loss would be unrecoverable.
**Assumption (owner: Engagement lead (Dinesh Naik) unless noted).** Per-FR states hold at 08add05 except named deltas (A-43-01); all numeric defaults of Stages 24, 27, 28, 31 (PBKDF2 600,000; lockout 5/15/15; rate limit 100/60 s; retries 3; breaker 3/60 s; cap 64; RTO 4 h / RPO 1 working day; SLO candidates); Stage 0C cost ranges; PNFR targets (99.5 %, 06:00, 4 h, 24 h); field-class map; evidence-access matrix; Stage 27 error behaviours; severity and likelihood ratings.
**Unknown.** Existence and size of the real problem; any production KPI value; real consumers of the 13 legacy outputs; real systems and credentials; real privacy regime; who would own the service; test totals at HEAD; ADR-by-ADR acceptance intent; 3.12+ behaviour of goldens; FTS5 availability on the target; remote branch-protection state; cost of hosting, toolchain and effort.

### 5. Reconciliation against the as-found PRD and earlier stage documents (headline)
The as-found/initial PRD (Stage 9, 52 FR / 20 PNFR / 10 capabilities / No-AI) is **honoured, not copied**: IDs are unchanged, scope boundaries and non-goals NG-01..NG-10 stand, product intent is unchanged. Differences between intent and as-built are: 4 Changed FRs, 1 Deferred FR, 3 split FRs, PNFR rewordings/target changes (PNFR-03/04/06/13), the runtime decision (production 3.12+, code floor 3.10), the OD-18 intake key, inactive rule sets, human-only facts, schedule held, and the added BX-01..BX-05 scope. The Stage 17 PRD is the closest predecessor; its 48 changes PCH-01..PCH-48 are carried (41 Applied, remainder Proposed/Recorded) and the later-stage deltas are in AB-4.

### 6. Reconciliation register (differences found between documents)
| ID | Difference | Resolution used here | Class |
|---|---|---|---|
| AB-1 | Stage 42 index C-32 says Stages 38 and 41 do not exist | Superseded by OD-38: both exist (PRs #28, #30), both BLOCKED | Verified Fact |
| AB-2 | Stage 16 hub size 163 files / 13,994 lines vs 204 / 17,247 counted at 08add05 | Use the later count; growth is Stages 20-31 | Verified Fact (my count) |
| AB-3 | PNFR-05 RTO 8 h / RPO 24 h (Stage 17) vs Stage 29 RTO 4 h / RPO 1 working day | Both are agent assumptions; unreconciled; Dinesh to choose (Q-29-03, C-5) | Verified Fact (conflict); Unknown (intent) |
| AB-4 | Stage 17 per-FR gaps closed later: POL-01 withdrawal (Stage 20 DW-07), CO-01 observed probes (DW-04), REV-01 produce-traces command (DW-08), single Zone H check (DW-06) | Matrix updated; marked A-43-01 | Verified Fact |
| AB-5 | Stage 17 baseline is main 8a8e8db / code 2c63b07; as-built is main 08add05 | As-built = 08add05 | Verified Fact |
| AB-6 | Stage 25 compliance matrix predates Stage 23/24 (RP-10) | Not re-issued; flagged as stale | Verified Fact |
| AB-7 | Stage 40 roadmap baseline ef72e4e: Stage 39 unmerged, F-29-01 unfixed, Stage 30 outcome unrecorded | Corrected in `approved-roadmap.md` RM-2 | Verified Fact |
| AB-8 | Stage 26 reports mutants M5/M9/M10 surviving; Stage 27 reports 13 of 13 killed | Stage 27 is later; I did not re-run the mutation gate | Verified Fact (as reported) |
| AB-9 | '22 release approvals' vs '40 records' | 22 release-scope + 18 cutover-step = 40 (counted from the JSON) | Verified Fact |
| AB-10 | Stage 10 summary calls ADRs PROPOSED; files carry status DRAFT; Stage 42 U-42-01 asked if any is ACCEPTED | None is ACCEPTED (18 of 18 DRAFT) | Verified Fact |
| AB-11 | Stage 42 prompt folder `docs/42-executive/` vs actual `docs/42-executive-defence/` | Actual folder referenced (S42-DEV-01) | Verified Fact |
| AB-12 | Stage prompt names this stage 'FINAL' (run 46 of 46) and `docs/final-prd/`; engagement lead calls it Stage 43 and named `docs/43-final/` | `docs/final-prd/` used per the prompt's folder rule; stage label 'FINAL (run as Stage 43)' | Verified Fact |
| AB-13 | Test counts: 241 planned acceptance tests (Stage 16/17), 396 ok (Stage 16), 419 methods (`run_hub_groups.py --all`, Stage 20), 31 groups (Stage 30) | Different counting bases; no single current total; T-05 not run | Verified Fact; Unknown (HEAD total) |
| AB-14 | Stage 17 PCH-04 labels contract-binding change 'ZH-10'; code and Stage 23 use ZH-10 for rule-row edit / policy withdrawal | Code authoritative; the contract-binding change is a policy event `CONTRACT_BINDING_CHANGED` via the gate (label to be fixed in a spec addendum) | Verified Fact |
| AB-15 | OD-05 'Pending repo creation' vs a tracked `origin/main` | A remote exists; protection state Unknown | Verified Fact / Unknown |
| AB-16 | `implementation-baseline-signoff.md` says acceptance pending; OD-25 records Dinesh's answers accepting the Stage 17 baseline | Treat OD-25 as the acceptance record; file not edited | Verified Fact |

### 7. Operating position summary
See `final-operating-boundaries.md`, `final-ownership-map.md`, `known-limitations.md`, `residual-risk-register.md`. In one sentence: this is a tested but unused, unowned, unreleased shadow build; the next steps are decisions, not engineering.

### 8. Deviations of this stage run
| ID | Deviation | Tag |
|---|---|---|
| S43-DEV-01 | Folder is `docs/final-prd/` (prompt) not `docs/43-final/` (instruction); prompt's folder rule applied | Verified Fact |
| S43-DEV-02 | A 20th artifact `open-items-and-decision-register.md` added at the engagement lead's request | Verified Fact |
| S43-DEV-03 | `approved-roadmap.md` keeps the prompt's file name but its content is NOT approved | Verified Fact |
| S43-DEV-04 | Docs-only: no test, script or hub command was executed; counts come from read-only `ls`/`find`/`wc`/`grep` of the worktree and from cited documents | Verified Fact |
| S43-DEV-05 | Gate computed as BLOCKED (not CONDITIONAL PASS) because the prompt forbids baseline sign-off while a blocking condition remains and sign-off cannot be recorded by an agent | Inference |
| S43-DEV-06 | Work done in worktree `~/fde_sbx/wt-s43` on branch `stage-43-final`; nothing pushed | Verified Fact |

### 9. What Dinesh must decide (summary; full list in the register)
1. Accept, amend or reject this PRD as an as-built-not-released record (sign-off form). 2. Whether the engagement continues toward a pilot or ends as a documented sandbox build. 3. The release question across the 40 records (DV-01..DV-11, CUT-1..CUT-5, G1..G10, OPS-01..13). 4. Zone H holders or 'unused'. 5. Owners / second reviewer / receiver. 6. After-window and KPI baseline. 7. Python floor and 3.12+ run. 8. Data and exposure posture. 9. Route the risk registers. 10. Sign the three walkthroughs. 11. Rule on RTO/RPO (AB-3) and on Stage 39/40-before-38 (HO-18). 12. Install CI or not (HAR-07).

## Evidence References
Companion files in this folder, and the stage documents named in `evidence_sources`. Decision log: `.fde/orchestrator-decisions.md` OD-01..OD-38.

## Assumptions
- A-43-01, A-43-02 (see `requirement-disposition-matrix.md`); A-43-04..A-43-17 in companion files.
- A-43-18 [Assumption] Main 08add05 is the final state of the repository for this PRD; any later commit supersedes it. Confirm: orchestrator.

## Unknowns
- See section 4 and U-43-01..U-43-21.

## Unresolved Issues
- B-1..B-4; the 40 approval records; every row of `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md` R1-R18 (especially R10 misreading evidence, R18 PRD read as acceptance).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
