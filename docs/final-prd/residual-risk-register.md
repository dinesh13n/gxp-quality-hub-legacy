---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "residual-risk-register.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/risk-acceptance-register.md", "docs/24-security-privacy/residual-security-risks.md", "docs/26-tevv/residual-tevv-risks.md", "docs/33-vendor-risk/vendor-risk-acceptance.md", "docs/42-executive-defence/residual-risks.md", "docs/27-hardening/vulnerability-disposition.md", "docs/40-scale/scale-risk-assessment.md", "docs/38-handover/open-handover-items.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
One index of every open risk register at main 08add05. None is accepted by this stage. Eighteen grouped top risks (R1-R18) update Stage 42's list for the OD-38 changes (Stages 38 and 41 now exist, both BLOCKED).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RR-1 Position [Verified Fact]
**Nothing in this register is accepted by this document.** The only acceptances on record are RA-01..RA-11 (Dinesh, scope/sequence decisions, `docs/25-governance/risk-acceptance-register.md`) and the general single-approver acceptance in OD-30 (RS-16, RP-01). Severities are agent inference (OD-33). OD-32's default-answer authority never accepted a risk. Individual rows live in their source registers; they are listed here by ID so that the FINAL baseline has one index.

### RR-2 Open registers
| Register | IDs | Open | Accepted | Source |
|---|---|---|---|---|
| Release approvals | AP-REL-01, AP-GATE-G1..G10, AP-DV-01..11, AP-CUT-1..5, AP-OPS-01..13 | 40 | 0 | `docs/30-release/evidence/approvals-register.json` |
| Release technical criteria not passing | G1, T-09, T-10 fail; T-05 not run | 4 | n/a | go-no-go-criteria |
| Governance | RP-01..RP-12 | 12 | 0 | risk-acceptance-register |
| Security residual | RS-01..RS-16 | 16 | 0 (RS-16 general acceptance OD-30) | residual-security-risks |
| TEVV residual | RTR-01..RTR-15 | 15 | 0 | residual-tevv-risks |
| Vendor | VA-01..VA-07 | 7 PROPOSED | 0 | vendor-risk-acceptance |
| Vulnerabilities (High) | VR-02, VR-03, VR-04 | 3 | 0 | vulnerability-disposition |
| Findings | F-11 and 9 functions over complexity 15; F-29-02..16; F-31-01..07 | per source | 0 | OD-34..OD-36 |
| Surviving mutants (Stage 26) | M5, M9, M10 (killed in Stage 27 per its gate) | 0 current per Stage 27 | n/a | tevv-results; hardening-plan |
| Scale | SR-01..SR-16 | 16 proposed | 0 | scale-risk-assessment |
| Value leakage | VL-01..VL-17 | 17 | 0 | value-leakage-analysis |
| Handover | HO-01..HO-21 | 21 | n/a | open-handover-items |
| Retirement | D-41-01..16 and RL gates | 16 | n/a | retirement docs |
| Stage 9 product risks | PR-xx | per source | per source | `docs/09-initial-prd/product-risks.md` |
Totals are not summed: registers overlap.

### RR-3 Consolidated top risks (grouped; from Stage 42 RR-2, re-checked against OD-38)
| # | Risk | Source IDs | Likelihood / impact (agent) | Consequence | Status |
|---|---|---|---|---|---|
| R1 | Release never happens, or happens without approvals properly recorded | AP-*, C-19 | H / H | No value; project is a rehearsal | OPEN |
| R2 | Single human decider; vacant owners | RP-01, RS-16, VL-06/07 | H / H | Nobody can realise or defend value | OPEN |
| R3 | Value never measured (no window, no time capture, unsigned baseline) | VL-11..13, D-34-02 | H / H | ROI stays NOT COMPUTABLE | OPEN |
| R4 | Human gate unexercised | RP-09, RP-08 | H / M | Controls may not fit real reviewers | OPEN |
| R5 | Real data before classes, tenant, regime, retention are decided | RS-06, RP-07, RP-04 | M / H if real | Privacy / integrity exposure | OPEN |
| R6 | Exposure beyond loopback without TLS, 2FA, token expiry | RS-01, RS-02, RS-08, VR-03 | L (loopback) / H | Security incident on first exposure | OPEN |
| R7 | Audit anchor weakness; no retention policy | RP-03, RP-04, RS-03 | L-M / M | Audit claims overread | OPEN |
| R8 | Controls built but not wired; CI not installed | VL-04/05, RP-05, D-28-*, D-31-* | M / M | Protections absent at run time | OPEN |
| R9 | Python 3.10 EOL; no 3.12+ evidence | VR-02, RS-10, RT-14 | M / M | Production runtime untested | OPEN |
| R10 | Misreading evidence (parity as improvement, synthetic as real, defaults as decisions, built as delivered) | SR-01, SR-02, SR-06, SR-07 | H / H | Over-reliance | OPEN |
| R11 | Legacy retains control gaps; double work | RP-11, VL-14 | H / M | Risk persists | OPEN |
| R12 | Recovery unproven by people | Stage 29 F-29-02..16 | M / H | Recovery claims impossible | OPEN |
| R13 | 'Tamper-evident' read as 'compliant' | RP-02 | M / M | Compliance exposure | OPEN |
| R14 | Vendor concentration on build toolchain | VA-01..07 | M / M | Untracked-change risk | OPEN |
| R15 | Documentation drift and stale registers | RP-10, AB-1..AB-14 | M / L-M | Contradictory evidence | OPEN (this PRD reduces, does not remove) |
| R16 | Handover and retirement BLOCKED: no receiving team, no legal-hold determination | HO-01..03, D-41-10 | H / M | No operating owner; nothing may be deleted | OPEN (supersedes Stage 42's 'Stages 38/41 absent') |
| R17 | Sequencing deviation: Stages 39/40 merged before 38; FINAL produced before release and handover | HO-18 | M / L | Reader may think lifecycle completed | OPEN, Dinesh to rule |
| R18 | PRD read as an acceptance record | this document | M / H | False assurance | Mitigated by header label and sign-off OPEN |

### RR-4 Risks that become blocking at an event
| Event | Blocking risks |
|---|---|
| Any real data | R5, RS-06, RP-07, RP-04, D-41-10 |
| Any exposure beyond loopback | R6, RS-05, RS-07, VR-03 |
| Any cutover step | DV decisions, R1, R4, R12, T-09, T-10, G1 |
| Any pilot with people | R2, R3, R4, walkthroughs, owners and responder |
| Any retirement/deletion | legal-hold check, hold-all, D-41-* |
| Any AI added | RS-15 and RQ-1..RQ-3 |

### RR-5 Residual security risks RS-01..RS-16 (one line each) [Verified Fact]
RS-01 no TLS; RS-02 single-factor passwords; RS-03 anchor same host, unsealed by default; RS-04 no per-source rate limiting (Stage 27 added a refusal limiter, assumption); RS-05 finance read path unreachable; RS-06 field classes/tenant/privacy regime unknown; RS-07 login CSRF; RS-08 service-token expiry optional; RS-09 `?reason=` in URL; RS-10 Python 3.10 / SQLite 3.37 EOL; RS-11 legacy defects; RS-12 `schema_migrations` trigger (added Stage 27) and mutable `case_state`/`active_ruleset`; RS-13 hand-written HTTP/auth code; RS-14 static analysis only, no pen test; RS-15 AI added later without re-qualification; RS-16 single approver.

### RR-6 Governance risks RP-01..RP-12 (title) [Verified Fact]
RP-01 single approver; RP-02 Part 11 framing; RP-03 audit anchor unsigned; RP-04 no retention policy; RP-05 no CI gate; RP-06 hardening gaps (header values, non-loopback refusal; H3/H5 killed at Stage 23); RP-07 privacy regime not assessed; RP-08 11 deviations unapproved; RP-09 no Zone H holder; RP-10 Stage 25 pre-dates Stage 23/24; RP-11 legacy control gaps; RP-12 definitions and 48 h clock unowned.

### RR-7 TEVV and vendor [Verified Fact]
RTR-01 restricted note readable (fixed Stage 27, rule D-27-01 open); RTR-02/03/04/05 fixed or closed in Stage 27; RTR-06 backlog; RTR-07 walkthroughs unsigned; RTR-08 no 3.12+; RTR-09 full regression at final HEAD; RTR-10 CT-13 Node drift; RTR-11 host-level audit rewrite; RTR-12 unauthenticated audit growth; RTR-13..15 method limits. VA-01 runtime EOL; VA-02 code host private/2FA/second mirror; VA-03 AI assistant and workspace terms; VA-04 two-key setup/CI parity; VA-05 hosting/real data/SSO deferred; VA-06 SHA pins; VA-07 No-AI deny-list as release gate. All PROPOSED.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- Likelihood / impact are those of the source stages (agent inference).

## Unknowns
- True likelihood in a real environment.

## Unresolved Issues
- Routing of every item (accept / fix / defer) is Dinesh's: AP-OPS-11, D-39-09, PC-10, CA-14.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
