---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "operating-contract-updates.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/02-stakeholders/decision-rights-map.md DR-08", "docs/23-human-control/autonomy-catalogue.json", "tests/hub/non_add_edits.json", ".fde/orchestrator-decisions.md OD-25, OD-27, OD-29", "docs/17-implementation-prd/implementation-prd.md IP-5", "docs/23-human-control/stage12-v0.2/README.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Stage 0B originals are **not edited** (HAR-13). This document records, beside them, what Stage 23 found when HAR-01..HAR-16 and the Zone H list ZH-01..ZH-10 were reconciled with the built hub, the changes Stage 23 made to existing files (OD-27), the deviations, and the updates it **proposes**. Nothing is loosened: no HAR is relaxed, no holder or approver is added, no authority is expanded. The HAR set stays PROVISIONAL (DR-08) until Dinesh Naik confirms it.

## Findings
### U-1 HAR-01..HAR-16 reconciled with the code (classification machine-checked by STG23 S40)
| HAR | Trigger | Class | Code | Tests | Note |
|---|---|---|---|---|---|
| HAR-01 | write, restore or regenerate working-tree data/ | partial | `hub/guards/sandbox.py`; `hub/guards/sandbox.py` | co_06_sandbox_guard TST_CO_06 | the hub refuses a data directory inside the worktree or a protected root; restore of data/ itself is a human act (sha256 manifest) |
| HAR-02 | choose or override the authoritative baseline dataset | process-only | - | - | no code path chooses a baseline; recorded in the OD log |
| HAR-03 | delete any file in the repo or backup | process-only | - | - | tests scan hub/ for deletion of the data tree (scan G6) but deleting files in the repo is a tool permission, not a hub control |
| HAR-04 | merge a BUILD branch into main | process-only | - | - | git workflow; no hub code |
| HAR-05 | run a service bound beyond 127.0.0.1 | code-enforced | `hub/web/server.py`; `hub/security/exposure.py` | hub_stg23_controls S03; hub_stg23_controls S04; hub_stg23_controls S05 | Stage 23 DW-15: a non-loopback bind is refused even with exposure approval and TLS keys; Docker/Compose is not shipped |
| HAR-06 | change approval/priority thresholds or decision logic | partial | `hub/gate/actions.py`; `hub/control/flags.py` | hub_stg23_controls S10; hub_stg23_catalogue S41 | hub policy changes need ZH-05/06/10 and a holder; decision flags need approval_ref. Editing the legacy source is process (legacy tree is byte-identical, checked by the characterization harness) |
| HAR-07 | change CI, Dockerfile, Compose, env profiles, pyproject | process-only | - | - | no hub code; Stage 23 changed none |
| HAR-08 | install dependencies / third-party packages | code-enforced | `hub/guards/no_ai.py` | co_11_no_ai_denylist TST_CO_11 | deny-list covers AI/ML/network clients; a general new dependency is caught only by review (heuristic) |
| HAR-09 | send data outside the device | code-enforced | `hub/guards/egress.py` | hub_stg21_egress_guard S; hub_stg23_egress_guard E23 | egress guard refuses non-loopback connects in tests; git remotes are process |
| HAR-10 | introduce any AI/LLM call or automated action into the product | code-enforced | `hub/guards/no_ai.py`; `hub/obs` | co_12_egress_tripwire TST_CO_12 | structural (deny-list, tripwire = 0); an automated action that is not AI is held back by Zone H and by the decision-flag approval rule |
| HAR-11 | record a decision, owner, KPI target or stakeholder statement as approved/final | partial | `hub/control/flags.py` | hub_stg23_controls S10 | the hub refuses a non-default decision flag without approval_ref; it cannot verify the reference is a real approval (Unknown). Recording OD entries is process |
| HAR-12 | make, simulate or automate batch disposition / QA release / e-signature | code-enforced | `hub/gate/actions.py`; `hub/gate/service.py` | gate_01_22_disposition_gate TST_GATE_09; gate_01_22_disposition_gate TST_GATE_11; gate_01_22_disposition_gate TST_GATE_12; hub_stg23_catalogue S41 | ZH-01..03 only by a human holder; shipped holders list is EMPTY so every action is refused |
| HAR-13 | modify prior-stage artifacts or .fde/ control files | partial | `tests/hub/non_add_edits.json` | co_05_legacy_paths_unchanged TST_CO_05 | the non-add edit register makes every change to an existing hub file visible and tested; .fde/ edits are process |
| HAR-14 | proceed past a BLOCKED gate or waive a stop condition | process-only | - | - | orchestrator and Dinesh; no hub code |
| HAR-15 | access E3/E4 environments or real external systems | process-only | - | - | none exist; the egress guard (HAR-09) keeps tests on loopback |
| HAR-16 | execute code in the working tree (E0) | partial | `hub/guards/sandbox.py` | co_06_sandbox_guard TST_CO_06 | the hub refuses to run mutating commands from the working tree; running tests there is process (this stage ran every test in sandbox copies) |

Counts: code-enforced 5 (HAR-05, 08, 09, 10, 12), partial 5 (HAR-01, 06, 11, 13, 16), process-only 6 (HAR-02, 03, 04, 07, 14, 15). [Verified Fact]

### U-2 ZH-01..ZH-10 reconciled
[Verified Fact] 10 of 10 Zone H actions are in `hub/` and equal the keys of `ZONE_H_ACTIONS`; each has an entry with code and tests in `autonomy-catalogue.json`; the shipped holder list is empty. This matches HAR-12, STOP-07 and the Stage 8 Zone H list (disposition, QA release, e-signature, closure exception, authoritative definition / rule, exception-rule acceptance).

### U-3 Proposed updates (for Dinesh Naik; not applied)
| ID | Proposal | Why | Loosens a control? |
|---|---|---|---|
| UP-1 | Add **HAR-17**: setting any decision flag or `capability_authority` away from its default needs a recorded approval, referenced by `approval_ref` | the hub now refuses without a reference; 0B has no matching human rule (closest: HAR-06, HAR-11) | no (adds) |
| UP-2 | Decide whether the authority switch is also a Zone H action (ZH-11) | FF-2 intent; needs a holder | no (adds) |
| UP-3 | Confirm HAR-01..HAR-16 as the engagement's approval list (remove PROVISIONAL) | DR-08 asks Stage 23 / 25 to confirm | no |
| UP-4 | Record the Stage 12 v0.2 addendum (IC-1..IC-8) and the two exit-code clash decisions in the contract | OD-25, OD-29 | no |
| UP-5 | Name the real Zone H holder(s) when they exist; until then `zone_h.holders` stays empty | HAR-12; U-23-01 | no |

### U-4 Edits to existing files (OD-27; `tests/hub/non_add_edits.json` reset for Stage 23)
| File | Work item | Deviation | Edit |
|---|---|---|---|
| `hub/config.py` | DW-17 | S23-DEV-01 | the authority validation loop is replaced by `hub.control.flags.check` |
| `hub/admin/cli.py` | DW-17 | S23-DEV-01 | `_Run.config_loaded` records a `capability_authority` change made in the config file |
| `hub/web/app.py` | DW-17 | S23-DEV-01 | `WebApp.start` records the same at serve start |
| `tests/hub/_inc03.py` | DW-17 | S23-DEV-02 | `write_config` adds a synthetic `approval_refs` entry for each non-default flag a test sets |
| `tests/hub/test_tst_sec_21_config_loaded.py` | DW-17 | S23-DEV-02 | the hand-written holder config carries the same synthetic marker; assertions unchanged |
| `tests/hub/regression_groups.json` | DW-13..18 | S23-DEV-01 | groups S23 and E23 added |
| `tests/hub/non_add_edits.json` | OD-27 reset | S23-DEV-01 | reset for Stage 23 |

### U-5 Deviations
| ID | Deviation | Effect |
|---|---|---|
| S23-DEV-01 | Stage 23 edits three existing hub files (DW-17) and two data files; all listed in U-4 | defaults unchanged; the shipped configuration ships OFF |
| S23-DEV-02 | Test fixtures carry a synthetic `approval_refs` marker that states it is not a human approval | existing tests keep their configurations |
| S23-DEV-03 | A hand-edited decision flag other than `capability_authority` is audited only through the CONFIG_LOADED config hash, not as CONFIG_CHANGED; the CLI audits all flags | auditing every non-default flag at load would change audit rows that frozen tests count |
| S23-DEV-04 | The v0.2 schemas and the registry files were generated into the working-tree `docs/23-human-control/` folder (docs only). That ran two small generator scripts from the working tree (HAR-16 E0 execution; they read only `hub/` and `docs/12-specs`, never `data/`); all tests ran in sandbox copies; `data/` checksums rc 0 before and after | recorded here for Dinesh's attention |
| S23-DEV-05 | `hub-config` v0.2 describes the effective configuration (nested objects the build uses), not the v0.1 shape | v0.1 rejected the built config (S32) |
| S23-DEV-06 | The mutation runs used a full copy of the working tree including the untracked `data/` (a git clone lacks it); the Stage 16 mutant H1 anchor moved to `hub/security/zone_h.py` in Stage 20 | none |
| S23-DEV-07 | A folder `docs/25-governance/` appeared untracked in the working tree during the stage; it is not part of Stage 23 and was not committed | none |
| S23-DEV-08 | `approval_ref` is a reference string; the hub cannot verify it | RR-HC-1 |

### Findings
- [Verified Fact] No `.fde/` file and no Stage 0B document was modified by Stage 23.
- [Verified Fact] The non-add register lists every Stage 23 edit to an existing file (7 entries) and TST-CO-05 c passes with it.
- [Inference] UP-1 is an addition, not a loosening: it makes a gate stricter than 0B.
- [Unknown] Whether the 0B list is complete for a real GxP deployment (no client input).

## Evidence References
Files named in U-4; the catalogue; `.fde/orchestrator-decisions.md` OD-25, OD-27, OD-29.

## Assumptions
- A-23-11 Dinesh Naik remains the sole approver for the engagement (OD-01).

## Unknowns
- U-23-01 Real holders. U-23-13 Whether HAR-17 is wanted.

## Unresolved Issues
- Decisions UP-1..UP-5 are open.

## Residual Risks
- If the proposals are ignored, the hub's approval rule is stricter than the written contract; the contract would then understate a control (RR-HC-6, Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
