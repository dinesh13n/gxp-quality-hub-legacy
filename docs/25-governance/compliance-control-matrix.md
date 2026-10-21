---
stage: "25 — Governance + Compliance + Assurance"
artifact: "compliance-control-matrix.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/25-governance/compliance-obligations.md (OB-01..OB-16)", "hub/security/{audit,zone_h,scan,authz,settings}.py", "hub/ops/release.py", "hub/guards/no_ai.py", "hub/coexistence/{register.py,seed_s20.json}", "hub/golden/compare.py", "hub/policy/{rulesets.py,as_found_pins.json}", "docs/10-architecture/adrs/ADR-002,005,006,007", "docs/12-specs/{security-spec,api-contracts,acceptance-criteria}.md", "docs/14-transformation/{feature-flag-plan,rollback-strategy,transformation-gates}.md", "docs/16-repo-validation/{security-scan-summary,repo-quality-gate,behavior-difference-report}.md", "docs/17-implementation-prd/finalized-nfrs.md", "docs/20-application/{deterministic-ai-boundary,access-control-implementation,application-test-summary}.md", "docs/18-delivery/delivery-backlog.md (DW-13..DW-20)", "docs/00-preflight/operating-contract/*.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. A control listed as 'present' means it exists in code or process and has the cited test or document evidence; it does NOT mean the obligation is met or compliant. Stage 23 and Stage 24 outputs were not merged when this stage ran: controls they will add (DW-13..DW-19) are listed as PLANNED and carry no evidence. Control owner for every human decision: Engagement lead (Dinesh Naik).**

## Summary
22 controls (GC-01..GC-22) are mapped to the 16 obligations. Of the 22: 12 are PRESENT with cited evidence (code plus test or document), 7 are LIMITED (evidence exists but a known weakness is recorded: GC-01, GC-02, GC-06, GC-08, GC-09, GC-10, GC-16), and 3 are ABSENT or PLANNED (GC-20 second reviewer, GC-21 retention policy, GC-22 Stage 23/24 additions). Of the 16 obligations: 10 are MAPPED to controls with evidence and a decision owner (OB-01, 02, 03, 04, 06, 10, 11, 12, 13, 16), 2 are PARTIAL (OB-05 retention, OB-07 evidence-before-closure) and 4 are UNMAPPED because no basis, owner or control exists (OB-08 privacy, OB-09 cross-tenant, OB-14 contractual, OB-15 external AI governance). Every mapping states an approval point and, where evidence is missing, says so instead of claiming the obligation is met. Test counts below come from earlier-stage documents; this stage executed no code (documents-only mode), so no test result here is new.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CM-1 Control catalogue
Status: PRESENT = implemented and evidenced by an earlier stage; LIMITED = present with a recorded weakness; PLANNED / ABSENT = no evidence yet.

| GC | Control | Type | Where (path / document) | Evidence (earlier stage) | Status | Tag |
|---|---|---|---|---|---|---|
| GC-01 | Hash-chained, insert-only audit trail; each record's SHA-256 covers the previous hash; out-of-DB anchor file; `verify-audit`; secret-like keys refused in `details`; change and audit record in one transaction | Detective + preventive | `hub/security/audit.py`; ADR-005 (PROPOSED) | PNFR-09 "met in shadow"; TST-SEC audit tests; `verify-audit` rc 0 (`finalized-nfrs.md`) | LIMITED: anchor is an unsigned local file (RTD-29); records appended after the last anchor and then removed are undetectable (R-SEC-1, in the module docstring); a host compromise can rewrite chain and anchor together (ADR-005 residual) | [Verified Fact] |
| GC-02 | Insert-only triggers and no delete paths on retained tables; deletion-path grep | Preventive | `hub/security/scan.py` `RETAINED_TABLES`; migrations; error `E-SEC-RETAINED` | PNFR-10 "met"; TST-SEC-13, TST-SEC-18, TST-DEC-03; TST-NFR-10 exists at `tests/hub/test_tst_nfr_measurements.py` L343 | LIMITED: `RETAINED_TABLES` omits tables that TST-NFR-10 itself treats as retained (e.g. `case_state`, `flag_action`, `rule_trace`, `metric_value`, `zone_h_action`) — gap recorded as DW-19 / RETAINED_TABLES | [Verified Fact] (tuple read in `scan.py`; test table list read) |
| GC-03 | Decision event record: actor, time, basis, evidence refs; per-case decision chains; structural evidence-presence check for closure | Preventive + detective | `hub/decision/`; FR-DEC-01..05 | PNFR-09 verification; TST-DEC family (241 planned tests all pass in sandbox, `implementation-prd.md`) | PRESENT (sufficiency of evidence is policy, OPD-07 open) | [Verified Fact] |
| GC-04 | Zone H single choke point: ZH-01..ZH-10 only via `POST /api/v2/zone-h/actions`; holder list, role `dispositioner`, fresh re-authentication, current `pack_hash`, human session only (services, scheduler, importer rejected); rejected attempts audited | Preventive | `hub/security/zone_h.py` (one holder rule), `hub/gate/`, `hub/security/authz.py` | TST-GATE (AC-GATE-02, -09); mutant H1 KILLED; `mutation-gate.json`; shipped default `zone_h.holders` [] refuses every action | PRESENT | [Verified Fact] |
| GC-05 | Disposition modes `none` (default) / `event` / `external_ref`; no cryptographic or legal e-signature is implemented | Preventive | ADR-006 (PROPOSED); `hub/gate/`; ZH-03 semantics in `api-contracts.md` | AC-GATE-03..08; `disposition.mode` ships `none` (SS-02) | PRESENT | [Verified Fact] |
| GC-06 | Role-based access: 6 roles, deny-by-default route registry of 48 operations, re-authentication window, lockout, CSRF | Preventive | `hub/security/route_registry.json`, `authz.py`, `auth.py`; `docs/12-specs/security-spec.md` | TST-SEC-01; I8 HTTP tests; mutants H2, H4 KILLED | LIMITED: control values are proposals (RTD-26); header values and non-loopback refusal untested (H3, H5 survived, SS-04 / SS-08) until DW-14 / DW-15 | [Verified Fact] |
| GC-07 | Rule sets ship as named, versioned, INACTIVE candidates; `evaluate` with no active set returns `E-POL-NO-ACTIVE-RULESET`; activation (ZH-06) needs a holder and a recorded `POLICY_DECISION_RECORDED` (`E-POL-DECISION-REQUIRED`); as-found pins detect drift (`E-POL-ASFOUND-DRIFT`) | Preventive | `hub/policy/rulesets.py`, `as_found_pins.json`, `service.py`; ADR-007; OD-16 | FAC-04; TST-POL; TST-CO-03 a-c (rule-set parity); observed `E-POL-NO-ACTIVE-RULESET` | PRESENT | [Verified Fact] |
| GC-08 | Configuration flags with safe (non-adopting) defaults, validated against `hub-config.schema.json`; Zone H or HAR approval to move a decision flag; `exposure_approved` + `exposure_approval_ref` + TLS for any non-loopback bind (and the bind is refused anyway, DEV-75) | Preventive | `hub/security/settings.py`; `docs/14-transformation/feature-flag-plan.md` FF-1/FF-2 | SS-02 (defaults hold); TST-SEC-16 | LIMITED: FF-2 rule 3 (non-default needs `approval_ref`, audited `CONFIG_CHANGED`) is a plan until DW-17 is built at Stage 23; not evidenced today | [Verified Fact] defaults; [Inference] plan |
| GC-09 | Deviation register DV-01..DV-11 (all `proposed`, none approved); `golden-compare` exits 6 (E-CO-UNAPPROVED-DEVIATION) while any difference lacks an approved row with a non-empty `approval_ref` | Detective + preventive | `hub/coexistence/register.py`, `seed_s20.json`; `hub/golden/compare.py` | TST-CO-01; `behavior-difference-report.md` (D5 = 0; D3 approved = 0) | LIMITED: 7 of 11 probes still compare declared values until FAC-05 / DW-04 evidence is carried (OD-27: DEV-01 plain compare marks module probes not run) | [Verified Fact] |
| GC-10 | Pre-release checklist G1..G10; `mark_ready` refuses unless all ten gates are `pass`; DB trigger backstop; each gate recorded with evidence path or `not_run` | Preventive | `hub/ops/release.py` | AC-CO-10, AC-CO-15; PNFR-19 "partly met" (G4, G8, G9, G10 not run, RTD-74) | LIMITED: gates not wired to CI (RTD-01/02/14) | [Verified Fact] |
| GC-11 | No-AI tripwire: `no-ai-check` deny-list of imports / dependencies, loopback-only egress guard over tests, `model_calls_total` = 0, no `record_model_call` site | Preventive + detective | `hub/guards/no_ai.py`; `python -m hub no-ai-check` | `docs/20-application/evidence/no-ai-check.json` rc 0, findings []; TST-CO-11 40/40; TST-CO-12 c/d; E05..E09, E20EGRESS | PRESENT, but manual gate not CI (RTD-14, RR-AI-1) | [Verified Fact] |
| GC-12 | Secret scan and deletion-path grep | Detective | `hub/security/scan.py` | `docs/16-repo-validation/evidence/secret-scan.txt` (1 deliberate fixture hit, 0 real); TST-SEC-18 | PRESENT | [Verified Fact] |
| GC-13 | Untrusted-content guard: free text carried as `{text, trust: untrusted}`; never reaches a decision field | Preventive | `hub/core/untrusted.py` | PNFR-13 met on existing fixtures (86 feed rows + 22 injection docs + 10 variants, PCH-31 wording pending acceptance) | PRESENT (static check AC-INT-23 not built) | [Verified Fact] |
| GC-14 | Engagement change control: one branch + PR per increment, orchestrator review and full regression, squash-merge, OD-log entry; prior-stage artifacts immutable (errata only); versioned artifacts with Change History | Preventive | CC-01..CC-12; OD-01, OD-13, OD-23; git history (PR #1..#11) | OD log; `git log` | PRESENT; single human approver (GC-20) | [Verified Fact] |
| GC-15 | Data protection of the baseline: backup with SHA-256 manifest (1,512 files), execute only in a full-copy sandbox, checksum before / after | Detective | OD-03, OD-03a; `../_data-backup-2026-10-17/SHA256SUMS.txt` | Stage 16 `validation-signoff.md` VS-1 (rc 0 before and after every execution) | PRESENT | [Verified Fact] |
| GC-16 | Evidence contract and honest labelling: evidence classes, no fabricated approvals / KPIs, "synthetic, unvalidated" labels | Preventive | `evidence-contract.md`; OD-04; PNFR-20 | metric outputs labelled (`hub/metrics/service.py`); R2 report labels not separately verified | LIMITED (PNFR-20 R2 labels [Unknown]) | [Verified Fact] / [Unknown] |
| GC-17 | Rollback ladder L1 (revert), L2 (hub store restore), L3 (authority flip back to shadow) with rehearsals INC-03, -06, -07, -08, -09 | Corrective | `docs/14-transformation/rollback-strategy.md`; `docs/15-modernization/rollback-rehearsal-inc*.md` | rehearsals pass in sandbox (PNFR-05) | PRESENT in sandbox; L3 not executable until DW-17 | [Verified Fact] |
| GC-18 | Mutation gates over control behaviours | Detective | `docs/16-repo-validation/evidence/hub-mutation.json` (8 of 10 killed); `docs/20-application/evidence/mutation-gate.json`; legacy mutation gate 15/15 | as cited | PRESENT (H3, H5 open until DW-14 / DW-15) | [Verified Fact] |
| GC-19 | Hub backup / restore with checksum match; backup-before-migrate | Corrective | `hub.admin backup / restore`; `E-STORE-BACKUP-INVALID` | G7 rehearsal; PNFR-05 (RTO / RPO are unvalidated assumptions) | PRESENT (sandbox only) | [Verified Fact] |
| GC-20 | Second reviewer / separation of duties for GxP-relevant changes | Preventive | none | DR-10, GD-05, Q-02-09, DQ-17 | ABSENT (single approver; decision open) | [Verified Fact] |
| GC-21 | Retention policy (period, archival, disposal authority) | Preventive | none; interim hold-all (OD-15, OD-S12-09) | PNFR-10 | ABSENT (policy), hold-all as stand-in | [Verified Fact] |
| GC-22 | Stage 23 additions (Stage 12 v0.2, header-value and bind-refusal tests, schema tests, approval-gated authority switch, HITL catalogue) and Stage 24 additions (control values, field map, anchor decision, RETAINED_TABLES fix) | Mixed | DW-13..DW-19 in `docs/18-delivery/delivery-backlog.md` | none merged when this stage ran | PLANNED | [Verified Fact] plan; no evidence |

### CM-2 Obligation to control to owner to evidence to approval point
"Decision owner" is always **Engagement lead (Dinesh Naik)** (OD-04). "Control operator" names who or what runs the control; a client-role holder is a **GAP** unless a document names one (none does).

| Obligation | Controls | Control operator | Evidence on hand | Evidence gap | Approval point (who approves what) | Mapping verdict |
|---|---|---|---|---|---|---|
| OB-01 attributable, tamper-evident | GC-01, GC-03, GC-02, GC-18 | hub code; reviewer / quality-lead roles (holders GAP) | PNFR-09 evidence, `audit.py`, tamper tests, `verify-audit` | external anchor and strength (OD-S12-18, Stage 24); no Part 11 claim possible (GAP-13-22) | Dinesh: anchor decision (DQ-09); framing statement (DQ-17) | MAPPED; framing only; limited by GC-01 weakness |
| OB-02 human disposition | GC-04, GC-05, GC-11 (no automation), GC-06 | `dispositioner` role holders (**GAP**: `zone_h.holders` []) | TST-GATE, mutant H1, default refuses all | no named holder; no real disposition performed in any mode | Dinesh: OD-S12-05 (mode), OD-S12-06 (holders), HAR-12 prohibition stands | MAPPED; control strong, owner of the human act is a GAP |
| OB-03 no e-signature claim | GC-05, GC-16 | hub code | ADR-006; ZH-03 contract | Part 11 e-signature requirements never assessed [Unknown] | Dinesh + qualified review before any signature use | MAPPED for the product position only |
| OB-04 data integrity themes | GC-01, GC-02, GC-03, GC-09, GC-15 | hub code; orchestrator for checksums | PNFR-11 (10,983 raw items, 67 REPLAY -> NOOP_DUPLICATE, legacy DB sha unchanged), PNFR-16/17, BD-01..BD-14 | attribute-level assessment never done; no real data | Dinesh: DV-01..DV-11 preserve-or-fix (OD-S12-13) | MAPPED at theme level |
| OB-05 retention | GC-02, GC-21 | hub code (technical hold-all) | PNFR-10, TST-NFR-10 (test exists; sandbox pass recorded in earlier regressions; no Stage 25 log) | no policy, no period, no owner; unbounded growth (RTD-30) | Dinesh: OD-S12-09 | PARTIAL: interim hold-all only; policy GAP |
| OB-06 access control | GC-06, GC-04 | hub code | TST-SEC-01, I8 HTTP tests | control values unvalidated; header values and bind refusal untested until DW-14/15; TLS absent | Dinesh: DQ-09 (Stage 24) | MAPPED; limited |
| OB-07 compliance evidence-before-closure | GC-03 (structural presence), GC-04 | hub code | AC-DEC-27/28 structural check; DR-20 | sufficiency criteria OD-S12-07; Compliance holder GAP | Dinesh: OD-S12-07 | PARTIAL; basis is a document claim (NE-1) |
| OB-08 privacy regime | GC-13, GC-06 (access); `data_origin` flag | hub code | field classes C0..C3 (PNFR-12, RTD-83 proposed) | regime Unknown; no PIA; no real data | Dinesh + qualified review | UNMAPPED beyond access controls; Stage 24 |
| OB-09 no silent cross-tenant action | none specific (single-tenant by construction) | n/a | [Inference] only | no test | Dinesh: confirm A-25-OB-2 | UNMAPPED (Assumption) |
| OB-10 No-AI | GC-11, GC-12 (deps), GC-10 (G5) | hub code; orchestrator runs the guard | `no-ai-check.json`, TST-CO-11/12, E-tests, `not-applicable.md` (Stage 19) | not in CI (RTD-14); dev tooling out of the guard's scope by definition (OD-08) | Dinesh: HAR-10 for any change; RQ-1..RQ-3 re-qualification | MAPPED; manual gate |
| OB-11 change control | GC-14, GC-10, GC-15, GC-17 | orchestrator (agent) executes; Dinesh approves | PR #1..#11; OD log; Stage 16 `validation-signoff.md` | no CI gate; GC-20 absent; several HAR items still PROVISIONAL | Dinesh: OD-13 delegation (approved), HAR-04 | MAPPED; single approver |
| OB-12 no fabrication | GC-16, GC-14 | all agents; Dinesh reviews | this document set; PNFR-20 | R2 labels unverified | Dinesh (OD-04) | MAPPED |
| OB-13 untrusted content | GC-13 | hub code | PNFR-13 | static check; Stage 24 values | Dinesh: PCH-31 wording | MAPPED |
| OB-14 contractual | none | n/a | none | no SOW | Dinesh | UNMAPPED (Unknown) |
| OB-15 AI-governance external | GC-11 (product has no AI); `ai-system-register.md` | n/a | none cited | no framework chosen | Dinesh + qualified review | UNMAPPED (Unknown) |
| OB-16 behaviour-change approval | GC-09, GC-10, GC-07, GC-17 | hub code; Dinesh approves deviations | `behavior-difference-report.md`; golden-compare exit 6 by design | declared probes; DV-01..11 unapproved | Dinesh: OD-S12-13 per DV row (Stage 30) | MAPPED; blocks cutover |

### CM-3 Change control for rule sets and feature flags
| Item | Change path today | Approval point | Evidence | Gap |
|---|---|---|---|---|
| Add or edit a rule set | A rule set is a named, versioned candidate; adding one is code (PR + review, GC-14); the three as-found sets are pinned and drift is detected | HAR-06 (Dinesh) for any threshold or logic change; no domain owner (DR-23 GAP) | `hub/policy/as_found_pins.json`; `E-POL-ASFOUND-DRIFT`; TST-CO-03 | owner of the rule decision (RC-3 / RC-4, OD-S12-04) |
| Activate a rule set | ZH-06 by a Zone H holder with a recorded `POLICY_DECISION_RECORDED`; audited; mutation H1 guards the holder rule | Zone H holder (GAP) + OD-S12-04 | FAC-04; AC-GATE-09 | impossible by design until holders named (OD-17) |
| Adopt / withdraw a policy or definition | ZH-05 adopt, ZH-10 withdraw (`authority_ref` required, FAC-13 approved as built, OD-29) | Zone H holder (GAP) | `docs/20-application/business-logic-map.md` | holders |
| Change a decision flag (disposition mode, holders, schedule, contract binding, closure behaviour) | config edit; ZH-08 / ZH-09 for mode and schedule are audited Zone H events | OD-S12-xx per flag (feature-flag-plan FF-1) | `hub-config.schema.json`; FF-1 | `approval_ref` enforcement + `CONFIG_CHANGED` audit are DW-17 (PLANNED) |
| Flip a capability to authoritative | refused in the R1 build (`capability_authority = authoritative`) until DW-17 | CUT step approval (HAR-11) + DV approvals (HAR-06) | `hub/config.py` L41-42; IF-2 in `increment-plan.md` | DW-17 not built |
| Change a security value (lockout, session, TLS, anchor) | code / config PR | HAR-07 for CI, Dockerfile, env profiles; Dinesh for values (DQ-09) | `settings.py` | Stage 24 |

### CM-4 No-AI governance (zero-model-call tripwire and re-qualification)
| Element | Rule | Evidence | Owner |
|---|---|---|---|
| Boundary | No model client, prompt, embedding or network path beyond loopback; AI coding assistants used to build the system are development tooling, not product AI (OD-08) | `deterministic-ai-boundary.md`; `not-applicable.md` (Stage 19); `docs/22-agentic-engineering/not-applicable.md` | Engagement lead (Dinesh Naik) |
| Tripwire | `model_calls_total` must be 0; `no-ai-check` rc 0; G5 in the release checklist; Stage 32 tracks zero model calls (OD-08) | GC-11 | Engagement lead (Dinesh Naik); orchestrator runs it |
| Change | Any AI element needs a new Dinesh decision and HAR-08 / HAR-09 / HAR-10 approvals | OD-08; HAR-10 | Engagement lead (Dinesh Naik) |
| Re-qualification | RQ-1 (labelled corpus >= 50 questions proposed; baseline recall below a threshold Dinesh sets, proposal 80 % top-5), RQ-2 (multilingual / noisy content the baseline fails), RQ-3 (named stakeholder request with a reviewer-time budget); RQ-4 only after RQ-1..3. Thresholds are proposals, not measurements | `qualification-decision.md` QD-3 | Engagement lead (Dinesh Naik) |
| Gap | Guard runs only when someone runs it (CI is Stage 27) | RTD-14; RR-AI-1 | Engagement lead (Dinesh Naik) |

## Evidence References
Paths in `evidence_sources`; item-level locations in `audit-evidence-index.md`.

## Assumptions
- A-25-CM-1 [Assumption] The earlier-stage test results cited here still hold at the current `main` (hub code unchanged since the cited runs apart from Stage 20 and 21 merges, which re-ran their own groups). A fresh full regression is the orchestrator's job (OD-23); this stage did not run code.
- A-25-CM-2 [Assumption] An agent-written "control operator" entry is a description, not an assignment of duty; assignment is Dinesh's (TP-14).

## Unknowns
- U-25-CM-1 Whether the `RETAINED_TABLES` tuple is the authoritative list of immutable tables (the TST-NFR-10 table list is wider).
- U-25-CM-2 Which Stage 23 / 24 controls will land and with what values.
- U-25-CM-3 Whether any control is acceptable to a real quality assurance reviewer (none exists).

## Unresolved Issues
- GC-20, GC-21 absent; OB-07, OB-08, OB-09, OB-14, OB-15 unmapped or partial; DW-17 not built; CI absent.

## Residual Risks
- RR-CM-1 Controls that depend on a human holder cannot be exercised end to end (no holder): Medium.
- RR-CM-2 Control status can drift after this snapshot because there is no CI gate: Medium until Stage 27.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
