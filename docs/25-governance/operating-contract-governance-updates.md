---
stage: "25 — Governance + Compliance + Assurance"
artifact: "operating-contract-governance-updates.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/00-preflight/operating-contract/{provisional-operating-contract,provisional-human-approval-rules,provisional-tool-agent-permissions,change-control-rules,evidence-contract,stop-conditions,open-governance-decisions,operating-contract-readiness}.md (Stage 0B originals, not modified)", "docs/02-stakeholders/{operating-contract-confirmations,approval-authority-map}.md (Stage 2)", ".fde/orchestrator-decisions.md (OD-01..OD-29)", "git branch -a / git remote -v / git log (read-only, 2026-10-21)", "docs/18-delivery/delivery-backlog.md DQ-17", "docs/25-governance/*.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The Stage 0B originals are PRESERVED and not edited (HAR-13, CC-07); this document records updates beside them. 'CONFIRMED BY RECORD' means a quoted OD entry carries approval wording from Dinesh. 'EVIDENCED IN PRACTICE' means later work followed the item but no approval wording exists, so it is NOT confirmed. Only Engagement lead (Dinesh Naik) can confirm a 0B item (TP-14, AG-5); this stage proposes, he decides.**

## Summary
Of the **15 governance decisions (GD-01..GD-15)**, **16 approval triggers (HAR-01..HAR-16)** and **7 contract assumptions (A-0B-01..A-0B-07)** from Stage 0B: **6 are CONFIRMED BY RECORD** (GD-02 and HAR-02 via OD-09; HAR-04 via OD-13; HAR-10 for the AI part via OD-08; HAR-11 via OD-04; HAR-13 for the Stage 12 v0.2 addendum path via OD-25 / OD-29); **3 are DONE as actions awaiting his acknowledgement** (GD-03, GD-08, GD-14); **8 are EVIDENCED IN PRACTICE without approval wording** (GD-01, GD-04, GD-11, GD-15 in part, HAR-01, HAR-03 narrowly, HAR-09 for the private remote, HAR-16) and are therefore not confirmed; the rest remain **OPEN** or unused for his explicit answer. Three 0B texts are **out of date** and need an updated wording: the remote/CI position (GD-09; OD-05 still reads 'Pending repo creation' although the remote and eleven squash-merged PRs exist), the single-automated-actor assumption (A-0B-05; a GitHub Actions workflow file exists), and the PROVISIONAL tag on HAR-04. No 0B item is declared confirmed without a quoted record.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### UP-1 Governance decisions GD-01..GD-15
| ID | 0B position | Evidence since 0B | Stage 25 status | Proposed updated wording / action | Owner |
|---|---|---|---|---|---|
| GD-01 decision rights | Dinesh sole approver, PROVISIONAL (A-0B-06) | He has approved or answered OD-01, -04, -08, -09, -12, -18, -22, -24..-29 | EVIDENCED IN PRACTICE for every recorded decision; wider authority stays [Assumption]; Q-02-01 not asked as such | Keep PROVISIONAL for anything not in the OD log; no change to scope of what agents may do | Engagement lead (Dinesh Naik) |
| GD-02 baseline dataset | Shipped 125-case DB (OD-02 provisional) | OD-09 "Approved by Dinesh": shipped 125 cases, seed 4100 | **CONFIRMED BY RECORD** | Close GD-02 | closed |
| GD-03 checksum manifest of all data files | extend to 1,512 files | OD-03a "Done"; manifest covers all files; Stage 2 verified 1,512 lines | DONE, acknowledgement pending | Acknowledge | Engagement lead (Dinesh Naik) |
| GD-04 tool / agent permission matrix TP-01..TP-15 | PROVISIONAL | followed in practice (e.g. this stage writes only its own folder and runs no code; the orchestrator commits); no approval wording | EVIDENCED IN PRACTICE; OPEN | Ask Dinesh to confirm TP-01..TP-15 as written (one answer) | Engagement lead (Dinesh Naik) |
| GD-05 separation of duties | single approver | none; recorded as DQ-17 with default 'single approver, recorded risk' (delivery-backlog) | OPEN; **Stage 25 decision needed** | Decide: add a second reviewer role or accept RP-01 | Engagement lead (Dinesh Naik) |
| GD-06 environment ownership; isolated Docker host | none exists | reference laptop (3.10.12) and orchestrator cloud workspace (3.13, OD-23); no Docker run | OPEN [Unknown]; the two real environments are now named in OD-23 | Record owner of both environments as Engagement lead (Dinesh Naik) when he confirms | Engagement lead (Dinesh Naik) |
| GD-07 retention of sandbox logs | excerpts in artifacts | OD-16: sandbox copies deleted after each run | OPEN; proposal RC-6 (excerpt + hash, no full sandboxes) | Decide with OD-S12-09 | Engagement lead (Dinesh Naik) |
| GD-08 tag `baseline-as-found` | recommended | tag exists (`git tag -l`); OD-06 "Done" | DONE, acknowledgement pending | Acknowledge | Engagement lead (Dinesh Naik) |
| GD-09 private remote; CI-on-push | OD-05 pending | `git remote -v` shows origin `dinesh13n/gxp-quality-hub-legacy`; `remotes/origin/main` exists; 11 squash-merged PRs (#1..#11); OD-13 (approved) has the orchestrator open PRs on GitHub | **UPDATED**: remote exists and PR flow approved (OD-13); OD-05 row is stale; whether Actions runs the workflow and whether CI-on-push is accepted are [Unknown]; OD-14 kept `.github/workflows` unchanged | Orchestrator to append an OD entry correcting OD-05's status; Dinesh to state CI-on-push acceptance | Engagement lead (Dinesh Naik) / orchestrator |
| GD-10 scope ambiguities SCOPE-AMB-01..05 | unresolved | OD-28 (b): consumer inventory complete as far as the repo shows, outside consumers Unknown; security hardening scheduled at Stage 24 (DW-19) | PARTLY ADDRESSED; remains OPEN | none new | Engagement lead (Dinesh Naik) |
| GD-11 GxP / Part 11 = framing | assumed (A-08) | PRD baseline approved (OD-22) with NG-06 and PNFR-09 framing wording; every later stage kept the framing; no explicit answer to Q-02-06 | EVIDENCED IN PRACTICE; OPEN; **Stage 25 decision needed** | Decide framing-only vs binding (DQ-17) | Engagement lead (Dinesh Naik) |
| GD-12 human-control rules for AI / agents | always human-approved; no automated GxP decisions | OD-08 No-AI (approved); HAR-12 stands; Zone H built (holders empty) | PARTLY CONFIRMED (No-AI part, OD-08); Stage 23 will complete the HITL catalogue (DW-18) | Re-check at Stage 23 merge | Engagement lead (Dinesh Naik) |
| GD-13 steady-state ownership | none | none | OPEN; Stage 37 | carried | Engagement lead (Dinesh Naik) |
| GD-14 amend OD-03: full-repo sandbox | mandated | OD-03a "Done" | DONE, acknowledgement pending | Acknowledge | Engagement lead (Dinesh Naik) |
| GD-15 precedence of instructions | lead > OD log > contract > stage prompt > legacy docs | OD log header: "Every stage agent MUST read this file and honour it" | PARTLY EVIDENCED (OD log binding); full order not approved | Ask Dinesh to confirm the order | Engagement lead (Dinesh Naik) |

### UP-2 Human approval triggers HAR-01..HAR-16
| HAR | Evidence since 0B | Stage 25 status |
|---|---|---|
| HAR-01 data writes / restore | OD-03, OD-03a; checksum gate used before and after every execution (VS-1) | EVIDENCED IN PRACTICE; no approval wording |
| HAR-02 baseline dataset | OD-09 Approved | **CONFIRMED BY RECORD** |
| HAR-03 deleting files | OD-21 / OD-27: Dinesh approved re-enabling deletion in the connected folder (git lock files only) | NARROWLY EVIDENCED (scope: lock-file deletion); general rule stays PROVISIONAL |
| HAR-04 merge BUILD branch | OD-13: orchestrator opens PR, verifies tests and checksums, squash-merges, reports to Dinesh (Approved) | **CONFIRMED BY RECORD** (delegated merge); no personal merge approval required unless he says so |
| HAR-05 Docker / non-loopback | never exercised; bind refused in code even with approval (DEV-75) | PROVISIONAL; unused |
| HAR-06 logic / threshold changes | rule sets built inactive under OD-12 defaults (OD-16); DV-01..DV-11 not approved | OPEN; no logic change has been approved |
| HAR-07 CI / Dockerfile / env / pyproject | OD-14: no `pyproject.toml` change, `.github/workflows` unchanged | PROVISIONAL; first real use at Stage 27 |
| HAR-08 egress / dependencies | zero third-party dependencies (SS-01); no egress | PROVISIONAL; unused |
| HAR-09 off-device data / remote / public repo | private remote exists; OD-13 approves PRs on it; DBs and lake not committed (SS-02) | EVIDENCED IN PRACTICE for the private remote; prohibitions on public repo and data commit stand |
| HAR-10 introduce AI or automated action | OD-08 No-AI approved; scheduler OFF pending OPD-11 | **CONFIRMED BY RECORD** for AI (OD-08); automated-action interpretation (OD-S12-10) OPEN |
| HAR-11 record decisions as final | OD-04; the OD-log practice | **CONFIRMED BY RECORD** (OD-04) |
| HAR-12 disposition / QA release / e-signature | no exception requested; built as human-only, holders empty | PROHIBITION STANDS; no approver exists to permit an exception |
| HAR-13 modify prior-stage artifacts / `.fde/` | OD-10, OD-24, OD-25, OD-29: Stage 12 stays frozen; Stage 12 v0.2 content approved | **CONFIRMED BY RECORD** for the Stage 12 addendum path; general rule PROVISIONAL |
| HAR-14 pass a BLOCKED gate | OD-01 "stop only on BLOCKED" | OPEN (no BLOCKED gate has occurred in the OD record) [Unknown] |
| HAR-15 real systems / E3 / E4 | none exist (OD-04, OD-28 a) | MOOT |
| HAR-16 execute code in working tree | OD-03a forbids; honoured | EVIDENCED IN PRACTICE |

### UP-3 Contract assumptions A-0B-01..A-0B-07
| ID | 0B assumption | Status | Note |
|---|---|---|---|
| A-0B-01 | No SOW or brief beyond `engagement-context.md` | OPEN; still true so far as the repo shows | no contractual obligation mapped (OB-14 Unknown) |
| A-0B-02 | Device connector blocks deletion by default | SUPPORTED: OD-21 records that deletion had to be re-enabled by Dinesh's approval | [Inference] from OD-21 / OD-27 |
| A-0B-03 | Device is a single-user workstation | OPEN | Stage 24 |
| A-0B-04 | "Synthetic" claims accurate for every file | OPEN | spot-checked only; STOP-04 never reported; Stage 24 |
| A-0B-05 | `claude-fde-agent` is the only automated actor; CI only after OD-05 | **OUT OF DATE**: remote exists; `.github/workflows/verify.yml` is in the repo; whether it runs on the remote is [Unknown] | Dinesh to state; correct the assumption |
| A-0B-06 | Dinesh holds approval authority | EVIDENCED for recorded decisions; wider authority [Assumption] | as GD-01 |
| A-0B-07 | Orchestrator review is adequate code review for one human | SUPPORTED by OD-13 (approved delegation) for ordinary changes; for GxP-relevant changes it depends on DQ-17 | linked to RP-01 |

### UP-4 Other 0B contract elements
- **Tool / agent permissions TP-01..TP-15, change control CC-01..CC-12, stop conditions STOP-01..STOP-12, evidence contract EV-01..EV-08 / NE-1..NE-6 / EO-1..EO-4:** followed in every stage reviewed; none carries approval wording. CC-10 should be updated to the observed remote and PR flow; CC-12 (tag) is done; CC-02 commit message convention `stage-<ID>: <title> v<ver> (<GATE>)` is used. [Verified Fact]
- **New items this stage proposes to add to the contract (not adopted):** (1) a no-"compliant"-wording rule (RP-02); (2) the risk-acceptance procedure RR-C in `risk-acceptance-register.md`; (3) a rule that a Stage 25 mapping is re-issued when Stage 23/24 merge; (4) a rule that any decision flag moved away from its default requires an `approval_ref` once DW-17 exists. [Inference]

### UP-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| UF-01 | [Verified Fact] The OD log has become the real approval register, but 0B still calls most items PROVISIONAL because nobody consolidated | OD-01..OD-29 vs `operating-contract-confirmations.md` | Two sources disagree on what is approved | Medium | High | Will Dinesh confirm a short list in one answer? |
| UF-02 | [Verified Fact] OD-05 and A-0B-05 describe a state that no longer exists | `git remote -v`; PR history | Stale control text | Low | High | orchestrator correction |
| UF-03 | [Inference] One consolidated confirmation request (GD-04, GD-15, TP matrix, HAR-01/05/07/08/16, A-0B-03/05) would close most OPEN rows without new analysis | UP-1..UP-3 | Reduces approval fatigue | Low | Medium | Dinesh's call |

## Evidence References
0B originals in `docs/00-preflight/operating-contract/` (unchanged); Stage 2 confirmations; OD log; read-only git output (remote, branches, tag, merge count).

## Assumptions
- A-25-UP-1 [Assumption] The OD-log wording "Approved by Dinesh" / "Approved" is a valid approval form (EV-07). Confirm: Engagement lead (Dinesh Naik).
- A-25-UP-2 [Assumption] "Done" entries (OD-03, -03a, -06) were executed under OD-01 delegation (carried from A-02-06).

## Unknowns
- U-25-UP-1 Whether GitHub Actions executes `verify.yml` on the remote, and whether that run is destructive to anything (it runs on a runner copy, ENV-F4 / CC-10).
- U-25-UP-2 Whether a BLOCKED gate has ever occurred and how HAR-14 was applied.

## Unresolved Issues
- GD-04, GD-05, GD-06, GD-07, GD-10, GD-11, GD-12 (Stage 23), GD-13, GD-15; HAR-05..HAR-08, HAR-12, HAR-14; A-0B-01, -03, -04, -05, -06.

## Residual Risks
- RR-UP-1 A stale PROVISIONAL tag can hide a real approval, or a real approval can be assumed where only practice exists: Low-Medium; each row above separates the two.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue; 0B originals preserved. |
