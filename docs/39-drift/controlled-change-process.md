---
stage: "39 — Drift + Continuous Improvement"
artifact: "controlled-change-process.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/37-operating-model/change-governance.md", "docs/00-preflight/operating-contract/change-control-rules.md", "docs/25-governance/governance-model.md", "docs/14-transformation/feature-flag-plan.md", "docs/26-tevv/release-thresholds.md", "tests/hub/non_add_edits.json", "hub/config.py", "hub/policy/as_found_pins.json", ".fde/orchestrator-decisions.md (OD-01, OD-13, OD-16, OD-23, OD-27, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
How a drift finding becomes a change, and why an untracked change cannot be silently absorbed. The process does not invent a new governance body: it routes drift findings into the existing change classes C0..C8 and E of `docs/37-operating-model/change-governance.md` and the engagement's own practice (branch per stage, PR, full regression, squash-merge, orchestrator decisions log). Preventive controls (stop a change) and detective controls (notice a change) are separated, with the evidence state of each. **Honest status: the process blocks untracked changes by design and by several enforced tests, but three enforcement links are missing (CI not installed, branch protection not evidenced, one human reviewer). The gate condition "controlled change process blocks untracked changes" is therefore met as DESIGN plus partial enforcement, not as fully enforced.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CCP-1 Steps
| Step | Action | Output | Who (interim) |
|---|---|---|---|
| 1 Detect | an evaluation session, a CI/regression failure, or a person notices a signal (TRG-nn) | evaluation record entry | operator |
| 2 Classify | INVESTIGATE or not (tier); map to class C0..C8/E | backlog item with trigger id and class | operator |
| 3 Investigate (read-only) | reproduce in a sandbox copy; no change to main, to `data/`, to goldens or to thresholds | finding with evidence and confidence | operator |
| 4 Propose | write the change request: what, why, class, blast radius, rollback, tests to run, baselines affected | change request document (docs file or decision-log entry) | operator |
| 5 Decide | the class approver decides; for every class in practice this is Dinesh (roles VACANT). Risk acceptance, naming holders, cutover and irreversible steps are Dinesh only (OD-32). The agent never approves its own proposal (HAR-11, TP-14) | decision recorded as OD-nn with date, wording of the answer and the `approval_ref` where the class needs one | Dinesh Naik |
| 6 Implement | on a `stage-NN-*` or `change-*` branch only; non-add edits listed in `tests/hub/non_add_edits.json` with a work item; behaviour changes via an approved deviation row; docs-only stays docs-only | PR | builder |
| 7 Verify | tests relevant to the class run; the orchestrator runs the full regression once before merge; checksum rc 0 before and after; characterization and golden-compare where behaviour is touched | recorded results | orchestrator |
| 8 Merge | squash-merge by the orchestrator (OD-13) | commit on main with PR number | orchestrator |
| 9 Re-baseline (if the change moves a baseline) | see CCP-4 | new version of the baseline, old retained | Dinesh decision |
| 10 Close | evaluation record updated; backlog item closed with evidence; drift metric re-run | closure entry | operator |

Emergency path E: for a SEV-A/SEV-B defect, fix first on a branch with the safe default kept, run the same tests after the fact only if safe, ratify at the next gate; an emergency never waives a release gate (EH-08, HAR-14).

### CCP-2 Controls that block or reveal an untracked change
| Control | Type | What it catches | Enforced where | Evidence state |
|---|---|---|---|---|
| Egress guard on every `python -m hub` call; zero-counter tripwires | preventive + detective | a model/network call | code + ALT-01/02, INV-01/02 | [Verified Fact] |
| Closed config key schema (`E-CFG-INVALID`); safe defaults; `approval_ref` for authority moves | preventive | an unknown or unapproved flag | `hub/config.py`; DW-17 | [Verified Fact] schema; DW-17 built, ships off |
| Rule sets ship INACTIVE; activation is a Zone H act with holders EMPTY | preventive | rule-set activation | policy service, gate | [Verified Fact]; refused today |
| as-found and baseline sha256 pins ("changing a pin = reviewed PR") | detective | change to rule sources or baseline stores | tests + pin files | [Verified Fact] |
| TST-CO-05 a/b/c: legacy tree bytes unchanged; non-add edits only when listed | preventive (fails the suite) | unlisted edit of an existing file | test suite | [Verified Fact] |
| Backup checksum rc before/after every run | detective | data change | OD-03a procedure | [Verified Fact] procedure; manual |
| Golden-compare and characterization | detective | behaviour change | harness | [Verified Fact]; CT-13 open |
| Doc-vs-code tests D03/C05/A01 | detective | doc divergence | Stage 31 tests | [Verified Fact] for Stage 31 only |
| `schema_migrations` insert-only triggers | preventive | rewriting migration history | Stage 27 A-27-05 | [Verified Fact] |
| Branch-per-stage, PR, squash, orchestrator regression | process | any code or doc change | convention | [Verified Fact] practice; **not technically enforced** |
| CI workflow `ci/hub-hardening.yml` | preventive | merge without tests | not installed (HAR-07 needs approval) | [Verified Fact] absent |
| Branch protection / required review | preventive | direct push to main | unknown | [Unknown] U-39-09 |
| Second reviewer | preventive | self-approved change | none exists | [Verified Fact] single approver; risk open (DQ-17) |

### CCP-3 Residual untracked-change paths [Inference]
(a) Someone with write access pushes to main directly: not technically prevented (no evidence of protection); detected only by AM-01. (b) A change that keeps hashes and tests green but alters meaning in an unpinned file: detected only by review. (c) A baseline edited together with the code that is checked against it (for example a golden re-recorded in the same PR): prevented by the rule in CCP-4 and by TST-CO-05 c for the harness, otherwise by review. (d) A threshold edited to turn a trigger green: prevented by rule CCP-5 only (no test). Each is listed as a backlog item (IB-11..IB-14).

### CCP-4 Baseline rules
1. A baseline (backup checksums, pins, goldens, MANIFEST, thresholds RT-xx, SLO candidates, this stage's thresholds) is never edited in place. A new version is a new file or a new entry carrying the old value, the reason, the approving decision and the date.
2. A baseline may not be refreshed in the same PR that produces the value it is compared to, unless Dinesh's decision is cited and the old baseline remains available (Stage 26 RT rule).
3. Re-recording a golden because of environment drift (CT-13 case) is a change request of class C2/C6, not a test fix.

### CCP-5 Threshold rules
A trigger threshold is changed only through steps 4-8; a change made after results exist is a new version marked "changed after results" and cannot alter the outcome already computed (same rule as Stage 26 TH-0). Thresholds that are agent candidates remain labelled CANDIDATE until recalibrated on real data at TRG-13.

### CCP-6 Drift that is not a change request
A tripwire event (TRG-01) is an incident under Stage 29, not a change. A known-and-registered drift (CT-13 with its signature) stays INVESTIGATE-open until the decision is made; it is not silently accepted. No finding is closed by the agent as "accepted risk".

## Evidence References
See header.

## Assumptions
- A-39-18 Using `change-*` as a branch prefix for post-stage maintenance changes (in addition to `stage-NN-*`) is a proposal; no such prefix is defined today. Confirm: Dinesh.
- A-39-19 Class approvers equal Dinesh until roles are filled; this is a placement, not an acceptance (OD-34).

## Unknowns
- U-39-09 Remote branch protection. U-39-14 Whether there will be post-Stage-46 maintenance and who funds it (Stage 32: costs Unknown).

## Unresolved Issues
- CCP-2 rows "CI", "branch protection", "second reviewer" are missing controls; D-27-03 (install CI under `.github` with SHA pins), DQ-17.

## Residual Risks
- RR-39-13 The controls are strong against accidental drift and weak against a deliberate or careless single operator. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
