---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "open-items-and-decision-register.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/approvals-register.json", "docs/38-handover/open-handover-items.md", "docs/41-retirement/decommission-checklist.md", "docs/27-hardening/hardening-plan.md", "docs/28-reliability/resilience-readiness.md", "docs/31-observability/observability-validation.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/39-drift/improvement-backlog.md", "docs/29-incident-bcdr/incident-readiness.md", "docs/35-variance/corrective-action-backlog.md", "docs/12-specs/spec-readiness.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
Single register of the final open items and decisions: 40 release approvals (all OPEN), 21 handover items, 16 retirement decisions, carried D-27/D-28/D-31/D-34/D-39 decisions, Stage 29/35/36/42 lists, the 19 spec decisions with their state, and pointers to the risk registers. Everything is OPEN; nothing is decided here. (Extra artifact beyond the prompt's 19, requested by the engagement lead.)

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OI-1 How to read this register
[Verified Fact] Consolidates every open decision and item family that earlier stages left to Dinesh Naik. Owner of every row: **Engagement lead (Dinesh Naik)** unless stated. **Every row is OPEN**; no row is decided by this document. 'Agent default' means what the build ships or the agent recommended; it is an Assumption (OD-32 covers scope/sequencing only, never risk acceptance, holders, cutover or irreversible steps). Rows are copied from the source files named in each heading and truncated; the source file is authoritative. Counts (extracted by script from the source tables): D-27 9, D-28 10, D-31 10, D-34 8, D-39 9, D-41 16, HO 21, Q-29 9, C-1..C-7 7, CA 17, approvals 40.

### OI-2 Release approvals register (40 records; all OPEN; 0 APPROVED)
Source: `docs/30-release/evidence/approvals-register.json` (schema hub-release-approvals/v1). Composition: 22 release-scope (AP-REL-01, AP-GATE-G1..G10, AP-OPS-01..11) + 18 cutover-step (AP-DV-01..11, AP-CUT-1..5, AP-OPS-12, AP-OPS-13). A record counts only when APPROVED with a named human approver, approval_ref, approved_on and evidence_ref (`hub.release.gonogo.approval_problems`). Release criteria today: technical 16 pass, G1 / T-09 / T-10 fail, T-05 not run; evaluator = **NO-GO**.

| ID | Title | Scope | Agent-recommended default | Status | Approver / ref / date |
|---|---|---|---|---|---|
| AP-REL-01 | Release decision (go / no-go) for the hub in shadow mode | REL | no-go until every technical criterion passes and AP-GATE-*, AP-OPS-* (REL) are recorded | **OPEN** | None/None/None |
| AP-GATE-G1 | Human acknowledgement of the evidence for gate G1: golden diff: unapproved differences = 0 | REL | acknowledge only after reading the evidence file named in gate-results.json; G1 cannot pass while any DV row is proposed | **OPEN** | None/None/None |
| AP-GATE-G2 | Human acknowledgement of the evidence for gate G2: replay-safety suite (AC-INT-04/05) passes | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G3 | Human acknowledgement of the evidence for gate G3: verify-audit ok | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G4 | Human acknowledgement of the evidence for gate G4: verify-projection 0 mismatches | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G5 | Human acknowledgement of the evidence for gate G5: No-AI tripwire: deny-list clean, no egress, model_calls_total = 0 | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G6 | Human acknowledgement of the evidence for gate G6: secret scan 0; deletion-path grep 0 | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G7 | Human acknowledgement of the evidence for gate G7: backup/restore rehearsal checksum match | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G8 | Human acknowledgement of the evidence for gate G8: Zone H negative tests (AC-GATE-09/11/12) pass | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G9 | Human acknowledgement of the evidence for gate G9: planted-string fixture suite (86/22/44) 0 effects | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-GATE-G10 | Human acknowledgement of the evidence for gate G10: determinism: bit-identical across PYTHONHASHSEED/TZ/locale | REL | acknowledge after reading the evidence file named in gate-results.json | **OPEN** | None/None/None |
| AP-DV-01 | Preserve-or-fix decision for DV-01: SQL month-end total 742,956.61 (join fan-out) becomes 622,826.44 | CUT step CUT-4 | fix (adopt the hub figure) for CUT-4; keep legacy report running as comparator | **OPEN** | None/None/None |
| AP-DV-02 | Preserve-or-fix decision for DV-02: replayed message: legacy DUPLICATE 64 becomes NOOP_DUPLICATE 67 / REVISED_CONFLICT | CUT step CUT-3 | fix | **OPEN** | None/None/None |
| AP-DV-03 | Preserve-or-fix decision for DV-03: quantity out of range: legacy REJECTED 154 becomes NEGATIVE_VALUE flag, item kept | CUT step CUT-3 | change of class: adopt as built | **OPEN** | None/None/None |
| AP-DV-04 | Preserve-or-fix decision for DV-04: Java blank amounts: silently skipped becomes UNPARSABLE_AMOUNT quarantine | CUT step CUT-4 | fix | **OPEN** | None/None/None |
| AP-DV-05 | Preserve-or-fix decision for DV-05: JS tolerance with 'abc' / null becomes E-POL-INPUT-INVALID | CUT step CUT-2 | fix | **OPEN** | None/None/None |
| AP-DV-06 | Preserve-or-fix decision for DV-06: unknown region / year 999999 becomes the same value marked defaulted | CUT step CUT-2 | accept the additive marker | **OPEN** | None/None/None |
| AP-DV-07 | Preserve-or-fix decision for DV-07: reconcile overwrites status in place becomes append-only outcomes (DV-07a: outcome classification EXCEPTION 8,109 etc.) | CUT step CUT-3 | fix, after Dinesh has seen the 7,903 UNMATCHED_REF volume | **OPEN** | None/None/None |
| AP-DV-08 | Preserve-or-fix decision for DV-08: night-shift distinct objects 118 vs 500 (reference query, no batch job built; weak evidence) | CUT step CUT-4 | do not cut over this figure; keep legacy authoritative until a hub job exists | **OPEN** | None/None/None |
| AP-DV-09 | Preserve-or-fix decision for DV-09: invalid gateway event: counted, not stored becomes quarantined, stored (label MISSING_ENVELOPE_FIELD) | CUT step CUT-3 | fix, with the corrected label | **OPEN** | None/None/None |
| AP-DV-10 | Preserve-or-fix decision for DV-10: partner outcomes: exact ref_id matching, most legacy-ACCEPTED rows become EXCEPTION / UNMATCHED_REF (proposed row) | CUT step CUT-3 | fix (exact match, BEH-INT-08) | **OPEN** | None/None/None |
| AP-DV-11 | Preserve-or-fix decision for DV-11: JS partial-year threshold: prefix match 15000 becomes 999999 defaulted (proposed row, DEV-29) | CUT step CUT-2 | fix (4-digit year required) | **OPEN** | None/None/None |
| AP-CUT-1 | Decision to make 'decision and evidence record, audit' authoritative (CUT-1) | CUT-1 | decide last of the value-bearing steps only after the Zone H and closure questions are answered; keep shadow until then | **OPEN** | None/None/None |
| AP-CUT-2 | Decision to make 'rule evaluation' authoritative (CUT-2) | CUT-2 | first step in the recommended order (CUT-2, CUT-1, CUT-3, CUT-4, CUT-5); needs DV-05, DV-06, DV-11 and OD-S12-04 | **OPEN** | None/None/None |
| AP-CUT-3 | Decision to make 'intake and reconcile outcomes' authoritative (CUT-3) | CUT-3 | after CUT-1 and CUT-2; needs a named consumer and a decision to stop the in-place legacy reconcile | **OPEN** | None/None/None |
| AP-CUT-4 | Decision to make 'metrics, month-end and night-shift figures' authoritative (CUT-4) | CUT-4 | after CUT-3; needs consumers named and the OD-S12-01/-02/-08 definitions | **OPEN** | None/None/None |
| AP-CUT-5 | Decision to make 'automation and exposure' authoritative (CUT-5) | CUT-5 | last; keep loopback-only and the scheduler off unless Dinesh decides otherwise (D-27-09, HAR-10) | **OPEN** | None/None/None |
| AP-OPS-01 | target host and promotion path named and approved (environment-promotion-plan.md) | REL | there is no production host; name one or accept shadow-on-the-laptop as the only environment | **OPEN** | None/None/None |
| AP-OPS-02 | rollback authority, rollback triggers and who may call them | REL | Dinesh is the only rung (F-29-07); record that explicitly | **OPEN** | None/None/None |
| AP-OPS-03 | cutover window, change freeze and communications | REL | no window exists; choose one only when a real consumer exists | **OPEN** | None/None/None |
| AP-OPS-04 | off-device copy of the baseline and the hub backups (HAR-09, F-29-02) | REL | approve an encrypted off-device copy (HAR-09) or accept the single-device risk in writing | **OPEN** | None/None/None |
| AP-OPS-05 | monitoring owner and alert channel for the release window (D-31-08, F-29-03) | REL | manual evaluation (RB-00) until a second human exists (D-31-08) | **OPEN** | None/None/None |
| AP-OPS-06 | manual walkthroughs TST-REV-03 / 04 / 08 signed or explicitly left open (D-27-08) | REL | leave open and say so, or perform and sign the three walkthroughs | **OPEN** | None/None/None |
| AP-OPS-07 | runtime floor and Python 3.12+ evidence (D-27-02) | REL | keep the 3.10 floor as shipped; run 3.12 / 3.13 evidence in the orchestrator cloud before any exposure | **OPEN** | None/None/None |
| AP-OPS-08 | install the hardening CI file under .github with pinned SHAs, or not (D-27-03, HAR-07) | REL | do not install CI now; decide with the SHA pins when a remote exists | **OPEN** | None/None/None |
| AP-OPS-09 | legacy Dockerfile / compose hardening, or leave the legacy files as they are (D-27-06) | REL | leave the legacy files unchanged (frozen path); the hardened recipe is in deployment-strategy.md as a proposal | **OPEN** | None/None/None |
| AP-OPS-10 | wire the Stage 28 / 31 mechanisms before release, or release without them (D-28-01, D-28-02, D-31-01, D-31-02) | REL | release without wiring (as built); wiring is a separate approved change | **OPEN** | None/None/None |
| AP-OPS-11 | residual risks RS / RP / VA / RTR / F-xx accepted, rejected or carried (none is accepted by any stage) | REL | carry every risk as open; accept none by default | **OPEN** | None/None/None |
| AP-OPS-12 | consumers of the legacy outputs identified and a re-pointing owner named (U-14-01) | CUT-2/CUT-3/CUT-4 | name the consumers or keep CUT-2..CUT-4 closed | **OPEN** | None/None/None |
| AP-OPS-13 | real Zone H holders named, only if the Zone H gate is to be used (OD-S12-05 / 06, HAR-12) | CUT-1 | keep holders empty; the Zone H gate stays unused | **OPEN** | None/None/None |

### OI-3 Stage 38 handover items HO-01..HO-21
Source: `docs/38-handover/open-handover-items.md`. HO-01..HO-03 are the three blocking conditions of the Stage 38 gate.

| ID | Open handover item | Owner / source | Status |
|---|---|---|---|
| HO-01 | **Name the receiver.** Accept RL-01/RL-02 steady-state yourself, or name a receiving party; 0 of 28 assets have an accepted owner; 2 are VACANT (PA-25, PA-26) | Stage 38 purpose is moot without a receiver; Stage 37 gap carried here | OPEN |
| HO-02 | **Receiving operator passes OX-01..OX-10** (deploy, observe, diagnose, roll back L1/L2/L3, recover, contain, govern, No-AI) on a sandbox | Completion Gate condition 1 | OPEN |
| HO-03 | **Handover acceptance sign-off** recorded by an accepting owner | Completion Gate condition 2; Dinesh-owned and OPEN | OPEN |
| HO-04 | Who runs orchestrator duties (stage method, full regression, merges) after Stage 38; ties to Stage 39 U-39-02 | OD-34 | OPEN |
| HO-05 | Stage 30 release: 40 approvals OPEN, 0 APPROVED; DV-01..DV-11, CUT-1..CUT-5, AP-REL-01, G1..G10 acknowledgement, AP-OPS-01..13; then Stage 30 v0.2 | OD-37, `release-outcome.md` RO-2 | OPEN |
| HO-06 | Close or reopen the Stage 0B operating contract (draft OC-5, **not adopted**); GD-06, GD-07, GD-10, GD-15; steady-state ownership acceptance (GD-13); Stage 37 question: make owner acceptance a CUT-1 entry condition | OD-34, `operating-contract-closure.md` OC-3/OC-4 | OPEN |
| HO-07 | Vacant roles: RL-02..RL-11, RL-13 (service owner, process owner, Zone H dispositioner, risk/security, compliance, data, integration, finance, legacy technical owner, reviewers, independent verifier); and two ownerless assets PA-25 nightly exchange, PA-26 parallel workflow | Stage 37 | OPEN |
| HO-08 | Off-device backup (HAR-09, AP-OPS-04, F-29-02); live tabletop with human participants; RTO/RPO targets (Q-29-01..09, C-1..C-7) | OD-35 | OPEN |
| HO-09 | Carried decisions D-27-01..09, D-28-01..10, D-31-01..10, D-34-01..08; Stage 32 items (toolchain charges, hosting, effort, RL-09 holder); HAR-07 CI install under `.github` | OD-34..OD-36 | OPEN |
| HO-10 | Risk registers stay open and unaccepted: RS-01..RS-16, RP-01..RP-12, VA-01..VA-07 (PROPOSED), RTR-01..RTR-15, F-11, F-29-02..16, F-31-01..07; 3 open High vulnerabilities; surviving mutants M5, M9, M10 | OD-33..OD-36 | OPEN |
| HO-11 | Reviewer walkthroughs TST-REV-03/04/08 and RT-13 (UNSIGNED, need a human) | OD-24, OD-33, `walkthrough-records.md` | OPEN |
| HO-12 | Accept or reject the exit-17 behaviour change (F-29-01 fix, S30-DEV-01) and S30-DEV-02..09 | OD-37 | OPEN |
| HO-13 | Durable home for the git-ignored baseline (`data/*.sqlite3`, `data/lake/`) and for the Python 3.13 cloud workspace (provider Unknown, PA-18); VA-02..VA-04 | AHF-02, ENF-01 | OPEN |
| HO-14 | Python runtime: 3.12+ evidence absent; ADR-018 vs pyproject; D-27-02 | OD-24, OD-33 | OPEN |
| HO-15 | Stages 34, 35, 36 must be re-run as v0.2 once a real after-window exists; ROI/NPV/payback not computable; benefits sign-off BS-2 unsigned | OD-36 | OPEN |
| HO-16 | Preserve-or-fix decisions on DV-01..DV-11 (so `golden-compare` can exit 0) and OD-S12 open decisions (19 listed in `spec-readiness.md` RD-3) | OD-15, OD-37 | OPEN |
| HO-17 | Legacy knowledge: owner of the nightly file exchange "transferred 2024" (unnamed), INC-2025-014 follow-up, consumers of the 13 legacy outputs | PA-25, DR-27, OD-28 | OPEN |
| HO-18 | **Sequencing deviation.** Stages 39 (drift) and 40 (scale) are already merged (PRs #25, #26) although Stage 38 precedes them in the spine and the Stage 38 prompt says not to proceed to 39 on a blocking condition. They inherit this BLOCKED status for handover and BLOCKED release (OD-37) | Inference | OPEN |
| HO-19 | Exercise gaps OX-G1..OX-G6 (no install script, no read-only verify, observe not wired, kill switch for live server, no off-device exercise, Python 3.12+ untested) | Verified Fact | OPEN |
| HO-20 | Stage 38 did not re-execute any command (docs-only); command spellings come from CLI parsers and Stage 30 logs | Verified Fact | OPEN |
| HO-21 | Memory of the delivery method lives in the OD log, the stage artifacts and the three-agent roles; there is no other knowledge store | Verified Fact | OPEN |

### OI-4 Stage 41 retirement decisions D-41-01..D-41-16
Source: `docs/41-retirement/decommission-checklist.md` (approval family AP-RET proposed by D-41-16; none recorded).

| ID | Decision / item | Agent default or note | Status |
|---|---|---|---|
| D-41-01 | Scope of "retirement": legacy capabilities only, or also the engagement toolchain and the hub at engagement end | both are planned; legacy first; execution only per wave | OPEN |
| D-41-02 | Is any real cutover / legacy retirement intended at all (U-30-12) | undecided; plan stays shelf-ready | OPEN |
| D-41-03 | Rollback window length and any read-only period after retirement | no number proposed | OPEN |
| D-41-04 | Archived, hash-pinned reference copies of legacy sources for `asfound.py` pins | yes, before any legacy removal | OPEN |
| D-41-05 | Approved change to TST-CO-05 and G1 when legacy paths retire | yes, as a frozen-test change under HAR | OPEN |
| D-41-06 | Retention: hold-all vs named periods | hold-all | OPEN |
| D-41-07 | Ever build a hub purge capability | no | OPEN |
| D-41-08 | Session/login-attempt rows and privacy regime | archive with the store; decide with regime | OPEN |
| D-41-09 | Archive location, medium, custodian, encryption | not decided | OPEN |
| D-41-10 | Legal/QA reviewer or "synthetic only" | name one before any RL-2 | OPEN |
| D-41-11 | Build an audited disable-principal operation before any real user | yes, as a spec addendum | OPEN |
| D-41-12 | Second custodian for archives and accounts | yes | OPEN |
| D-41-13 | Anchor seal key custody and end of life | keep verification role through the window | OPEN |
| D-41-14 | Supply vendor terms or mark not applicable | supply or mark | OPEN |
| D-41-15 | Owners for the nightly file exchange (PA-25) and CO-WF-01 (PA-26, OPD-15) | protected; not retired | OPEN |
| D-41-16 | Adopt the AP-RET approval family in the register | yes | OPEN |

### OI-5 Carried decisions D-27, D-28, D-31, D-34, D-39
**D-27 (hardening)** - `docs/27-hardening/hardening-plan.md`

| ID | Decision / item | Agent default or note | Status |
|---|---|---|---|
| D-27-01 | Restricted-evidence read rule for the event `basis` (F-02) | withhold from roles that may not read the record (A-27-02) | OPEN |
| D-27-02 | Adopt the Python 3.12 floor (ADR-018) before any exposure; Python 3.10 reached end of life on 2026-10-01 (VR-02) | keep floor 3.10 as shipped; run the 3.12 / 3.13 evidence in the orchestrator cloud | OPEN |
| D-27-03 | Install `ci/hub-hardening.yml` as `.github/workflows/hub-hardening.yml` (HAR-07) and pin actions to commit SHAs | not installed | OPEN |
| D-27-04 | Limiter defaults (enabled, 60 s, 100) and the shared-loopback limitation | as built | OPEN |
| D-27-05 | Spec addenda for E-REQ-TIMEOUT (408), E-REQ-RATE-LIMITED (429), E-STORE-UNAVAILABLE (503), `rate_limit`, `crosswalk_view`, `intake_reports` | none written (Stage 12 documents are not edited in place, OD-10) | OPEN |
| D-27-06 | Stage 30: harden the legacy `Dockerfile` / `compose.yaml` / `environments/*.env.example` (VR-04) | leave unchanged until Stage 30 | OPEN |
| D-27-07 | Residual complexity debt (9 functions over 15): accept as backlog or schedule | backlog, ratchet test keeps it from growing | OPEN |
| D-27-08 | Sign or reject the walkthroughs TST-REV-03 / 04 / 08 (RTR-07) | unsigned | OPEN |
| D-27-09 | TLS / exposure (DQ-S24-03): stay loopback | loopback (unchanged) | OPEN |

**D-28 (reliability)** - `docs/28-reliability/resilience-readiness.md`

| ID | Decision / item | Agent default or note | Status |
|---|---|---|---|
| D-28-01 | Wire `GuardedGateway` into `hub.intake gateway-pull` and persist breaker state across runs (file beside the audit anchor [recommended: file, atomic write, malformed = refuse] vs store table + migration); adds `resilience` config section (closed key set) and metrics for Stage 31 | Engagement lead (Dinesh Naik) | OPEN |
| D-28-02 | Wire `BoundedLoopbackServer` into `hub web serve` / `hub r2 serve` with a cap [64] | Engagement lead (Dinesh Naik) | OPEN |
| D-28-03 | Confirm or change defaults A-28-01..A-28-03 once a real source exists | Engagement lead (Dinesh Naik) | OPEN |
| D-28-04 | Late-delivery catch-up (FG-02 / DQ-S21-06) [manual idempotent catch-up run now; scheduled catch-up only after the scheduler decision HAR-10] | Engagement lead (Dinesh Naik) | OPEN |
| D-28-05 | Shape errors: fail fast [yes, as built in the guarded path] (DQ-S21-03) | Engagement lead (Dinesh Naik) | OPEN |
| D-28-06 | Capacity, freshness and RTO / RPO targets (none exist) [declare as SLO candidates at Stage 31, not requirements] | Engagement lead (Dinesh Naik) | OPEN |
| D-28-07 | Approved host / harness for disk-full and power-loss injection and restore timing | Engagement lead (Dinesh Naik) | OPEN |
| D-28-08 | CT-18 container restart: approve HAR-05 or keep NOT-RUN | Engagement lead (Dinesh Naik) | OPEN |
| D-28-09 | Lower SQLite `busy_timeout` (30 s) [5 s] - behaviour change in `hub/web/app.py` | Engagement lead (Dinesh Naik) | OPEN |
| D-28-10 | Freshness indicator on reads / reports (F-GD-01) [add run-age to the status view] | Engagement lead (Dinesh Naik) | OPEN |

**D-31 (observability)** - `docs/31-observability/observability-validation.md`

| ID | Decision / item | Agent default or note | Status |
|---|---|---|---|
| D-31-01 | Persist HTTP metrics periodically (flush on an interval and a `hub runs obs-snapshot`-style job) [yes, at Stage 30; edit to `hub/web/app.py`] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-02 | Wire `resilience_samples` into the snapshot together with `GuardedGateway` (D-28-01) [yes, together] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-03 | SLO-02: keep PNFR-02 at 100 % of nights or adopt 95 % [95 % as the SLO, 100 % stays the requirement] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-04 | A read-only `/metrics` route (route-registry change) [defer; file exposition suffices] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-05 | Log destination and hold-all retention [append-only file by the launcher; no rotation that deletes] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-06 | Export the six gap metrics and align OBS-4 labels (spec addendum or code) [after the F-29-01 fix] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-07 | Send `X-Correlation-Id` on the gateway GET [yes; non-add edit in `hub/adapters`] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-08 | Alert delivery channel / on-call [none until a second human exists; manual evaluation RB-00] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-09 | Emit or retire the 17 never-emitted log events; tighten the id pattern [emit auth_denied, zone_h_attempt, decision_appended; retire the rest; no e-mail-shaped ids] | Engagement lead (Dinesh Naik) | OPEN |
| D-31-10 | Re-derive all SLO / alert numbers after 30 days of real use; decide whether any becomes a commitment [no SLA before a measured window] | Engagement lead (Dinesh Naik) | OPEN |

**D-34 (measure-after)** - `docs/34-measure-after/after-intervention-kpi-sheet.md`

| ID | Decision / item | Default state | Status |
|---|---|---|---|
| D-34-01 | Confirm the hub is not in production and no pilot or parallel run with real people has happened (A-34-02, U-34-08) | Not in production; K-21 = 0 | OPEN |
| D-34-02 | Define the real after-window: start date, exposure (which cases/sites), minimum duration, data owner; supply the production measurements listed in production-performance-report.md PP-1 and adoption-metrics.md AD-2 | None; all production values stay Unknown | OPEN |
| D-34-03 | Decide whether hub metrics should accept an `as_of` parameter (code change, Stage 30/hardening scope) so ageing can be compared at the frozen 2025-12-19T07:11Z | Ageing declared not comparable | OPEN |
| D-34-04 | Raise the Stage 4 v0.2 addendum proposed in kpi-comparability-check.md CC-5 (OD-07 follow-up) and sign or amend the Stage 4 freeze | Stage 4 stays FROZEN-PROVISIONAL, untouched | OPEN |
| D-34-05 | Confirm the artifact path `docs/34-measure-after/` (stage prompt says `docs/34-after-kpis/`) | `docs/34-measure-after/` | OPEN |
| D-34-06 | Decide whether an override/acceptance KPI should be added (would be a new KPI id in Stage 4 v0.2, not a redefinition) | No override KPI; counts only | OPEN |
| D-34-07 | Re-run Stage 34 after Stage 30 (cutover/release) and Stage 31 (telemetry) land and a real window exists | This v0.1 is the sandbox edition | OPEN |
| D-34-08 | Confirm K-11 may be counted by its own "accepted open" wording (2 of 2) | Counted, with the caveat that it records no decision | OPEN |

**D-39 (drift)** - `docs/39-drift/improvement-backlog.md`

| ID | Decision / item | Agent default or note | Status |
|---|---|---|---|
| D-39-01 | Accept the drift-layer reading in DF-1 (No-AI: deterministic drift only) | accept | OPEN |
| D-39-02 | Accept the cadence in `evaluation-cadence.md` (E0..E4; monthly hygiene candidate) | accept as candidate | OPEN |
| D-39-03 | Accept the triggers TRG-01..16 as candidates (not commitments) | accept as candidate | OPEN |
| D-39-04 | Python 3.10 end of life: floor move now, or keep the 3.10 floor with 3.12+ target and record exposure | obtain 3.12+ evidence first (IB-02); decision stays Dinesh's | OPEN |
| D-39-05 | CT-13: Node pin or golden re-record | Node pin for the reference environment (smaller blast radius); Dinesh decides | OPEN |
| D-39-06 | Who runs evaluations after Stage 38/FINAL | Dinesh by default; any other name must come from Dinesh | OPEN |
| D-39-07 | Confirm remote branch protection state; whether to install CI (HAR-07) | check first (IB-11), then decide | OPEN |
| D-39-08 | Priority order of IB-01..IB-20 | as listed (P1 first) | OPEN |
| D-39-09 | Whether any drift finding should become an accepted risk (none is accepted here) | no; leave all RS/RP/VA/RTR/F-xx open | OPEN |

### OI-6 Stage 29 questions and conditions
Source: `docs/29-incident-bcdr/incident-readiness.md`. Also F-29-02..F-29-16 (findings; F-29-01 fixed in Stage 30).

| ID | Question | Note | Status |
|---|---|---|---|
| Q-29-01 | Take part in a live tabletop of TT-1 (as L3)? | desk + sandbox accepted for now | OPEN |
| Q-29-02 | Confirm the AI-incident meaning AI-1..AI-4 | as written | OPEN |
| Q-29-03 | Confirm RTO/RPO targets in `rto-rpo.md` | targets, unadopted | OPEN |
| Q-29-04 | Approve an encrypted off-device copy of `data/` backup and hub backups (HAR-09)? | no copy; risk stays open | OPEN |
| Q-29-05 | Route F-29-01 to a Stage 30 fix? | yes, as a finding | OPEN |
| Q-29-06 | Name an alternate decision-maker (ES-09)? | none | OPEN |
| Q-29-07 | Where should the hub config live and be backed up? | repo-tracked file with approval refs | OPEN |
| Q-29-08 | Add incident/restore/BC sections to `operations/runbook.md` at Stage 30? | yes | OPEN |
| Q-29-09 | Allow a sandbox test of data regeneration equivalence and a sandbox rehearsal of RV-3 on a copy of `data/`? | not run | OPEN |

| ID | Condition | Note | Status |
|---|---|---|---|
| C-1 | Run a conversational tabletop with Dinesh as the L3 participant, or record that it is accepted open | Engagement lead (Dinesh Naik) | OPEN |
| C-2 | Reconcile failover, RTO/RPO and DR with the Stage 28 design once merged; issue v0.2 as an addendum | Engagement lead (Dinesh Naik); orchestrator drafts | OPEN |
| C-3 | Triage F-29-01 (fix at Stage 30 with a test, or record a decision) | Engagement lead (Dinesh Naik) | OPEN |
| C-4 | Decide on an off-device copy of baseline and hub backups (HAR-09) or accept the single-device risk in writing | Engagement lead (Dinesh Naik) | OPEN |
| C-5 | Confirm or amend RTO/RPO targets and the AI-incident framing (A-29-RR-1..4, A-29-PB-1) | Engagement lead (Dinesh Naik) | OPEN |
| C-6 | Transcribe incident, restore and continuity steps into the operations runbook | Engagement lead (Dinesh Naik) to assign | OPEN |
| C-7 | Name an alternate decision-maker and owners for RL-02/05/06/08 before any pilot | Engagement lead (Dinesh Naik) | OPEN |

### OI-7 Stage 35 corrective actions CA-01..CA-17
Source: `docs/35-variance/corrective-action-backlog.md`.

| ID | Corrective action | Note | Status |
|---|---|---|---|
| CA-01 | Define the real after-window: start date, exposure (cases/sites), minimum duration, data owner; supply production measurements listed in Stage 34 PP-1/AD-2 | VL-01, CNF-01, U-35-01 | OPEN |
| CA-02 | Confirm the hub is not in production and no pilot has happened | A-34-02, BA-F1 | OPEN |
| CA-03 | Add an `as_of` parameter to hub metrics so ageing can be compared at 2025-12-19T07:11Z (code change, Stage 30/hardening scope) | VL-12, CNF-06 | OPEN |
| CA-04 | Design the pilot with a comparison: unexposed cases/sites or stable pre-trend, pre-registered KPIs, no concurrent behaviour changes during the window | CNF-09, CNF-13 | OPEN |
| CA-05 | Raise the Stage 4 v0.2 addendum (A-04-01 refutation; reference-time rule; separate KPI ids for hub K-09U/K-06) and sign or amend the freeze | VL-13, CNF-05, CNF-12 | OPEN |
| CA-06 | Add time capture (closure, evidence-complete, reviewer effort) so K-04, K-05, K-22 become measurable | VL-11 | OPEN |
| CA-07 | Decide who decides closed/resolved (DR-20/21) and adopt or reject candidate policy `D-OPS@1`; define D-FIN or declare it out of scope | VL-10, CNF-08 | OPEN |
| CA-08 | Name accepted owners for the 28 assets and the vacant roles, or record a waiver; appoint a second reviewer or record the single-approver design as accepted by Dinesh | VL-06, VL-07, ADL-4 | OPEN |
| CA-09 | Name real Zone H holders, or record that Zone H stays unused | VL-02 | OPEN |
| CA-10 | Decide on wiring Stage 28 mechanisms into the serve path and installing `ci/hub-hardening.yml` (HAR-07) | VL-04, VL-05, ADL-6 | OPEN |
| CA-11 | Obtain human sign-off of TST-REV-03/04/08 | VL-08 | OPEN |
| CA-12 | Define a parallel-run/coexistence plan so reviewers do not do the work twice; define an override/acceptance KPI as a new id if wanted | VL-14, ADL-2 | OPEN |
| CA-13 | Supply 0C inputs C-1..C-5 (volumes, rate, cost per case), actual or estimated build effort, toolchain plans, hosting decision; appoint cost owner RL-09 | CLK-5..CLK-9, BNV-1 | OPEN |
| CA-14 | Route open registers (RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-11, 9 complex functions) to accept / fix / defer decisions | VL-09 | OPEN |
| CA-15 | Label 0C S3/S4 cost files as AI-option-only (edit outside this docs-only stage) | CLK-2 | OPEN |
| CA-16 | Investigate the 5-row K-06 gap (173 vs 168) and legacy replay safety (K-07 before) in a sandbox | U-34-02, U-34-03 | OPEN |
| CA-17 | Re-run Stage 34, then Stage 35, after Stage 30/31 and a real window exist | all | OPEN |

### OI-8 Stage 36 inputs and preconditions
I-01..I-19 (inputs) and PC-1..PC-10 (preconditions) in `docs/36-roi/` (`roi-model.md`, `benefit-assumptions.md`): PC-1 real after-window; PC-2 Zone H holders or unused + a rule set activated by recorded human decision; PC-3 owners / second reviewer / recorded single-approver acceptance; PC-4 closed/resolved decided; PC-5 time capture; PC-6 Stage 4 v0.2 addendum and `as_of`; PC-7 parallel-run plan; PC-8 Stage 28 wired, CI installed (decisions); PC-9 cost inputs and owner; PC-10 risk registers routed. BS-2 benefits sign-off UNSIGNED. All OPEN.

### OI-9 Stage 42 decisions only Dinesh can make (NS-1, 14 items)
1 pilot or stop; 2 release decision over the 40 records; 3 Zone H holders or 'unused'; 4 owners / 'Dinesh alone' / second reviewer; 5 after-window; 6 sign or amend KPI freeze, Stage 4 v0.2, `as_of`; 7 Python floor and 3.12+ run; 8 data posture (classes, tenant, regime, retention, exposure); 9 route residual registers; 10 sign walkthroughs; 11 accept/reject S30-DEV-01, Stage 27 defaults (A-27-02/04/05), Stage 28/31 numbers; 12 CI install (HAR-07); 13 cost inputs; 14 instruct Stages 38 and 41 and FINAL (items 14 now done as documents: 38 BLOCKED, 41 BLOCKED, this FINAL BLOCKED). Source: `docs/42-executive-defence/next-step-recommendations.md` NS-1.

### OI-10 Spec-readiness decisions OD-S12-01..19 (19) and their state
Source: `docs/12-specs/spec-readiness.md` RD-3; `docs/17-implementation-prd/implementation-prd.md` IP-7.
| ID | Topic | State | Authority |
|---|---|---|---|
| OD-S12-01 | Definitions closed / resolved / approved | Accepted open | OD-22 |
| OD-S12-02 | '48 h' clock | Accepted open | OD-22 |
| OD-S12-03 | Closing-state set when no closure policy | Default applied (treat_label_CLOSED_as_closing) | OD-12 |
| OD-S12-04 | Rule-set authority / activation / 999,999 default | Accepted open; sets inactive | OD-16, OD-22 |
| OD-S12-05 | Where disposition is recorded | Accepted open (mode none) | OD-20, OD-22 |
| OD-S12-06 | Zone H holders / user admin | Accepted open (holders empty) | OD-17, OD-31 |
| OD-S12-07 | Evidence sufficiency | Default (structural presence only) | OD-12 |
| OD-S12-08 | Month-end cut-off, denominator, cost source | Accepted open (parameters required) | OD-22 |
| OD-S12-09 | Retention | Interim hold-all | OD-15, OD-30 |
| OD-S12-10 | Scheduler as automated action (HAR-10) | Accepted open (schedule OFF) | OD-19, OD-22 |
| OD-S12-11 | Source-contract scope | Decided: record_only everywhere | OD-28 |
| OD-S12-12 | Target runtime | Decided: production 3.12+, code floor 3.10 (no 3.12+ evidence) | OD-24 |
| OD-S12-13 | Preserve-or-fix DV-01..DV-11 | **OPEN** (AP-DV-01..11) | decided at Stage 30; not decided |
| OD-S12-14 | Initial PRD approval | Decided: approve, refine at Stage 17 | OD-22 |
| OD-S12-15 | Who records facts | Default (human only) | OD-12 |
| OD-S12-16 | Transition table | Default (structural) | OD-12 |
| OD-S12-17 | Intake natural key | Decided | OD-18 |
| OD-S12-18 | Audit anchor location | Default (config path) | OD-15 |
| OD-S12-19 | How new cases enter | Default (backfill only; creation disabled) | OD-12 |

### OI-11 Risk registers (consolidated by ID; none accepted)
RS-01..RS-16, RP-01..RP-12, VA-01..VA-07, RTR-01..RTR-15, VR-02..VR-04 (High), F-11, F-29-02..16, F-31-01..07, SR-01..SR-16, VL-01..VL-17 - see `residual-risk-register.md`. Routing to accept / fix / defer: AP-OPS-11, PC-10, CA-14, D-39-09, SB-38 (all OPEN).

### OI-12 Other open items from the OD log
OD-33: restricted-evidence read rule (F-02), F-01..F-11 and RTR-01..RTR-15 routing, walkthrough sign-off, VA-01..VA-07. OD-34: D-27-01..09; Stage 37 owner acceptance, 0B closure OC-5, GD-06/07/10/15, vacant roles, orchestrator duties after Stage 38. OD-35: D-28-01..10, Q-29, Stage 32 items (toolchain charges, hosting, effort, RL-09 holder, HAR-07). OD-36: D-34-01..08, D-31-01..10, CA-01..17, I-01..19, PC-1..10, BS-2. OD-37: S30-DEV-01..09 acceptance, DV-01..DV-11, CUT-1..CUT-5, G1..G10 acknowledgement, 13 operational decisions. OD-38: Stages 39/40 merged before 38 (HO-18) - Dinesh to rule. Stage 25: GD-03/08/14, TP-01..15, AI register scope (OD-31 accepted several; remaining per Stage 25).

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- Rows are truncated extracts from the source tables (script-extracted); the source file wins on any difference.

## Unknowns
- U-43-21 Items that exist in stage documents I did not parse (e.g. Stage 32 and Stage 25 item lists beyond their IDs).

## Unresolved Issues
- All rows.

## Residual Risks
- Decision fatigue: ~250 open rows for one decider (RP-01, R2).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
