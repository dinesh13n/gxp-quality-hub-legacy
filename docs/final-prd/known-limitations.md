---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "known-limitations.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/17-implementation-prd/", "docs/24-security-privacy/residual-security-risks.md", "docs/25-governance/risk-acceptance-register.md", "docs/42-executive-defence/residual-risks.md", "docs/37-operating-model/", "docs/29-incident-bcdr/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
Twenty-four limitations, each traced to evidence, that a reader must know before relying on the as-built hub for anything beyond a synthetic shadow demonstration.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### KL-1 Known limitations (each with impact and confidence)
| ID | Limitation | Impact | Evidence | Confidence |
|---|---|---|---|---|
| KL-01 | Everything is synthetic; the problem is documented at repo level only, not in an organisation | No claim of real-world effect | OD-04; C-01, C-02 | High |
| KL-02 | Hub not in production, 0 users, 0 principals; no after-window | Value, adoption, KPIs improvement all unmeasurable | K-21 = 0 of 125 | High |
| KL-03 | No Zone H holder: human gate never exercised by a real person | Control effectiveness unproven | RP-09 | High |
| KL-04 | No policy adopted, no rule set active; verdicts `not_available_no_adopted_policy`; time to close `null` | Hub cannot produce a KPI verdict | PCH-17 | High |
| KL-05 | 11 behaviour deviations DV-01..DV-11 unapproved; golden-compare exits 6 | Release criterion G1 fails; cutover cannot start | gate-results G1 | High |
| KL-06 | Intake matching is exact-key; 7,903 partner items UNMATCHED_REF on shipped data; contract fails 3 of 4 sources | Reviewer queue dominated by exceptions on shipped data | PCH-06; OD-28 | High (synthetic) |
| KL-07 | Imported cases' as-of history is a proxy; legacy events not imported | Past-state reconstruction approximate for 125 cases | PCH-12 | High |
| KL-08 | Month-end figure differs from legacy report by 120,130.17 (742,956.61 vs 622,826.44) | Needs a human preserve-or-fix decision | DV-01 | High (arithmetic by me: 742,956.61 - 622,826.44) |
| KL-09 | JS partial-year match and 'abc'/null coercion not reproduced | Two as-found behaviours changed | DV-05, DV-11 | High |
| KL-10 | No TLS, single-factor auth, loopback only, no external pen test | Not safe to expose | RS-01, RS-02, RS-14 | High |
| KL-11 | Audit anchor unsigned local file by default; tail truncation after last anchor undetectable | 'Tamper-evident' limited | RP-03 | High |
| KL-12 | Retention hold-all, unbounded growth, no disposal authority | Storage growth; privacy tension | RP-04; D-41-06 | High |
| KL-13 | Resilience and observability built but not wired; 6 metrics unexported; no alerting | Failure/outage would not be detected automatically | OD-35, OD-36; T-09 | High |
| KL-14 | Python 3.10 floor (end of life); no 3.12+ golden evidence; CT-13 Node drift | Runtime risk before any exposure | VR-02; RTR-08 | Medium (EOL date recalled) |
| KL-15 | Single approver, all roles but Dinesh VACANT; 0 of 28 assets with accepted owner | No steady-state operation | Stage 37 | High |
| KL-16 | Recovery: single device, no off-device copy, tabletop with no humans, RTO/RPO agent targets | Recovery claims cannot be made | Stage 29 | High |
| KL-17 | R2 features dark; search ranking quality unassessed; FTS5 on target Unknown | R2 value unknown | RTD-79/80 | Medium |
| KL-18 | Two HTTP entry points; seven migration runners | Operational complexity | S16-D03/D05 | High |
| KL-19 | Agent-assumed defaults (Stage 24, 27, 28, 31 numbers; Stage 27 behaviours) not approved | 'Defaults' may differ from what Dinesh wants | OD-32..OD-36 | High |
| KL-20 | Stage 4 KPI sheet frozen-provisional; A-04-01 refuted; K-10 compares unrelated populations | Baseline contestable | OD-07; CC-5 | High |
| KL-21 | Legacy estate keeps its control gaps while it runs (no audit trail, no enforced gate, weak hash, 0.0.0.0 bind in compose) | Risk persists until cutover | RP-11 | High |
| KL-22 | Part 11 / GxP: framing only | No compliance claim | GD-11 | High |
| KL-23 | Build process defects were caught late by the orchestrator regression (S21-DEV-02, S24-DEV-05, S28-DEV-08, S31-DEV-08) | Process, not product, risk; regression is manual | C-31 | High |
| KL-24 | The nightly file exchange owner ('transferred 2024') and the parallel workflow CO-WF-01 owner are unnamed | Protected assets with no owner | PA-25, PA-26 | High |

### KL-2 Documentation limitations
[Verified Fact] Stage 25 matrix (v0.1) predates Stage 23/24 (RP-10). Stage 40 roadmap baseline is main ef72e4e. Stage 42 index is at b1de232 and states that Stages 38/41 do not exist (superseded by OD-38). Stage 34/35/36 are the sandbox editions (v0.1).

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- Confidence ratings are mine; ratings of source risks are agent inference (OD-33).

## Unknowns
- U-43-14 Limitations that only a real operating environment would reveal.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
