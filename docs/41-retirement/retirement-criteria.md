---
stage: "41 — Retirement / Decommissioning"
artifact: "retirement-criteria.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-03a, OD-04, OD-08, OD-09, OD-15, OD-30, OD-32, OD-33..OD-37)", "docs/14-transformation/{cutover-plan,coexistence-strategy,rollback-strategy}.md", "docs/30-release/{release-outcome,cutover-checklist,rollback-plan}.md", "docs/30-release/evidence/approvals-register.json", "docs/37-operating-model/{service-ownership-map,data-ownership}.md", "docs/25-governance/{evidence-retention-policy,compliance-obligations}.md", "docs/33-vendor-risk/{vendor-inventory,exit-plan}.md", "docs/07-repo-assessment/{dependency-map,critical-workflow-inventory}.md", "tests/hub/test_tst_co_05_legacy_paths_unchanged.py", "hub/policy/asfound.py", "hub/golden/run.py", "tests/characterization/harness.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. This is a retirement PLAN with preconditions. Nothing is retired, frozen, archived, revoked, terminated or deleted by this stage, and nothing here is an approval. Legacy stays authoritative (Stage 30 gate BLOCKED, no cutover, 0 of 40 approvals: OD-37). The only human is Dinesh Naik, Engagement lead (OD-04). No retention period, legal conclusion, regulatory conclusion, stakeholder or approval is invented. Retention, archive and legal-hold decisions are owned by Dinesh Naik with qualified QA / legal review and are OPEN.**

## Summary
Defines **when** an asset may be retired, **in what stages**, and **what may never be retired**. Four things drive the result:

1. **Nothing is eligible today.** Retirement of any legacy capability presupposes that the hub is authoritative for it (CUT-1..CUT-5, `docs/14-transformation/cutover-plan.md`). No cutover has happened, zero approvals are recorded and the release gate is BLOCKED (`docs/30-release/release-outcome.md`, OD-37). [Verified Fact]
2. **Retirement is a ladder, not a switch.** Four levels (RL-0..RL-3 below). Level 3 (deletion) is not proposed for any asset in this document; it needs an adopted retention policy, a completed legal-hold check, an archive and a named approver, none of which exist. [Inference]
3. **A protected list exists.** Eight classes of asset (NR-1..NR-8) must never be retired by this plan, including the baseline data, the audit chain and anchor, the engagement evidence and the protected parallel workflow CO-WF-01.
4. **The AI categories in the prompt scope are empty.** The product is No-AI (OD-08): there are no models, prompts, agents or model-serving APIs to retire; PA-28 is N/A (`docs/37-operating-model/service-ownership-map.md`). The only derived index is the hub's own keyword search index, which is derived from retained records. [Verified Fact]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RC-1 Retirement levels
| Level | Name | Meaning | Reversible? | Earliest permitted | Tag |
|---|---|---|---|---|---|
| RL-0 | Live | Asset runs and is authoritative or a required comparator (today for every legacy asset) | n/a | n/a | [Verified Fact] |
| RL-1 | Frozen read-only | Asset stays runnable, is no longer authoritative for its capability, accepts no new business writes, is kept as comparator and fallback (this is what `coexistence-strategy.md` CR-1/CR-2 already do for legacy) | Yes (flip authority back: L3 rollback) | After the capability's CUT step is APPROVED, executed and accepted | [Inference] |
| RL-2 | Stopped and archived | Asset no longer scheduled or started, access revoked, a verified archive exists (see `archive-plan.md`), source stays in git history | Yes, by restoring from archive (restore test required) | After all RC-2 criteria below | [Inference] |
| RL-3 | Deleted | Working copy or data removed from the live location or media | **No** for data outside git; code remains recoverable from git history only | Never proposed in this stage; requires adopted retention policy + legal-hold completed + owner approval | [Inference] |

### RC-2 Universal preconditions (every asset, every move to RL-1 or higher, all must be true and evidenced)
| ID | Criterion | Evidence required | Status today | Tag |
|---|---|---|---|---|
| PR-01 | Owner approval for this move recorded as an APPROVED entry with named approver, reference, date, evidence pointer, in the same form as `docs/30-release/evidence/approvals-register.json` (proposed id family AP-RET-nn; not added to the register by this stage) | register entry | 0 exist | [Verified Fact] (0 approvals); the AP-RET family is a [Assumption] proposal |
| PR-02 | The hub is authoritative for the capability: the matching AP-CUT-n is APPROVED, the cutover was executed, and the CO-2 step 5 verification window passed with zero UNEXPLAINED differences | Stage 30 v0.2 GO; daily golden-compare reports | not met: gate BLOCKED | [Verified Fact] |
| PR-03 | Every DV row that touches the capability is decided (preserve or fix) and approved | DV register `status=approved` with `approval_ref` | DV-01..DV-11 all proposed | [Verified Fact] |
| PR-04 | Consumers of the legacy output are identified and re-pointed (or confirmed none) | consumer list signed by the data/service owner | consumers outside the repo Unknown (U-14-01, OD-28 b) | [Unknown] |
| PR-05 | Dependency clearance entry for the asset reads CLEARED (see `dependency-clearance.md`) | clearance record with commands/greps re-run at retirement time | all NOT CLEARED | [Verified Fact] |
| PR-06 | Retention class decision adopted for the asset's records (OD-S12-09), period named by the decision-maker | decision record | hold-all interim only (OD-15, OD-30) | [Verified Fact] |
| PR-07 | Legal-hold check completed and recorded by an accountable human (see `legal-hold-check.md`) | signed check | not completed: no hold register, no QA/legal owner | [Unknown] |
| PR-08 | Archive created, hash-listed and restore-tested (`archive-plan.md` AP-1..AP-8) | manifest + restore log | none | [Verified Fact] (absence) |
| PR-09 | Audit evidence preserved: `verify-audit` rc 0 on the hub store, anchor file retained with the chain, backup manifest `sha256sum -c` rc 0 | command output stored under a stage `evidence/` folder | rehearsed on sandbox copies only (Stage 30 BV-1..BV-7) | [Verified Fact] |
| PR-10 | A steady-state owner has accepted the asset's retirement consequences (Stage 37) | accepted owner record | 0 of 28 assets have an accepted steady-state owner (OD-34) | [Verified Fact] |
| PR-11 | The rollback window for the move has elapsed with no L3 rollback and no unexplained difference; the length of the window is set by Dinesh | decision record naming the window | window length Unknown | [Unknown] |
| PR-12 | Access and secrets plan for the asset approved and rehearsed on a copy (`access-revocation-plan.md`, `secret-key-revocation.md`) | rehearsal log | none | [Verified Fact] (absence) |
| PR-13 | Tests and gates that name the asset are changed by a recorded, approved change first (TST-CO-05, golden-compare G1, characterization harness: see `dependency-clearance.md` DF-03..DF-05) | merged PR with approval_ref | none | [Verified Fact] |
| PR-14 | The No-AI invariant is unaffected (OD-08): retirement adds no model, vendor or egress | TST-CO-11/12 green in the orchestrator regression | green at last merge (OD-37) | [Verified Fact] |

### RC-3 Protected assets (never retired by this plan)
| ID | Asset | Why protected | Source | Tag |
|---|---|---|---|---|
| NR-1 | Baseline data `data/legacy.sqlite3` (125 cases, seed 4100, sha256 c254649f…d70aa) and the other as-found `data/` files; the backup `../_data-backup-2026-10-17/` with `SHA256SUMS.txt` | golden source (HAR-01); hold-all; checksum-gated every run (OD-03a) | OD-02, OD-09, OD-15, `coexistence-strategy.md` CS-2 ("always") | [Verified Fact] |
| NR-2 | Hub retained tables, audit chain and its anchor file | tamper-evident decision and evidence record; insert-only triggers; no purge path exists | `evidence-retention-policy.md` RC-1..RC-3; `hub/security/audit.py` | [Verified Fact] |
| NR-3 | Engagement evidence: `docs/00..40`, `docs/*/evidence/` with `SHA256SUMS.txt`, `.fde/orchestrator-decisions.md`, tag `baseline-as-found` (a6eb4e8) | before/after comparison, errata-not-overwrite (CC-06/07, HAR-13) | `evidence-retention-policy.md` RC-4, RC-5 | [Verified Fact] |
| NR-4 | Protected parallel workflow CO-WF-01 (older-customer workflow) | read-only to the hub, owner unknown, "may it ever be retired" is OPEN (OPD-15) | BEH-CO-05, CR-7, `open-product-decisions.md` OPD-15 | [Verified Fact] |
| NR-5 | Anything under legal hold or a regulatory retention duty, once identified | none identified; unknown, therefore protected by default | `legal-hold-check.md` | [Unknown] |
| NR-6 | Git history of the repository (no history rewrite or force-push) | CC-01; every code retirement relies on history for recoverability | `evidence-retention-policy.md` RC-4 | [Verified Fact] |
| NR-7 | Deviation, approval, risk and vendor-acceptance registers (DV, RA/RP/RS, VA) | decision records | `service-ownership-map.md` PA-24 | [Verified Fact] |
| NR-8 | The as-found rule-set sources and goldens used to prove parity, until a superseding reference is approved | `hub/policy/asfound.py` reads them at pinned hashes; goldens in `docs/07-repo-assessment/evidence/golden/` | `dependency-clearance.md` DF-01 | [Verified Fact] |

### RC-4 Candidate order (conditional, not scheduled)
Order follows cutover order CUT-2, CUT-1, CUT-3, CUT-4, CUT-5 (`cutover-plan.md`) and reverses internal import fan-in so nothing is retired while something in the legacy tree still imports it (`dependency-map.md`: `app.store` fan-in 11, `app.legacy_logic` fan-in 2).

| Wave | Content | Pre-condition beyond RC-2 | Highest level proposed in this plan | Tag |
|---|---|---|---|---|
| W0 | Nothing. Current state. | n/a | RL-0 | [Verified Fact] |
| W1 | Disposable toolchain copies: sandbox copies (RA-17), cloud-workspace data copy (RA-18) | engagement-close or provider-change decision; evidence already in git (RC-6 excerpt-plus-hash practice) | RL-2 (copies are derived; deleting a derived copy is not deleting a record, but see RA-18 note) | [Inference] |
| W2 | Legacy rule evaluation (CUT-2): `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json` | CUT-2 executed and accepted; DV-05/06 decided; HAR-06; legacy API and baseline no longer import `legacy_logic` | RL-1 (RL-2 only after all PR-xx) | [Inference] |
| W3 | Legacy intake and reconcile (CUT-3): `app/gateway_bridge.py`, `app/partner_feeds.py` reconcile, `app/historical_estate.py`, `services/source_gateway/` | CUT-3 executed; DV-02/03/07/09; consumer identified; the in-place-overwrite reconcile stopped by an operational decision | RL-1 | [Inference] |
| W4 | Legacy reporting (CUT-4): `app/baseline.py`, `app/operational_report.py`, `legacy_java/`, `sql/legacy_reports.sql`, `legacy_batch/` | CUT-4 executed; DV-01/04/08; finance-facing consumers identified | RL-1 | [Inference] |
| W5 | Legacy API shell and provisioning: `app/server.py`, `app/store.py`, generators, `run.sh`, Docker, legacy CI, 7 legacy test files | W2..W4 complete and no module imports them; regeneration (CW-12) still needed for the baseline? decision | RL-1 | [Inference] |
| W6 | Engagement-end items: AI coding assistant access, orchestrator cloud workspace account, off-device copies, GitHub remote | handover (Stage 38) outcome; VA-02..VA-04 decisions; archive complete | RL-2 for access; the repository itself is NOT deleted | [Inference] |

No wave has a date: dates would be invented. Each wave starts only on Dinesh's recorded decision.

### RC-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CF-41-01 | [Verified Fact] No asset is eligible for any retirement level above RL-0 today | `release-outcome.md` RO-1; `approvals-register.json` (0 APPROVED); OD-37 | The stage can plan but not execute | none (by design) | High | none |
| CF-41-02 | [Verified Fact] Legacy is the fallback for every hub rollback (L3 re-points consumers to legacy) | `rollback-plan.md` L3; A-14-11 | Retiring legacy before the hub is accepted removes the rollback | High | High | Length of the post-cutover window (PR-11) |
| CF-41-03 | [Inference] The hub is not independent of the legacy tree: its as-found rule sets, golden comparison and characterization all read or run legacy files | `hub/policy/asfound.py`, `hub/golden/run.py`, `tests/characterization/harness.py` | A legacy file cannot simply be deleted from `main` | High | High | Which legacy files become archived references (D-41-04) |
| CF-41-04 | [Verified Fact] TST-CO-05 fails by design if any legacy path differs from the `baseline-as-found` tag | `tests/hub/test_tst_co_05_legacy_paths_unchanged.py` | Retirement needs an approved test change before any removal | Medium | High | Approval path (HAR) |
| CF-41-05 | [Verified Fact] No retention period, retention authority, legal-hold register, QA or legal owner, contract or SOW exists | `evidence-retention-policy.md` RF-01; `compliance-obligations.md` OB-05, OB-14; `data-ownership.md` DAF-01 | PR-06 and PR-07 cannot be met by agent work | High (for real data) | High | Dinesh with qualified QA/legal |
| CF-41-06 | [Verified Fact] The AI retirement categories (models, prompts, agents, model APIs) are empty | OD-08; PA-28 N/A | Nothing to retire; recorded to prove it was checked | Low | High | none |
| CF-41-07 | [Inference] "Retirement" of the whole engagement (rather than of legacy capabilities) may be what Dinesh means by Stage 41 at the end of the programme; the plan covers both (W1..W5 legacy; W6 engagement) | stage position 44 of 46 | Scope choice | Low | Medium | D-41-01 |

## Evidence References
See `evidence_sources`. Cross-checks: `dependency-clearance.md`, `data-retention-plan.md`, `archive-plan.md`, `legal-hold-check.md`, `decommission-checklist.md`.

## Assumptions
- A-41-01 [Assumption] The four-level ladder RL-0..RL-3 is an acceptable vocabulary; it is a modelling choice, not found in the repo. Confirm: Engagement lead (Dinesh Naik).
- A-41-02 [Assumption] A new approval family AP-RET-nn in the same register format is the right record for retirement approvals. Confirm: Engagement lead (Dinesh Naik). Not added to the register in this stage (docs only).
- A-41-03 [Assumption] Wave order W2..W5 mirrors CUT order and import fan-in; it is a proposal.
- A-41-04 [Assumption] "Retired" never means "deleted" in this plan unless RL-3 is separately approved.

## Unknowns
- U-41-01 Whether Dinesh intends any real cutover (U-30-12); if not, W2..W5 never occur.
- U-41-02 Length of the rollback window (PR-11) and of any post-retirement read-only period.
- U-41-03 Whether any hosting, DNS, certificate or secrets store exists outside the repo (U-37-SO-2).

## Unresolved Issues
- UI-41-01 All PR-xx criteria are unmet. Owner: Engagement lead (Dinesh Naik).
- UI-41-02 Decisions D-41-01..D-41-12 (listed in `decommission-checklist.md`).

## Residual Risks
- RR-41-01 Retiring on a shorter evidence trail than PR-01..PR-14 would remove the fallback and the comparator at once (High).
- RR-41-02 A criterion list written by the agent may omit a duty only a QA/legal reviewer knows (Medium). Not accepted.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
