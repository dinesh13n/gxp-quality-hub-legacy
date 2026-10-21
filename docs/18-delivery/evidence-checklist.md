---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "evidence-checklist.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/{delivery-backlog,acceptance-test-plan,definition-of-done}.md", "docs/13-traceability/test-to-evidence-map.md", "docs/14-transformation/transformation-gates.md TG-2, TG-4", "docs/16-repo-validation/evidence/SHA256SUMS.txt (evidence integrity pattern)", ".fde/stage-prompts/19..43 (artifact paths)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. This checklist says what evidence must EXIST before an item can be called done; none of it exists yet unless stated. Paths follow the stage-prompt artifact folders.**

## Summary
Every work item DW-01..DW-50 and every decision item DQ-01..DQ-19 has required evidence, a location, a producer and a check. Common evidence (E0) applies to every executable item. An item with any missing or failing evidence row stays open (DoD universal rule). Evidence integrity: every evidence folder carries a `SHA256SUMS.txt` (Stage 16 pattern).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EC-0 Common evidence for every executable item (E0)
| # | Evidence | Check | Tag |
|---|---|---|---|
| E0-1 | data backup checksum log before and after (`sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0) | rc 0 both | [Verified Fact] OD-03a |
| E0-2 | sandbox path and cleanup line (`~/fde_sbx/<x>` removed) | path outside working tree; removed | [Verified Fact] OD-16 |
| E0-3 | commit / branch / tree id the evidence applies to | matches PR head | [Verified Fact] VS-1 pattern |
| E0-4 | `git status --porcelain` showing only the item's paths | no DB / lake / earlier-stage file | [Verified Fact] CG-11 |
| E0-5 | `SHA256SUMS.txt` in the evidence folder | `sha256sum -c` rc 0 | [Verified Fact] |
| E0-6 | runtime line (Python / SQLite version) | recorded | [Verified Fact] |

### EC-1 Evidence per work item
| Item | Required evidence (beyond E0) | Location | Producer | Check that makes it "done" | Tag |
|---|---|---|---|---|---|
| DW-01 | not-applicable record; `no-ai-check` output | `docs/19-intelligence/` | Stage 19 agent | cites OD-08; rc 0 | [Verified Fact] |
| DW-02 | regression log with per-file counts | `docs/20-application/evidence/` | Orchestrator | TST-CO-03 3/3 present; executed = discovered | [Verified Fact] |
| DW-03 | timing log per group | same | Build agent | every group < target; count unchanged (397) | [Assumption] target |
| DW-04 | golden-compare JSON report; diff vs `docs/16-repo-validation/evidence/obs-laptop.json` | same | Build agent | 0 `declared:`; D5 = 0; values equal | [Verified Fact] |
| DW-05 | register dump (all DV rows, status, approval_ref) | same | Build agent | DV-01..DV-11 present, all `proposed`, approval_ref empty | [Verified Fact] |
| DW-06 | import / cycle report; mutation H1 result; test logs | same | Build agent | 0 domain->web imports; H1 KILLED; tests green | [Verified Fact] |
| DW-07 | FAC-13 test log; audit excerpt POLICY_WITHDRAWN | same | Build agent | green; refusal with holders [] | [Assumption] FAC-13 |
| DW-08 | trace-producer test log | same | Build agent | AC-REV-05..08, AC-GATE-18..20 green without manual `record-trace` | [Inference] |
| DW-09 | CLI error-shape test log; DQ-05 reference | same | Build agent | all runners conform to the chosen shape | [Verified Fact] |
| DW-10 | contract pack: per-source counts, failing fields, reproduce command | `docs/21-integration/evidence/` | Build agent | reproducible; no binding changed | [Verified Fact] |
| DW-11 | consumer inventory; Dinesh confirmation line | `docs/21-integration/` | Build agent / Engagement lead (Dinesh Naik) | each output: consumer or Unknown | [Unknown] |
| DW-12 | TST-CO-04/05 log; legacy-path diff | `docs/21-integration/evidence/` | Build agent | green; diff empty | [Verified Fact] |
| DW-13 | Stage 12 v0.2 addendum files; generated registry; collision proposal | `docs/23-human-control/` | Build agent | registry diff 0; approval or 'accepted open' in OD log | [Verified Fact] |
| DW-14 / DW-15 | test logs; mutation result H3 / H5 | `docs/23-human-control/evidence/` | Build agent | green; KILLED | [Verified Fact] |
| DW-16 | schema test log (16 schemas) | same | Build agent | 16/16 exercised, 0 invalid | [Verified Fact] |
| DW-17 | test log both modes; audit excerpt CONFIG_CHANGED with approval_ref; L3 flip log | same | Build agent | refused without approval_ref; flip restores shadow | [Verified Fact] |
| DW-18 | autonomy / HITL catalogue; ZH coverage grep | `docs/23-human-control/` | Stage 23 agent | 10/10 ZH ids covered | [Verified Fact] |
| DW-19 | threat model; decisions table; TST-SEC log; scan output | `docs/24-security-privacy/` | Build agent | each value decided or accepted open; scan rc 0 | [Verified Fact] |
| DW-20 | obligation -> control -> evidence map; TST-NFR-10 log | `docs/25-governance/` | Stage 25 agent | no obligation marked met without evidence | [Verified Fact] |
| DW-21 | per-runtime result files; harness report | `docs/26-tevv/evidence/` | Stage 26 agent | 0 unregistered failures | [Verified Fact] |
| DW-22 | walkthrough record per TST-REV-03/04/08 (steps, observations, outcome, signer, date) | `docs/26-tevv/` | Engagement lead (Dinesh Naik) | signed by Dinesh; deviations logged | [Verified Fact] OD-24 |
| DW-23 | mutation report INC-05/07/08 | `docs/26-tevv/evidence/` | Stage 26 agent | KILLED or registered | [Verified Fact] |
| DW-24 | per-decision class-B re-run log | stage folder of the increment | Build agent | green in decided mode | [Verified Fact] |
| DW-25 | CI fixture provisioning description; hash-check log | `docs/27-hardening/` | Orchestrator | hash matches `c254649f…d70aa` | [Verified Fact] |
| DW-26 | CI workflow file diff; CI run log for 3.12+ and 3.10 | `docs/27-hardening/evidence/` | Orchestrator | both green; gates fail the job | [Verified Fact] |
| DW-27 | reviewed golden PR; new golden files + sums | `tests/characterization/golden/` (new versioned files) + `docs/27-hardening/` | Build agent / Engagement lead (Dinesh Naik) | Stage 7 goldens unchanged; 0 diff on each runtime | [Verified Fact] CT-H4 |
| DW-28 | FTS5 check log | `docs/27-hardening/evidence/` | Build agent | result recorded | [Unknown] outcome |
| DW-29 | runner design note; restore rehearsal record | `docs/27-hardening/` | Build agent | G7 checksum match | [Verified Fact] |
| DW-30 | entry-point decision ref; HTTP test log | `docs/27-hardening/` | Build agent | one documented entry point | [Verified Fact] |
| DW-31 | disk log; TST-NFR-06 log | `docs/27-hardening/evidence/` | Build agent | no residue; green | [Verified Fact] |
| DW-32 | TST-NFR-01/02/05, CT-17 logs (labelled proxies) | `docs/28-resilience/` | Stage 28 agent | labelled; CT-18 NOT-RUN unless HAR-05 | [Verified Fact] |
| DW-33 | tabletop record | `docs/29-incident-bcdr/` | Stage 29 agent | detect / contain / recover steps executed in sandbox | [Inference] |
| DW-34 | release checklist with G1..G10 rows, evidence path each | `docs/30-release/` | Build agent | every gate pass/fail with path | [Verified Fact] AC-CO-15 |
| DW-35 | DV decision refs; golden-compare after change | `docs/30-release/evidence/` | Build agent | decided DVs D3 / D0; D5 = 0 | [Verified Fact] |
| DW-36..DW-40 | per-step runbook; decision refs; L3 rehearsal log; go / no-go record or "not run" record | `docs/30-release/cut-<n>/` (Assumption) | Stage 30 agent / Engagement lead (Dinesh Naik) | DoD-C met or recorded not run | [Verified Fact] DoD-C |
| DW-41 | per-R2-item decision ref; test log on chosen entry point | `docs/30-release/` | Build agent | decided items only enabled | [Verified Fact] |
| DW-42 | 12 test logs; SLO candidate table (measure only) | `docs/31-observability/` | Stage 31 agent | labelled synthetic | [Verified Fact] |
| DW-43 | tripwire log; `model_calls_total` = 0 | `docs/32-finops/` | Stage 32 agent | 0 | [Verified Fact] |
| DW-44 | dependency inventory | `docs/33-vendor-risk/` | Stage 33 agent | every dependency listed with exit note | [Inference] |
| DW-45 | synthetic measurement set; Stage 4 v0.2 addendum | `docs/34-after-kpis/` .. `docs/36-*` | Stage agents | every figure labelled; unmeasurable stays unmeasurable | [Verified Fact] OD-07 |
| DW-46 | RACI with GAP cells | `docs/37-operating-model/` | Stage 37 agent | no invented holder | [Verified Fact] |
| DW-47 | handover dry-run record | `docs/38-handover/` | Stage 38 agent | steps executed from docs only | [Inference] |
| DW-48 | drift thresholds (Assumption-labelled) | `docs/39-continuous-improvement/` | Stage 39 agent | labelled | [Inference] |
| DW-49 | retirement criteria; dependency check | `docs/41-retirement/` | Stage 41 agent | CO-WF-01 untouched | [Verified Fact] |
| DW-50 | roadmap; defence pack; FINAL FR dispositions; trace re-run output | `docs/40-*`, `docs/42-*`, `docs/final-prd/` (per engagement-context) | Stage agents | 52/52 FR dispositioned | [Verified Fact] SUM-5 |

### EC-2 Evidence for decision items (DQ-01..DQ-19)
| Evidence | Check | Tag |
|---|---|---|
| OD-nn entry in `.fde/orchestrator-decisions.md` with "Approved by Dinesh", "ANSWERED", or "accepted open" wording and date | entry exists; wording names Dinesh as the decider | [Verified Fact] OD-22 pattern |
| approval_ref on the affected flag / DV row / policy event | non-empty; audited | [Verified Fact] FF-2 |
| class-B re-run log (DW-24) | green in decided mode | [Verified Fact] |

## Evidence References
`delivery-backlog.md`; `definition-of-done.md`; stage-prompt artifact paths.

## Assumptions
- A-18-EC-1 [Assumption] Folder names for Stages 35, 36, 40, 42 follow their stage prompts (not read in full here); exact names are taken from those prompts when the stage runs.
- A-18-EC-2 [Assumption] Per-CUT sub-folders under `docs/30-release/`.

## Unknowns
- U-18-EC-1 CI log retention location (GitHub Actions retention vs committed copy) - decided with DQ-06.

## Unresolved Issues
- None blocking.

## Residual Risks
- RR-EC-1 Evidence produced and checked by agents, with one human checker (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
