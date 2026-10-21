---
stage: "25 — Governance + Compliance + Assurance"
artifact: "system-card.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/17-implementation-prd/{implementation-prd,finalized-nfrs,release-boundaries,prioritized-capabilities}.md", "docs/16-repo-validation/{repo-quality-gate,behavior-difference-report,security-scan-summary,validation-signoff}.md", "docs/20-application/{application-component-map,application-readiness,application-test-summary,deterministic-ai-boundary,access-control-implementation}.md", "docs/21-integration/integration-readiness.md", "docs/10-architecture/{target-architecture,component-model,security-architecture}.md", "docs/12-specs/security-spec.md", "docs/14-transformation/feature-flag-plan.md", "docs/09-initial-prd/{non-goals,product-risks}.md", ".fde/orchestrator-decisions.md (OD-08, OD-09, OD-16, OD-17, OD-22, OD-24, OD-27, OD-28)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Every number is from synthetic data (FX-BASE125, 125 cases, seed 4100, OD-09) or a sandbox and is not a production measure. The system is in shadow beside the untouched legacy estate and has no users except the Engagement lead on sandbox copies (OD-03a, OD-04). This card describes the system as evidenced at the end of Stage 21 (main f4c38f8 plus OD-29); Stage 23 and 24 changes are not reflected. Owner: Engagement lead (Dinesh Naik).**

## Summary
The **GxP Quality Hub ("hub")** is a stdlib-only Python package (`hub/`) that records, beside the legacy batch-deviation / CAPA estate, an attributable decision record, an intake and reconcile pipeline with quarantine, a rule service, metrics with declared definitions, a loopback HTTP and CLI surface, and a reviewer workspace. It does **not** decide anything consequential: batch disposition, QA release, e-signature, rule activation, policy adoption and scheduling are human-only Zone H actions with **no holder configured**, and the product contains **no AI**. It is intended as a modernisation baseline for a synthetic training scenario, **not compliance certification** (`docs/domain-assurance.md`).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SC-1 Identity and purpose
| Field | Value | Tag |
|---|---|---|
| Name / version | GxP Quality Hub, shadow implementation baseline (RB-0); artifact version v0.1 | [Verified Fact] |
| Purpose | one attributable record of each batch-deviation / CAPA case and its decisions; safe handling of external case information; figures that declare their definitions; batch disposition stays human; No-AI (PRD-1..PRD-9, OD-08) | [Verified Fact] |
| Intended users | operations reviewers, quality lead, compliance, dispositioner, integration, admin (6 roles, `security-spec.md` SEC-2); derived from documentary personas, not observed users (A-12-SEC-1) | [Verified Fact] roles; users none |
| Out of scope (never) | AI / LLM / ML / agentic capability (NG-01); making, pre-filling or automating disposition, QA release or e-signature (NG-02); choosing a definition, clock, threshold or sufficiency rule for the organisation (NG-03); auto-closing cases or guessing links (NG-04); real data, people or systems in this engagement (NG-09); Part 11 / GxP certification target (NG-06) | [Verified Fact] |
| Deployment | single host, loopback 127.0.0.1, stdlib `ThreadingHTTPServer`; no TLS; no Docker; production target Python 3.12+, code floor 3.10 / SQLite 3.37 (OD-24) | [Verified Fact] |

### SC-2 Components and boundaries
| Area | Packages (`hub/`) | Role in governance | Tag |
|---|---|---|---|
| Decision record and audit | `decision`, `security/audit.py`, `store` | attributable, insert-only, hash-chained | [Verified Fact] |
| Human gate | `gate`, `security/zone_h.py`, `security/authz.py` | Zone H choke point ZH-01..ZH-10 | [Verified Fact] |
| Rules and policy | `policy` | inactive candidate rule sets; adoption and activation via Zone H | [Verified Fact] |
| Intake and integration | `intake`, `adapters`, `crosswalk` | read-only adapters, quarantine, identity key (partner, record_kind, ref_id, source_ts), per-source contract binding `record_only` | [Verified Fact] |
| Runs and metrics | `runs`, `metrics`, `obs` | run records, metrics with definition tags; schedule OFF | [Verified Fact] |
| Reviewer and search | `review`, `search`, `web`, `r2` | rule traces, overrides with reason; search / FTS / templates built dark | [Verified Fact] |
| Change safety | `coexistence`, `golden`, `ops`, `guards` | deviation register, golden-compare, release checklist G1-G10, No-AI guard | [Verified Fact] |
| Legacy | `app`, `legacy_batch`, `services`, `ops`, `integration`, `legacy_js` | unchanged since `baseline-as-found` (a6eb4e8); read-only to the hub | [Verified Fact] |

### SC-3 Shipped state of every consequential switch
| Switch | Shipped value | What it prevents | Decision that can change it |
|---|---|---|---|
| `zone_h.holders` | `[]` | every Zone H action (HTTP 423, `E-GATE-NO-HOLDERS`) | OD-S12-06 |
| `disposition.mode` | `none` | any disposition record | OD-S12-05 + HAR-12 |
| active rule set | none | any rule evaluation without an explicit ruleset ref | OD-S12-04 + HAR-06 |
| policy adoption / definitions | none adopted | metric verdicts (`not_available_no_adopted_policy`) | OD-S12-01 / -02 |
| `schedule.enabled` | `false` | unattended runs | OD-S12-10 / HAR-10 |
| contract bindings | `record_only` | quarantine by contract | OD-S12-11 (kept, OD-28) |
| `network.bind` / `exposure_approved` | 127.0.0.1 / false (non-loopback refused even if approved) | remote access | HAR-05, Stage 23-25 |
| `case_creation.enabled` | `false` | creating non-legacy cases | OD-S12-19 |
| `search.enabled`, `search.fts`, `templates.enabled` | off | document search, drafts | OPD-12, PCH-22 |
| `data_origin` | `synthetic` | production data | HAR-15 |
Source: SS-02, `release-boundaries.md` RB-0. [Verified Fact]

### SC-4 Human oversight
- **Zone H (human only):** batch disposition, QA release, e-signature record, close-exception, policy adopt / withdraw, rule-set activation, exception-rule accept, disposition-mode change, schedule enable, policy change. Service identities, the scheduler and importers are rejected at the gate; re-authentication and (for ZH-01..03) a current `pack_hash` are required; every attempt is audited. [Verified Fact] (`api-contracts.md` OP-GATE-02; AC-GATE-09)
- **Reviewer actions:** override / dismiss / refuse flags need a reason; rule outputs show a rule trace once a trace has been produced (PNFR-15 partly: traces only after `record-trace` or the Stage 20 producer; human walkthroughs open until Stage 26). [Verified Fact]
- **What the system never does:** infer a closure, guess a link, auto-close a case, or recommend a disposition. [Verified Fact] (NG-02, NG-04)

### SC-5 Evaluation evidence and its limits
| Evidence | Result | Limit | Tag |
|---|---|---|---|
| Acceptance suite (241 planned tests; hub regression 419 methods, executed = expected, OD-27) | pass in sandbox / orchestrator regression | synthetic data; no production telemetry; PNFR-01..05 are mechanisms, not measures | [Verified Fact] |
| Legacy characterisation | 134/134 checks on the reference runtime (Python 3.10.12), 6 runs | goldens are runtime-specific: 10 of 16 CTs differ on 3.13 by environment only (IA-12) | [Verified Fact] |
| Behaviour comparison | D5 (unexplained) = 0; D3 approved = 0; D4 proposed = 9 registered + 2 explained (DV-01..DV-11) | none approved; golden-compare exits 6 by design | [Verified Fact] |
| Mutation gates | hub 8 of 10 killed (H3 header values and H5 non-loopback bind survived); legacy 15 of 15; Stage 20 gate | survivors close under DW-14 / DW-15 at Stage 23 | [Verified Fact] |
| Security scan | no HIGH in `hub/`; 41 bandit findings triaged (35 B608 constant SQL fragments); 1 deliberate fixture secret hit, 0 real | TLS absent; control values unvalidated | [Verified Fact] |
| Manual reviewer walkthroughs TST-REV-03/04/08 | open (automated stand-ins only) | OD-24: until Stage 26 | [Verified Fact] |

### SC-6 Known limitations and risks (not exhaustive)
1. Not compliant and not claimed compliant with anything (GAP-13-22); "tamper-evident" is framing, anchor is an unsigned local file (RTD-29).
2. Behaviour differs from legacy in 11 registered ways, none approved (DV-01..DV-11); cutover steps CUT-1..CUT-5 cannot start (RB-4).
3. No CI gate: control tests run only when someone runs them (RTD-01/02/14).
4. No retention policy: hold-all, unbounded growth (RTD-30).
5. Eight migration directories with seven version tables (IA-06); package cycles and 10 over-complex functions remain as debt until Stage 27 (OD-27).
6. Security hardening incomplete: TLS, header-value assertions, bind-refusal test, cookie flags, anchor strength (Stage 23 / 24).
7. Reproducibility depends on the Python 3.10.12 / SQLite 3.37.2 reference runtime for legacy goldens.
8. Figures are synthetic and unvalidated (K-04 / K-05 unmeasurable, OD-07).

### SC-7 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SY-F1 | [Verified Fact] Every consequential capability ships in its safe state, so the system can be reviewed without any decision having been made | SC-3 | Governance risk of premature activation is low | Low | High | — |
| SY-F2 | [Verified Fact] The system cannot be used for its main purpose (human disposition) until a holder and a mode are named | OD-17; ADR-006 | No pilot possible | Medium (value) | High | OD-S12-05/06 |
| SY-F3 | [Inference] The card's accuracy depends on Stages 23 and 24, which change tests, schemas, flags and security values; it must be re-issued at their merge | `delivery-backlog.md` DW-13..DW-19 | v0.1 may be stale within days | Medium | High | re-issue trigger |

## Evidence References
See `evidence_sources`. Item-level index: `audit-evidence-index.md`.

## Assumptions
- A-25-SC-1 [Assumption] The shipped defaults listed in SC-3 are unchanged on `main` after Stage 21 (read from Stage 16 / 17 / 20 / 21 documents; `hub/security/settings.py` DEFAULTS was seen for the network block only). Confirm: orchestrator regression and Stage 26.
- A-25-SC-2 [Assumption] The six roles are sufficient for a real organisation (A-12-SEC-1).

## Unknowns
- U-25-SC-1 Behaviour on real data or at real volume.
- U-25-SC-2 Real holder identities and user population.
- U-25-SC-3 Consumers of the 13 hub outputs outside the repo (OD-28: Unknown).

## Unresolved Issues
- Re-issue after Stage 23 and Stage 24 merge; OD-S12-05/06; DQ-09.

## Residual Risks
- RR-SC-1 Reader over-reads "all tests pass" as production readiness: High if unlabelled; the card repeats the synthetic label and the limits above.
- RR-SC-2 Shadow-mode value is unproven: no user, no real data.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
