---
stage: "14 — Transformation / Migration Plan"
artifact: "feature-flag-plan.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/contracts/schemas/hub-config.schema.json (keys: zone_h.holders, disposition.mode, closure.unconfigured_behaviour, schedule.enabled, contract_bindings, network.bind/exposure_approved, audit.anchor_path, data_origin)", "docs/12-specs/spec-readiness.md RD-3 (OD-S12-xx defaults), RD-4 (blocked actions)", "docs/12-specs/features/f10-coexistence-change-safety.md (G1..G10, BEH-CO-02)", "docs/10-architecture/adrs/ADR-006, ADR-007, ADR-010, ADR-015, ADR-018", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md (HAR-05/06/10/11/12)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
The hub uses **configuration-driven flags** (stdlib, validated against `hub-config.schema.json`), not a flag service (ADR-015/018: single host, no dependencies). Flags serve three purposes: (1) **decision flags** — every open Dinesh decision (OD-S12-xx) is a config value whose shipped default is the *safe, non-adopting* option from RD-3, so code can be built before the decision; (2) **exposure flags** — shadow vs authoritative per capability for cutover; (3) **kill switches**. Flipping any decision or authority flag away from its default is a **human approval (HAR-11, and HAR-06/10/12 where applicable) recorded with an approval_ref**; the hub refuses non-default values whose `approval_ref` is empty. Legacy code has no flags and gets none (CR-1).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### FF-1 Flag register
| Flag (config key) | Values | Shipped default | Decision / approval to change | Introduced | Removal criterion | Tag |
|---|---|---|---|---|---|---|
| `disposition.mode` | none / event / external_ref | **none** | OD-S12-05 + HAR-12 | INC-08 | never (permanent policy) | [Verified Fact] schema + RD-3 |
| `zone_h.holders` | list | **[]** | OD-S12-06 + HAR-11 | INC-03 (C2) / INC-08 (C5) | permanent config | [Verified Fact] |
| `closure.unconfigured_behaviour` | treat_label_CLOSED_as_closing / none | **treat_label_CLOSED_as_closing** | OD-S12-03 | INC-05 | when a closure policy is adopted (OD-S12-01) | [Verified Fact] |
| `schedule.enabled` | bool | **false** | OD-S12-10 (HAR-10 interpretation) | INC-07 | permanent | [Verified Fact] |
| `contract_bindings[].mode` | record_only / enforce (per source) | **record_only** | OD-S12-11 | INC-06 | permanent per-source | [Verified Fact] RD-3; key shape [Inference] |
| `network.bind` + `network.exposure_approved` + `exposure_approval_ref` | 127.0.0.1 / other | **127.0.0.1, false, null** | HAR-05 + Stage 23-25 | INC-08 | permanent | [Verified Fact] |
| `audit.anchor_path` | path | config path outside DB dir | OD-S12-18 | INC-03 | permanent | [Verified Fact] |
| `data_origin` | synthetic / production | **synthetic** | HAR-15 (no real data exists) | INC-02 | permanent | [Verified Fact] |
| `policy.active_rule_set` *(proposed key)* | none / rule_set_id | **none** | OD-S12-04 + HAR-06 (ZH-05/06) | INC-04 | permanent | [Inference]; not in schema v0.1 → addendum |
| `workflow.transition_table` *(proposed key)* | structural / strict | **structural** | OD-S12-16 | INC-05 | when strict table approved | [Inference] RD-3 |
| `facts.derivation` *(proposed key)* | human_only / rule | **human_only** | OD-S12-15 | INC-05 | permanent | [Inference] RD-3 |
| `metrics.adopted_definitions` *(proposed key)* | {} / map | **{}** → verdict `not_available_no_adopted_policy` | OD-S12-01/-02/-08 | INC-07 | permanent | [Inference] RD-4 |
| `capability.<cap>.authority` *(proposed key; cutover flag)* | shadow / authoritative | **shadow** | CUT step approval (HAR-11) + DV approvals (HAR-06) | INC-02 (read by pages/reports) | removed when legacy counterpart retired | [Inference] |
| `search.fts` *(R2, proposed)* | auto / off | **off** | OD-S12-12/-14 | INC-09 | when FTS5 confirmed | [Inference] |
| `hub.kill` *(kill switch, proposed)* | bool | false | operator (no approval to *disable* the hub) | INC-02 | permanent | [Inference] |

Keys marked *proposed* are not in `hub-config.schema.json` v0.1 [Verified Fact]; they need a schema addendum in the Stage 15 PR of the increment that introduces them (HAR-13: Stage 12 file not edited in place).

### FF-2 Flag rules
1. **Default = safe**: no default adopts a definition, enables an automated action, exposes the network, records a disposition, or makes the hub authoritative. [Inference] RD-4.
2. **Both modes tested**: every decision flag's class-B tests run in both modes in the increment that introduces it (Stage 12 RD-1 "both modes specified and tested"). [Verified Fact] RD-1.
3. **Non-default requires approval_ref**: start-up self-check fails with a reason code if a non-default value lacks an approval reference. [Inference]
4. **Flag changes are audited** (C2 audit event `CONFIG_CHANGED` with old/new/approval_ref) and listed in the Stage 16 behaviour comparison. [Inference]
5. **No flags in legacy**; cutover is a hub-side authority flag + consumer re-pointing, never an `if` inside legacy code. [Inference] CR-1.
6. **Kill switch semantics**: `hub.kill=true` stops hub jobs and pages; legacy is unaffected because nothing depends on the hub in R1. [Inference]

### FF-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| FL-1 | Config schema v0.1 covers 8 of the ~15 needed flag keys | `hub-config.schema.json` key list | schema addendum needed in INC-04/05/07 | Low | High | none |
| FL-2 | All RD-3 defaults are non-adopting, so build can precede decisions | RD-3 default column | Stage 15 can start with minimal approvals | Low | High | Dinesh may still prefer to decide first |
| FL-3 | Flag sprawl risk across 19 decisions | RD-3 | config drift | Medium | Medium | Stage 16 prints effective config in every evidence pack |

## Evidence References
`hub-config.schema.json`; spec-readiness RD-1/RD-3/RD-4; ADR-006/007/010/015/018; HAR list.

## Assumptions
- A-14-09 [Assumption] Config file + env is sufficient flag infrastructure for a single-host R1. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-09 Whether a real deployment would require flags to be changed under formal change control (GxP); out of scope until Stage 24/27.

## Unresolved Issues
- Proposed keys need schema addenda (FL-1).

## Residual Risks
- RR-FF-1 A flag flipped without approval_ref in a manually edited config: mitigated by start-up self-check + audit event.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial flag plan (Stage 14). |
