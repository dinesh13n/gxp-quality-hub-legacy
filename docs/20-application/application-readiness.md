---
stage: "20 — Application & Services Engineering"
artifact: "application-readiness.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/20-application/*.md", "docs/20-application/evidence/*", "docs/18-delivery/{increment-plan,delivery-backlog,definition-of-done,evidence-checklist}.md", "tests/hub/non_add_edits.json", ".fde/orchestrator-decisions.md OD-01..OD-26", "git log stage-20-application (from main 41098c0)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. "Ready" here means "ready for the orchestrator's full regression and PR review", not approved, released or cut over. No deviation is approved; zone_h.holders stays EMPTY; nothing ships adopted, active, scheduled, exposed or authoritative.**

## Summary
All eight Stage 20 work items of the Stage 18 plan (DW-02..DW-09; increments DI-02, DI-03, DI-04) are implemented with tests on branch `stage-20-application`; the nine required artifacts and the CLI addendum exist. Every test the build agent ran is green; both mutation gates are KILLED; the characterisation harness is 134/134 with unchanged digests; backup checksums rc 0 before and after every run. **Stage 20 gate: CONDITIONAL PASS** - no blocking gap; open, non-blocking items carry owners below.

## Findings
### RD-1 Work items
| DW | Acceptance (Stage 18) | Status | Evidence | Tag |
|---|---|---|---|---|
| DW-02 | TST-CO-03 runs; executed = discovered | DONE in code; full-regression log pending (orchestrator) | manifest selects 419/419 once, TST-CO-03 in I45 (STG20 S01); `run_hub_groups.py` checks executed = expected per group | [Verified Fact] |
| DW-03 | every group < 120 s; count unchanged | PARTIAL: group C split in 3 (C1 82.6 s, C2 106.4 s, C3 77.2 s latest; C2 153.8 s once); I8 split into I8a / I8b + E8 | `evidence/regression-groups-laptop.json` | [Verified Fact] |
| DW-04 | 0 `declared:`; D5 = 0; values = Stage 16 observation | DONE | golden-compare observed: 13 probes, 0 declared, D5 0; STG20 S04; G1S20 KILLED | [Verified Fact] |
| DW-05 | DV-01..DV-11 proposed, approval_ref empty | DONE | `evidence/register-dump.json`; STG20 S07/S08 | [Verified Fact] |
| DW-06 | one Zone H check; 0 domain->web; cycles reported; H1 KILLED; behaviour unchanged | DONE (cycles 6->4 / 10->6, not 0) | static checks; H1S20 KILLED; TST-GATE/SEC/POL green | [Verified Fact] |
| DW-07 | FAC-13 (proposed) green; refusal with holders [] | DONE (FAC-13 still proposed) | STG20 S11-S13 | [Verified Fact] |
| DW-08 | AC-REV-05..08, AC-GATE-18..20 without manual record-trace | DONE | STG20 S14/S15 | [Verified Fact] |
| DW-09 | all runners conform to the DQ-05 option | DONE (addendum option) | `spec-addendum-cli-error-shape.md`; STG20 S10 | [Verified Fact] |

### RD-2 Deviations (edits of frozen earlier-increment files; each listed in `tests/hub/non_add_edits.json`)
| ID | Files | Work item | Reason | Tag |
|---|---|---|---|---|
| S20-DEV-01 | hub/cli.py, hub/golden/run.py | DW-04 | observed provider, new options / command; golden-compare default now NOT-RUN for module probes (was: declared values) | [Verified Fact] |
| S20-DEV-02 | hub/coexistence/register.py | DW-05 | seed v2 + guarded refresh of unchanged INC-02 rows | [Verified Fact] |
| S20-DEV-03 | tests/hub/_driver.py, test_tst_co_12_egress_tripwire.py | DW-03 | `--shard`; TST-CO-12 e -> e1/e2/e3 | [Verified Fact] |
| S20-DEV-04 | test_tst_co_01, test_tst_co_02, test_inc02_supplementary, test_inc03_supplementary | DW-04/05 | expectations follow the observed probes and 11 register rows (counts 9->11, 10->3) | [Verified Fact] |
| S20-DEV-05 | test_tst_co_05_legacy_paths_unchanged.py | DW-02..09 | the add-only check (c) now accepts ONLY listed, work-item-bound modifications of hub / tests/hub files; deletions / renames / legacy paths still fail | [Verified Fact] |
| S20-DEV-06 | hub/policy/service.py, clocks.py, decision/service.py, r2/consistency.py, metrics/service.py, gate/actions.py | DW-07 | withdrawal must take effect in every consumer of adopted policies | [Verified Fact] |
| S20-DEV-07 | hub/web/cli.py | DW-08 | produce-traces command | [Verified Fact] |
| S20-DEV-08 | hub/gate/service.py, policy/gate.py, security/authz.py, gate/dispositions.py, review/service.py, search/schema.py, web/errors.py, web/schema.py, metrics/cli.py, policy/cli.py, security/auth.py, web/server.py, web/ui.py | DW-06 | one holder rule, layer fix, pyflakes | [Verified Fact] |

### RD-3 Common increment gate (IN-5)
CG-1 sandbox-only: yes. CG-2 CT-01..CT-16 green on 3.10.12: yes (134/134). CG-4 legacy unchanged: yes. CG-5 checksum rc 0 before/after: yes, every run. CG-7 No-AI: yes. CG-8 increment tests pass: yes (agent scope). CG-9 D5 = 0: yes. CG-10 rollback: L1 = revert the squash commit (no migration, no data change); stores touched by the register refresh keep valid proposed rows (refresh is text-only on unapproved rows). CG-11 clean status, no DB / lake committed: yes (only the other agent's untracked docs/22-* exists). [Verified Fact]

### RD-4 Gate evaluation (stage prompt Completion Gate)
| Condition | Met? | Tag |
|---|---|---|
| implementation conforms to specs | yes for the specified parts; new CLI surfaces / ZH-10 op / FAC-13 await Stage 12 v0.2 (DW-13) | [Inference] |
| deterministic-AI boundary enforced in code | yes | [Verified Fact] |
| tests pass | yes for every run in scope; full regression pending (orchestrator, OD-23) | [Verified Fact] |
| all required artifacts exist | yes (9 + addendum) | [Verified Fact] |
| critical gaps resolved or documented | yes (RD-5) | [Verified Fact] |
| evidence supports the conclusion | yes | [Verified Fact] |
**Outcome: CONDITIONAL PASS.**

### RD-5 Open items (non-blocking)
| Item | Owner | Due (stage-relative) | Risk |
|---|---|---|---|
| Full hub regression with `run_hub_groups.py --all` (replaces `full_regression.sh`), incl. TST-CO-03 3/3 and 419 = 419 | Orchestrator | before merge | Medium |
| Accept S20-DEV-01..08, in particular DEV-05 (allow-listed edits) and DEV-01 (default NOT-RUN) | Engagement lead (Dinesh Naik) | PR review | Medium |
| Stage 12 v0.2 entries: golden-observe, --observe/--observed, produce-traces, ZH-10 withdraw_policy, FAC-13, CLI addendum | Engagement lead (Dinesh Naik) / Stage 23 agent | Stage 23 (DW-13) | Low |
| Remaining cycles (4 + 6) and 10 McCabe > 15 | Orchestrator | Stage 27 | Low |
| Sandbox build time dominates group wall time (DW-03 target) | Orchestrator | Stage 27 (DW-31) | Low |
| DV-01 / DV-08 still reference queries, not built modules (S20-D02) | Build agent | Stage 30 (DW-34/35) | Low |
| Reset `tests/hub/non_add_edits.json` for the next BUILD stage | next BUILD stage agent | Stage 21/23 | Low |

## Evidence References
All files in `docs/20-application/` and `docs/20-application/evidence/`.

## Assumptions
- A-20-RD-1 [Assumption] One branch for DI-02..DI-04 (OD-26) instead of three (IN-2 sketch) is acceptable; confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-20-RD-1 Full-regression outcome on the cloud workspace (Python 3.13) - pending.

## Unresolved Issues
- As RD-5.

## Residual Risks
- RR-RD-1 23 frozen hub files edited in one PR: higher review load; mitigated by the allow-list, targeted runs and mutation gates (Medium).
- RR-RD-2 Git in the connected folder cannot delete its lock files in this session (deletion not permitted); stale locks were moved to `.git/stale-locks/` after each commit (Low, housekeeping).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
