---
stage: "17 — Finalise Implementation PRD"
artifact: "implementation-prd.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/09-initial-prd/ (Initial PRD v0.1 - approved baseline, OD-22; NOT edited)", "docs/10-architecture/ (ADR-001..ADR-018, all PROPOSED except No-AI)", "docs/11-data-context/data-contracts.md", "docs/12-specs/ (spec-readiness RD-3, error-handling-spec, schema-specifications, contracts/)", "docs/13-traceability/ (rtm.csv, traceability-summary)", "docs/14-transformation/ (cutover-plan, schema-migration-plan, transformation-gates)", "docs/15-modernization/ (modernization-summary close-out, transformation-log DEV-01..DEV-107, remaining-technical-debt RTD-01..RTD-90, approved-behavior-changes, inc05..inc09-design-notes)", "docs/16-repo-validation/ (repo-quality-gate, validation-signoff, behavior-difference-report, remaining-debt-register, data-contract-results, architecture-conformance-report, security-scan-summary)", "docs/07-repo-assessment/repo-assessment.md, baseline-behaviour.md", "docs/03-problem-value/, docs/04-baseline-kpis/ (problem, SUC, KPI baseline - unchanged)", "hub/ at main 8a8e8db (code identical to 2c63b07 validated by Stage 16: 2c63b07..8a8e8db change only docs/16-repo-validation and .fde/orchestrator-decisions.md)", "hub/core/errors.py and hub/*/errors.py (exit codes)", "hub/*/settings.py, hub/config.py (config keys)", "hub/*/migrations/, hub/store/forward/ (M000..M007)", "hub/coexistence/seed_inc02.json (DV-01..DV-09)", ".fde/orchestrator-decisions.md (OD-01..OD-24)", ".fde/engagement-context.md"]
supersedes: "none (complements docs/09-initial-prd/initial-prd.md v0.1, which stays the baseline)"
---
**Label: synthetic repository, unvalidated against any organisation (GxP Quality (FDE Capstone), GxP Quality Hub Modernisation). This is the IMPLEMENTATION baseline, not the as-built PRD: it reconciles the approved Initial PRD with what Stages 15/16 built and validated in a sandbox shadow build, and states the remaining scope. Nothing here approves a deviation, rule, policy, holder, schedule, exposure or cutover. All figures from FX-BASE125 are synthetic, unvalidated.**

## Summary
**Product intent is unchanged** (Stage 9 PRD-1..PRD-9): one attributable record of each batch-deviation / CAPA case and its decisions, safe handling of external case information, and figures that declare their definitions - with batch disposition staying human, and **No-AI** (OD-08).

**Where the build stands (evidence, not as-built claim).** At `main` 8a8e8db (code = 2c63b07) a stdlib-only `hub/` package runs in shadow beside the untouched legacy estate. Of 52 FRs, 49 are built (13 R1 with a stated limitation, 8 R2 built dark), 2 are partial (FR-POL-01 withdrawal, FR-RUN-01 schedule held), 1 is not built (FR-MET-08). All 241 planned acceptance tests pass in sandbox; Stage 16 found D5 = 0 unexplained differences, 9 proposed deviations, 2 unregistered-but-explained ones, 0 approved. Every consequential switch ships off: no Zone H holder, disposition mode `none`, no adopted policy, no active rule set, schedule off, contract bindings `record_only`, search / templates off, loopback only.

**What this PRD fixes.** (1) 48 logged changes (`prd-change-log.md`), incl. the OD-18 intake identity key, per-source contract binding, inactive rule sets, closure / fact / creation / transition defaults; (2) the **implementation-contract addendum** IC-1..IC-8 to the Stage 12 specs (error and exit codes, config keys, migrations M000..M007 with their own version tables, token formats, audit actions, API additions, schema additive fields); (3) the **deviation-register addendum** DV-07a, DV-09 label, DV-10, DV-11 - recorded, not approved (OD-24); (4) the decision register IP-7: decided items (OD-08, -09, -18, -22, -24) and every other open human decision as **accepted open, owner Engagement lead (Dinesh Naik)**; (5) finalised NFRs (incl. runtime NFR-RT: production Python 3.12+, code floor 3.10, OD-24), acceptance-criteria addenda, release boundaries and priorities in the companion files.

**Gate (recorded in `implementation-baseline-signoff.md`): CONDITIONAL PASS** - every material change is logged and the agent sign-off is recorded; the engagement lead's acceptance of this implementation baseline is pending, and three proposed items await him.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IP-1 Problem, users, goals (unchanged from the baseline)
[Verified Fact] Stage 9 PRD-1 (problem P-1..P-5), PRD-2 (RC-1..RC-8), PRD-3 (PER-01..PER-08), PRD-4 (J1..J4), PRD-5 (goals G-1..G-5, SUC-01..SUC-11 - thresholds provisional, A-03-12) and PRD-8/PRD-9 (human gate, No-AI) carry forward without change. No KPI target, benefit or ROI is added (OD-04, OD-07, NG-10). [Verified Fact] K-04/K-05 remain unmeasurable on the baseline (time to close `null`, `no_completed_cycles`).

### IP-2 Baseline references
| Item | Value | Tag |
|---|---|---|
| Requirements baseline | `docs/09-initial-prd/` v0.1, approved as build baseline 2026-10-20 (OD-22); IDs stable; 52 FR = 43 R1 / 9 R2; 20 PNFR = 17 R1 / 3 R2 | [Verified Fact] |
| Code baseline | `main` 8a8e8db; hub code identical to 2c63b07 validated in Stage 16 (CONDITIONAL PASS, accepted by Dinesh, OD-24) | [Verified Fact] |
| Behaviour baseline | Stage 7 goldens; FX-BASE125 sha256 `c254649f…d70aa`; tag `baseline-as-found`; reference runtime Python 3.10.12 / SQLite 3.37.2 | [Verified Fact] |
| Architecture baseline | ADR-001..ADR-018 PROPOSED; conformance per Stage 16 AC-1 (ADR-014 partial, ADR-016 partial, ADR-017 not assessable, ADR-018 superseded for production by OD-24) | [Verified Fact] |

### IP-3 Capabilities and scope
[Verified Fact] Capability set CAP-01..CAP-10 unchanged. Implementation state, remaining scope and priorities per FR: `prioritized-capabilities.md` PC-3. Remaining scope inside R1 (not built or limited): policy withdrawal (DEV-36), scheduled runs held (OPD-11), automatic rule-trace producer (RTD-69), static Untrusted check (AC-INT-23), D-EVID backlog (DEV-69), observed golden probes (S16-D01), CI wiring (RTD-01/02/14). New scope constraints from the build: no case-creation path (OD-S12-19), structural transition table default (OD-S12-16), human-only facts (OD-S12-15).

### IP-4 Interfaces as built (for downstream stages)
| Surface | Built form | Tag |
|---|---|---|
| CLI | `python -m hub` (core: no-ai-check, golden-compare, guards), `hub.admin` (users, migrate, verify-audit, backup/restore, startup-check), `hub.policy`, `hub.decision`, `hub.intake`, `hub.runs`, `hub.metrics`, `hub.web` (serve, token, record-trace), `hub.search` (schema, corpus load / drop-index), `hub.r2` (serve, R2 reports) - one runner per package (S16-D03) | [Verified Fact] |
| HTTP | `/api/v2` + server-rendered pages, 48 registry operations from `docs/12-specs/contracts/openapi.yaml`; stdlib `ThreadingHTTPServer`, loopback only; R1 `WebApp` (`hub.web serve`) and R2 `R2WebApp` (`hub.r2 serve`) | [Verified Fact] |
| Store | one hub SQLite file; insert-only tables with triggers; legacy stores read-only via adapters AD-01..AD-08 | [Verified Fact] |
| Logs | JSON log lines on stderr, results on stdout (DEV-70) | [Verified Fact] |

### IP-5 Implementation-contract addendum to Stage 12 (IC-1..IC-8)
Stage 12 files are frozen; this addendum is the authoritative record until a Stage 12 v0.2 is issued (approval HAR-13: accepted open, owner Engagement lead (Dinesh Naik)). Source: `hub/**/errors.py`, settings modules, migrations, design notes; RTD-13/23/24/38/47/55/58/66/78.

**IC-1 Exit codes (CLI)** [Verified Fact] (grep of `exit_code` assignments in `hub/`)
| Exit | Codes | Origin | Note |
|---|---|---|---|
| 0 / 1 | OK / generic HubError | INC-02 | — |
| 2 | usage, E-FX-HASH, E-CFG-INVALID, E-AUTH-PASSWORD-POLICY | INC-02/03 | **shared** (RTD-21) |
| 3 | E-HUB-KILLED | INC-02 | — |
| 6 / 7 / 8 | E-CO-UNAPPROVED-DEVIATION / E-CO-NOT-SANDBOX / E-CO-RUNTIME-UNSUPPORTED | Stage 12 spec | as specified |
| 9 | E-CO-DENYLIST-IMPORT, E-SEC-EXPOSURE-NOT-APPROVED | INC-02 / spec | **collision** (RTD-24, DEV-23) |
| 10..15 | E-CO-LEGACY-WRITE-REFUSED, E-CO-EGRESS-ATTEMPT, E-INT-UNTRUSTED-USE, E-CO-LEGACY-SCHEMA-DRIFT, E-OBS-TRIPWIRE, E-STORE-MIGRATION-DRIFT | INC-02 | — |
| 16..18 | E-SEC-SCAN-FINDINGS; E-SEC-AUDIT-TAMPER-DETECTED; E-SEC-AUDIT-WRITE-FAILED, E-SEC-SECRET-IN-AUDIT | INC-03 | 18 shared by two audit-write failures |
| 19 | E-AUTH-* (BAD-CREDENTIALS, FORBIDDEN, LOCKED, SESSION-EXPIRED, UNAUTHENTICATED), E-GATE-NO-HOLDERS / NOT-AUTHORISED / REAUTH-REQUIRED / UNKNOWN-ACTION, E-SEC-CSRF, E-SEC-REASON-REQUIRED | INC-03/04/08/09 | access-refusal family |
| 20..22 | E-CO-RELEASE-BLOCKED; E-STORE-BACKUP-INVALID; E-STORE-NOT-MIGRATED | INC-03 | — |
| 23 / 24 | E-POL-* (10 codes incl. NO-ACTIVE-RULESET, DECISION-REQUIRED, INPUT-INVALID) / E-POL-ASFOUND-DRIFT | INC-04 | — |
| 25 / 26 / 27 | E-DEC-* (18 codes incl. CREATION-DISABLED, TRANSITION-NOT-ALLOWED, EVIDENCE-REQUIRED) / E-ID-* (7) / E-DEC-BACKFILL-MISMATCH | INC-05 | — |
| 28 | E-INT-* (7 codes incl. ENVELOPE-INVALID, URL-SCHEME-REFUSED) | INC-06 | — |
| 29 / 30 | E-RUN-* (incl. SCHEDULE-DISABLED; UNKNOWN-JOB also for an unknown run id) / E-MET-* (9 codes incl. CUTOFF-REQUIRED, TAG-MIX, NOT-AVAILABLE) | INC-07 | — |
| 31 | E-GATE-MODE-NONE / VALUES-UNSET / PACK-STALE / PAYLOAD-INVALID / EXTREF-INVALID / REASON-REQUIRED, E-REQ-INVALID / NOT-IMPLEMENTED / TOO-LARGE, E-REV-* (7) | INC-08 | — |
| 32 | E-R2-INPUT-INVALID, E-REV-INDEX-ABSENT | INC-09 | — |
[Inference] Exit-code collisions (2, 9) should be resolved or explicitly accepted before CI scripts depend on them (Stage 27).

**IC-2 Error codes added beyond the 82-code registry** [Verified Fact] All codes listed in IC-1 that are not in `docs/12-specs/error-handling-spec.md` (e.g. E-CO-LEGACY-SCHEMA-DRIFT, E-OBS-TRIPWIRE, E-CFG-INVALID, E-HUB-KILLED, E-STORE-MIGRATION-DRIFT, E-CO-PROTECTED-WORKFLOW (DEV-10); E-SEC-SECRET-IN-AUDIT, E-SEC-SCAN-FINDINGS, E-CO-RELEASE-BLOCKED, E-STORE-BACKUP-INVALID, E-AUTH-PASSWORD-POLICY, E-STORE-NOT-MIGRATED (RTD-23); E-POL-DECISION-REQUIRED, E-POL-ASFOUND-DRIFT, E-POL-INVALID (DEV-37); E-DEC-CREATION-DISABLED, E-DEC-TRANSITION-NOT-ALLOWED and other INC-05 codes (DEV-49); E-INT-* (DEV-60); E-RUN-* / E-MET-* (DEV-68); E-REQ-TOO-LARGE, E-REQ-NOT-IMPLEMENTED, E-REV-*, E-GATE-MODE-NONE / VALUES-UNSET / PACK-STALE / PAYLOAD-INVALID, E-SEC-CSRF (RTD-66); E-REV-INDEX-ABSENT (409), E-R2-INPUT-INVALID (422), E-SEC-REASON-REQUIRED (DEV-103)). The authoritative list is the code (`hub/**/errors.py`); a generated registry is a Stage 23 task. CLI error output shape differs from the HTTP envelope (SS-07, FAC-10).

**IC-3 Configuration keys added to `hub-config.schema.json` v0.1** [Verified Fact]
| Group | Keys (default) | Decision link |
|---|---|---|
| core (INC-02) | `hub.kill` (false), `runtime.floor` (3.10/3.37) and 2 further INC-02 keys (RTD-13) | OD-14, OD-24 |
| security (INC-03) | `auth.lockout_threshold` / `lockout_window_seconds` / `lockout_duration_seconds` / `password_min_length` / `session_idle_seconds` (proposed values 5 / 15 min / 15 min / 12 / 30 min), `audit.anchor_path` (required, no default), `audit.anchor_every`, `network.bind` (127.0.0.1), `network.tls` | RTD-26 (values), OD-S12-18 |
| Zone H | `zone_h.holders` ([]), `zone_h.reauth_window_seconds` (300) | OD-S12-06 |
| decision (INC-05) | `closure.unconfigured_behaviour` (treat_label_CLOSED_as_closing), `facts.derivation` (human_only), `case_creation.enabled` (false), `workflow.transition_table` (structural), `workflow.transitions` | OD-S12-03/15/19/16 |
| intake (INC-06) | `gateway.retries`; contract binding is a policy event, not a key (DEV-55) | OD-S12-11 |
| runs / metrics (INC-07) | `schedule.expected`, `schedule.grace_minutes`, `runs.batch_size`, `runs.heartbeat_stale_seconds`, `site.timezone` (UTC / fixed offset only); `schedule.enabled: true` is refused (flag = policy event, DEV-64) | OPD-11, RTD-62 |
| web / gate (INC-08) | `disposition.*` (mode `none`, values unset), `search.enabled` (false) | OD-S12-05 |
| R2 (INC-09) | `search.fts` (off), `search.max_doc_chars`, `search.require_c3_reason`, `templates.enabled` (false), `crosswalk_view.*`, `intake_reports.*` (4 h / 24 h, Assumption) | OPD-12, PCH-32 |

**IC-4 Migrations and version tables (M000..M007)** [Verified Fact]
| Migration | File | Applied by | Version table | Main tables | Inc |
|---|---|---|---|---|---|
| M000 | `hub/store/migrations/M000_coexistence.sql` | `python -m hub` | `schema_migrations` | deviation_register, coexistence_inventory (update/delete blocked) | INC-02 |
| M001 | `hub/store/forward/M001_access_audit.sql` | `hub.admin migrate` | `schema_migrations` | principal, principal_role, session, login_attempt, audit_log, release_record, release_gate_result | INC-03 |
| M002 | `hub/policy/migrations/M002_policy_rules.sql` | `hub.policy migrate` | `policy_schema_migrations` | policy objects / events, rule_set, rule_row, active_ruleset | INC-04 |
| M003 | `hub/decision/migrations/M003_decision_crosswalk.sql` | `python -m hub.decision` (schema module) | `decision_schema_migrations` | decision_events, evidence_record, case_state, crosswalk_link, crosswalk_link_event, decision_idempotency | INC-05 |
| M004 | `hub/intake/migrations/M004_intake.sql` | `python -m hub.intake` (schema module) | `intake_schema_migrations` | raw_intake, intake_outcome (+ addendum columns), intake_item_attr, intake_run_event | INC-06 |
| M005 | `hub/runs/migrations/M005_runs_metrics.sql` | `python -m hub.runs` (schema module) | `runs_schema_migrations` | run_event, metric_definition, metric_value, obs_metric | INC-07 |
| M006 | `hub/web/migrations/M006_web_gate_review.sql` | `hub.web migrate` | `web_schema_migrations` | service_token, service_token_revocation, rule_trace, flag_action | INC-08 |
| M007 | `hub/search/migrations/M007_search_r2.sql` | `python -m hub.search` (schema module) | `search_schema_migrations` | search_doc, search_corpus_load, consistency_finding, review_draft; FTS5 virtual tables are derived objects built by the corpus loader | INC-09 |
All forward-only with backup-before-migrate; rollback = backup restore (INC-09 also `drop-index`). Seven version tables and per-package runners deviate from the Stage 14 single-runner plan (IA-06; S16-D03). `hub/security/scan.py` RETAINED_TABLES misses `intake_item_attr`, `intake_run_event`, `run_event`, `metric_value`, `metric_definition`, `obs_metric` (RTD-54, RTD-63).

**IC-5 Token and credential formats** [Verified Fact] (INC-08 D-04..D-07; values Assumption A-INC08-1..5 for Stage 24)
- Session: opaque token from `os.urandom`; stored hashed; cookie `hub_session` (HttpOnly, SameSite=Strict, Path=/, **no `Secure` flag over loopback HTTP**); login response body also returns `token` and `csrf_token`.
- Service token: prefix `svc_`, role integration, never Zone H; only SHA-256 stored; shown once at issue (`python -m hub.web token issue`); revocable by token or 8-hex digest prefix; optional expiry.
- CSRF: JSON writes need header `X-Hub-Request: 1`; form posts need `csrf_token = sha256("csrf:" + session digest)` (derived, not stored); login POST has none.
- Re-auth: `reauth_token = sha256("reauth:" + session digest + ":" + reauth_at)` from OP-SEC-05; window `zone_h.reauth_window_seconds`.
- Passwords: PBKDF2, 600,000 iterations (proposal, RTD-26).

**IC-6 Audit actions and event types added** [Verified Fact] CONFIG_LOADED, ZONE_H_ATTEMPT, ZONE_H_REFUSED, POLICY_SEEDED, POLICY_VERSION_CREATED, POLICY_ADOPTED, POLICY_ACCEPTED_OPEN, POLICY_DECISION_RECORDED, POLICY_SCHEMA_APPLIED, RULESET_LOADED, RULESET_ACTIVATED, RULESET_DEACTIVATED, CONTRACT_BINDING_CHANGED, CONTRACT_VIOLATION, SCHEDULE_CHANGED, SEARCH_SCHEMA_APPLIED, SEARCH_CORPUS_LOADED, SEARCH_CORPUS_DROPPED, C3_READ, RULE_DIVERGENCE_REPORTED, CONSISTENCY_CHECK_RUN, DRAFT_CREATED (from `hub/` string constants; RTD-38, RTD-58, RTD-78).

**IC-7 API and schema additions** [Verified Fact] Query parameters `reason` (C3 reads), `view` (freshness), `as_of`, `window_start`, `window_end`, `source`, `kind` (OP-MET-03); response fields `engine_reason`, `depth_capped`, `null_outputs`, `count`; OP-MET-01 `{items: [...]}`; OP-INT-01 envelope names `source_key, partner, schema_rev, source_ts, ref_id, record_kind, payload_text` (+ optional `idempotency_key`) (DEV-80, DEV-83, DEV-94, DEV-98). JSON schemas: `intake-outcome` needs `contract_missing`, `conflicts_with`, `reason_detail`; `metric-value` needs `detail`; storage-to-schema mapping 0/1 -> boolean, JSON text -> object, BLOB -> base64 (data-contract-results DC-02, A-16-DC-1). Route registry must be regenerated when OpenAPI changes (RTD-35).

**IC-8 Runtime** [Verified Fact] OD-24: production target Python 3.12+; code keeps the 3.10 / SQLite 3.37 floor; runtime self-check refuses below floor (E-CO-RUNTIME-UNSUPPORTED, exit 8). ADR-018's 3.12 statement holds for production; the floor is a compatibility floor for tests and goldens.

### IP-6 Deviation-register addendum (recorded, NOT approved - OD-24)
All rows `proposed`; preserve-or-fix per row is OD-S12-13 (accepted open, decided at Stage 30). Source: `hub/coexistence/seed_inc02.json`; Stage 16 BD register.
| DV | Golden ref | Legacy value | New value (observed at 2c63b07) | Register action | CUT step | Tag |
|---|---|---|---|---|---|---|
| DV-01 | CT-12 sql_report_1_total_gross | 742956.61 | 622826.44 | none | CUT-4 | [Verified Fact] |
| DV-02 | CT-08 replayed source message | 64 DUPLICATE | 67 NOOP_DUPLICATE, 0 REVISED_CONFLICT (3 REPLAY rows legacy-REJECTED first) | none | CUT-3 | [Verified Fact] |
| DV-03 | CT-08 quantity out of range | 154 REJECTED | 161 items flagged NEGATIVE_VALUE, kept (DEV-58) | none | CUT-3 | [Verified Fact] |
| DV-04 | CT-11 java_tiny count | "2390" (10 skipped silently) | 2,390 + 10 QUARANTINED UNPARSABLE_AMOUNT | none | CUT-4 | [Verified Fact] |
| DV-05 | CT-13 allows[7:9] | 'abc' false / null true | E-POL-INPUT-INVALID (= DEV-30) | none | CUT-2 | [Verified Fact] |
| DV-06 | CT-13 table[0] | APAC 2019 999999 | 999999 `defaulted: true` | none | CUT-2 | [Verified Fact] |
| DV-07 | CT-08 partner_status_after_all | ACCEPTED 7917 / DUPLICATE 64 / REJECTED 586 | legacy table untouched; append-only outcomes | **DV-07a (text extension):** "new value also includes outcome classification: EXCEPTION 8,109 (UNMATCHED_REF 7,903, NO_BUSINESS_KEY 206), QUARANTINED 223, VALIDATED 165, VALIDATED_WITH_FLAGS 3, NOOP_DUPLICATE 67" | CUT-3 | [Verified Fact] |
| DV-08 | CT-10 shift distinct objects | 118 | 500 (reference query; weak evidence, no batch job built) | none | CUT-4 | [Verified Fact] |
| DV-09 | CT-07 lib.missing_field | invalid 1, not stored | quarantined 1, stored | **label correction:** reason `MISSING_ENVELOPE_FIELD` (not `envelope_invalid`) | CUT-3 | [Verified Fact] |
| **DV-10 (new, proposed)** | CT-08 partner outcomes | most rows ACCEPTED (legacy never checks ref_id) | exact ref_id matching -> EXCEPTION / UNMATCHED_REF for unmatched items (BEH-INT-08, AC-INT-18) | register | CUT-3 | [Verified Fact] |
| **DV-11 (new, proposed)** | JS threshold partial year (no golden; INC-04 S05 live run) | `threshold('APAC', 202 / 2 / '')` -> 15000 (prefix match) | 999999 `defaulted: true` (4-digit year required) (DEV-29) | register | CUT-2 | [Verified Fact] |
[Inference] DV-10 and DV-11 numbering follows the Stage 16 proposal; the register itself (DB rows) is not changed by this document - adding the rows is build work at the next increment touching the coexistence seed (Stage 18 plans it).

### IP-7 Decision register (decided / default-accepted / accepted open)
Owner of every open item: **Engagement lead (Dinesh Naik)**. "Accepted open" = recorded open on OD-22 / this PRD, the product carries a non-adopting default.
| ID | Decision | Status | Shipped default / effect | Source | Needed by |
|---|---|---|---|---|---|
| OD-08 | No-AI | **Decided** (Dinesh 2026-10-18) | no model calls | OD-08 | — |
| OD-09 | Baseline dataset = shipped 125 cases, seed 4100 | **Decided** | FX-BASE125 | OD-09 | — |
| OD-S12-14 / OPD-13 | Initial PRD approval | **Decided** ("Approve, refine at Stage 17") | this PRD | OD-22 | — |
| OD-S12-17 | Intake identity key | **Decided**: (partner, record_kind, ref_id, source_ts) | built | OD-18 | — |
| OD-S12-12 | Runtime | **Decided**: production 3.12+, code floor 3.10 | floor enforced | OD-24 | Stage 27 work |
| Stage 16 gate | Accept CONDITIONAL PASS; conditions to Stages 24/26/30 | **Decided** | — | OD-24 | — |
| TST-REV-03/04/08 | Human walkthroughs | **Decided: stay open until Stage 26 TEVV** | automated stand-ins | OD-24 | Stage 26 |
| DV register corrections | record DV-07a, DV-09 label, DEV-29 row | **Decided: record, do not approve** | IP-6 | OD-24 | — |
| OD-S12-01 / OPD-01 | Definitions closed / resolved / approved | Accepted open | candidates only | OD-22 | any KPI target, CUT-1/4 |
| OD-S12-02 / OPD-02 | 48 h clock | Accepted open | no verdict | OD-22 | CUT-4 |
| OPD-03 | Speed-vs-evidence decider | Accepted open | FAIL-02 rule | OD-22 | KPI targets |
| OD-S12-03 | Closing-state set without policy | Default accepted (OD-12); content accepted open | treat_label_CLOSED_as_closing | OD-12 | CUT-1 |
| OD-S12-04 / OPD-04 | Rule authority, active set, 999,999 default | Accepted open | 3 sets inactive | OD-16, OD-22 | CUT-2 |
| OD-S12-05 / OPD-05 | Disposition recording location | Accepted open | mode `none` | OD-20, OD-22 | Zone H use |
| OD-S12-06 / OPD-06 | Zone H holders; user admin | Accepted open | holders [] | OD-22 | any adoption / activation |
| OD-S12-07 / OPD-07 | Evidence sufficiency, exception rule | Accepted open | structural presence | OD-12 | CUT-1 |
| OD-S12-08 / OPD-08 | Month-end cut-off, denominator, cost source | Accepted open | required params; cost not available | OD-12 | CUT-4, FR-MET-08 |
| OD-S12-09 / OPD-09 | Retention | Accepted open | hold-all | OD-15, OD-22 | any deletion |
| OD-S12-10 / OPD-11 | Scheduler vs HAR-10 | Accepted open | schedule OFF | OD-19, OD-22 | CUT-5 |
| OD-S12-11 | Source contract scope / owner; contract vs data (DC-04) | Accepted open | record_only | OD-10(d), OD-12 | CUT-3 |
| OD-S12-13 | Preserve-or-fix DV-01..DV-11 | Accepted open | all proposed; golden-compare exit 6 | OD-15, OD-17 | Stage 30 |
| OD-S12-15 | Who records ops-closed / evidence-complete | Accepted open | human_only | OD-12 | CUT-1 |
| OD-S12-16 | Legal transition table | Accepted open | structural | OD-12 | CUT-1 |
| OD-S12-18 | Audit anchor location (real deployment) | Accepted open | config file path | OD-15 | Stage 24 |
| OD-S12-19 | Case creation path | Accepted open | backfill only | OD-12 | CUT-1 |
| OPD-10 | Buy vs build | Accepted open | not evaluated | — | Stage 33 / FINAL |
| OPD-12 | Labelled search question set; RQ-1..RQ-3 | Accepted open | generated set, baseline only | — | R2 FR-REV-03 enable |
| OPD-14 | Performance targets | Accepted open | measure only | OD-22 | Stage 31 |
| OPD-15 | Parallel legacy-customer workflow owner | Accepted open | protected | — | Stage 37 |
| OPD-16 | Synthetic capstone vs real organisation | Accepted open | all labelled synthetic | — | Stage 34 |
| RTD-26 / A-INC08-1..5 / RTD-83 | Security control values, token / cookie choices, field classes | Accepted open | proposals | — | Stage 24 |
| HAR-13 | Approval of IC-1..IC-8 as Stage 12 v0.2 | Accepted open | addendum recorded here | — | Stage 23 |
| PCH-22 | FR-REV-04 keep / reject | **Proposed** (needs answer) | off | RTD-87 | FINAL |
| PCH-31 | PNFR-13 target wording | **Proposed** | existing fixtures | DEV-89 | Stage 26 |
| PCH-47 | Accept this implementation baseline | **Proposed** | — | this stage | before Stage 18 relies on it as final |

### IP-8 Corrections list for earlier (frozen) stages
| Source | Statement | Correction | Ref |
|---|---|---|---|
| Stage 12 brief / downstream citations | 41 R1 / 11 R2 | 43 / 9 | PCH-02, IA-01 |
| Stage 11 DC-03; ADR-008 | identity = feed_id/business_key | natural key (OD-18) | IA-02 |
| ADR-018 | Python 3.12 | production 3.12+, code floor 3.10 (OD-24) | IA-03 |
| Stage 11 DQ / Stage 9 FR-INT-04 | contract enforceable on all sources | per-source binding, record_only default | IA-04 |
| Stage 14 schema-migration-plan | single runner | 7 version tables (IC-4) | IA-06 |
| Stage 12 schemas / error registry | complete, freezable | IC-2, IC-7 addenda | IA-07, IA-08 |
| Deviation seed DV-07 / DV-09 | text / label | IP-6 | IA-09, IA-10, IA-11 |
| Stage 13 coverage note | CT-11 needs JDK, absent | JDK 11 present | IA-19 |

### IP-9 Constraints and dependencies (updated)
[Verified Fact] CON-01 (synthetic, one human), CON-02 (FX-BASE125), CON-03 (sandbox-only execution), CON-06 (HAR-06 / HAR-11), CON-07 (loopback), CON-08 (KPI proxies) unchanged. CON-04 superseded (harness exists, PCH-37). CON-05 extended by NFR-RT (OD-24). DEP-01 closed (design-both, PCH-38); DEP-02 met (INC-01); DEP-03 still open (OPD-01..04 accepted open). New: DEP-04 CI fixture provisioning for the git-ignored FX-BASE125 data (RTD-01) before CI can run the harness; DEP-05 test-suite device cap (group C ~145 s of 180 s, OD-21) - split before adding load.

## Companion artifacts
`prd-change-log.md`, `prioritized-capabilities.md`, `finalized-nfrs.md`, `release-boundaries.md`, `finalized-acceptance-criteria.md`, `invalidated-assumptions.md`, `implementation-baseline-signoff.md` (all `docs/17-implementation-prd/`).

## Evidence References
See `evidence_sources`; IC tables were produced by reading `hub/` source at 8a8e8db (grep of `exit_code` assignments, settings docstrings, audit constants, migration directories). Reproduce: `grep -rhoE 'code, exit_code(, http)?, message = "E-[A-Z0-9-]+", [0-9]+' hub`.

## Assumptions
- A-17-IP-1 [Assumption] Code-derived addendum tables (IC-1..IC-8) are the right source of truth until a Stage 12 v0.2 is issued. Confirm: Engagement lead (Dinesh Naik) (HAR-13).
- A-17-IP-2 [Assumption] Staged R1 entry by CUT step (release-boundaries.md A-17-RB-1). Confirm: Engagement lead (Dinesh Naik).
- A-09-01..A-09-06 (carried) remain assumptions.

## Unknowns
- U-09-01..U-09-05 (carried): definitions, rule owner, disposition location, real volumes/costs, document Q&A need, retention, performance, parallel-workflow owner.
- U-17-IP-1 Behaviour of the legacy estate and FTS5 on the 3.12+ production runtime (ENV-4/6, RTD-79).
- U-17-IP-2 Owner of `source-contract-v1` and whether contract or data is wrong (DC-04).

## Unresolved Issues
- Engagement-lead acceptance of this implementation baseline (PCH-47); PCH-22, PCH-31.
- P1 pre-cutover work: observed golden probes, CI on 3.12+, release gates, security test gaps (prioritized-capabilities.md PS-01).

## Residual Risks
- RR-IP-1 Single author / single approver (PR-10): no independent challenge of this reconciliation (Medium).
- RR-IP-2 A large accepted-open set means most consequential behaviour is unverifiable until decisions are taken; tests green on defaults may need rework (Medium).
- RR-IP-3 Implementation baseline could be mistaken for the as-built PRD; FINAL (Stage 43) alone dispositions requirements (Low; labelled).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue (incorporates OD-24, recorded during the stage). |
