---
stage: "25 — Governance + Compliance + Assurance"
artifact: "audit-evidence-index.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/25-governance/{compliance-obligations,compliance-control-matrix,evidence-retention-policy}.md", ".fde/orchestrator-decisions.md", "docs/16-repo-validation/evidence/", "docs/20-application/evidence/", "docs/21-integration/evidence/", "tests/hub/", "hub/", "docs/18-delivery/evidence-checklist.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. This index points to where evidence lives; it does not re-assert it. Every path below was checked to exist in the working tree when this index was written (read-only `test -e`). 'Reproduce' commands are given for a later runner; this stage executed no code (documents-only mode; OD-03a: code runs only in a full-copy sandbox, never in the working tree). Index owner: Engagement lead (Dinesh Naik).**

## Summary
The index lists **34 evidence items (AE-01..AE-34)** grouped by what an auditor would ask: who decided (approvals), what controls exist (code and tests), what was observed (validation and regression), what changed (change control), and what is missing. Each item shows what it supports, the obligation(s) and control(s) it serves, how integrity is checked, how to reproduce, and its status. Section AX lists evidence that is **expected but does not exist** (no CI logs, no Stage 23/24 outputs, no signed approvals beyond OD entries, no retention policy, no real holder records). Nothing is claimed as evidence that is not on disk.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AI-1 Decisions and approvals
| ID | Evidence | Path | Supports (OB / GC) | Integrity | Reproduce / read | Status |
|---|---|---|---|---|---|---|
| AE-01 | Orchestrator decision log OD-01..OD-29 (+OD-03a): the only approval record | `.fde/orchestrator-decisions.md` | OB-02, OB-10, OB-11, OB-12; GC-14 | git history (append-only, CC-09) | read | Verified Fact: exists; approver wording per row |
| AE-02 | Human approval triggers HAR-01..HAR-16 (PROVISIONAL) | `docs/00-preflight/operating-contract/provisional-human-approval-rules.md` | OB-11 | git | read | Verified Fact |
| AE-03 | Approval authority map; confirmations of 0B items after Stage 2 | `docs/02-stakeholders/approval-authority-map.md`; `docs/02-stakeholders/operating-contract-confirmations.md` | OB-11; GC-14 | git | read | Verified Fact (most items OPEN) |
| AE-04 | Domain assurance statement (Part 11 and GMP data integrity as background; synthetic, not certification) | `docs/domain-assurance.md` | OB-01, OB-02, OB-04 | git | read | Verified Fact (document claim, NE-1) |
| AE-05 | Implementation baseline sign-off (agent) and Stage 16 validation sign-off (human acceptance recorded in OD-24, OD-25) | `docs/17-implementation-prd/implementation-baseline-signoff.md`; `docs/16-repo-validation/validation-signoff.md` | OB-11, OB-16 | git | read | Verified Fact |

### AI-2 Controls: code and tests
| ID | Evidence | Path | Supports | Integrity | Reproduce (sandbox only) | Status |
|---|---|---|---|---|---|---|
| AE-06 | Hash-chained audit trail module | `hub/security/audit.py` | OB-01; GC-01 | git | `python -m hub.admin verify-audit` on a sandbox store | Verified Fact (module read) |
| AE-07 | Audit tests: events, verify ok, tamper detection | `tests/hub/test_tst_sec_09_audit_events.py`, `..._sec_10_verify_audit_ok.py`, `..._sec_11_tamper_detection.py` | OB-01; GC-01 | git | run via `tests/hub/run_hub_groups.py` in a sandbox | Verified Fact: files exist; results per AE-20/AE-21 |
| AE-08 | Zone H holder rule | `hub/security/zone_h.py`; `hub/gate/` | OB-02; GC-04 | git | read | Verified Fact |
| AE-09 | Disposition gate tests (AC-GATE, TST-GATE-01..22) | `tests/hub/test_tst_gate_01_22_disposition_gate.py` | OB-02, OB-03; GC-04, GC-05 | git | group runner | Verified Fact: exists |
| AE-10 | Route registry (48 operations, deny-by-default) and its test | `hub/security/route_registry.json`; `tests/hub/test_tst_sec_01_route_registry.py` | OB-06; GC-06 | git | group runner | Verified Fact |
| AE-11 | Retained-table guard and deletion-path grep | `hub/security/scan.py` (`RETAINED_TABLES`); `docs/16-repo-validation/evidence/secret-scan.txt` | OB-05, OB-12; GC-02, GC-12 | `docs/16-repo-validation/evidence/SHA256SUMS.txt` | the hub security scan (see TST-SEC-18 for the invocation), sandbox only | Verified Fact (list is narrower than TST-NFR-10's, RF-02) |
| AE-12 | TST-NFR-10 (no deletions across a mixed flow) | `tests/hub/test_tst_nfr_measurements.py` L343 | OB-05; GC-02 | git | group runner, sandbox | Verified Fact: test exists. Stage 25 produced NO run log (documents-only). See AX-1 |
| AE-13 | Rule-set module and as-found pins | `hub/policy/rulesets.py`; `hub/policy/as_found_pins.json` | OB-16; GC-07 | git | read | Verified Fact |
| AE-14 | Release checklist G1..G10 | `hub/ops/release.py` | OB-11, OB-16; GC-10 | git | read | Verified Fact |
| AE-15 | Deviation register seed and golden-compare engine | `hub/coexistence/seed_s20.json`; `hub/golden/compare.py` | OB-16; GC-09 | git | `python -m hub golden-compare` (sandbox; exit 6 expected) | Verified Fact |
| AE-16 | No-AI guard and its tests | `hub/guards/no_ai.py`; `tests/hub/test_tst_co_11_no_ai_denylist.py`; `tests/hub/test_tst_co_12_egress_tripwire.py`; `docs/20-application/evidence/no-ai-check.json` | OB-10; GC-11 | `docs/20-application/evidence/SHA256SUMS.txt` | `python -m hub no-ai-check` (sandbox) | Verified Fact (rc 0, findings []) |

### AI-3 Validation and regression evidence
| ID | Evidence | Path | Supports | Integrity | Reproduce | Status |
|---|---|---|---|---|---|---|
| AE-17 | Behaviour-difference report (DV-01..DV-11, D5 = 0) | `docs/16-repo-validation/behavior-difference-report.md` | OB-04, OB-16; GC-09 | `docs/16-repo-validation/evidence/SHA256SUMS.txt` | commands in the report's Evidence References | Verified Fact (synthetic) |
| AE-18 | Hub mutation gate (8 of 10 killed) | `docs/16-repo-validation/evidence/hub-mutation.json`; `docs/20-application/evidence/mutation-gate.json` | GC-18, GC-04, GC-06 | SHA256SUMS files | `s16_hub_mutation_gate.py`, `s20_mutation_gate.py` (throw-away copies) | Verified Fact |
| AE-19 | Security scan summary (bandit, secret scan, SS-01..SS-08) | `docs/16-repo-validation/security-scan-summary.md` | OB-06, OB-13; GC-06, GC-12 | git | read | Verified Fact |
| AE-20 | Stage 16 regression and test results | `docs/16-repo-validation/regression-results.md` | OB-11; GC-14 | git | read | Verified Fact |
| AE-21 | Stage 20 application test summary and regression groups | `docs/20-application/application-test-summary.md`; `docs/20-application/evidence/regression-groups-laptop.json` | OB-10, OB-11 | `docs/20-application/evidence/SHA256SUMS.txt` | `tests/hub/run_hub_groups.py --all` (cloud, OD-27) | Verified Fact (419 methods, executed = expected) |
| AE-22 | Characterisation goldens and harness (legacy 134/134 on 3.10.12) | `docs/07-repo-assessment/evidence/golden/`; `tests/characterization/`; `docs/20-application/evidence/characterization-summary.json` | OB-04, OB-16; GC-09 | checksums in report | harness on the reference laptop only (OD-23) | Verified Fact |
| AE-23 | Data checksum log before / after executions | `docs/16-repo-validation/evidence/checksum-log.txt` | OB-04, OB-11; GC-15 | `../_data-backup-2026-10-17/SHA256SUMS.txt` | `sha256sum -c` from repo root | Verified Fact |
| AE-24 | Rollback rehearsals INC-03, -06, -07, -08, -09 | `docs/15-modernization/rollback-rehearsal-inc*.md` | OB-11; GC-17, GC-19 | git | per document | Verified Fact (sandbox) |
| AE-25 | Integration evidence and readiness | `docs/21-integration/integration-readiness.md`; `docs/21-integration/evidence/` | OB-04, OB-13 | evidence folder manifests | per document | Verified Fact |

### AI-4 Specifications and requirements traceability
| ID | Evidence | Path | Supports | Integrity | Status |
|---|---|---|---|---|---|
| AE-26 | Finalised NFRs PNFR-01..20 and NFR-RT | `docs/17-implementation-prd/finalized-nfrs.md` | OB-01, OB-05, OB-06, OB-10, OB-13 | git | Verified Fact |
| AE-27 | Acceptance criteria (AC-GATE, AC-SEC, AC-NFR-10) and ACC-8 compliance framing row | `docs/12-specs/acceptance-criteria.md` | all | git | Verified Fact |
| AE-28 | Test plan (241 tests; TST-NFR-10 assigned to Stage 25) and RTM | `docs/13-traceability/evidence/tests_plan.csv`; `rtm.csv` | OB-05; GC-02 | git | Verified Fact |
| AE-29 | Security specification (roles, permission matrix, Zone H checklist) | `docs/12-specs/security-spec.md` | OB-06; GC-06 | git | Verified Fact |
| AE-30 | Architecture decisions ADR-002 (No-AI), ADR-005 (audit), ADR-006 (gate), ADR-007 (rules) | `docs/10-architecture/adrs/` | OB-01, OB-02, OB-10; GC-01, GC-04, GC-07, GC-11 | git | Verified Fact (status PROPOSED) |
| AE-31 | Coverage gap register incl. GAP-13-22 (no Part 11 / GxP compliance can be evidenced) | `docs/13-traceability/coverage-gap-register.md` | OB-01 | git | Verified Fact |
| AE-32 | Feature-flag plan and hub config schema | `docs/14-transformation/feature-flag-plan.md`; `docs/12-specs/contracts/schemas/hub-config.schema.json` | OB-16; GC-08 | git | Verified Fact (some keys proposed) |
| AE-33 | AI qualification decision and re-qualification triggers | `docs/08-ai-qualification/qualification-decision.md`; `docs/19-intelligence/not-applicable.md`; `docs/22-agentic-engineering/not-applicable.md` | OB-10, OB-15 | git | Verified Fact |
| AE-34 | Delivery backlog and evidence checklist (DW-20 expects this stage's map) | `docs/18-delivery/delivery-backlog.md`; `docs/18-delivery/evidence-checklist.md` | OB-11 | git | Verified Fact |

### AI-5 Evidence that is expected but absent (AX)
| ID | Missing evidence | Why it matters | Resolves at | Owner |
|---|---|---|---|---|
| AX-1 | A Stage 25 run log of TST-NFR-10 (DW-20 evidence checklist names "TST-NFR-10 log") | acceptance plan AT-08 wants it under `docs/25-governance/`; this stage could not execute code | orchestrator in the next full regression, or Stage 26 | Engagement lead (Dinesh Naik) / orchestrator |
| AX-2 | Stage 23 and Stage 24 artifacts (Stage 12 v0.2, HITL catalogue, threat model, control values, header and bind tests, RETAINED_TABLES fix) | controls GC-22 are PLANNED | Stage 23/24 merge; re-issue as v0.2 | Engagement lead (Dinesh Naik) |
| AX-3 | CI run logs | no CI gate exists | Stage 27 | Engagement lead (Dinesh Naik) |
| AX-4 | Retention policy and disposal authority | none exists | OD-S12-09 | Engagement lead (Dinesh Naik) |
| AX-5 | Named Zone H holder records; real disposition events | none exist | OD-S12-06 | Engagement lead (Dinesh Naik) |
| AX-6 | Independent review record (second reviewer) | none exists | DQ-17 | Engagement lead (Dinesh Naik) |
| AX-7 | Stage 26 TEVV results and human walkthrough records | scheduled | Stage 26 | Engagement lead (Dinesh Naik) |
| AX-8 | Any external regulatory assessment or legal opinion | out of scope for this stage; none cited | qualified reviewer, if needed | Engagement lead (Dinesh Naik) |

### AI-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| AEF-1 | [Verified Fact] Every approval is traceable to one file, the OD log, which is in git | AE-01 | Single source for audit; also single point | Medium | High | none |
| AEF-2 | [Verified Fact] Each evidence folder has a SHA-256 manifest; the manifests are in git beside the files | AE-11, AE-16, AE-23 | Integrity is checkable offline | Low | High | none |
| AEF-3 | [Inference] An auditor could re-run most evidence only on the Python 3.10.12 reference laptop (goldens) plus a cloud runner (hub regression); no single environment reproduces everything | OD-23; IA-12 | Reproduction needs two environments | Medium | High | Stage 27 CI on 3.12+ and 3.10 |
| AEF-4 | [Verified Fact] DW-20's own evidence item (a TST-NFR-10 log under `docs/25-governance/`) is not satisfied by this stage | AX-1 | Completion-gate wording "no obligation marked met without evidence" is honoured by not marking OB-05 met | Low | High | who runs it |

## Evidence References
Paths in the tables above are the references. Manifests: `docs/16-repo-validation/evidence/SHA256SUMS.txt`, `docs/20-application/evidence/SHA256SUMS.txt`, `../_data-backup-2026-10-17/SHA256SUMS.txt`.

## Assumptions
- A-25-AE-1 [Assumption] Results quoted from earlier-stage documents remain valid at the current `main`. Confirm: orchestrator full regression before Stage 26 (OD-23).

## Unknowns
- U-25-AE-1 Whether an external auditor would accept git history plus SHA-256 manifests as tamper-evident evidence for the engagement records.

## Unresolved Issues
- AX-1..AX-8.

## Residual Risks
- RR-AE-1 Evidence is as strong as the repository's custody; the repo and the backup are on one device plus a private remote (RF-06): Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
