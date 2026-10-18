---
stage: "12 — Spec-Driven Design"
artifact: "system-spec.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/target-architecture.md", "docs/10-architecture/component-model.md", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/09-initial-prd/capability-map.md", "docs/12-specs/features/", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

System-level behaviour: context and boundaries, zones, safe fresh-install state, case lifecycle, six main flows, 12 testable system invariants, the open-decision mode table, and coverage of all 52 FRs (43 R1 / 9 R2) by ten features.

## Findings
### SYS-1 Purpose and boundaries [Verified Fact: requirements; Inference: design]
The target system is a **No-AI (OD-08) modular monolith built beside the legacy estate** (ADR-001, ADR-003): a decision-and-evidence record, a human disposition gate, a policy/rule service, a safe intake pipeline, an identity crosswalk, idempotent runs, definition-tagged metrics, reviewer support, access/audit and a coexistence harness. It reads the legacy SQLite files read-only; it writes only to its own `hub.sqlite3`, audit anchor and logs. It performs **no model call and no non-loopback network call**. It never decides, pre-fills, simulates or auto-triggers a batch disposition, QA release or e-signature (FR-GATE-01).

In scope (R1, 43 FRs): F01-F10 as specified. R2 (9 FRs): FR-POL-05, FR-INT-08, FR-ID-03, FR-ID-04, FR-MET-07, FR-MET-08, FR-REV-03, FR-REV-04, FR-SEC-03. Out of scope: AI features (NG-01..NG-04), the legacy customers' parallel workflow (FR-CO-02), real e-signature (HAR-12), buy-vs-build evaluation (OPD-10), SSO, cloud deployment, a visual dashboard.

### SYS-2 Context (text diagram)
```
 humans (reviewer, quality_lead, compliance, finance_read, dispositioner)
        | HTTPS-capable, loopback by default           service principals (integration, scheduler/OS cron)
        v                                                    |
 +--------------------- hub process (stdlib) ------------------v-------------+
 | C1 HTTP/UI  -> services (C3 Decision, C4 Policy/Rules, C5 Gate[Zone H],     |
 |                C6 Intake, C7 Crosswalk, C8 Runs, C9 Metrics, C10 Review)    |
 |                C2 Access+Audit (called by every write)                       |
 | repositories -> hub.sqlite3 (insert-only event tables + projections)         |
 | C11 adapters (READ-ONLY) -> legacy.sqlite3, enterprise_legacy.sqlite3,       |
 |                 documents/archive files, source gateway (loopback), CSV      |
 +-----------------------------------------------------------------------------+
 outputs: audit anchor file (outside DB dir), JSON logs, backups (file copy + SHA-256)
 NOT present: model/LLM calls, outbound internet, message broker, legacy writes
```

### SYS-3 Zones (Stage 8 B-1) and where each requirement lives
| Zone | Meaning | Components / actions |
|---|---|---|
| H (human only) | accepted only from an authenticated human holder | C5 `GateService`; ZH-01..ZH-10 |
| D (deterministic) | pure rules, validation, arithmetic, templates | C2-C4, C6-C11 |
| A (AI-eligible) | none admitted | empty (ADR-002) |

### SYS-4 Fresh-install state (safe by default) [testable: AC-GATE-01, AC-POL-01, AC-RUN-02, AC-SEC-04]
| Item | Value on a fresh install |
|---|---|
| Users | none (created offline by operator) |
| Zone H holders | empty -> Zone H unavailable |
| `disposition.mode` / `values` | `none` / empty |
| Policy objects | 3 DEFINITION + 2 CLOCK candidates; **none adopted** |
| Active rule sets | none; three as-found sets loaded read-only |
| Closure unconfigured behaviour | `treat_label_CLOSED_as_closing` (fail closed) |
| Schedule | disabled |
| Contract bindings | `record_only` for all sources |
| Network bind | 127.0.0.1 |
| Data origin label | `synthetic` -> every KPI labelled 'synthetic, unvalidated' |
| Retention | hold-all (no delete path) |

### SYS-5 Case lifecycle (behavioural)
State vocabulary `case_status` = OPEN, UNDER_REVIEW, CLOSED, ESCALATED, REOPENED (as found; no cross-vocabulary mapping). Transition rules are data (`structural` mode by default, OD-S12-16). Normative constraints:
```
 any state --STATUS_CHANGE--> state'            (distinct state; event appended)
 CLOSED* --REOPEN(basis)--> REOPENED, cycle+1   (only via REOPEN event)
 any --> closing state: needs evidence ref OR Zone H CLOSE_EXCEPTION
 (*) 'closing' set = active CLOSURE policy, else closure.unconfigured_behaviour (SBR-DEC-03)
 facts (no state change): FACT_RECEIVED, FACT_OPS_CLOSED, FACT_EVIDENCE_COMPLETE per cycle
 Zone H (human holder only): DISPOSITION / QA_RELEASE / ESIGNATURE record, CLOSE_EXCEPTION
```
Elapsed time under any configured clock is computed from facts, never from the word 'closed' (FR-DEC-06).

### SYS-6 Main flows
1. **Intake** -> receive raw (append) -> identity/hash check (NOOP or conflict) -> validate (envelope, payload, contract) -> classify (reason codes) -> match via crosswalk -> outcome appended -> exception queue (human) (F04, F05, F08).
2. **Review** -> reviewer opens queue item -> rule trace explains triage (F03/F08) -> may override with reason (F02) -> attaches evidence -> records facts -> changes state with evidence (F01).
3. **Disposition** (only when holders and mode are configured) -> holder opens read-only evidence pack -> re-authenticates -> posts ZH-01 with `pack_hash` -> event (mode event) or external reference (mode external_ref) + audit (F02).
4. **Policy** -> candidate created -> Zone H adoption or recorded 'accepted-open' -> every figure shows tag and policy version (F03, F07).
5. **Run** -> operator/service triggers job -> run record, checkpoint, backlog -> metrics (F06, F07).
6. **Release** -> golden compare, replay gate, audit/projection verify, No-AI tripwire, rollback rehearsal (F10).

### SYS-7 System invariants (each has at least one acceptance criterion)
| ID | Invariant | Verified by |
|---|---|---|
| INV-01 | No Zone H event exists unless authored by an authenticated human holder | AC-GATE-09, 11, 12 |
| INV-02 | Retained records are never updated or deleted | AC-DEC-02, 03, AC-INT-02, AC-SEC-13, AC-NFR-10 |
| INV-03 | Case state equals the fold of its events | AC-DEC-05 |
| INV-04 | raw_intake count equals items received; duplicates change no queue or total | AC-INT-01, 04, AC-NFR-11 |
| INV-05 | No policy is adopted, no rule set active, no holder, no mode, no schedule at fresh install | AC-GATE-01, AC-POL-01, AC-RUN-02 |
| INV-06 | No model call, no non-loopback egress | AC-CO-11, 12, AC-OBS-06 |
| INV-07 | Every KPI is tagged where required, documented, reproducible, labelled | AC-MET-01, 02, 14, 15 |
| INV-08 | Audit chain verifies; tamper is detected | AC-SEC-10, 11 |
| INV-09 | Legacy files and the baseline checksum manifest are unchanged by any run | AC-CO-05, 07 |
| INV-10 | Untrusted text never alters any decision, status, priority, queue, approval or disposition | AC-INT-22, 24, AC-GATE-13 |
| INV-11 | Defaults are always visible (defaulted / partial / limit_reached / not_configured) | AC-POL-19, AC-MET-12, AC-RUN-08, AC-DEC-28 |
| INV-12 | Identical inputs give bit-identical outputs for core paths | AC-POL-22, AC-CO-13 |

### SYS-8 Open-decision modes (summary; full register in spec-readiness.md)
| Decision | Mode A (specified, tested) | Mode B (specified, tested) | Default shipped |
|---|---|---|---|
| Disposition recording (OD-S12-05) | `event` | `external_ref` | `none` (blocked) |
| Closure when no policy active (OD-S12-03) | `treat_label_CLOSED_as_closing` | `none` | A (fail closed) |
| Contract scope (OD-S12-11) | `record_only` | `enforce` (per source) | `record_only` |
| Schedule (OD-S12-10) | disabled / manual only | enabled for non-Zone-H jobs via ZH-09 | disabled |
| Transition table (OD-S12-16) | `structural` | strict table | `structural` |
| Search engine (OD-S12-12) | FTS5 | fallback | auto-detect |
| Definitions, 48 h clock, approval-rule authority, evidence sufficiency, cut-off, retention | mechanism only; no adopted value | | none adopted |

### SYS-9 Feature and requirement coverage (52 FRs; 43 R1, 9 R2)
| Feature | FR count | FRs (release) |
|---|---|---|
| F01 | 6 | FR-DEC-01(R1), FR-DEC-02(R1), FR-DEC-03(R1), FR-DEC-04(R1), FR-DEC-05(R1), FR-DEC-06(R1) |
| F02 | 6 | FR-GATE-01(R1), FR-GATE-02(R1), FR-GATE-03(R1), FR-GATE-04(R1), FR-GATE-05(R1), FR-GATE-06(R1) |
| F03 | 6 | FR-POL-01(R1), FR-POL-02(R1), FR-POL-03(R1), FR-POL-04(R1), FR-POL-05(R2), FR-POL-06(R1) |
| F04 | 8 | FR-INT-01(R1), FR-INT-02(R1), FR-INT-03(R1), FR-INT-04(R1), FR-INT-05(R1), FR-INT-06(R1), FR-INT-07(R1), FR-INT-08(R2) |
| F05 | 4 | FR-ID-01(R1), FR-ID-02(R1), FR-ID-03(R2), FR-ID-04(R2) |
| F06 | 3 | FR-RUN-01(R1), FR-RUN-02(R1), FR-RUN-03(R1) |
| F07 | 8 | FR-MET-01(R1), FR-MET-02(R1), FR-MET-03(R1), FR-MET-04(R1), FR-MET-05(R1), FR-MET-06(R1), FR-MET-07(R2), FR-MET-08(R2) |
| F08 | 4 | FR-REV-01(R1), FR-REV-02(R1), FR-REV-03(R2), FR-REV-04(R2) |
| F09 | 3 | FR-SEC-01(R1), FR-SEC-02(R1), FR-SEC-03(R2) |
| F10 | 4 | FR-CO-01(R1), FR-CO-02(R1), FR-CO-03(R1), FR-CO-04(R1) |
All 52 FRs and 20 PNFRs are covered by at least one acceptance criterion (acceptance-criteria.md coverage check).

### SYS-10 Glossary
Case, event, fact, evidence record, policy object, rule set, clock, Zone H, holder, pack_hash, identity key, content hash, quarantine, orphan, definition tag, run record, checkpoint, tripwire. Terms follow docs/11-data-context/knowledge-model.md; 'closed' has no adopted meaning in this system.

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-SYS-1 The R1/R2 split (43/9) is the Stage 9 proposal (A-09-02). The orchestrator brief quoted 41/11; the Stage 9 register parses to 43 R1 and 9 R2 (40 Must + 3 Should in R1; 7 Should + 2 Could in R2). The register is used.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-SYS-1 Target deployment host, scheduler and operator roles are unknown.

## Unresolved Issues
- Approval of PRD/R1-R2 split (OPD-13) is still open.

## Residual Risks
- System spec is a design view; Stage 13 may regroup features without changing IDs.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
