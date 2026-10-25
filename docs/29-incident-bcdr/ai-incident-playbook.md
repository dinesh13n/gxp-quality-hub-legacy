---
stage: "29 — AI Incident Response + BC/DR"
artifact: "ai-incident-playbook.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md (OD-04, OD-08, OD-28, OD-31, OD-32, OD-34)", "docs/24-security-privacy/threat-model.md", "docs/24-security-privacy/residual-security-risks.md", "docs/23-human-control/escalation-matrix.md", "docs/37-operating-model/escalation-model.md", "docs/37-operating-model/support-model.md", "docs/25-governance/ai-system-register.md", "docs/21-integration/failure-semantics.md", "hub/obs/", "hub/guards/", "hub/admin/cli.py", "operations/incidents/INC-2025-014.md", "docs/29-incident-bcdr/evidence/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
This is the incident playbook for the GxP Quality Hub engagement. It first says honestly **what "AI incident" means here**, then gives one procedure row for each of the twelve scenario classes the stage lists (IS-01..IS-12): how it would be detected, how severe it is, the first containment move, and where the detail lives.

**What "AI incident" means in this repository [Verified Fact, with Inference where marked].**
- The product is **No-AI** by Dinesh's decision (OD-08). It makes zero model calls; `model_calls_total` is a tripwire that nothing increments (`hub/obs/metrics.py`), the egress guard blocks non-loopback traffic (`hub/guards/egress.py`), and AI packages are on a deny-list (`hub/guards/no_ai.py`). There is therefore **no model, prompt, retrieval index, embedding store, or provider** whose behaviour could cause an incident. No model incident is described, rehearsed or invented in this stage.
- An "AI incident" in this engagement is therefore one of four things:
  - **AI-1 Build-side agent error.** The AI coding assistant that builds the system (dev tooling, not product AI; BR-AI-7, OD-08, listed in the AI register by OD-31) does something unsafe or wrong: writes to working-tree `data/`, deletes files, merges or pushes without approval, fabricates an approval or a stakeholder, is steered by instruction-like text found in a file it reads (STOP-05), or leaks a secret. [Verified Fact: the controls exist as written rules (STOP-01..12, HAR-01..16); no such incident is on record in the repository.]
  - **AI-2 Deterministic control failure.** A rule, gate, authentication, audit or integration control gives a wrong or unsafe result (chain break, Zone H bypass, rule output diverging from a human decision, feed totals mismatch). It is "AI-adjacent" only because these controls are what keep AI out and humans in charge.
  - **AI-3 Tripwire event.** Something that should never occur in a No-AI product occurs: a model call counter moves, an AI package is imported, an egress attempt is recorded (EH-04, `E-CO-DENYLIST-IMPORT`, `E-CO-EGRESS-ATTEMPT`, `E-OBS-TRIPWIRE`). Treated as SEV-B at minimum because it means the No-AI premise is broken.
  - **AI-4 Dormant future-AI.** If AI is ever added (re-qualification triggers RQ-1..RQ-3, new Dinesh decision, HAR-10), model-specific scenarios (prompt injection into a model, bad retrieval, provider outage, cost runaway) become real. Section PB-6 keeps those rows **dormant**; they must be activated, tested and re-reviewed before any AI release.
- Infrastructure incidents (laptop loss, disk full, GitHub or workspace outage, store corruption) are not "AI" incidents but are in scope for the continuity half of this stage.

**Scale of the system the playbook protects [Verified Fact].** A loopback-only service (`hub/web`, binds 127.0.0.1, non-loopback peers dropped), a SQLite store plus an audit anchor file on the same host, synthetic data only (125-case baseline, OD-09), no real users, no on-call, no alerting, no ticketing, no SLA, no deployment beyond the laptop and the orchestrator's cloud workspace (support-model SUF-01). So the playbook is deliberately small: it is a set of decisions and commands that one engagement lead and an agent can follow, plus the gaps that block a real service.

## Findings
### PB-1 Roles used (roles only; no names except Dinesh) [Verified Fact: ladder from Stage 37]
| Role | Holder | In this playbook |
|---|---|---|
| L0 Operator / reviewer / in-engagement agent | `claude-fde-agent` in the engagement; real users VACANT | detect, record, stop, never self-repair |
| L1 Service owner (RL-02) | VACANT; Dinesh INTERIM (not accepted) | triage, contain, kill switch, request restore |
| L2 Domain owners RL-03, RL-05, RL-06, RL-08 | all VACANT | called by role; if vacant the call goes to L3 |
| L3 Engagement lead (RL-01) | Dinesh Naik | declares SEV-A, approves restore (HAR-01), accepts risk, ends incident |
| Incident commander (IC) | the highest staffed rung present: L1 if staffed, otherwise Dinesh | one IC per incident |
| Scribe | the agent that detected it, otherwise Dinesh | keeps the incident record (PB-5) |

### PB-2 Lifecycle (applies to every scenario)
1. **Detect** (a signal in PB-4 fires, or a person or agent notices).
2. **Stop and record.** Stop the work that produced the signal (STOP rule). Do not self-repair. Write the first line of the incident record (time, signal, who).
3. **Classify** using `incident-severity-matrix.md`. If unsure, classify one level up.
4. **Preserve** evidence before touching anything (`forensics-evidence-policy.md`). Note: `hub.admin verify-audit` and `backup` **append audit records and rewrite the anchor**, so copy the store first.
5. **Contain** with the procedure for the scenario (`containment-procedures.md`, CT-xx).
6. **Communicate** to the audiences in `communications-plan.md`.
7. **Recover** only with the approvals the recovery procedure names (`recovery-procedure.md`; restore into working-tree `data/` is HAR-01).
8. **Close and learn.** Dinesh closes the record; lessons go into this document's change history as a new version (never overwrite, CC-06).

### PB-3 Scenario table (one row per scope item)
Likelihood and impact are agent judgements for the shadow, loopback deployment [Inference]. "Class" uses the AI-1..AI-4 meaning above.
| ID | Scenario (stage scope item) | What it means in this repo | Class | First detection signal (DS) | Default severity | Containment (CT) | Recovery | Confidence |
|---|---|---|---|---|---|---|---|---|
| IS-01 | Prompt injection | Instruction-like text inside a feed row, document, note or file, aimed at a person, a script, or the build agent. No model reads it, so the product effect is nil by construction (T-01); the live exposure is the build agent reading repo/data content (STOP-05) | AI-1, AI-2 | DS-01, DS-02, DS-12 | SEV-C product-side; SEV-B if an agent obeyed it | CT-01 | RV-1 (re-run, no state change expected) | High (product), Medium (agent) |
| IS-02 | Unsafe action | An automated actor or agent takes an action reserved to a human: writes `data/`, merges, pushes, creates a remote, performs or simulates a disposition, adds a Zone H holder, activates a rule set | AI-1 | DS-03, DS-04, DS-05, DS-06 | SEV-A for disposition/Zone H/data write; SEV-B otherwise | CT-02 | RV-2, RV-3 | High |
| IS-03 | Compromised tool | The AI assistant, GitHub, the cloud workspace, an Action, a dependency or the Docker image misbehaves or is malicious (V-01..V-09) | AI-1 | DS-07, DS-08 | SEV-B (SEV-A if secrets or data left the device) | CT-03 | RV-4, failover FO-3..FO-5 | Medium |
| IS-04 | Data leakage | Data or a secret leaves the host or lands where it should not: egress attempt, secret in audit/log/commit, restricted evidence note read by the wrong role, DB or lake committed to git | AI-1, AI-2, AI-3 | DS-05, DS-09, DS-10 | SEV-A if real data or credentials (STOP-04); SEV-B for synthetic data in the wrong place | CT-04 | RV-5 | High |
| IS-05 | Bad retrieval | Keyword/FTS search misses or mis-ranks a record, a stale index, a wrong crosswalk match. There is no semantic retrieval or embedding store (T-13, `hub/search/`) so this is a deterministic defect, not a model failure | AI-2 | DS-11 | SEV-C (SEV-B if a reviewer decision was taken on a wrong result) | CT-05 | RV-6 | Medium |
| IS-06 | Model / provider failure | **No model exists.** Real analogue: the build assistant or workspace becomes unavailable or changes terms (V-04, V-05). Dormant row for AI-4 | AI-1 / AI-4 | DS-13 | SEV-C (delivery delay) | CT-06 | FO-3, FO-4 | Medium |
| IS-07 | Cost runaway | No metered cost exists in the product (zero model calls, Stage 32 absent). Real analogues: assistant/workspace spend and disk (VM ~9.8 GB, OD-16). `model_calls_total` > 0 is a tripwire, not a bill | AI-3 / AI-1 | DS-02, DS-13 | SEV-C; SEV-B if a tripwire moved | CT-07 | RV-7 | Low (no cost data, Unknown) |
| IS-08 | Corrupted configuration | A config, decision flag, `approval_ref`, anchor path, runtime floor or authority switch is wrong or changed without a human decision (T-23) | AI-2 | DS-04, DS-14 | SEV-B; SEV-A if an authority switch flipped without a recorded approval | CT-08 | RV-8 | Medium |
| IS-09 | Infrastructure outage | Laptop, VM, GitHub, workspace or disk unavailable or full | infra | DS-13, DS-15 | SEV-C; SEV-B if evidence is at risk | CT-09 | RV-9, FO-1..FO-5 | High |
| IS-10 | Disaster | Loss or ransomware/corruption of the device including `hub.sqlite3`, anchor, `data/` and `_data-backup-2026-10-17` (all on one device) | infra | DS-15, DS-16 | SEV-A if the baseline or the only evidence copy is lost | CT-10 | RV-10, FO-1, FO-2 | High (single-copy fact), Low (outcome) |
| IS-11 | Integrity: audit or decision chain break | `verify-audit` reports broken chain or anchor mismatch (EH-03) | AI-2 | DS-04 | SEV-A | CT-11 | RV-2 | High |
| IS-12 | Feed delay or divergence (class of INC-2025-014) | A partner feed is late, retried, and totals diverge from downstream; in the hub this surfaces as `E-RUN-TOTALS-MISMATCH` or a missed run | AI-2 | DS-17 | SEV-C | CT-12 | RV-11 | Medium |

### PB-4 Detection signals (what exists, who would see it)
| DS | Signal | Source in repo | Seen by | Tag |
|---|---|---|---|---|
| DS-01 | Quarantine / reason code on a hostile or malformed intake item | `hub/intake/` outcomes, reason codes | reviewer queue (no reviewer exists) | [Verified Fact] code; no watcher |
| DS-02 | Tripwire counters `model_calls_total`, `egress_attempts_total`, `zone_h_service_actor_accepted` | `hub/obs/metrics.py`, `hub/obs/collect.py` | whoever runs the collector | [Verified Fact] |
| DS-03 | Checksum mismatch of working-tree `data/` | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` (1,512 files = 1,512 files in `data/`, observed 2026-10-25) | the agent before/after each stage (STOP-01) | [Verified Fact] |
| DS-04 | `E-SEC-AUDIT-TAMPER-DETECTED` (17), `E-DEC-CHAIN-BROKEN` (25), `CONFIG_CHANGED`/`CONFIG_LOADED` audit actions, `E-CFG-INVALID` (2) | `hub/admin/cli.py verify-audit`, `hub/config.py` | operator who runs it | [Verified Fact]; see F-29-01 for an exit-code defect |
| DS-05 | `E-CO-EGRESS-ATTEMPT` (11), `E-CO-DENYLIST-IMPORT` (9), `E-OBS-TRIPWIRE` (14), permission prompts for egress or deletion (STOP-10) | `hub/guards/`, tool layer | operator, agent | [Verified Fact] |
| DS-06 | `E-GATE-NO-HOLDERS` (19/423), `E-GATE-NOT-AUTHORISED` (19/403), `ZONE_H_ATTEMPT` records | `hub/security/authz.py`, `hub/gate/` | operator reads audit | [Verified Fact] |
| DS-07 | Unexpected diff, new dependency, new network call, CI change | `git status --porcelain` (STOP-03), stdlib-only test S30, deny-list TST-CO-11 | agent, orchestrator | [Verified Fact] |
| DS-08 | Orchestrator regression red / golden compare change not under HAR-06 (STOP-12) | `tests/hub/run_hub_groups.py --all` | orchestrator | [Verified Fact] |
| DS-09 | Secret-like value in audit (`E-SEC-SECRET-IN-AUDIT`, 18); secret scan S33 | `hub/security/audit.py`, `scan.py` | operator, test | [Verified Fact] |
| DS-10 | DB or lake file staged in git | `git status`, `.gitignore` | agent | [Inference] (no pre-commit hook verified) |
| DS-11 | Search/crosswalk mismatch found by a reviewer or a test | `hub/search/`, `hub/crosswalk/` | reviewer (VACANT) | [Verified Fact] code |
| DS-12 | Agent notices instruction-like text in data/docs/logs | STOP-05 self-check | agent | [Verified Fact] rule; effectiveness untested at scale |
| DS-13 | Tool/provider unavailable, quota or terms message | tool responses | agent, Dinesh | [Inference] |
| DS-14 | Flag without `approval_ref` at start-up (EH-07); `capability_authority` divergence (EH-10) | `hub/config.py`, `hub/control/` | operator | [Verified Fact] |
| DS-15 | Disk full (VM ~9.8 GB, OD-16), host down | OS | operator | [Verified Fact] constraint |
| DS-16 | `hub.sqlite3` unreadable / `E-STORE-BACKUP-INVALID` (21) / schema errors | `hub/store/`, `hub/ops/backup.py` | operator | [Verified Fact] |
| DS-17 | `E-RUN-TOTALS-MISMATCH` (29/500), missed-run detector, run records | `hub/runs/`, `hub/metrics/` | operator | [Verified Fact] |

### PB-5 Incident record (minimum fields; stored as a new file per incident, never edited after close)
Incident id (`IR-YYYY-NNN`), scenario IS-xx, detected at / by / signal DS-xx, severity and re-classifications with reason, evidence preserved (paths + sha256), containment steps with time, approvals obtained (HAR-xx + OD reference), communications sent, recovery steps + checks, closure decision (Dinesh), lessons. Location proposal: `operations/incidents/` already holds `INC-2025-014.md` (legacy; its follow-up owner is unknown). Creating new records there is outside this stage's write boundary [Assumption A-29-PB-2].

### PB-6 Dormant AI-4 rows (activate only if AI is added after RQ re-qualification and a new Dinesh decision)
| Dormant scenario | Would need before activation |
|---|---|
| Prompt injection against a model | injection corpus run against the actual model path, output handling, tool allow-list, human gate on every action |
| Bad retrieval / grounding failure | retrieval evaluation, citation check, quarantine of unsupported answers |
| Provider or model failure | fallback or no-AI degrade path, version pinning, change notice process |
| Cost runaway | metering, per-run and daily budget limits, kill switch tested, Stage 32 economics |
| Model drift or silent update | evaluation re-run on version change |
These are listed so that nothing is silently assumed covered; none has a procedure beyond this table [Inference].

### PB-7 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| PBF-01 | [Verified Fact] The product has no model, so no product-side AI incident can occur without first breaking a tripwire; the realistic AI incident is a build-side agent error | OD-08, `hub/obs/metrics.py`, `hub/guards/` | Incident effort belongs on agent guardrails and integrity controls, not model monitoring | Low (product), Medium (agent) | High | Is AI-coding-assistant misconduct to be handled by a policy outside this repo? |
| PBF-02 | [Verified Fact] Detection is pull-based: signals exist as codes and counters but nothing watches them (no alerting, on-call, telemetry sink) | support-model SM-3 | A signal can fire unseen | High if activated; Low while inert | High | Who watches (RL-02 VACANT)? |
| PBF-03 | [Verified Fact] Product logs are JSON lines on stderr and are not persisted (DEV-70, RC-9) | `hub/obs/log.py` docstring | Log evidence is lost when the terminal closes unless captured | Medium | High | Persist logs in a real deployment? |
| PBF-04 | [Verified Fact] `verify-audit` and `backup` write audit records and the anchor | `hub/admin/cli.py` lines for `verify-audit`, `backup`; rehearsal logs 03-06 | Running them on the live store before copying alters the evidence | Medium | High | None; handled in forensics policy FE-03 |
| PBF-05 | [Inference] `hub.kill` is read when a CLI command starts (`hub/admin/cli.py`, `hub/web/cli.py`); whether an already-running HTTP server re-reads it is not shown | `hub/admin/cli.py` `_Run.__init__` | Kill flag alone may not stop a running server; stopping the process is the sure step | Medium | Medium | Confirm in a sandbox at Stage 30 [Unknown] |

## Evidence References
`docs/24-security-privacy/threat-model.md` T-01..T-26; `docs/23-human-control/escalation-matrix.md` EH-01..EH-10; `docs/37-operating-model/escalation-model.md` ER-01..ER-18 and SEV classes; `docs/00-preflight/operating-contract/stop-conditions.md` STOP-01..STOP-12; `provisional-human-approval-rules.md` HAR-01..HAR-16; `docs/21-integration/failure-semantics.md` FS-1; `operations/incidents/INC-2025-014.md`; rehearsal evidence `docs/29-incident-bcdr/evidence/` (sandbox, 2026-10-25).

## Assumptions
- A-29-PB-1 [Assumption] Four-way meaning of "AI incident" (AI-1..AI-4) is an agent framing, taken under OD-32 default authority. Confirm: Engagement lead (Dinesh Naik).
- A-29-PB-2 [Assumption] Incident records would be new files under `operations/incidents/`; not created now (outside write boundary). Confirm: Dinesh.
- A-29-PB-3 [Assumption] Likelihood/impact judgements are for the shadow loopback deployment only and would be redone before any exposure or real data.

## Unknowns
- U-29-PB-1 Whether any consumer outside the repository depends on hub outputs (OD-28 b: Unknown), which sets real business impact.
- U-29-PB-2 Whether the running HTTP server honours `hub.kill` after start (PBF-05).
- U-29-PB-3 Real incident history for the hub: none; the one legacy incident INC-2025-014 has no follow-up owner.

## Unresolved Issues
- No staffed first responder or alternate (ES-09, EF-01); IS-12 and several domain routes have no owner.
- Stage 28 resilience design is not available to this run (see `incident-readiness.md` IR-03); reconcile when it merges.
- Playbook has not been exercised by anyone except a desk tabletop (see `tabletop-results.md`).

## Residual Risks
- RR-29-PB-1 A signal fires and nobody sees it (High if activated, Low while inert).
- RR-29-PB-2 Single point of failure at L3 (RR-37-EM-1).
- RR-29-PB-3 Build-side agent error is controlled by written rules plus checksum/diff checks, not by an enforcing technical barrier; a missed check could change `data/` before it is noticed (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
