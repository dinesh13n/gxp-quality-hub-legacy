---
stage: "38 — Handover + Knowledge Transfer"
artifact: "security-handover.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/24-security-privacy/ (threat-model, attack-surface-map, security-control-matrix, security-readiness, residual-security-risks, privacy-impact-assessment)", "docs/23-human-control/", "docs/25-governance/ (risk-acceptance-register, accountability-map)", "docs/27-hardening/", "docs/33-vendor-risk/", "docs/37-operating-model/security-ownership.md", "hub/security/", "hub/guards/", ".fde/orchestrator-decisions.md OD-17, OD-30, OD-31, OD-32, OD-34"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. This is the handover of a PREPARED-BUT-UNRELEASED system: Stage 30 is BLOCKED (0 of 40 approvals), no cutover, authority flip, tag or release happened, and the hub is not deployed beyond loopback. The only human is Dinesh Naik, Engagement lead (OD-04). No receiving team, trainee, walkthrough audience, exercise result, sign-off or approval is invented here; vacant roles stay vacant (Stage 37). Nothing here accepts a risk (HAR-11). The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
Security, privacy and governance knowledge the receiver must hold. The honest headline: **controls are strong in code and ownerless in people** (Stage 37 `security-ownership.md`). The hub is hardened for a synthetic, loopback, No-AI deployment; nothing is exposed, no real data exists, no external penetration test has been done, and **no residual risk has been accepted by anyone**. The receiver inherits open risks, not closed ones.

## Findings
### SH-1 Controls in place [Verified Fact unless marked; sources in parentheses]
- Authentication and accounts: local principals, PBKDF2 hashes, lockout, service tokens (`hub/security/auth.py`, `authz.py`); user creation is offline host-operator only (`python -m hub.admin user create`), no web bootstrap.
- Authorisation and Zone H: one holder rule in one gate; disposition, QA release, e-signature stay with an authorised human outside the engagement; `zone_h.holders` ships EMPTY, so the gate refuses every request on a fresh install (AC-GATE-02, OD-17, OD-31). Authority switch = CLI plus `approval_ref` (ZH-11 not adopted, OD-31).
- Audit integrity: hash chain plus anchor file (`hub/security/audit.py`, `anchor_seal.py`); `verify-audit` exit 17 on tamper; anchor seal is opt-in and **unsealed by default** (RS-03, DQ-S24-01..10 taken as assumptions, OD-32).
- Network: loopback bind only, non-loopback refused (exit 9 `E-SEC-EXPOSURE-NOT-APPROVED`, `startup-check`); no TLS (RS-01).
- Input handling: untrusted text is data (`hub/core/untrusted.py`); hostile corpus (22 injection docs + 10 variants) passes; mutation gate killed 8 of 8 at Stage 24; Stage 27 later fixed F-01..F-07 and added 401/400/408/503, rate limit 429 after 100 refusals in 60 s, insert-only `schema_migrations` triggers (**all agent assumptions, none approved**, OD-34).
- Egress/No-AI: guards on every CLI (`hub/guards/`); release gate G5.
- Secrets: secret scan with `python -m hub.admin scan` (exit 16 on findings); no real credentials exist (OD-28).

### SH-2 Risks that remain open and owned by no one but Dinesh [Verified Fact: OD-30, OD-33..OD-36]
RS-01..RS-16 (residual security), RP-01..RP-12 (risk register), VA-01..VA-07 (vendor acceptances, PROPOSED only), RTR-01..RTR-15 (TEVV residual), F-xx remainder (F-11, F-29-02..16, F-31-01..07). **None is accepted.** The single-approver risk (DQ-17) is accepted as a general risk only (OD-30). A High-severity finding existed at TEVV (F-02 restricted-evidence read rule; fixed at Stage 27 with a placeholder note whose rule D-27-01 is still undecided). Severities are agent Inference (OD-33). Also open: 3 High vulnerabilities with owner and decision pending (`vulnerability-disposition.md`), SCN-11 and SCN-12 scans not run for lack of a tool.

### SH-3 What a receiver must NOT do without a recorded Dinesh decision [Verified Fact: HAR-01..HAR-17, OD-32]
Accept a risk; name a Zone H holder or stakeholder; activate a rule set; flip an authority switch; expose beyond loopback; switch the scheduler on; install CI under `.github/`; restore over live data; waive a failed release gate; make or simulate a disposition (`support-model.md` SM-2). "Default-answer authority" in OD-32 covers scope and sequencing only, **not** these.

### SH-4 Privacy and compliance framing [Verified Fact: OD-30]
GxP / 21 CFR Part 11 appear as **framing only**; no "compliant" claim may be made (GD-11). The privacy impact is rated Low for synthetic data only; **real data is not rated**, privacy regime and retention are undecided (hold-all retention, OD-S12-09; RS-06, RP-07). Field classes, tenant and regime must be decided before real data (DQ-S24 assumptions).

### SH-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SCF-01 | [Verified Fact] 0 of the 22 governance controls (GC-01..GC-22) and the security duties have an accepted owner; risk/security owner RL-05, compliance RL-06, privacy owner are VACANT | `security-ownership.md`; `accountability-map.md` | Security incidents route to Dinesh alone (ES-24 gap) | High (real use) | High | Who is RL-05? |
| SCF-02 | [Verified Fact] No external penetration test, no independent security review; static analysis and mutation gate only | `security-readiness.md` SR-2; RS-14 | Control effectiveness unproven externally | High before exposure | High | When, by whom |
| SCF-03 | [Verified Fact] Anchor seal and token expiry are off or optional by default; backups and anchor share one host (TF-07) | `security-readiness.md`; `tabletop-results.md` TF-07 | Host-level actor could alter chain and backups together | Medium | High | Decide seal and key custody before exposure |
| SCF-04 | [Verified Fact] Stage 27 behaviour changes are agent assumptions; the CI hardening workflow is not installed | OD-34 | Receiver may treat them as approved policy | Medium | High | D-27-01..09 |
| SCF-05 | [Inference] The system is safe today only because it is inert; the security case for any activation is not made | TF-03 | Activation without owners is unsafe | High on activation | High | Entry conditions for CUT-1 |
| SCF-06 | [Verified Fact] TEVV reviewer walkthroughs TST-REV-03/04/08 unsigned; a person must perform them | `docs/26-tevv/walkthrough-records.md` (header: UNSIGNED, RT-13 OPEN) | Hostile-text display and paging unverified by a human | Medium | High | Who signs |

## Evidence References
See `evidence_sources`; `docs/24-security-privacy/threat-model.md` (26 threats, 58 routes, 12 CLIs per `security-readiness.md` SR-1).

## Assumptions
- A-38-SH-1 Severities for security findings are agent Inference (OD-33). Confirm: RL-05 once named, else Dinesh.

## Unknowns
- U-38-SH-1 Applicable privacy/GxP regime; U-38-SH-2 real Zone H holders; U-38-SH-3 external threat landscape beyond the synthetic scope.

## Unresolved Issues
- SH-2 list; D-27-01..09; DQ-S24 residuals; walkthrough sign-off.

## Residual Risks
- RR-38-SH-1 Handing a receiver an apparently well-secured system whose risks are unaccepted may be read as assurance. High if misread; this document states the opposite.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 38). |
