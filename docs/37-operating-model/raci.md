---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "raci.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/accountability-map.md AM-1..AM-3", "docs/18-delivery/ownership-map.md OM-1..OM-3", "docs/02-stakeholders/decision-rights-map.md DR-01..DR-31", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md HAR-01..HAR-16", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md TP-01..TP-15", "docs/23-human-control/escalation-matrix.md", ".fde/orchestrator-decisions.md OD-13, OD-23, OD-30..OD-32"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Target RACI for 24 steady-state activities across the roles defined in `target-operating-model.md` TOM-4. Rules applied: **exactly one A per activity**; A is the *role* that should be accountable in steady state; **Today** shows who actually acts now. Because every client-side role is VACANT and Dinesh Naik is the only human, "A (interim)" means Dinesh is accountable by default and has not accepted the steady-state role. R cells held by an agent mean execution only (TP-14: agents hold no approval rights).

Legend: A accountable, R responsible (does), C consulted, I informed, `-` none. A subscript `i` = INTERIM holder (Dinesh); `v` = VACANT role (no holder). Role columns: **E**=RL-01 Engagement owner, **S**=RL-02 Service owner, **P**=RL-03 Process owner, **Z**=RL-04 Dispositioner, **K**=RL-05 Risk/security, **Q**=RL-06 Compliance/quality, **D**=RL-07 Data owner, **N**=RL-08 Integration owner, **F**=RL-09 Finance, **T**=RL-12 Toolchain owner, **G**=agents (`claude-fde-agent`).

## Findings
### RC-1 RACI matrix
| # | Activity | E | S | P | Z | K | Q | D | N | F | T | G | Today (evidence) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Approve a change to hub code (PR merge) | C | A | I | - | C | I | - | I | - | R | R | Dinesh approves standing (OD-13); orchestrator merges after review |
| 2 | Run full regression before merge | I | A | - | - | - | - | - | - | - | R | R | Orchestrator, cloud workspace (OD-23) |
| 3 | Release / go-no-go for each cutover step CUT-1..CUT-5 | A | R | C | C | C | C | C | C | C | I | R | Dinesh only (AP-5, HAR-11); none can start (RB-4) |
| 4 | Decision-flag move (any `OD-S12-xx` flag) | C | R | A | - | C | C | - | - | - | - | R | Needs `approval_ref`; Dinesh decides (OD-26, DW-17) |
| 5 | Activate a rule set | C | I | R | A | C | C | - | - | - | - | I | Not exercisable: no holder (AP-4) |
| 6 | Adopt or withdraw a policy (ZH-10) | C | I | R | A | C | C | - | - | - | - | I | Not exercisable |
| 7 | Batch disposition / QA release | I | I | I | A,R | C | C | - | - | - | - | - | Never by agent or engagement (HAR-12, STOP-07); no holder |
| 8 | Maintain the Zone H holder list | C | R | C | I | A | C | - | - | - | - | R | `zone_h.holders` empty; Dinesh must approve any name (OD-17, OD-31) |
| 9 | Operate and review the audit chain (`verify-audit`) | I | R | - | - | A | C | - | - | - | - | R | No scheduled run (AM-3); orchestrator runs it in regression |
| 10 | Accept a risk | A | C | C | - | C | C | - | - | - | - | I | Dinesh only (AP-7); nothing accepted by Stage 37 |
| 11 | Approve a behaviour deviation DV-xx (preserve-or-fix) | A | R | C | - | - | C | - | C | - | - | R | HAR-06; none approved; golden-compare exits 6 |
| 12 | Define closed / resolved / 48 h clock (OPD-01..03) | C | I | A | - | - | C | - | - | - | - | I | No decider (DR-20); accepted open (OD-22) |
| 13 | Source-contract change / schema_version allow-list | C | R | I | - | - | - | C | A | - | - | R | record_only everywhere (OD-28); owner Unknown |
| 14 | Late or missing feed: manual catch-up run | I | R | C | - | - | - | C | A | - | - | R | Manual only (OD-28 (c)) |
| 15 | Retention and disposal decision | C | I | C | - | A | C | R | - | - | - | I | Hold-all (OD-30); no authority to dispose |
| 16 | Backup, checksum verification, restore | I | A | - | - | C | - | R | - | - | - | R | `SHA256SUMS.txt`; restore only with HAR-01 |
| 17 | Access grants, token issue/revoke | I | R | - | - | A | - | - | - | - | - | R | Local accounts; no real users exist |
| 18 | Security event triage | I | R | - | - | A | C | C | - | - | - | R | No route (ES-24); synthetic data only |
| 19 | Vendor / toolchain terms review (VA-01..VA-07) | A | C | - | - | C | - | - | - | C | R | I | PROPOSED only; Dinesh to decide |
| 20 | Cost tracking and budget | I | R | - | - | - | - | - | - | A | - | R | Cost today USD 0 model spend; infra Unknown (FB-01, FB-12) |
| 21 | Documentation / evidence upkeep (`docs/`) | A | R | C | - | - | C | - | - | - | - | R | Stage agents; versioned, errata not overwrite (CC-06/07) |
| 22 | Independent verification of GxP-relevant change | C | I | - | - | C | A | - | - | - | - | I | None; walkthroughs by Dinesh, unsigned; DQ-17 |
| 23 | Re-qualify AI (RQ-1..RQ-3) | A | R | C | - | C | C | C | - | C | - | R | Not triggered (OD-08); new Dinesh decision required |
| 24 | Close the engagement contract | A | I | I | - | I | I | I | I | I | I | R | Dinesh only; see `operating-contract-closure.md` |

Holder states for the A column: rows 1, 2, 16 (S, VACANT, interim E); rows 4, 12 (P, VACANT); rows 5, 6, 7 (Z, VACANT, outside engagement); rows 8, 9, 15, 17, 18 (K, VACANT); rows 13, 14 (N, VACANT); row 20 (F, VACANT); row 22 (Q, VACANT); rows 3, 10, 11, 19, 21, 23, 24 (E, INTERIM Dinesh). **Seventeen of 24 activities have a VACANT accountable role.** For those, Dinesh Naik is the accountable party of record in practice (accountability-map AM-2) but this RACI does not assign it to him, because that would present an unaccepted placement as assigned.

### RC-2 RACI checks
| Check | Result | Tag |
|---|---|---|
| Exactly one A per row | Pass (row 7 uses A,R for the same role Z) | [Verified Fact] by inspection |
| No agent is A | Pass (TP-14; AG-5) | [Verified Fact] |
| No agent R for Z-reserved acts (rows 5, 6, 7) | Pass (agents `I`/`-`) | [Verified Fact] |
| Segregation: author is not sole reviewer | **Fail** today (E performs and approves; RP-01, RS-16) | [Verified Fact] |
| Every A has a holder | **Fail** (17 of 24 rows have a VACANT A) | [Verified Fact] |

### RC-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RF-01 | [Verified Fact] 17 of 24 steady-state activities have no holder for the accountable role | RC-1 | RACI is clear on roles, empty on people | High (real use) | High | Who fills S, P, Z, K, N, F, Q? |
| RF-02 | [Verified Fact] Row 7 (disposition) cannot be given a holder by this engagement by design | HAR-12; STOP-07 | The most important A is permanently outside scope | High (any pilot) | High | Does a real authorised human exist? |
| RF-03 | [Inference] Rows 1, 2, 16 would be the first to need a real S (service owner), since they run every release | OD-13, OD-23 | Release throughput depends on one person | Medium | Medium | Is "S" = Dinesh in a steady state he will accept? |

## Evidence References
See `evidence_sources`. Today column cites the document that records the present behaviour.

## Assumptions
- A-37-RC-1 [Assumption] The activity list covers the recurring actions the repo implies; additions are expected. Confirm: Engagement lead (Dinesh Naik).
- A-37-RC-2 [Assumption] Placing A for rows 4 and 12 with the process owner (P) matches DR-20/DR-23 intent (business definitions belong to the business). Confirm: Engagement lead (Dinesh Naik).
- A-37-RC-3 [Assumption] Row 22 A = Compliance/quality (Q) is a design choice to avoid author-as-reviewer; no holder exists. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-RC-1 Whether any role would be combined (for example S and T) in a real organisation.
- U-37-RC-2 Whether a quality unit or change board would own rows 3, 10, 11.

## Unresolved Issues
- Fill or waive VACANT A holders; DQ-17 second reviewer.

## Residual Risks
- RR-37-RC-1 A reader treats the matrix as staffed: mitigated by the holder-state paragraph and the Today column. Low.
- RR-37-RC-2 Single person is the practical A for all rows: decision latency and no separation of duties. Medium (accepted by Dinesh in OD-30 as a general risk only).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
