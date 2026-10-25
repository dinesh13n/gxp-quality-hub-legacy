---
stage: "41 — Retirement / Decommissioning"
artifact: "decommission-checklist.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/41-retirement/{retirement-criteria,dependency-clearance,data-retention-plan,archive-plan,legal-hold-check,access-revocation-plan,secret-key-revocation,vendor-termination-plan}.md", "docs/30-release/{cutover-checklist,release-outcome,rollback-plan}.md", "docs/30-release/evidence/approvals-register.json", "docs/37-operating-model/service-ownership-map.md", ".fde/orchestrator-decisions.md (OD-03a, OD-04, OD-15, OD-32, OD-37)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. EVERY ITEM BELOW IS NOT STARTED. Nothing has been executed. A tick may be placed only by the named owner, with an evidence pointer, after the gate in the "Entry" section is met. An agent may not tick an approval item. Nothing is retired or deleted by this stage; legacy stays authoritative.**

## Summary
A single ordered checklist for decommissioning one asset or one wave. It is generic on purpose: the same sections A-H apply to every wave in `retirement-criteria.md` RC-4; wave-specific rows are marked. Status today: **0 of 58 items done (plus 6 entry conditions, all BLOCKED); 36 of the 58 are owned by a human (Dinesh Naik or a reviewer he names); 16 decisions D-41-01..D-41-16 are only his to make (section I).** The checklist is executable only after Stage 30 v0.2 returns GO for the relevant capability, which requires approvals that do not exist (OD-37). [Verified Fact]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
Legend: Owner = who may tick; "H" = human-only decision; "Ag" = an agent may prepare evidence but not tick; Status values: NOT STARTED / BLOCKED / DONE (none is DONE).

### Entry gate (all must be true before any item in A-H)
| # | Condition | Status | Blocker |
|---|---|---|---|
| E-1 | Stage 30 v0.2 GO for the capability; AP-CUT-n APPROVED; verification window passed | BLOCKED | 0 of 40 approvals (OD-37) |
| E-2 | Retirement approval recorded (AP-RET-nn) by a named human (PR-01) | BLOCKED | none exist |
| E-3 | Dependency clearance CLEARED for the asset (PR-05) | BLOCKED | all NOT CLEARED |
| E-4 | Legal-hold check recorded and current (PR-07) | BLOCKED | not completed |
| E-5 | Retention decision adopted for the asset's records (PR-06) | BLOCKED | hold-all interim only |
| E-6 | Steady-state owner accepted (PR-10) | BLOCKED | 0 of 28 |

### A Archive (see `archive-plan.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| A-01 | Decide archive location, medium, custodian (D-41-09) | H Dinesh | OD entry | NOT STARTED |
| A-02 | HAR-09 approval if any copy leaves the device | H Dinesh | approval ref | NOT STARTED |
| A-03 | Work on a full copy outside the working tree (OD-03a) | Ag | environment note | NOT STARTED |
| A-04 | `verify-audit` rc 0 and manifest `sha256sum -c` rc 0 before archiving (PR-09) | Ag | command output + hash | NOT STARTED |
| A-05 | Build AU-1 legacy code bundle (baseline tag and final commit) | Ag | bundle + tree-hash compare | NOT STARTED |
| A-06 | Build/confirm AU-2 legacy data archive and manifest | Ag | manifest rc 0 | NOT STARTED |
| A-07 | Build AU-3 hub store archive incl. anchor, config, `pre-restore/` if present | Ag | manifest, verify-audit | NOT STARTED |
| A-08 | Build AU-4 repository mirror and PR text export | Ag + H | `git fsck`; `ls-remote` SHAs | NOT STARTED |
| A-09 | Restore test into scratch path for each unit | Ag | restore log | NOT STARTED |
| A-10 | Negative test: corrupted archive is refused | Ag | exit code log | NOT STARTED |
| A-11 | Commit archive evidence under a new `evidence/` with `SHA256SUMS.txt` (no overwrite) | Ag | commit hash | NOT STARTED |
| A-12 | Owner reviews archive index and accepts it | H Dinesh | signed record | NOT STARTED |

### B Access (see `access-revocation-plan.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| B-01 | Freeze writers: stop hub serve and legacy jobs | H Dinesh | audit/stop record | NOT STARTED |
| B-02 | Confirm no listener on 8080, 8090 and the hub port | Ag | host check output | NOT STARTED |
| B-03 | Revoke each service token (AC-02) | H Dinesh | revocation rows; 401 on a copy | NOT STARTED |
| B-04 | End sessions (AC-03) | Ag | session state | NOT STARTED |
| B-05 | Neutralise human principals (AC-01) by method available then | H Dinesh | store archived; disable record if built | NOT STARTED |
| B-06 | Confirm `zone_h.holders` empty or removed with approval_ref (AC-04) | H Dinesh | config | NOT STARTED |
| B-07 | Code-host: archived/read-only; remove collaborators and authorised apps (AC-08, AC-10) | H Dinesh | host export | NOT STARTED |
| B-08 | Cloud workspace data copy removed (AC-09) | H Dinesh | provider record | NOT STARTED |
| B-09 | Device folders disconnected / wiped per policy (AC-11; HAR-03) | H Dinesh | attestation | NOT STARTED |
| B-10 | Keep one custodian read path until A-09 passes | H Dinesh | note | NOT STARTED |

### C Secrets and keys (see `secret-key-revocation.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| C-01 | Owner signs the secret inventory SK-01..SK-14 plus external credentials | H Dinesh | signed list (no values) | NOT STARTED |
| C-02 | Run secret scan over final tree | Ag | scan output + hash | NOT STARTED |
| C-03 | Run secret scan over git history on a clone (SK-14) | Ag | scan output + hash | NOT STARTED |
| C-04 | Seal key decision: stop sealing, escrow or destroy verification role after the window (D-41-13) | H Dinesh | decision record (no key) | NOT STARTED |
| C-05 | Unset scripted-password variables on hosts and in scripts | H Dinesh | attestation | NOT STARTED |
| C-06 | Rotate/remove code-host keys and tokens used for the repo | H Dinesh | host export | NOT STARTED |
| C-07 | Revoke workspace and assistant credentials | H Dinesh | provider record | NOT STARTED |
| C-08 | Confirm no secret value in docs, logs, audit rows | Ag | grep output | NOT STARTED |

### D Vendors (see `vendor-termination-plan.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| D-01 | Owner supplies contract/terms or records "none; not applicable" per V-03/04/05 (D-41-14) | H Dinesh | record | NOT STARTED |
| D-02 | Decide VA-02..VA-04 (second mirror, terms) | H Dinesh | OD entry | NOT STARTED |
| D-03 | Second custodian named or accepted-as-is (D-41-12) | H Dinesh | OD entry | NOT STARTED |
| D-04 | Terminate V-05 workspace copy/account | H Dinesh | deletion record or "not available" | NOT STARTED |
| D-05 | End V-04 assistant access | H Dinesh | provider record | NOT STARTED |
| D-06 | V-03: set repository archived/read-only; closure only by separate decision | H Dinesh | host state | NOT STARTED |
| D-07 | V-10: device decommission after archive verified | H Dinesh | attestation | NOT STARTED |
| D-08 | File each provider's deletion record or write "not available" honestly | H Dinesh | evidence file | NOT STARTED |

### E Dependency clearance (see `dependency-clearance.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| E-01 | Re-run DC-3 commands 1-6 on a full copy | Ag | outputs + hashes | NOT STARTED |
| E-02 | Replace legacy reference sources by archived hash-pinned copies for `hub/policy/asfound.py` pins (D-41-04) | H Dinesh + build stage | merged PR with approval_ref | NOT STARTED |
| E-03 | Approved change to TST-CO-05 and gate G1 for the retired paths (D-41-05) | H Dinesh + build stage | merged PR | NOT STARTED |
| E-04 | Update characterization harness policy: frozen goldens only | H Dinesh + build stage | merged PR | NOT STARTED |
| E-05 | Consumers re-pointed or confirmed none (PR-04) | H Dinesh / business | signed list | NOT STARTED |
| E-06 | Orchestrator full hub regression green after the change | Orchestrator | regression log | NOT STARTED |
| E-07 | Import fan-in zero for the retiring module (DF-07) | Ag | AST scan | NOT STARTED |

### F Legal hold and retention (see `legal-hold-check.md`, `data-retention-plan.md`)
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| F-01 | Name legal/QA reviewer or record "synthetic only" (D-41-10) | H Dinesh | OD entry | NOT STARTED |
| F-02 | Reviewer answers Q1-Q8; result dated and signed | H reviewer | signed record | NOT STARTED |
| F-03 | Repeat the check immediately before RL-2/RL-3 | H reviewer | dated record | NOT STARTED |
| F-04 | Retention decision per class (D-41-06) | H Dinesh | OD entry | NOT STARTED |
| F-05 | Any asset under hold moved to PROTECTED | H Dinesh | register | NOT STARTED |

### G Stop and verify
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| G-01 | Level move recorded (RL-1/RL-2) in the approvals register with evidence_ref | H Dinesh | register entry | NOT STARTED |
| G-02 | Post-move verification: hub regression, golden-compare for retained capabilities, `verify-audit` | Ag / Orchestrator | logs | NOT STARTED |
| G-03 | Rollback window observed; any L3 rollback resets the clock | H Dinesh | window record | NOT STARTED |
| G-04 | RL-3 (deletion) requested only after F-04, F-03, A-12 and HAR-03; separate approval | H Dinesh | approval | NOT STARTED |

### H Closure
| Step | Action | Owner | Evidence | Status |
|---|---|---|---|---|
| H-01 | Update `retirement-evidence.md` with executed steps and hashes | Ag | commit | NOT STARTED |
| H-02 | Publish errata, never overwrite earlier evidence (CC-06/07) | Ag | commit | NOT STARTED |
| H-03 | Update docs that describe retired assets (DF-12) | Ag | PR | NOT STARTED |
| H-04 | Hand final report to Stage 42 with retirement status | Ag | document | NOT STARTED |

### I Decisions only Dinesh Naik can make (all OPEN)
Agent-recommended defaults are scope choices under OD-32 and are not decisions or risk acceptances.

| ID | Decision | Recommended default | Used by |
|---|---|---|---|
| D-41-01 | Scope of "retirement": legacy capabilities only, or also the engagement toolchain and the hub at engagement end | both are planned; legacy first; execution only per wave | all |
| D-41-02 | Is any real cutover / legacy retirement intended at all (U-30-12) | undecided; plan stays shelf-ready | all |
| D-41-03 | Rollback window length and any read-only period after retirement | no number proposed | PR-11, G-03 |
| D-41-04 | Archived, hash-pinned reference copies of legacy sources for `asfound.py` pins | yes, before any legacy removal | E-02 |
| D-41-05 | Approved change to TST-CO-05 and G1 when legacy paths retire | yes, as a frozen-test change under HAR | E-03 |
| D-41-06 | Retention: hold-all vs named periods | hold-all | F-04 |
| D-41-07 | Ever build a hub purge capability | no | G-04 |
| D-41-08 | Session/login-attempt rows and privacy regime | archive with the store; decide with regime | A-07 |
| D-41-09 | Archive location, medium, custodian, encryption | not decided | A-01 |
| D-41-10 | Legal/QA reviewer or "synthetic only" | name one before any RL-2 | F-01 |
| D-41-11 | Build an audited disable-principal operation before any real user | yes, as a spec addendum | B-05 |
| D-41-12 | Second custodian for archives and accounts | yes | D-03 |
| D-41-13 | Anchor seal key custody and end of life | keep verification role through the window | C-04 |
| D-41-14 | Supply vendor terms or mark not applicable | supply or mark | D-01 |
| D-41-15 | Owners for the nightly file exchange (PA-25) and CO-WF-01 (PA-26, OPD-15) | protected; not retired | RA-12, RA-13 |
| D-41-16 | Adopt the AP-RET approval family in the register | yes | E-2 |

### Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DCF-01 | [Verified Fact] 0 of 58 checklist items are done and 6 of 6 entry conditions are BLOCKED | this file; OD-37 | Nothing can be executed | none by design | High | D-41-02 |
| DCF-02 | [Inference] 36 of the 58 items are owned by a human (decision or attestation); agents can prepare evidence for the rest | owner column | Throughput is bounded by one person | Medium | High | D-41-12 |

## Evidence References
See `evidence_sources`; companion artifacts as named in each section.

## Assumptions
- A-41-CL-1 [Assumption] The checklist applies per wave; some rows (A-08, D-xx) occur once at engagement end. Confirm: Engagement lead (Dinesh Naik).
- A-41-CL-2 [Assumption] Item counts are as written in this version; adding rows is a new version.

## Unknowns
- U-41-CL-1 Real step durations and effort (not estimated; Stage 32 has no cost lines).

## Unresolved Issues
- UI-41-CL-1 D-41-01..D-41-16.

## Residual Risks
- RR-41-CL-1 A checklist that is followed mechanically after the world has changed (Medium); mitigated by the entry gate and by F-03.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
