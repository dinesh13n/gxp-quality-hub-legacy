---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "security-ownership.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/24-security-privacy/{security-control-matrix,residual-security-risks,threat-model,security-readiness}.md RS-01..RS-16", "docs/26-tevv/{red-team-findings,residual-tevv-risks,walkthrough-records}.md F-01..F-11", "docs/25-governance/{compliance-control-matrix,risk-acceptance-register,evidence-retention-policy}.md", "hub/security/", "hub/guards/", "docs/33-vendor-risk/vendor-risk-acceptance.md VA-01..VA-07", ".fde/orchestrator-decisions.md OD-30, OD-31, OD-32, OD-33"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Security, privacy and assurance ownership. Controls are strong in code and **ownerless in people**: Stage 25 lists 22 controls GC-01..GC-22 with Dinesh Naik as owner of record "because no other owner can be named" (AM-3); the risk and security partner (SH-06) and compliance team (SH-09, SH-11) are unfilled. Stage 24 holds 16 residual risks (RS-01..RS-16), none accepted (RS-16 accepted by Dinesh only as a general risk, OD-30), and Stage 26 holds 11 findings (F-01..F-11, F-02 High), none fixed or accepted (OD-33). This stage records who owns what **in role terms**, keeps every risk open, and accepts nothing. Default routing assumed from OD-33: High/Medium findings go to Stage 27; that is an assumption, not a fix.

## Findings
### SE-1 Security responsibilities by role
| Area | Owner role | Holder | Operating mechanism (evidence) | State |
|---|---|---|---|---|
| Authentication, accounts, tokens | RL-05 (policy), RL-02 (operation) | VACANT / INTERIM | `hub/security/auth.py`, `authz.py`; PBKDF2, lockout; token expiry optional (RS-08) | INTERIM |
| Authorisation and Zone H | RL-05 sets policy; RL-04 holds act; RL-01 approves holder list | VACANT / INTERIM | `zone_h.py`; TP-01..TP-15 permission matrix confirmed (OD-31) | INTERIM; holders empty |
| Audit integrity | RL-05 oversight, RL-02 operation | VACANT / INTERIM | `audit.py`, `anchor_seal.py`; anchor unsealed by default (RS-03) | INTERIM |
| Network exposure and TLS | RL-01 with RL-05 | Dinesh | loopback-only; bind refusal (DEV-75); no TLS (RS-01) | INTERIM |
| Input handling, untrusted content, injection | RL-02 | VACANT / INTERIM | `docs/24-security-privacy/prompt-injection-controls.md`; hostile corpus; OB-13 | INTERIM |
| Privacy and data protection | RL-05 with RL-06 and RL-07 | VACANT | PIA; regime not assessed (RS-06, RP-07); OB-08, OB-09 "none assigned" | **VACANT** |
| Dependency and runtime vulnerability management | RL-12 / RL-02 | INTERIM | stdlib-only; Python 3.10 / SQLite 3.37 EOL risk (RS-10, VA-01); SBOM at Stage 27 (not yet) | INTERIM |
| Security testing and independent review | RL-06 / RL-13 | VACANT | static analysis only; no external pen test (RS-14); mutants M5, M9, M10 survive (OD-33) | **VACANT** |
| Compliance framing (GxP / Part 11 as framing only) | RL-06; RL-01 for wording | VACANT / INTERIM | GD-11 / OD-30; no "compliant" claim (OB-03) | INTERIM |
| Secrets in audit / evidence | RL-02 | INTERIM | E-SEC-SECRET-IN-AUDIT (EH-08) | INTERIM |
| Security incident handling | RL-05 | VACANT | ES-24 gap; ER-03, ER-14 in `escalation-model.md` | **VACANT** |

### SE-2 Risk and finding ownership (no acceptance by this stage)
| Item set | Count | Status (evidence) | Owner of record for follow-up | Routing (assumption) |
|---|---|---|---|---|
| Stage 24 residual risks RS-01..RS-16 | 16 | open; RS-16 accepted as general risk only (OD-30) | Dinesh | Stage 27 for rate limiting, migration hardening (OD-32); others to be confirmed |
| Stage 26 findings F-01..F-11 | 11 | registered, none fixed or accepted; F-02 High (restricted-evidence read rule) | Dinesh | High/Medium to Stage 27 (OD-33 assumption) |
| Stage 26 retest items RTR-01..RTR-15 | 15 | open | Dinesh | Stage 27 / 30 |
| Stage 25 risk register RP-01..RP-12 | 12 | open, none accepted (OD-30) | Dinesh | per register |
| Vendor acceptances VA-01..VA-07 | 7 | PROPOSED only (OD-33) | Dinesh | decision pending |
| Unsigned walkthroughs TST-REV-03/04/08 | 3 | UNSIGNED; need a human (OD-33) | Dinesh performs (independence gap) | decision pending |
Severity labels in F-xx are agent Inference.

### SE-3 Segregation of duties
Today the same person is the sole approver, the walkthrough performer and the risk acceptor. This is the single-approver risk (RP-01, RS-16, DQ-17). **It is not closed by this stage.** A role-based separation is proposed (author RL-02; verifier RL-13; risk acceptor RL-01; oversight RL-06) but has no holders.

### SE-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SEF-01 | [Verified Fact] No security or privacy owner exists other than Dinesh as default | AM-1; OB-08, OB-09 unassigned | Nobody to triage an event or accept a control gap | High if exposed; Low inert | High | Who is RL-05? |
| SEF-02 | [Verified Fact] 0 of 16 RS, 0 of 11 F-xx and 0 of 12 RP are accepted by a role-holder; RS-16 is a general-risk acceptance by Dinesh | OD-30, OD-33 | Residual risk is carried, not owned by an acceptor | Medium-High | High | Route or accept at Stage 27/30 |
| SEF-03 | [Verified Fact] F-02 (High) weakens the restricted-evidence read property | `tevv-results.md` RH-1 | Evidence access control unfinished | High (if real data) | High | Stage 27 fix or decision |
| SEF-04 | [Inference] Until a security owner exists, any exposure decision (SDR-07) rests on the same person who built the controls | OD-31, OD-32 | Self-assessed security | Medium | Medium | External review (RS-14) |

## Evidence References
See `evidence_sources`.

## Assumptions
- A-37-SE-1 [Assumption] Stage 27 will handle High/Medium items by default (OD-33); not verified (Stage 27 content not read). Confirm: Engagement lead (Dinesh Naik).
- A-37-SE-2 [Assumption] The role split in SE-3 is a proposal. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-SE-1 Whether an external security function or pen-test provider would take RL-05/RL-13 (OD-32: "to be confirmed").
- U-37-SE-2 Applicable regulation and data regime for any real data.
- U-37-SE-3 State of Stage 27 deliveries on branch `stage-27-hardening` (not read).

## Unresolved Issues
- RL-05 and RL-06 holders; F-01..F-11 routing; VA-01..VA-07; walkthrough sign-off.

## Residual Risks
- RR-37-SE-1 Controls without a human owner decay (High over time).
- RR-37-SE-2 Misreading "tamper-evident" as compliance (RP-02; Medium). None accepted by this stage.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
