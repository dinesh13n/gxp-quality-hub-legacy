---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "implemented-vs-deferred.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/17-implementation-prd/prioritized-capabilities.md", "docs/30-release/go-no-go-criteria.md", "docs/28-reliability/resilience-readiness.md", "docs/31-observability/", "docs/27-hardening/production-readiness-checklist.md", "hub/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
What exists as code, what exists only as documents, and what was deliberately left undone, with the switch state of the shipped defaults.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### ID-1 Implemented (built in shadow; not released) [Verified Fact]
- 10 capabilities CAP-01..CAP-10 (44 FRs Delivered, 3 Delivered + Deferred part, 4 Changed - see the matrix).
- Safety controls: Zone H gate, authority switch (OFF), decision flags with `approval_ref`, No-AI tripwires, loopback bind, hold-all retention, kill switch (`hub.kill`).
- Hardening (Stage 27), resilience modules (Stage 28), observability modules (Stage 31), release evaluator (Stage 30) - built, not wired.
- Documents for operations: runbook, incident/BCDR plan, handover pack (Stage 38), retirement plan (Stage 41), drift framework (Stage 39), scale roadmap (Stage 40), executive defence (Stage 42).

### ID-2 Deferred / not done [Verified Fact]
| # | Item | Why | Gate |
|---|---|---|---|
| DF-01 | FR-MET-08 case cost / rework | no cost source or owner (OPD-08) | decision + data |
| DF-02 | FR-INT-07 static build-failing check (AC-INT-23) | not built | P3 |
| DF-03 | FR-MET-05 D-EVID backlog | needs evidence check | P3 |
| DF-04 | FR-CO-04 / PNFR-18 / PNFR-19 CI wiring | `ci/hub-hardening.yml` not installed (HAR-07) | decision |
| DF-05 | FR-RUN-01 scheduling ON | OPD-11 / HAR-10; CUT-5 | decision |
| DF-06 | Wiring resilience and observability into shipped paths | D-28-01/02, D-31-01/02 | decision + build |
| DF-07 | Spec addenda for Stage 27 additions | D-27-05 | decision |
| DF-08 | Persisted metrics, alert delivery, on-call | D-31-01, D-31-08 | second human |
| DF-09 | Policy rule-derivation mode for facts (FR-DEC-06) | OD-S12-15 default | P3 |
| DF-10 | Off-device backup, live tabletop, timed restore drill | HAR-09, Q-29-01..09 | Dinesh |
| DF-11 | TLS, second factor, mandatory token expiry, external pen test | exposure decision | exposure |
| DF-12 | 3.12+ evidence for goldens; Node pin for CT-13 | D-27-02, D-39-05 | orchestrator + Dinesh |
| DF-13 | 44-string planted fixture | PCH-31 reword approved instead | optional |
| DF-14 | Stage 25 v0.2 re-issue; Stage 4 v0.2 addendum; Stage 34/35/36 v0.2 | needs real after-window or decision | later |
| DF-15 | 9 complex functions, F-11 | backlog | Stage 27 successor |
| DF-16 | Legacy Dockerfile/compose hardening | frozen path (D-27-06) | cutover |
| DF-17 | `as_of` parameter for hub metrics | D-34-03 | code change |
| DF-18 | Audited disable-principal operation | D-41-11 | spec addendum |
| DF-19 | Time/effort capture design (K-04, K-05, K-22 Unknown) | CA-06 | design |

### ID-3 Not executed (process, not code) [Verified Fact]
Release; cutover CUT-1..CUT-5; authority flip (rehearsed in sandbox only); tagging; CI install; Zone H holder naming; policy adoption; rule-set activation; retirement of any asset; handover to a receiver; operator exercises; benefits sign-off.

### ID-4 Switch state at the as-built baseline [Verified Fact; T-07 pass on shipped defaults]
| Switch | State |
|---|---|
| `zone_h.holders` | `[]` |
| `disposition.mode` | `none` |
| Policies adopted / rule set active | none / none |
| `schedule.enabled` | OFF (ZH-09 only) |
| `capability_authority.<cap>` | unset (authority = legacy) |
| `case_creation.enabled` | false |
| `search.enabled`, `search.fts`, `templates.enabled` | false / off / false |
| Source-contract binding | `record_only` |
| Network bind | 127.0.0.1, no TLS |
| Data | synthetic only |

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-12 [Assumption] The shipped-default posture (ID-4) is that evaluated by Stage 30 T-07 and unchanged since.

## Unknowns
- U-43-13 Whether any local, uncommitted configuration differs on the laptop.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
