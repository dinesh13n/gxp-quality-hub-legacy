---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-capability-map.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/capability-map.md", "docs/17-implementation-prd/prioritized-capabilities.md", "hub/ (package layout at main 08add05)", "docs/23-human-control/approval-gates.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
Ten capabilities, all built in shadow, none authoritative, none released. Switch state (everything consequential OFF) is shown per capability.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CM-1 Capability state (CAP-01..CAP-10)
| Cap | Capability | Layer | FRs R1/R2 | Hub packages | As-built state (shadow) | Switch state / what is OFF | Tag |
|---|---|---|---|---|---|---|---|
| CAP-01 | Decision & evidence record | record | 6/0 | `hub/decision` | Insert-only events, per-case hash chain, projection, evidence refs, human-only facts; 125 cases backfilled read-only; no case-creation path | `case_creation.enabled` false; closure policy not adopted; `workflow.transition_table` structural | [Verified Fact] |
| CAP-02 | Human disposition gate (Zone H) | trust | 6/0 | `hub/gate`, `hub/control` | Single holder rule; ZH-01..ZH-10 actions; evidence pack; override with reason; approval-gated authority switch (BX-01) | `zone_h.holders` `[]`; `disposition.mode` `none`; no `capability_authority.*` set | [Verified Fact] |
| CAP-03 | Policy, definitions & rule service | meaning | 5/1 | `hub/policy` | Versioned policy objects, clocks, 3 as-found rule sets loaded inactive, withdrawal (Stage 20), divergence report (R2) | No policy adopted, no active rule set | [Verified Fact] |
| CAP-04 | Safe intake & exceptions | flow | 7/1 | `hub/intake`, `hub/adapters` | Append-only raw intake, natural-key replay safety, quarantine, reason codes, untrusted-text guard | Contracts `record_only`; gateway not wired to resilience controls | [Verified Fact] |
| CAP-05 | Shared identity & crosswalk | record | 2/2 | `hub/crosswalk` | 168 exact-key links; human links as events; consistency check and joined view (R2) | R2 items dark; no CONSISTENCY policy | [Verified Fact] |
| CAP-06 | Scheduled runs & run records | flow | 3/0 | `hub/runs` | Manual authorised trigger, run records, cap/backlog/checkpoint | Schedule OFF (ZH-09 only) | [Verified Fact] |
| CAP-07 | Metrics with declared definitions | meaning | 6/2 | `hub/metrics` | Tagged figures, cut-off required, exact decimals, per-clock median/p90 (null on baseline) | Verdicts `not_available_no_adopted_policy`; FR-MET-08 not built | [Verified Fact] |
| CAP-08 | Reviewer support | meaning | 2/2 | `hub/review`, `hub/search`, `hub/r2` | Exception queue, rule-trace text, produce-traces command; keyword/FTS search and templates built dark | `search.enabled` false, `search.fts` off, `templates.enabled` false | [Verified Fact] |
| CAP-09 | Access control, audit & data protection | trust | 2/1 | `hub/security`, `hub/admin`, `hub/web` | Deny-by-default 48-route registry, PBKDF2 login, CSRF, lockout, hash-chained audit, field classes (R2), loopback bind | No TLS; loopback only; anchor seal opt-in | [Verified Fact] |
| CAP-10 | Coexistence & change safety | constraint | 4/0 | `hub/coexistence`, `hub/golden`, `hub/guards`, `tests/characterization/` | Characterisation harness, deviation register DV-01..DV-11 (proposed), No-AI guards, rollback rehearsals | Golden-compare exits 6 by design; no CI | [Verified Fact] |

Capabilities added after Stage 9 (not CAPs): resilience (`hub/resilience`), observability (`hub/obs`), release evaluator (`hub/release`), approval-gated control flags (`hub/control`), operations helpers (`hub/ops`). [Verified Fact] none is wired into a shipped command path except as stated in `as-built-architecture.md` AB-AR-4.

### CM-2 Capability by state summary
[Verified Fact] All 10 capabilities exist in the shadow build. [Verified Fact] **None is authoritative**: legacy remains authoritative for every business output (CUT-1..CUT-5 undecided, Stage 30 BLOCKED). [Inference] A capability's value is unproven: no production use, no principal, K-21 = 0 of 125.

### CM-3 Out of scope / non-goals that still stand
[Verified Fact] No AI/LLM/ML (OD-08, FR-CO-04, NG-01..NG-04); no change or retirement of the parallel workflow for older customers (FR-CO-02); no auto-disposition, release or e-signature (FR-GATE-01); no deletion/retention purge (hold-all, OD-15); no real data; no exposure beyond loopback.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-03 [Assumption] Package-to-capability mapping follows Stage 17 PC evidence refs. Confirm: Engagement lead.

## Unknowns
- U-43-03 Which capability, if any, a real consumer would use first (consumers of the 13 legacy outputs Unknown, OD-28).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
