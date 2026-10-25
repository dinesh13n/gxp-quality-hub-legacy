---
stage: "41 — Retirement / Decommissioning"
artifact: "vendor-termination-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/33-vendor-risk/{vendor-inventory,exit-plan,portability-assessment,substitution-strategy,vendor-risk-acceptance,data-processing-dependencies,vendor-scorecards}.md", "docs/32-finops/{finops-model,tco-model}.md", "docs/25-governance/risk-acceptance-register.md", "docs/37-operating-model/service-ownership-map.md", "docs/02-stakeholders/operating-contract-confirmations.md A-0B-01", ".github/workflows/verify.yml", "Dockerfile, compose.yaml", ".fde/orchestrator-decisions.md (OD-04, OD-05, OD-08, OD-28, OD-33..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. No contract is terminated, no subscription cancelled, no account closed, no vendor contacted. No contract, SOW, SLA, DPA, order form or vendor document exists in the repository (A-0B-01; OD-04): notice periods, fees, minimum terms, data-return and deletion-certificate rights are UNKNOWN, not "none". Vendor-risk acceptances VA-01..VA-07 are PROPOSED only. This is not legal advice.**

## Summary
Eleven third-party entries exist (V-01..V-11, Stage 33). **Not one has a contract in the repo.** Termination here therefore means mostly "stop using, export what is needed, close the account, obtain deletion proof where a provider holds data", and the real obligations (notice, fees, data return) can only be stated once the owner supplies the terms. Four entries are services or accounts that can be terminated (V-03 code host, V-04 AI coding assistant, V-05 orchestrator cloud workspace, V-10 device/VM as owned hardware); the rest are runtimes or tooling with a steward, not a contracting party. There are no model vendors, no hosting vendors, no data suppliers and no SaaS in the product (OD-08; ADR-015). [Verified Fact]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### VT-1 Termination plan per entry
Common pre-conditions for every row: PR-01..PR-14 for the dependent assets are met; archive verified (`archive-plan.md`); access plan approved (`access-revocation-plan.md`); legal-hold check recorded for any data the vendor holds (`legal-hold-check.md` Q7). Owner of every plan: Engagement lead (Dinesh Naik); steady-state owner RL-12 toolchain owner is INTERIM (Dinesh).

| ID | Third party | Role | Contract | What "terminate" means | Export / data return needed | Deletion proof needed | Dependency to clear first | Unknowns | Tag |
|---|---|---|---|---|---|---|---|---|---|
| V-01 | CPython (steward PSF) | runtime | none (licence not examined) | Stop installing on retired hosts; nothing to terminate | none | none | hub and legacy still need a runtime until they are archived | licence text not reviewed | [Verified Fact] |
| V-02 | SQLite (bundled) | datastore engine | none (licence not examined) | none; archives are SQLite files and stay readable by any SQLite 3.37+ | none | none | archives rely on it (format neutrality) | licence not reviewed | [Verified Fact] |
| V-03 | GitHub (private remote `dinesh13n/gxp-quality-hub-legacy`) | only remote copy of history and review workflow | none in repo; plan tier, residency, retention Unknown | Do NOT delete the repository at RL-2. After AU-4 mirror is verified, set to archived/read-only (owner decision); account closure is a separate decision | `git push --mirror` to the second remote (VA-02 proposes a second mirror); export PR text | host deletion terms Unknown | AU-4 verified; VA-02 decided; nothing else holds the only copy | collaborators, plan, terms, export tooling | [Verified Fact] usage; [Unknown] terms |
| V-04 | AI coding assistant (build tool; all 51 of 51 commits at Stage 33 carry its co-author trailer) | dev tooling, not product AI | none; commercial terms, data use, retention Unknown | End access; revoke authorisation at the code host; remove stored sessions per provider options | none held by product; session context is lost | provider-side deletion of session data: terms Unknown | no run-time dependency (OD-08); build continuity ends | retained context, output licence (LR-3) | [Verified Fact] usage; [Unknown] terms |
| V-05 | Orchestrator cloud workspace (provider Unknown) | full-regression runner on git-ignored data copies | none; provider, region, retention Unknown | Remove the data copy; end the workspace after AU-2 verified | none (copies only) | provider deletion record (Unknown form); relevant because the copy contains synthetic data only (Verified Fact) | the only environment for the full-regression evidence (V-05 critical) | provider, region, terms | [Verified Fact] usage; [Unknown] |
| V-06 | GitHub Actions | CI | none | Delete or leave the workflow file inert; never run | none | none | legacy CI file removal belongs to RA-10 | none | [Verified Fact] |
| V-07 | Docker / base image | optional container | none; not authorised for use (HAR-05), never executed | none | none | none | RA-10 | none | [Verified Fact] |
| V-08 | JDK | legacy month-end run | none | stop running Java job | none | none | RA-05 (CUT-4) | distributor | [Verified Fact] |
| V-09 | Node.js | legacy JS threshold | none | stop running JS | none | none | RA-02 (CUT-2) | distributor | [Verified Fact] |
| V-10 | Reference laptop / device VM | host for the 3.10.12 goldens | owned hardware; OS vendor Unknown | Wipe or repurpose per owner device policy after archive verified; HAR-03 applies to repo/backup files | restore repo + backup to another host (exit plan V-10) | owner attestation | only host of the 3.10.12 goldens (DF-04) | OS vendor, device policy | [Verified Fact] usage; [Unknown] |
| V-11 | Data suppliers / partners / counterparties | none real: all synthetic generated in-repo (seed 4100) | none | none | none | none | if real sources are ever named, re-plan | none | [Verified Fact] |

### VT-2 Termination mechanics that are Unknown (do not assume)
| Item | Position | Tag |
|---|---|---|
| Notice periods, minimum terms, early-termination fees | Unknown for V-03, V-04, V-05; no contract in repo | [Unknown] |
| Data-return rights and formats | Unknown; export is self-service through git for V-03; none for V-04/V-05 | [Unknown] |
| Deletion certificates / proof of destruction | Unknown for all providers holding any copy | [Unknown] |
| Costs of exit | Unknown: Stage 32 found model spend USD 0 by design and every other cost line Unknown; RL-09 cost owner VACANT | [Verified Fact] (OD-35) |
| Concentration | five critical entries; toolchain concentration is the real risk (V-03..V-05) | [Verified Fact] (Stage 33) |

### VT-3 Sequence (conditional)
1. Archive and mirror verified (AU-1..AU-5), second custodian decided (D-41-12).
2. Terminate the account that holds the least unique data first (V-05 workspace copy, V-04 assistant access).
3. Then the code host: archived/read-only before any closure; closure only if Dinesh decides, never as part of RL-2.
4. Hardware (V-10) last.
5. At each step obtain the provider's deletion record where one exists and file it under `evidence/` (or record "not available" honestly).

### VT-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| VTF-01 | [Verified Fact] No contract of any kind exists for any entry | `vendor-inventory.md` Summary; A-0B-01 | Termination obligations cannot be stated | Medium | High | Owner supplies terms or marks N/A (D-41-14) |
| VTF-02 | [Verified Fact] The exit plans (Stage 33) are unrehearsed | `exit-plan.md` UI-33-11 | Termination timing is a guess | Medium | High | Rehearse before use |
| VTF-03 | [Verified Fact] VA-01..VA-07 are PROPOSED, none accepted | `vendor-risk-acceptance.md` | Termination decisions reuse them; they are still open | Medium | High | Decide VA-02..VA-04 first |
| VTF-04 | [Inference] The product has no vendor lock-in at run time; retiring toolchain vendors does not endanger archived data | `lock-in-analysis.md`; stdlib-only stack (DM-08) | Low technical termination risk | Low | Medium | none |

## Evidence References
See `evidence_sources`. Companion: `access-revocation-plan.md` AC-08..AC-11; `decommission-checklist.md` steps D-01..D-08.

## Assumptions
- A-41-VT-1 [Assumption] Open-source runtimes (V-01, V-02, V-08, V-09) need no termination. Confirm: Engagement lead (Dinesh Naik); licence terms were not examined.
- A-41-VT-2 [Assumption] The Stage 33 inventory is complete (A-33-02). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-41-VT-1 All commercial and data-handling terms (U-33-01, U-33-02, U-33-20).
- U-41-VT-2 Whether any vendor exists outside the repository (U-33-05).

## Unresolved Issues
- UI-41-VT-1 D-41-14 (supply terms). Owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-41-VT-1 Unknown obligations at termination (Medium).
- RR-41-VT-2 Unrehearsed exit (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
