---
stage: "29 — AI Incident Response + BC/DR"
artifact: "incident-severity-matrix.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/37-operating-model/escalation-model.md (EM-3)", "docs/23-human-control/escalation-matrix.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/24-security-privacy/threat-model.md", "docs/24-security-privacy/residual-security-risks.md", "docs/29-incident-bcdr/ai-incident-playbook.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Severity classification for incidents. It **keeps the three classes already proposed in Stage 37 (SEV-A, SEV-B, SEV-C)** rather than inventing a second scale, adds explicit classification criteria, up-classing rules and a lookup for every scenario IS-01..IS-12 and every product error code EH-01..EH-10. **No response or resolution time is given**: Stage 37 EM-3 said these are Unknown until a real service owner and users exist, and this stage does not contradict it. What is given instead is the **minimum authority to declare and to close**, which is knowable today.

## Findings
### SV-1 Classes and criteria
| Class | Meaning [Inference, from EM-3] | Classify here if ANY is true | Declared by | Closed by |
|---|---|---|---|---|
| SEV-A | Integrity, authority or regulated-act risk | (a) audit/decision chain break or anchor mismatch; (b) a Zone H action, disposition, QA release or e-signature was made, simulated as real, or automated (HAR-12, STOP-07); (c) real personal/patient/client data or real credentials found (STOP-04); (d) working-tree `data/` or the backup changed (STOP-01 mismatch); (e) an authority switch flipped or a holder added without a recorded human decision; (f) the only copy of baseline data or evidence lost; (g) an approval, stakeholder or datum was fabricated and relied on | Any rung may declare; IC confirms; Dinesh informed immediately | Dinesh Naik (L3), plus RL-05/RL-06 once staffed |
| SEV-B | Control degraded, or unapproved change of behaviour | (a) tripwire moved (model call, egress attempt, AI import); (b) release gate failed or was bypassed; (c) flag/config without `approval_ref`; (d) `authoritative` capability diverges from human decisions; (e) agent followed instruction-like text from data (STOP-05) without effect on state; (f) secret-like value in audit/log/commit but synthetic; (g) tool compromise suspected with no data movement; (h) evidence at risk (disk full, single copy exposed) | IC | L1 service owner (Dinesh INTERIM); any waiver is Dinesh only (HAR-14) |
| SEV-C | Operational defect with a safe default | run mismatch, late feed, search/UI defect, tool outage, test red with no state change | any rung | L1 |

### SV-2 Up-classing and down-classing rules (proposed)
1. If two classes seem to fit, take the higher.
2. A SEV-C that touches an audit record, a Zone H path, `data/` or a config key becomes at least SEV-B.
3. Real data of any kind turns the incident SEV-A regardless of the technical cause (the product is synthetic-only, `data_origin: synthetic`).
4. Down-classing needs a written reason in the incident record and Dinesh's agreement for SEV-A.
5. Because the product is inert (loopback, shadow, no consumers known), **impact ratings below assume that**. If the product is ever exposed, given real users or fed real data, every class is re-rated before the next incident, not during it.

### SV-3 Scenario lookup
| Scenario | Default | Rises to | Falls to |
|---|---|---|---|
| IS-01 prompt injection (hostile text) | SEV-C | SEV-B if an agent or person obeyed it; SEV-A if it led to a Zone H/data/approval act | stays SEV-C when stored and quarantined as untrusted |
| IS-02 unsafe action | SEV-B | SEV-A for disposition, Zone H, `data/` write, fabricated approval | none |
| IS-03 compromised tool | SEV-B | SEV-A if data or secrets left the device | SEV-C if only an outage |
| IS-04 data leakage | SEV-B | SEV-A if real data/credentials | none |
| IS-05 bad retrieval | SEV-C | SEV-B if a decision was taken on it | none |
| IS-06 model/provider failure | SEV-C | SEV-B if delivery of a gate-critical stage is blocked and evidence is at risk | none |
| IS-07 cost runaway | SEV-C | SEV-B if a tripwire moved | none |
| IS-08 corrupted configuration | SEV-B | SEV-A if authority switch/holder/approval_ref falsified | SEV-C if caught at start-up refusal with no run |
| IS-09 infrastructure outage | SEV-C | SEV-B if evidence/backup not yet copied | none |
| IS-10 disaster | SEV-A | n/a | SEV-B only if an independent intact copy is confirmed by checksum |
| IS-11 chain break | SEV-A | n/a | none until explained |
| IS-12 feed delay/divergence | SEV-C | SEV-B if totals differ and decisions already taken | none |

### SV-4 Product error code lookup (EH-01..EH-10)
| Code (exit/HTTP) | Meaning | Default class |
|---|---|---|
| E-SEC-AUDIT-TAMPER-DETECTED (17/409), E-DEC-CHAIN-BROKEN (25/409) | chain/anchor does not verify | SEV-A |
| E-GATE-NO-HOLDERS (19/423) | Zone H requested, no holder | SEV-C (SEV-B if repeated) |
| E-GATE-NOT-AUTHORISED (19/403) | non-holder/non-human tried Zone H | SEV-C first time; SEV-B repeated (EH-02) |
| E-CO-DENYLIST-IMPORT (9), E-CO-EGRESS-ATTEMPT (11), E-OBS-TRIPWIRE (14) | No-AI/egress tripwire | SEV-B |
| E-SEC-EXPOSURE-NOT-APPROVED (9) | non-loopback bind attempted | SEV-B |
| E-RUN-TOTALS-MISMATCH (29/500) | run totals do not reconcile | SEV-C |
| E-CFG-INVALID (2) with flag/approval message | decision flag without approval_ref | SEV-B |
| E-CO-RELEASE-BLOCKED (20), E-SEC-SECRET-IN-AUDIT (18) | release gate failed / secret in audit | SEV-B |
| E-HUB-KILLED (3) | kill switch set | not an incident (by design) |
| E-STORE-BACKUP-INVALID (21) | backup manifest/checksum fails | SEV-B (restore refused, nothing touched; observed in rehearsal step 10) |
Exit code 9 is shared by two codes (clash documented, OD-29); the text of the error distinguishes them [Verified Fact: EH-04/EH-05 both cite 9].

### SV-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SVF-01 | [Verified Fact] The only evidenced severity scale is Stage 37's three classes without times | `escalation-model.md` EM-3 | A time-based SLA cannot be set today | Low while inert | High | Who sets times when a service owner exists? |
| SVF-02 | [Inference] Agent-assigned severities for scenarios are judgements | this table | May be mis-rated | Medium | Medium | Dinesh review (A-29-SV-1) |
| SVF-03 | [Verified Fact] A SEV-A needs Dinesh to close and he is the only human rung | EM-1 | Single point of failure | High (real use) | High | DQ-17 acknowledged in OD-30 as a general risk |

## Evidence References
`docs/37-operating-model/escalation-model.md` EM-3; `docs/23-human-control/escalation-matrix.md` EH-01..EH-10; `stop-conditions.md`; `hub/security/errors.py`; rehearsal log `evidence/s29-log-10-restore-corrupt-backup.txt`.

## Assumptions
- A-29-SV-1 [Assumption] The classification criteria and lookup are agent proposals under OD-32. Confirm: Engagement lead (Dinesh Naik).
- A-29-SV-2 [Assumption] No time targets are set until a real service owner and users exist (consistent with Stage 37 U-37-EM-2).

## Unknowns
- U-29-SV-1 Real response/resolution expectations (U-02-13).
- U-29-SV-2 Any regulatory notification clock (compliance regime Unknown, RS-06).

## Unresolved Issues
- Exit code 9 clash; response times; who is RL-05/RL-06 to co-close SEV-A.

## Residual Risks
- RR-29-SV-1 Mis-classification with no second reviewer (Medium).
- RR-29-SV-2 No time dimension means no escalation timer; a stalled SEV-A has no forcing function (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
