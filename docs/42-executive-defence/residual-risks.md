---
stage: "42 — Executive Defence & Final Value Story"
artifact: "residual-risks.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/risk-acceptance-register.md", "docs/24-security-privacy/residual-security-risks.md", "docs/26-tevv/residual-tevv-risks.md", "docs/33-vendor-risk/vendor-risk-acceptance.md", "docs/40-scale/scale-risk-assessment.md", "docs/30-release/", "docs/35-variance/value-leakage-analysis.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** A consolidated view of what is still open at main b1de232. **Nothing in this document accepts a risk.** Acceptance requires Dinesh Naik's recorded decision (HAR-11). Severities from earlier stages are agent inference. I did not re-rate them; I grouped them and added the *value/defence* consequences. Individual register rows live in their source documents (not copied in full to avoid divergence).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### RR-1 Open registers (counts as recorded)
| Register | Open items | Accepted | Source |
|---|---|---|---|
| Release approvals | 40 records (22 required release approvals per the evaluator rule; the rest are cutover, behaviour and gate items) | 0 | `evidence/approvals-register.json` |
| Release technical criteria | 4 not passing (G1, T-09, T-10 fail; T-05 not run) | n/a | `go-no-go-criteria.md` |
| Behaviour deviations DV-01..DV-11 | 11 | 0 approved | `release-approvals.md` |
| Cutover steps CUT-1..CUT-5 | 5 | 0 decided | OD-37 |
| Governance RP-01..RP-12 | 12 | 0 | `risk-acceptance-register.md` |
| Security RS-01..RS-16 | 16 | 0 | `residual-security-risks.md` |
| TEVV RTR-01..RTR-15 | 15 | 0 | `residual-tevv-risks.md` |
| Vendor VA-01..VA-07 | 7 | 0 | `vendor-risk-acceptance.md` |
| Scale SR-01..SR-16 | 16 | 0 (proposed; routing decision SB-38) | `scale-risk-assessment.md` |
| Value leakage VL-01..VL-17 | 17 | 0 | `value-leakage-analysis.md` |
| Findings F-11 + 9 complex functions | 10 | 0 | OD-34 |
| Readiness checks (Stage 27) | 14 of 38 unmet | n/a | `production-readiness-checklist.md` |
| Resilience D-28-01..10, observability D-31-01..10, hardening D-27-01..09, drift D-39-01..09, metrics D-34-01..08 | ~46 decisions | 0 decided | OD-34..OD-36, Stage 39 |
| Stage 29 Q-29-01..09, C-1..C-7 | 16 | 0 | OD-35 |
| Stage 35 CA-01..CA-17; Stage 36 I-01..I-19, PC-1..PC-10 | 46 | 0 | OD-36 |
| Stage 37 vacant roles | all but Dinesh | 0 accepted owners of 28 assets | OD-34 |
Totals are not summed because the registers overlap; the point is that none has an acceptance beyond RA-01..RA-11.

### RR-2 Consolidated top residual risks (grouped, with a defence-relevant consequence)
| # | Risk | Source IDs | Likelihood / impact (agent rating where given) | Consequence for the value story |
|---|---|---|---|---|
| R1 | Release never happens, or happens without approvals being properly recorded | C-19 | H / H | No value; the project is a rehearsal |
| R2 | Single human decider and vacant owners | RP-01, RS-16, VL-06, VL-07 | H / H | Nobody can realise or defend value; decisions queue |
| R3 | Value never measured (no window, no time capture, unsigned baseline) | VL-11, VL-12, VL-13, D-34-02 | H / H | ROI stays NOT COMPUTABLE indefinitely |
| R4 | Human gate unexercised; first real use may reveal gaps | RP-09, RP-08 | H / M | Controls may not fit real reviewers; walkthroughs unsigned |
| R5 | Real data introduced before field classes, tenant, regime, retention decided | RS-06, RP-07, RP-04 | M / H (H if real) | Privacy / data-integrity exposure |
| R6 | Exposure beyond loopback without TLS, second factor, token expiry | RS-01, RS-02, RS-08, VR-03 | L (loopback) / H | Security incident on first exposure |
| R7 | Audit anchor weakness and no retention policy | RP-03, RP-04, RS-03 | L-M / M | Audit claims overread |
| R8 | Controls built but not wired; CI not installed | VL-04, VL-05, RP-05 | M / M | Protections absent at run time |
| R9 | Runtime: Python 3.10 end of life, no 3.12+ evidence | VR-02, RS-10, RT-14 | M / M | Production runtime untested |
| R10 | Misreading evidence (parity as improvement, synthetic as real, defaults as decisions) | SR-01, SR-02, SR-06, SR-07 | H / H | Executive over-reliance |
| R11 | Legacy estate retains control gaps while it runs; coexistence/double work | RP-11, VL-14 | H / M | Risk persists; time cost before time saving |
| R12 | Recovery unproven by people: tabletop without humans, no off-device backup, RTO/RPO are agent targets | C-17 | M / H | Recovery claims cannot be made |
| R13 | Regulatory overreach: "tamper-evident" read as "compliant" | RP-02 | M / M | Reputational and compliance exposure |
| R14 | Vendor concentration on build toolchain; AI assistants drive repo change | VA-01..VA-07, `agent-drift-metrics.md` | M / M | Untracked-change risk |
| R15 | Documentation drift and stale registers (Stage 25 v0.2, Stage 4 addendum, 40-scale baseline at ef72e4e) | LL-15 | M / L-M | Contradictory evidence at defence |
| R16 | Stages 38 and 41 absent: no handover or exit plan accepted | C-32 | M / M | No receiving team, no decommission path |

### RR-3 Risks that become blocking at specific events
| Event | Risks that become blocking |
|---|---|
| Any real data | R5, RS-06, RP-07, RP-04 |
| Any exposure beyond loopback | R6, RS-05, RS-07 |
| Any cutover step | DV decisions, R1, R4, R12, T-09, T-10, G1 |
| Any pilot with people | R2, R3, R4, walkthroughs, owners and responder |
| Any AI added | RS-15 and the RQ triggers |

## Evidence References
As per RR-1 sources; OD-30..OD-37; claims C-13, C-14, C-19, C-27, C-28, C-29.

## Assumptions
Likelihood/impact are those of the source stages (agent inference). The grouping into R1..R16 is mine [Inference].

## Unknowns
True likelihood of any risk in a real operating environment.

## Unresolved Issues
Routing of every item above (Stage 27/30/acceptance) is Dinesh's decision. The default assumed by the orchestrator in OD-33 was: High/Medium to Stage 27 hardening; that stage is complete and the remainder is open.

## Residual Risks
This file is itself a risk: a long list can obscure which few items block value. The blockers are R1-R4.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
