---
stage: "25 — Governance + Compliance + Assurance"
artifact: "evidence-retention-policy.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/open-product-decisions.md OPD-09", "docs/12-specs/spec-readiness.md OD-S12-09", ".fde/orchestrator-decisions.md (OD-03, OD-03a, OD-15, OD-16, OD-21, OD-27)", "docs/17-implementation-prd/finalized-nfrs.md PNFR-10", "hub/security/scan.py RETAINED_TABLES", "hub/security/audit.py", "docs/00-preflight/operating-contract/{open-governance-decisions,change-control-rules,repository-write-boundaries}.md (GD-07, CC-06, CC-07, CC-11)", "docs/11-data-context/provenance-policy.md", "docs/13-traceability/coverage-gap-register.md", "docs/16-repo-validation/evidence/SHA256SUMS.txt", "docs/20-application/evidence/SHA256SUMS.txt"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. THIS IS A PROPOSAL, NOT A POLICY. No retention requirement, period or disposal authority exists in the repo (DR-24, OPD-09, OD-S12-09: 'accepted open'). The only decided rule is the interim default 'keep all records, no deletion or purge' (OD-15). No retention period is stated below because none can be derived from the evidence; every period is Unknown and belongs to Engagement lead (Dinesh Naik), with qualified review if a regulation is ever said to apply. Nothing here is legal advice.**

## Summary
The proposal sorts everything the engagement and the hub produce into **eleven retention classes (RC-1..RC-11)**, states for each what is **held today** and by which mechanism, what is **proposed**, and what is **Unknown**. Common rules: (1) hold everything until a policy is adopted; (2) integrity of retained evidence is checked by hash (chain, manifest or git), not by trust; (3) disposal of any record needs an adopted policy, a named authority, a legal-hold check and an audit event, and **no disposal path exists or is proposed to be built now**; (4) corrections to prior evidence are errata, never overwrites (CC-06/07). The decision Dinesh must make is OD-S12-09: keep hold-all as the standing rule, or name periods per class.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RP-1 Retention classes
| Class | Records | Held today (mechanism) | Proposed rule (not adopted) | Period | Integrity check | Tag |
|---|---|---|---|---|---|---|
| RC-1 Product decision and evidence records | `decision_events`, `evidence_record`, `policy_object`, `policy_events`, `raw_intake`, `intake_outcome`, `crosswalk_link`, `crosswalk_link_event`, `run_event`, plus `case_state`, `flag_action`, `rule_trace`, `metric_value`, `zone_h_action` (the last five are retained by TST-NFR-10's list but missing from `RETAINED_TABLES`) | insert-only triggers (`E-SEC-RETAINED`); no `DELETE` statements on retained tables (grep, AC-SEC-18); hold-all (OD-15) | keep all; fix the `RETAINED_TABLES` list to match the real set (DW-19) | Unknown | G3 `verify-audit`; G4 `verify-projection`; row-count non-decrease (TST-NFR-10) | [Verified Fact] mechanism; period [Unknown] |
| RC-2 Audit chain and anchor | `audit_log` (hash chain), anchor file at `audit.anchor_path` outside the DB directory | hash chain; anchor every N records and at end of run | retain chain and its anchor together for the same period as RC-1; the anchor's real location and strength are Stage 24 / OD-S12-18 | Unknown | `verify-audit`; known limit: tail after last anchor (R-SEC-1) | [Verified Fact] |
| RC-3 Human-decision and approval records inside the product | Zone H events, `release_record`, `release_gate_result`, `deviation_register`, `coexistence_inventory`, `principal`, `principal_role`, `session`, `login_attempt` | insert-only and in `RETAINED_TABLES` | keep with RC-1; flag the tension between permanent retention of `session` / `login_attempt` and any future data-minimisation rule (OB-08, Unknown) | Unknown | audit chain | [Verified Fact]; tension [Inference] |
| RC-4 Engagement governance records | `.fde/orchestrator-decisions.md`, stage artifacts under `docs/`, PR and commit history, tags (`baseline-as-found`) | git (private remote `dinesh13n/gxp-quality-hub-legacy`, PRs #1..#11); append-only OD log (CC-09); errata not overwrite (CC-06/07) | keep for the life of the repository; no history rewrite or force-push (CC-01) | Unknown | git object hashes; Stage 16 `validation-signoff.md` commit identity check | [Verified Fact] |
| RC-5 Test and validation evidence | `docs/*/evidence/` (golden captures, mutation reports, scan outputs, logs) each with a `SHA256SUMS.txt` | committed to git per stage | keep with RC-4; evidence files are never edited, only superseded by a new versioned file | Unknown | `SHA256SUMS.txt` per folder | [Verified Fact] |
| RC-6 Sandbox execution logs and scratch stores | full-copy sandboxes outside the working tree, run logs | **not retained**: sandboxes are deleted after each run (OD-16, disk ~9.8 GB); excerpts and hashes live in stage artifacts (GD-07 current position) | keep excerpts + hash + command + environment tier in the artifact (EV-02 format); do not retain full sandboxes; if a long-run log supports a gate claim, commit it under that stage's `evidence/` | Unknown | the artifact's recorded hash | [Verified Fact] position; proposal [Inference] |
| RC-7 Data backup and manifest | `../_data-backup-2026-10-17/` incl. `SHA256SUMS.txt` (1,512 files) | outside the repo on the device; checksum-gated before and after each execution (OD-03a) | keep until Dinesh decides disposal (HAR-03); never delete without it | Unknown | `sha256sum -c` | [Verified Fact] |
| RC-8 As-found legacy data | `data/legacy.sqlite3` (sha256 c254649f...d70aa), other `data/` files; git-ignored by the original repo | untouched; local only (HAR-09, CG-4) | keep unchanged as the baseline; not committed to git | Unknown | manifest | [Verified Fact] |
| RC-9 Product runtime logs | JSON log lines on stderr | not persisted by the product (DEV-70) | decide whether a real deployment must persist logs (observability stage) | Unknown | none | [Verified Fact] absence; need [Unknown] |
| RC-10 Imported source payloads | raw intake payloads and documents in the hub store | kept as `raw_intake` (RC-1); the originals stay in the legacy estate | same as RC-1; untrusted text stays marked untrusted | Unknown | raw count = received count (PNFR-11) | [Verified Fact] |
| RC-11 Generated reports and exports | metric outputs, R2 reports, search results, drafts | produced on demand from retained inputs; reproducible (PNFR-16) | do not retain separately; retain the inputs and the run record that produced them | Unknown | re-run identical | [Inference] |

### RP-2 Rules common to all classes (proposed)
1. **Hold-all default.** Until a policy is adopted by Dinesh, nothing is deleted (OD-15; PNFR-10). [Verified Fact] as the interim rule.
2. **No product disposal path now.** The hub has no purge function and none should be built before a policy names the authority; a future purge would be a Zone H action with an audit event, a legal-hold check and a restore-tested backup first. [Inference] design principle; not decided.
3. **Retrievability.** Records must be readable for the whole retention period: runtime floor and production target are Python 3.10 / 3.12+, SQLite 3.37; schema versions and migrations M000..M007 are retained with the code (IC-4). [Inference]
4. **Integrity before archive.** Before any archive or restore, run `verify-audit` and the checksum manifest; a failed check blocks the operation (G3, G7). [Inference]
5. **Legal hold.** No mechanism exists; hold-all is the only hold. [Verified Fact]
6. **Synthetic label.** Retained synthetic evidence stays labelled; it must never be mistaken for GxP records (PNFR-20). [Verified Fact]

### RP-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RF-01 | [Verified Fact] No retention requirement, period or authority exists anywhere in the repo | DR-24; OPD-09; OB-05 | Policy cannot be stated, only classes | Medium | High | OD-S12-09 |
| RF-02 | [Verified Fact] The immutable-table list in `hub/security/scan.py` is narrower than the list TST-NFR-10 treats as retained | `scan.py` `RETAINED_TABLES` vs `tests/hub/test_tst_nfr_measurements.py` L343+ | A new table can be added without being guarded by the deletion-path grep | Medium | High | Fix at Stage 24 (DW-19) |
| RF-03 | [Verified Fact] Audit retention and anchor location are tied: an anchor lost or not retained removes the chain's external reference | ADR-005; OD-S12-18 | Weakens tamper evidence | Medium | High | OD-S12-18 |
| RF-04 | [Verified Fact] Sandbox logs are not retained (GD-07 open); evidence for a gate is the excerpt in the artifact | OD-16; `open-governance-decisions.md` GD-07 | A reviewer cannot re-read a full log | Low-Medium | High | Is the excerpt-plus-hash practice enough? |
| RF-05 | [Inference] Permanent retention of session and login-attempt rows could conflict with a future privacy rule | OB-08 | none today (synthetic) | Low | Low | privacy regime |
| RF-06 | [Verified Fact] The backup folder lives outside the repository on one device, with no second copy | OD-03 | Single point of loss for RC-7 / RC-8 | Medium | High | Do you want an off-device copy? (HAR-09 applies) |

## Evidence References
See `evidence_sources`; item locations in `audit-evidence-index.md`.

## Assumptions
- A-25-RP-1 [Assumption] Git plus the private remote is an acceptable store for governance records while no policy exists. Confirm: Engagement lead (Dinesh Naik).
- A-25-RP-2 [Assumption] Keeping excerpts and hashes instead of full sandbox logs is acceptable (GD-07). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-25-RP-1 Any retention period, from any source (OB-05).
- U-25-RP-2 Whether a regulator or auditor would require a longer period or specific media (none cited).
- U-25-RP-3 Whether runtime logs (RC-9) must be persisted.

## Unresolved Issues
- OD-S12-09 (policy); GD-07 (sandbox logs); RF-02 (list mismatch, Stage 24); RF-06 (off-device copy).

## Residual Risks
- RR-RP-1 Unbounded growth of the hub store and of `docs/**/evidence` (RTD-30; disk ~9.8 GB on the device): Medium.
- RR-RP-2 A retention period adopted later cannot be applied retroactively without a purge capability that does not exist: Low-Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue (proposal). |
