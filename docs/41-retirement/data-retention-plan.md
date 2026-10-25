---
stage: "41 — Retirement / Decommissioning"
artifact: "data-retention-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/{evidence-retention-policy,compliance-obligations,audit-evidence-index}.md", "docs/37-operating-model/data-ownership.md", "docs/11-data-context/{data-source-inventory,metadata-model,data-context-risks}.md", "docs/05-current-state/control-points.md CG-11", "docs/24-security-privacy/{privacy-impact-assessment,data-protection-controls}.md", "docs/29-incident-bcdr/forensics-evidence-policy.md", "docs/00-preflight/operating-contract/{provisional-human-approval-rules,data-use-constraints}.md", "app/enterprise_legacy.py", ".fde/orchestrator-decisions.md (OD-03a, OD-09, OD-15, OD-30, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. THIS IS A PLAN, NOT A POLICY. No retention requirement, retention period, disposal authority or regulatory duty exists in the repository (OB-05, DR-24, OPD-09, OD-S12-09 are "accepted open"). EVERY RETENTION PERIOD BELOW IS UNKNOWN AND OWNED BY DINESH NAIK, with qualified QA / legal review if any regulation is ever said to apply. Nothing here is legal or regulatory advice and no regulatory conclusion is drawn. The only decided rule is the interim default: keep all records, no deletion or purge (OD-15, OD-30).**

## Summary
When a component is retired, its **data does not retire with it**. This plan states, per data domain, what happens to the data at each retirement level (RL-1 frozen, RL-2 archived; RL-3 deletion is not proposed), who must decide, and what is held today. The Stage 25 retention classes RC-1..RC-11 are reused; the Stage 37 data domains DD-01..DD-09 are mapped onto them. Three points matter most:

1. **Hold-all stays in force through every retirement level.** No disposal is proposed; retiring code is never a reason to dispose of its data. [Verified Fact: OD-15, OD-30; Inference: consequence]
2. **The hub cannot dispose of anything even if told to.** It has no purge function; retained tables are insert-only by trigger (`evidence-retention-policy.md` RP-2; `dependency-clearance.md` DF-14). A retention period adopted later is therefore not enforceable inside the hub without a new, approved capability. [Verified Fact]
3. **The legacy data model already carries a legal-hold flag that nothing acts on** (see `legal-hold-check.md` LH-3): `retention_events.legal_hold` in `data/enterprise_legacy.sqlite3`. The data is synthetic, but the same pattern in real data would make deletion unsafe by default. [Verified Fact]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DR-1 Data domains and what retirement does to them
Class = Stage 25 retention class. "At RL-1" and "At RL-2" are proposals only; "Decision owner" is Engagement lead (Dinesh Naik) for every row because no other owner exists (OD-04; DAF-01); the data-owner role RL-07 is VACANT.

| Domain (Stage 37) | Records (path) | Class | Held today | At RL-1 (frozen, comparator) | At RL-2 (archived, stopped) | Period | Tag |
|---|---|---|---|---|---|---|---|
| DD-01 Legacy baseline DB | `data/legacy.sqlite3` sha256 c254649f…d70aa (125 cases, seed 4100) | RC-8 | local, git-ignored, untouched | keep unchanged, read-only | keep in place AND archive copy; baseline is protected (NR-1) | Unknown | [Verified Fact] state; [Inference] proposal |
| DD-01 (other legacy stores) | `data/enterprise_legacy.sqlite3` (12 tables incl. `retention_events` 2,084 rows, `access_audit` 4,167), `data/archive_documents/` (210 `.eml` + 210 `.html` + manifest, git-tracked), `data/documents/source_documents.jsonl`, `data/lake/` (git-ignored) | RC-8 | local; part of the 1,512-file manifest | keep unchanged | keep and archive; never regenerate over them (`archived_documents.py` deletes its directory on regenerate: DM-12) | Unknown | [Verified Fact] |
| DD-02 Backup and manifest | `../_data-backup-2026-10-17/` + `SHA256SUMS.txt` | RC-7 | one device, no second copy (RF-06) | keep | keep; off-device copy needs HAR-09 | Unknown | [Verified Fact] |
| DD-03 Hub operational data | hub store `hub.sqlite3` tables (cases, decisions, runs, reviewer queue, rule sets) | RC-1, RC-3 | insert-only; hold-all | keep; hub still shadow | archive whole store with its audit chain and anchor as one unit (no partial disposal possible) | Unknown | [Verified Fact] |
| DD-04 Source feeds | partner feed (86 feed rows in fixtures; 8,567 items evaluated in S21), vendor CSV, gateway payloads | RC-10 | synthetic; originals stay in legacy estate; hub keeps `raw_intake` | keep | keep via hub archive; legacy originals via RA-11 | Unknown | [Verified Fact] |
| DD-05 Audit trail, hash chain, anchor | `audit_log`, anchor file at `audit.anchor_path` | RC-2 | chain + anchor (R-SEC-1 tail limit) | keep together | archive chain and anchor together; run `verify-audit` before and after | Unknown | [Verified Fact] |
| DD-06 R2 corpus and derived search index | 22 injection docs, 10 variants; FTS5 index (derived) | RC-1/RC-11 | derived index rebuildable | keep | archive source records; index is derived and need not be archived (Inference) | Unknown | [Inference] |
| DD-07 Regenerable 6,000-case dataset (seed 4326) | not in baseline (OD-09); regenerable | RC-11 | not present as baseline | n/a | n/a: regenerate on demand, not retained | n/a | [Verified Fact] |
| DD-08 Evidence data | `docs/*/evidence/` each with `SHA256SUMS.txt`; goldens; `docs/30-release/evidence/` (incl. 33 rehearsal logs) | RC-5 | in git | keep (NR-3) | keep in git; evidence is never edited, only superseded (CC-06/07) | Unknown | [Verified Fact] |
| DD-09 Credentials | none real; hashes/digests only | n/a | see `secret-key-revocation.md` | n/a | revoked, not archived; hashes in the hub store stay inside the archive | n/a | [Verified Fact] |
| - Sandbox copies, logs | full-copy sandboxes | RC-6 | deleted after each run (OD-16); excerpt + hash in artifacts | n/a | already disposable by practice; confirm none holds unique evidence (RA-17) | n/a | [Verified Fact] practice |
| - Cloud workspace copy | git-ignored data copy at provider Unknown | RC-6/RC-7 | exists (OD-23) | n/a | provider-side deletion terms Unknown (U-33-02) | Unknown | [Verified Fact] usage |
| - Assistant session context | AI coding assistant sessions | none | provider-held; terms Unknown | n/a | not under the repo's control; U-33-01 | Unknown | [Unknown] |
| - Runtime logs | JSON lines on stderr, not persisted (DEV-70, RC-9) | RC-9 | not retained | n/a | n/a | Unknown | [Verified Fact] |

### DR-2 Retention rules that apply to the retirement itself
1. **Hold-all first.** Until Dinesh adopts a policy, retirement moves no record out of retention. [Verified Fact: OD-15]
2. **Archive before stop.** RL-2 for a data-bearing asset requires a verified archive (`archive-plan.md`) before the service stops. [Inference]
3. **Whole-store archive for the hub.** Because retained tables are insert-only and the audit chain spans them, the hub store is archived or kept as one unit with its anchor; selective deletion would break `verify-audit`. [Inference from audit design; Verified Fact for insert-only triggers]
4. **Retention check precedes any RL-3.** No RL-3 request is valid without: adopted period per class, legal-hold check recorded (`legal-hold-check.md`), archive verified, owner approval, and HAR-03 (deleting any file in the repo or the backup). [Verified Fact: HAR-03 text; Inference: composition]
5. **Retirement records are themselves records.** The checklist, evidence index, approvals and any archive manifest created by retirement fall into RC-4/RC-5: committed, hashed, never edited. [Inference]
6. **Synthetic label stays.** Archived synthetic data keeps its label so it can never be mistaken for GxP records (PNFR-20). [Verified Fact]

### DR-3 Decisions needed (all OPEN, owner Engagement lead (Dinesh Naik))
| ID | Decision | Agent-recommended default (scope choice only, not a decision, not a risk acceptance) | Options |
|---|---|---|---|
| D-41-06 | Keep hold-all as the standing rule through retirement, or name a period per class (OD-S12-09) | Keep hold-all | (a) hold-all; (b) period per class named by Dinesh with qualified review; (c) other |
| D-41-07 | Is a hub purge capability ever wanted | No; do not build before a policy names the authority | (a) never; (b) later, as a Zone H action with audit event, legal-hold check and restore-tested backup |
| D-41-08 | Session and login-attempt rows (OB-08 privacy tension) | Archive with the store; decide with the privacy regime | (a) retain; (b) minimise in a successor; (c) other |

### DR-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RPF-01 | [Verified Fact] No retention period exists for any domain; every period here is Unknown | RF-01; OB-05 | Retirement cannot reach RL-3 | Medium | High | D-41-06 |
| RPF-02 | [Verified Fact] The hub has no disposal path and retained tables are insert-only | RP-2; DF-14 | A policy adopted later cannot be applied inside the hub | Low-Medium | High | D-41-07 |
| RPF-03 | [Verified Fact] Legacy `retention_events` (2,084 rows, expiry about 7 years after creation by generator, 123 `legal_hold=1`) is read by nothing | CG-11; MR-1; `app/enterprise_legacy.py` L23, L51 | If the pattern were real, "retention expiry" could trigger an unsafe purge by a successor; synthetic here | Medium | High | Treat as modelling evidence only |
| RPF-04 | [Verified Fact] Backup and baseline exist once, on one device (RF-06, DAF-05) | `evidence-retention-policy.md`; `data-ownership.md` | Retirement of the device or workspace could lose the only copy | Medium | High | Off-device copy (HAR-09) |
| RPF-05 | [Inference] Growth: hold-all means `docs/**/evidence` and the hub store grow without bound; device VM disk is about 9.8 GB | RR-RP-1; OD-16 | Practical limit before policy | Medium | Medium | Archive location (D-41-09) |

## Evidence References
See `evidence_sources`. Companion artifacts: `archive-plan.md`, `legal-hold-check.md`, `decommission-checklist.md`.

## Assumptions
- A-41-RP-1 [Assumption] Treating the hub store plus anchor as one archive unit is acceptable. Confirm: Engagement lead (Dinesh Naik).
- A-41-RP-2 [Assumption] Derived indexes (FTS5) need no archive. Confirm: Build agent at clearance time (rebuild test).
- A-41-RP-3 [Assumption] `retention_events` arithmetic: the generator emits a row only when `i%6==0`, so `i%3==0` and the class is always `standard`; `legal_hold` is `i%17==0`. This reproduces the Stage 11 observation (all `standard`, 123 holds) but the database was not re-queried in this stage.

## Unknowns
- U-41-RP-1 Any retention period, from any source (U-25-RP-1).
- U-41-RP-2 Whether a regulator or auditor requires specific media or a longer period (U-25-RP-2).
- U-41-RP-3 Whether runtime logs must be persisted in a real deployment (U-25-RP-3).
- U-41-RP-4 Provider-side retention for the cloud workspace and assistant (U-33-01, U-33-02).

## Unresolved Issues
- OD-S12-09 (policy); RF-02 retained-table list mismatch (Stage 24/27 status not re-checked here); off-device copy; D-41-06..D-41-08.

## Residual Risks
- RR-41-RP-1 Retiring a data-bearing asset before the policy exists leaves records without an authority (Medium).
- RR-41-RP-2 Hold-all growth (Medium); not accepted beyond OD-30.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
