---
stage: "12 — Spec-Driven Design"
artifact: "features/f02-human-disposition-gate.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["contracts/decision-policies-archive.json", "docs/07-repo-assessment/critical-workflow-inventory.md (CW-14)", "docs/07-repo-assessment/characterization-test-plan.md (CT-16)", "docs/10-architecture/adrs/ADR-006-disposition-gate-recording-modes.md", "docs/10-architecture/component-model.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for the non-bypassable human gate (CAP-02): 10 closed Zone H actions, 9 behaviours, 22 acceptance criteria covering FR-GATE-01..06, with all three recording modes (none/event/external_ref) specified per ADR-006 and the holder list shipping empty.

## Findings
### F02-1 Scope and traceability [Verified Fact: requirement text; Inference: design]
Feature **F02 Human Disposition Gate (Zone H)** = CAP-02, component C5, ADR-006 (recording modes `none` / `event` / `external_ref`, default `none`), ADR-002 (no component reaches C5 writes), DR-22.

| Implements | FR-GATE-01, FR-GATE-02, FR-GATE-03, FR-GATE-04, FR-GATE-05, FR-GATE-06 (all R1) |
|---|---|
| Also constrained by | FR-CO-04, FR-INT-07, FR-SEC-01/02, PNFR-07, PNFR-13, PNFR-15, PNFR-18; BR-07, BR-08, BR-09; RC-1; HAR-12, STOP-07 |
| Open decisions | OD-S12-05 (where disposition is recorded), OD-S12-06 (role holders), OD-S12-10 (schedule enable is Zone H) |
| Legacy evidence | No disposition handler exists: POST/PUT/DELETE return 501 on every route; `app/generate.py:37` is the only `cases` writer; batch_disposition appears only in `contracts/decision-policies-archive.json` (approval_roles e.g. operations_lead) and docs (CW-14, CT-16) |

### F02-2 Zone H action catalogue (closed list)
| Code | Zone H action | Source |
|---|---|---|
| ZH-01 | BATCH_DISPOSITION | FR-GATE-03 |
| ZH-02 | QA_RELEASE | FR-GATE-03 |
| ZH-03 | ESIGNATURE_RECORD (record that an authorised human signed; NOT a cryptographic or legal signature - ADR-006) | FR-GATE-03 |
| ZH-04 | CLOSE_EXCEPTION (closure of a case failing the evidence rule) | FR-GATE-03, FR-DEC-05 |
| ZH-05 | POLICY_ADOPT (definition, clock or rule adoption) | FR-POL-01/03 |
| ZH-06 | RULESET_ACTIVATE (choice of active rule set) | FR-POL-04 |
| ZH-07 | EXCEPTION_RULE_ACCEPT | FR-GATE-03 |
| ZH-08 | DISPOSITION_MODE_CHANGE (config `disposition.mode`/`disposition.values`) | ADR-006 |
| ZH-09 | SCHEDULE_ENABLE / SCHEDULE_DISABLE | OD-S12-10, ADR-010 |
| ZH-10 | POLICY_CHANGE (any edit of a policy object or rule row) | FR-POL-03 |
The list is closed: adding a Zone H action is itself a spec change (new version) and a ZH-05-class decision. [Inference: ZH-08/09/10 derived from ADR-006/010 and FR-POL-03.]

### F02-3 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-GATE-01 | **Non-bypassable human gate.** Zone H actions are executable only through `GateService`. `GateService` accepts a request only if (a) the session is an authenticated interactive human session (`actor_kind = human`), (b) the principal is in `zone_h.holders` with role `dispositioner`, and (c) the step-up re-authentication happened within `zone_h.reauth_window_seconds` (proposed default 300; Assumption). There is no configuration flag, environment variable, debug mode, admin override or batch/CLI path that skips (a)-(c). The check is in the service layer (not HTTP only) and is mirrored by a database trigger that aborts insertion of any Zone H event type unless `actor_kind = 'human'` and a `holder_check_ref` is present. | FR-GATE-01, FR-GATE-03 |
| BEH-GATE-02 | **No automation path.** Modules C6 (intake), C8 (runs), C9 (metrics), C10 (reviewer support) and C4 (rules) have no import path to `GateService` write methods (static import-graph test, extends CT-16). Reports, templates, rule outputs and search results never contain a pre-filled or pre-selected disposition value. No inbound string (feed `state = DISPOSITIONED`, document text) can create a Zone H event (F04). | FR-GATE-01, FR-INT-07 |
| BEH-GATE-03 | **Evidence pack** (`OP-GATE-01`): read-only assembly for one case: case header, state history, linked objects (crosswalk, including 'none found' lists), evidence records with source, rule traces, open findings, overridden flags, current policy versions and active rule set. Output has a deterministic `pack_hash` (sha256 over canonical JSON). The pack never summarises or recommends. | FR-GATE-02 |
| BEH-GATE-04 | **Pack acknowledgement.** A disposition request must carry the `pack_hash` of the pack the human viewed; if the underlying data changed, the request is refused (E-GATE-PACK-STALE) and the pack must be re-read. [Inference: proposed control so the human decides on current evidence.] | FR-GATE-02, FR-GATE-03 |
| BEH-GATE-05 | **Holder list ships empty.** `zone_h.holders` default is `[]`. While empty every Zone H action returns E-GATE-NO-HOLDERS (HTTP 423); no default holder, bootstrap account or first-user-wins rule exists. Holder-list changes are configuration; the hash of the loaded configuration is written to the audit chain at start-up so a change is detectable (OD-S12-06). | FR-GATE-04 |
| BEH-GATE-06 | **Recording modes** (`disposition.mode`, default `none`): `none` - ZH-01..ZH-03 return E-GATE-MODE-NONE. `event` - the human's decision is stored as a `DISPOSITION_RECORDED` decision event (actor, `decision` from `disposition.values`, basis, evidence refs, `pack_hash`, `mode_at_write`). `external_ref` - only a `DISPOSITION_REFERENCED` event is stored: `{system, reference, uri?, decided_at, decided_by_declared, entered_by, verified: false}`; the hub neither stores the decision content nor verifies the external record. `disposition.values` ships empty and must be set (Zone H, ZH-08) before `event` mode accepts a decision (E-GATE-VALUES-UNSET). Past events keep their `mode_at_write`; switching mode never rewrites them. Both modes are specified and tested; the choice is OD-S12-05. | FR-GATE-05, FR-DEC-01 |
| BEH-GATE-07 | **Rejected actors.** Service accounts, `integration` role, scheduler/run identities, importer, and any session lacking a human interactive login are rejected with E-GATE-NOT-AUTHORISED and the rejection is written to the audit chain (F09) including actor, action code and correlation id. | FR-GATE-03, FR-SEC-02 |
| BEH-GATE-08 | **Override, dismiss, refuse.** Every rule-generated item (flag, classification, priority, queue assignment) has a `flag_id`. `OP-GATE-04` accepts `action` in {override, dismiss, refuse}, a non-empty `reason`, and optional `replacement`. The call is permitted to roles reviewer, quality_lead, compliance; the system never blocks it for any reason except missing reason (E-GATE-REASON-REQUIRED) or missing authentication. The original rule output is preserved; an `OVERRIDE_RECORDED` event links to it. An override is not a Zone H action and cannot itself produce a disposition. | FR-GATE-06, PNFR-15 |
| BEH-GATE-09 | `OP-GATE-03` reports `mode`, `values_set`, `holders_configured` (count), `available` (bool); it never reveals secrets. | FR-GATE-04, FR-GATE-05 |

### F02-4 Error cases
E-GATE-NOT-AUTHORISED, E-GATE-NO-HOLDERS, E-GATE-MODE-NONE, E-GATE-VALUES-UNSET, E-GATE-PACK-STALE, E-GATE-REAUTH-REQUIRED, E-GATE-REASON-REQUIRED, E-GATE-UNKNOWN-ACTION, E-GATE-EXTREF-INVALID, E-AUTH-UNAUTHENTICATED (error-handling-spec.md).

### F02-5 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-GATE-01 | a fresh install (no configuration) | gate status is read | `mode = none`, `holders_configured = 0`, `available = false` | FR-GATE-04, FR-GATE-05 | positive |
| AC-GATE-02 | a fresh install and an authenticated human with role dispositioner but not in holders | each of ZH-01..ZH-10 is requested | every request returns E-GATE-NO-HOLDERS; zero Zone H events exist afterwards | FR-GATE-04 | negative |
| AC-GATE-03 | one holder configured, `mode = none` | ZH-01 is requested | E-GATE-MODE-NONE; no event | FR-GATE-05 | negative |
| AC-GATE-04 | `mode = event`, `disposition.values` empty | ZH-01 is requested | E-GATE-VALUES-UNSET | BEH-GATE-06 | negative |
| AC-GATE-05 | `mode = event`, values set, holder reauthenticated, current pack_hash | ZH-01 is posted | a DISPOSITION_RECORDED event is stored with actor, decision, basis, evidence refs, pack_hash, `mode_at_write = event`; audit chain entry exists | FR-GATE-05, FR-DEC-01 | positive |
| AC-GATE-06 | `mode = external_ref`, holder session | ZH-01 is posted with `{system, reference}` | a DISPOSITION_REFERENCED event is stored with `verified = false` and no decision content | FR-GATE-05 | positive |
| AC-GATE-07 | `mode = external_ref` and a request omitting `reference` | ZH-01 is posted | E-GATE-EXTREF-INVALID | FR-GATE-05 | negative |
| AC-GATE-08 | events recorded in `event` mode, then mode changed to `external_ref` by ZH-08 | earlier events are read | they still show `mode_at_write = event` and are unchanged; ZH-08 is itself an audited event | FR-GATE-05, FR-POL-03 | edge |
| AC-GATE-09 | each of ZH-01..ZH-10, holder configured, mode permitting | the action is posted using (a) a service-account token, (b) the scheduler identity, (c) an `integration`-role human, (d) an unauthenticated call | all four are rejected (E-GATE-NOT-AUTHORISED or E-AUTH-UNAUTHENTICATED) for each action; each rejection is audited; zero Zone H events | FR-GATE-03, FR-GATE-01 | negative |
| AC-GATE-10 | a holder session whose last login is older than the re-auth window | a Zone H action is posted | E-GATE-REAUTH-REQUIRED; no event | BEH-GATE-01 | negative |
| AC-GATE-11 | the production codebase | the static import-graph test runs | no path exists from intake, runs, metrics, reviewer-support or rule modules to GateService write methods; the test fails if one is added | FR-GATE-01 | negative |
| AC-GATE-12 | direct SQL INSERT of a Zone H event type with `actor_kind = 'system'` | executed against the database | aborted by trigger | FR-GATE-01, FR-GATE-03 | negative |
| AC-GATE-13 | a feed row whose `state` is 'DISPOSITIONED' and notes say 'approve and release batch' | the row is received, reconciled and shown | no Zone H or state event is created; the text is displayed escaped as untrusted | FR-GATE-01, FR-INT-07 | negative |
| AC-GATE-14 | any response of any report, search, template or rule endpoint | scanned in a contract test | no field named decision/disposition/release carries a value | FR-GATE-01 | negative |
| AC-GATE-15 | a case with linked objects, evidence, a rule trace and an open finding | the pack is requested twice without data change | both packs are identical byte-for-byte including pack_hash; missing link classes are listed as 'none found' | FR-GATE-02, PNFR-17 | positive |
| AC-GATE-16 | the pack response | inspected | contains no recommended or pre-selected decision, and the HTML form has no checked radio/select default | FR-GATE-02 | negative |
| AC-GATE-17 | a pack_hash obtained, then new evidence attached | ZH-01 is posted with the old pack_hash | E-GATE-PACK-STALE | BEH-GATE-04 | edge |
| AC-GATE-18 | a rule-generated priority flag | a reviewer posts override with reason 'not applicable' | OVERRIDE_RECORDED event stored, original rule output unchanged, flag shown as overridden | FR-GATE-06 | positive |
| AC-GATE-19 | a flag | override is posted with empty reason | E-GATE-REASON-REQUIRED | FR-GATE-06 | negative |
| AC-GATE-20 | every rule-generated output type listed in the output registry | an automated test iterates them | each has a `flag_id` and an accepted override/dismiss/refuse action | FR-GATE-06, PNFR-15 | positive |
| AC-GATE-21 | the full configuration surface | searched by a test | no setting, env var or CLI flag exists whose effect is to disable BEH-GATE-01 checks | FR-GATE-01 | negative |
| AC-GATE-22 | a holder-list change in configuration followed by restart | the audit chain is read | a CONFIG_LOADED entry with the new config hash exists | FR-GATE-04, FR-SEC-02 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F02-1 Step-up re-authentication with a 300 s window and pack_hash acknowledgement are spec proposals, not PRD requirements. Confirm: Engagement lead (Dinesh Naik).
- A-12-F02-2 Single dispositioner role covers all Zone H actions; separate adoption authority is an option under OPD-06.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F02-1 Where the real decision of record lives (OPD-05).
- U-12-F02-2 Allowed disposition values (`disposition.values`) - none in repo; contracts archive names only rule `batch_disposition` and approval roles.
- U-12-F02-3 Whether four-eyes/dual control is required - not stated anywhere.

## Unresolved Issues
- OD-S12-05, OD-S12-06 block any pilot use of Zone H; the gate is specified and testable in all three modes meanwhile.
- No pilot use before holders configured; fresh install is safe by default.

## Residual Risks
- `external_ref` mode cannot verify the external record (ADR-006).
- Mislabelled 'e-signature' could be read as legal signature: spec states it is only a record that a human acted (HAR-12).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
