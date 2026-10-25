---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-security-governance-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/24-security-privacy/", "docs/25-governance/", "docs/27-hardening/vulnerability-disposition.md", "docs/23-human-control/approval-gates.md", "docs/26-tevv/", "hub/security/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
Security and governance are adequate for a synthetic, loopback, shadow system only. The human gate is built but unexercised (no holder). Compliance is framing; no risk beyond RA-01..RA-11 is accepted.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SG-1 Security posture [Verified Fact]
Adequate **only for synthetic, loopback, shadow use** (security-readiness; Stage 27 gate). Not ready for real data, network exposure or AI.
| Control | As built | Evidence |
|---|---|---|
| Authentication | Local passwords (PBKDF2, 600,000 iterations - proposal), single factor, lockout 5/15/15, session 30 min idle / 8 h, password >= 12 chars | IC-5; RTD-26; RS-02 |
| Authorisation | Deny-by-default 48-route registry; roles reviewer, quality_lead, compliance, finance_read, integration, dispositioner; service tokens never Zone H | PCH-24 |
| Transport | Loopback only; no TLS; non-loopback bind refused by two independent checks | VR-03; PCH-45 |
| Audit | Hash-chained audit; `verify-audit`; anchor an unsigned local file, opt-in seal; tail truncation after last anchor undetectable; host compromise can rewrite chain and anchor | RP-03; RS-03 |
| Input hardening | Untrusted-text type guard; planted-string suites; Stage 27 fixes F-01..F-07 | OD-34 |
| Secrets | Scan 0 real secrets (1 deliberate fixture hit); no secrets in audit (E-SEC-SECRET-IN-AUDIT) | PNFR-08 |
| Supply chain | Zero third-party runtime dependencies; SBOM summary; CI not installed; actions not SHA-pinned (VA-06) | `docs/27-hardening/sbom-summary.md` |
| Testing | Static analysis, mutation gates (Stage 24: 8 of 8; Stage 27: 13 of 13), agent-run red team; **no external penetration test** | RS-14 |

### SG-2 Human-control model [Verified Fact]
Zone H actions ZH-01..ZH-10 enter one choke point (`hub/gate/actions.py`): ZH-01/02/03 disposition, ZH-04 close-exception transition, ZH-05 policy adopt/accept-open, ZH-06 rule-set activation decision/activate/deactivate, ZH-07 exception-rule accepted (record only; semantics undefined in the Stage 12 spec, RTD-67), ZH-08 disposition-mode change, ZH-09 schedule flag, ZH-10 rule-row edit and policy withdrawal (Stage 20). Note: Stage 17 PCH-04 labels the contract-binding change 'ZH-10' while the code and Stage 23 use ZH-10 for rule-row edit/withdrawal; the code is taken as authoritative (reconciliation item AB-14); only an authenticated human in `zone_h.holders` with re-auth and `authority_ref`. **No holder exists**, so the gate has never been exercised end to end by a real person (RP-09). ZH-11 (authority switch as Zone H) was not adopted (OD-31): the switch is CLI + `approval_ref`. Decision flags away from default need an `approval_ref`. HAR-01..HAR-17 are Dinesh-held engagement gates.

### SG-3 Governance [Verified Fact]
- Part 11 / GMP data integrity: **framing only**; no 'compliant', 'validated' or 'audit-ready' claim (GD-11, RP-02).
- Single approver, no separation of duties (RS-16, RP-01, DQ-17): accepted by Dinesh as a general risk in OD-30, not as a Stage 24 acceptance.
- Risk acceptances RA-01..RA-11 are Dinesh's scope/sequence decisions; **RP-01..RP-12, RS-01..RS-16, VA-01..VA-07, RTR-01..RTR-15, F-11 are all open and none is accepted** (see `residual-risk-register.md`).
- Stage 25 compliance matrix predates Stage 23/24 merge; v0.2 re-issue not done (RP-10).
- OD-32 default-answer authority covers scope/sequencing only; it never accepts risk, names holders, approves cutover or any irreversible step.

### SG-4 Open High items [Verified Fact]
VR-02 (Python 3.10 end of life), VR-03 (no TLS if exposed), VR-04 (legacy container files if exposed) have no accepted disposition (release criterion T-10 FAIL); S26-F-02 was fixed by an agent-assumed rule (D-27-01 open).

### SG-5 Privacy [Unknown / Assumption]
No privacy impact conclusion for real data: regime (DPDP/GDPR) not assessed, field classes proposed (RS-06). Synthetic data only. STOP-04 on real data.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-09 [Assumption] Control values (iterations, lockout, session, rate limit) remain agent proposals (OD-32, OD-34).

## Unknowns
- U-43-08 External penetration test result (none exists).
- U-43-09 Real privacy regime and field classes.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
