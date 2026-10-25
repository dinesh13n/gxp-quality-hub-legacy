---
stage: "42 — Executive Defence & Final Value Story"
artifact: "risk-control-summary.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/compliance-control-matrix.md", "docs/25-governance/risk-acceptance-register.md", "docs/24-security-privacy/residual-security-risks.md", "docs/23-human-control/", "docs/27-hardening/vulnerability-disposition.md", "docs/30-release/go-no-go-criteria.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** The control framework is real in code and tests, and consistently refuses by default. Its weakness is not mechanism but **operation**: the human gate has no holders, the audit anchor is an unsigned local file, monitoring has no delivery, owners are vacant, and **no risk register entry has been accepted beyond 11 scope/sequence acceptances**. Every residual-risk register is open. No GxP or Part 11 compliance is claimed (framing only) (C-12, C-13, C-28).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### RC-1 Control framework at a glance
| Layer | Control | State | Evidence | Class |
|---|---|---|---|---|
| Human control | Zone H single choke point (ZH-01..ZH-10), holder list, role dispositioner, fresh re-authentication, human session only; disposition mode `none` by default | Built and attacked: 80 of 80 attempts refused; mutants M1, M2 killed; **holders EMPTY, never exercised by a real holder** | `docs/23-human-control/`; `docs/26-tevv/tevv-release-gate.md` RT-10; OD-31 | [Verified Fact] |
| Authority | Authority switch (DW-17) via CLI + `approval_ref`; ships off; ZH-11 not adopted | Flip refused without reference (exit 2); rehearsed in sandbox; no flip in the repo | OD-26, OD-31; `docs/30-release/go-no-go-criteria.md` T-04 | [Verified Fact] |
| Audit | Hash-chained, insert-only; `verify-audit` | ok after concurrency, tamper detection, restore; exit-17 fix for malformed anchor line (S30-DEV-01, behaviour change awaiting Dinesh's acceptance) | Stage 26 RT-12; OD-37 | [Verified Fact] |
| Prevention of AI/egress | No-AI deny-list, egress guard, `model_calls_total = 0` | Tripwires zero | Stage 26 RT-05; Stage 30 G5 | [Verified Fact] |
| Input safety | Untrusted-content guard; planted-string suites (86/22/44) | 0 effects | G9; GC-13 | [Verified Fact] |
| Access | 6 roles, deny-by-default, 48-operation registry; rate limit 429 after 100 refusals/60 s (agent default) | 0 wrongly allowed in 138 allowed + 222 refused cells | `identity-rbac-hardening.md` | [Verified Fact] |
| Change control | Branch per stage, PR, orchestrator full regression, squash merge, OD log | Worked (caught four late defects) but **one human reviewer** | OD-13, OD-23; RP-01 | [Verified Fact] |
| Release | G1..G10 checklist, evaluator `hub.release`, 40-item approvals register | Evaluator returns NO-GO | `docs/30-release/` | [Verified Fact] |
| Rollback | L1, L2, L3 | Rehearsed on sandbox only | T-02..T-04 | [Verified Fact] (sandbox) |

The Stage 25 matrix (GC-01..GC-22) reported 12 PRESENT, 7 LIMITED, 3 ABSENT/PLANNED **before** Stages 23/24 merged; RP-10 requires it to be re-issued as v0.2. [Verified Fact] **That re-issue has not happened**, so the matrix understates later controls and must not be quoted as current without that caveat. Absent items then: second reviewer (GC-20), retention policy (GC-21).

### RC-2 Risks accepted vs open
| Register | Count | Accepted | Evidence |
|---|---|---|---|
| RA-01..RA-11 (Dinesh's scope/sequence acceptances) | 11 | 11 as scope/sequence choices; they carry conditions and are **not** risk acceptances of the open registers | `risk-acceptance-register.md` Part A |
| RP-01..RP-12 proposed | 12 | 0 | Part B; OD-30 |
| RS-01..RS-16 security | 16 | 0 (RS-16 single approver noted as accepted by Dinesh in OD-30 as a general risk, not as a Stage 24 acceptance) | `residual-security-risks.md` |
| VA-01..VA-07 vendor | 7 | 0 (proposed) | OD-33 |
| RTR-01..RTR-15 TEVV residuals | 15 | 0 | OD-33 |
| F-11 + 9 complex functions | 1 + 9 | 0 | OD-34 |
| RP/SR scale risks SR-01..SR-16 | 16 | 0 (proposed, routing = decision SB-38) | `scale-risk-assessment.md` |

### RC-3 Top risks to say out loud
1. **RP-01 / RS-16 single approver.** One human owns, measures, approves and signs. Self-review of walkthroughs is a separation-of-duties gap. Impact: every approval waits; independence is procedural only.
2. **RP-09 no Zone H holder.** The control that matters most for GxP (human disposition) is unexercised. Impact: blocks any pilot; safe by default.
3. **RP-08 / RP-12 / VL-10 unowned definitions and 11 unapproved behaviour differences.** Golden comparison is red by design; "closed" is still nobody's decision.
4. **RP-03 audit anchor weakness.** Tail records after the last anchor can be removed undetected; a compromised host can rewrite chain and anchor.
5. **RS-01/RS-02/RS-14 exposure.** No TLS, single factor, no penetration test. Safe only while loopback and synthetic.
6. **RP-11 legacy keeps its gaps** while it runs (no audit trail, weak hash, `0.0.0.0` bind in the legacy compose file).
7. **VR-02 Python 3.10 end of life** (interpreter reported at end of life around October 2026; the stage notes re-check). The floor remains 3.10 until Dinesh decides (D-27-02).
8. **Controls not wired** (Stage 28) and **CI not installed** (HAR-07): protection that exists on paper or in tests but not in the run path.
9. **RP-02 Part 11 over-reading.** "Tamper-evident" must never be read as "compliant".

### RC-4 High vulnerabilities (Stage 27)
VR-01 restricted note readable by reviewer: FIXED under an agent assumption (D-27-01 confirmation pending). VR-02 interpreter EOL: MITIGATED + ESCALATED. VR-03 no TLS: MITIGATED by refusing non-loopback binds. VR-04 legacy container files: DEFERRED to Stage 30, which did not run the release (still open; its High disposition criterion T-10 fails). None is ACCEPTED.

## Evidence References
`docs/25-governance/compliance-control-matrix.md`, `risk-acceptance-register.md`, `governance-readiness.md`; `docs/24-security-privacy/residual-security-risks.md`; `docs/27-hardening/vulnerability-disposition.md`; `docs/30-release/go-no-go-criteria.md`; OD-24..OD-37; claims C-12, C-13, C-14, C-19, C-27, C-28.

## Assumptions
All Stage 27/28/31 numeric defaults are agent assumptions (OD-32+). Severities are agent inference (OD-33).

## Unknowns
Real field classes, tenant model, privacy regime (DPDP/GDPR named, not assessed); retention policy; external audit expectations; effect of controls on real incidents.

## Unresolved Issues
Stage 25 v0.2 re-issue; DQ-17 second reviewer; D-27-01..09; walkthrough sign-off; HAR-07 CI install.

## Residual Risks
See `residual-risks.md` for the consolidated view.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
