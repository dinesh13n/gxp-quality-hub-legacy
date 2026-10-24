---
stage: "26 — TEVV + AI Red Teaming"
artifact: "release-thresholds.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/acceptance-test-plan.md AT-09/AT-10/AT-3", "docs/18-delivery/definition-of-done.md", "docs/18-delivery/evaluation-rubric.md ER-2/ER-3", "docs/14-transformation/transformation-gates.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval. These thresholds are DECLARED BEFORE any Stage 26 result and are not changed afterwards (stage prompt). A threshold edit after results exist would be a new version with a "changed after results" mark and would not be allowed to alter the gate computed from the earlier version.**

## Summary
Fifteen thresholds RT-01..RT-15 and a gate rule. RT-01..RT-06 are taken unchanged from Stage 18 (`acceptance-test-plan.md` AT-09: "0 fail or registered; mutants KILLED or registered"; ER-2 N1..N5; ER-3 Q1..Q10) and from the transformation gates, all dated before this stage. RT-07..RT-12 are the red-team and resilience thresholds written for the new S26 suite. Gate outcome rule RT-15 maps findings to PASS, CONDITIONAL PASS and BLOCKED, and states in advance that PASS is unreachable while the walkthroughs are unsigned or 3.12+ evidence is missing.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TH-0 Declaration record [Verified Fact]
- Declared in a git commit on branch `stage-26-tevv` BEFORE the S26 test files were added and before any S26 test was executed (sha in `tevv-results.md` TR-0).
- Honest ordering note: a baseline full-regression run on `main` (7c60c09) and a characterization run were executed BEFORE this file was written, to learn the starting state; every group was green, CT-13 failed on the known Node drift. RT-01..RT-06 do not derive from that observation; they restate Stage 18 text of 2026-10-20 and the S24-DEV-04 record of 2026-10-24.

### TH-1 Severity scale (used by RT-15) [Verified Fact: definitions are declared here]
| Severity | Definition |
|---|---|
| Critical | An unauthorised or non-human actor changes state, passes Zone H, or any model/network call happens; data checksum or legacy tree changes; audit chain silently broken |
| High | A control can be bypassed but only with host access or after leaving loopback; a request class yields HTTP 500 plus partial state change; secrets/credentials appear in any response or log |
| Medium | A refusal is wrong in code or message but safe in effect; unhandled-exception 500 without state change; control with a test gap (mutant survives); missing audit of a refused action |
| Low | Cosmetic, documentation or defence-in-depth gap; unbounded growth without loopback exposure |

### TH-2 Thresholds [Verified Fact: declared]
| ID | Dimension | Measure (metric id) | Pass threshold | Source | Blocking? |
|---|---|---|---|---|---|
| RT-01 | Functional | Full hub regression, every group: FAIL + ERROR (M-01); executed vs statically expected methods (M-02) | 0 FAIL/ERROR; executed = expected in every group; the only allowed skip is the registered inner-egress skip in group B | AT-09, OD-27 | Yes, unless each failure is registered with owner and cause |
| RT-02 | Functional / security | Named set TST-NFR-07/08/09/12/13 and TST-SEC-01..21 (TST-SEC-18 class B in the decided mode, OD-S12-09 hold-all) | all `ok` | AT-09 | Yes |
| RT-03 | Behaviour preservation | Characterization CT-01..CT-16 on the reference laptop (Python 3.10.12) | 0 FAIL, except the registered environment drift CT-13 `batch:node_cwd_other` (S24-DEV-04); CT-17/CT-18 NOT-RUN by design (U-07-05, HAR-05) | Q1, OD-32 | Yes for any other failure |
| RT-04 | Data integrity | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc before and after every run (M-03); legacy paths unchanged (TST-CO-05 a/b/c) | rc 0 every time; 0 changed legacy bytes | OD-03a, Q5 | Yes |
| RT-05 | No-AI tripwires | egress attempts (M-04); `model_calls_total` (M-05); `no-ai-check` rc; non-stdlib imports in `hub/` | 0; 0; rc 0; 0 | ER-2 N1..N5 | Yes (Critical) |
| RT-06 | Mutation strength | Mutants of INC-05, INC-07, INC-08 plus H3 and H5 (M-06) | every mutant KILLED, or each survivor registered with a named test gap, owner and route | AT-09, DW-23, Q7 | Non-blocking if registered; a survivor in a Zone H / authentication / authorisation / CSRF / loopback mutant is a Medium finding at least |
| RT-07 | Adversarial input | Hostile corpus v1 (114 strings + typed values + structure abuse) over every write and read surface (M-07, M-08, M-09) | 0 HTTP 500; 0 active markup in HTML; 0 injected response header; 0 unintended state change | PNFR-13, Stage 24 S40/S41 | Yes (High) |
| RT-08 | Injection invariance | Decision-relevant outputs for an item with instruction-like text vs the same item with neutral text (M-10) | identical (0 differing fields) | PNFR-13, T-01 | Yes (Critical) |
| RT-09 | Authorisation | Route x role matrix over the 48 API operations and the UI routes (M-11) | 100 % of cells equal the registry; refused cells change 0 rows outside the audit table | BEH-SEC-01, TST-SEC-01 | Yes (Critical for a wrongly allowed cell) |
| RT-10 | Control bypass (Zone H) | Zone H attempts by every actor kind with the SHIPPED empty holder list; look-alike identities and stale re-authentication with a test-only holder list (M-12) | 100 % refused; Zone H footprint (decision events, policy events, flag actions, Zone H audit success rows) unchanged; boundary: re-auth exactly at the window accepted, window + 1 s refused | AC-GATE-21/22, FR-GATE-04 | Yes (Critical) |
| RT-11 | Leakage | Secret markers, credential column values, absolute sandbox paths, tracebacks, SQL error text in any response body or header (M-13) | 0 hits | T-07, SCM-41 | Yes (High) |
| RT-12 | Resilience | Fault injections (read-only store, corrupt/missing config, tampered/truncated audit, concurrent requests, clock skew) (M-14) | each ends in a defined hub error code or a clean refusal; 0 corrupted store (`PRAGMA integrity_check` ok); `verify-audit` detects every tamper; audit chain verifies after concurrency | NFR, TST-SEC-11 | Yes (High) for corruption |
| RT-13 | Human validation | Walkthrough records TST-REV-03/04/08 | observed by the Engagement lead and signed by him; deviations logged | AT-10, OD-24 | Blocks PASS only (not CONDITIONAL PASS) while open and documented |
| RT-14 | Runtime parity | Hub regression on the 3.10 floor and on 3.12+ (Q8) | green on both | OD-24, AT-09 | Blocks PASS only while 3.12+ evidence is missing and documented |
| RT-15 | Gate rule | see TH-3 | | | |

### TH-3 Gate rule [Verified Fact: declared]
- **BLOCKED** when any of: RT-01 fails with an unregistered failure; RT-02 fails; RT-03 fails other than CT-13; RT-04 fails; RT-05 has any non-zero; any Critical finding is unremediated and unregistered with an owner; thresholds, datasets or tests were edited to produce a pass.
- **CONDITIONAL PASS** when nothing above applies and every remaining gap (High, Medium, Low findings, open RT-13, open RT-14, surviving mutants) is documented with owner, due date and risk, and routed (Stage 27, 30 or Dinesh).
- **PASS** only when every RT-01..RT-14 is met with evidence including a signed RT-13 and RT-14 3.12+ evidence.
- A High finding does not by itself block this stage: Stage 27 is the hardening stage that consumes the findings; but a Critical finding does. This is a scope decision under OD-32 (A-26-05), not an acceptance of any risk.

### TH-4 What the thresholds do not do [Inference]
They set no performance, throughput, availability, value, time or cost target (class-C proxies stay Stage 28/29; no production data exists). They do not accept any residual risk RS-01..RS-16 (all remain OPEN, OD-30, OD-32).

## Evidence References
`docs/18-delivery/acceptance-test-plan.md`, `docs/18-delivery/evaluation-rubric.md`, `docs/18-delivery/definition-of-done.md`, `docs/24-security-privacy/residual-security-risks.md`, `.fde/orchestrator-decisions.md` (OD-03a, OD-27, OD-32).

## Assumptions
- A-26-05 [Assumption, OD-32 default] Gate semantics in TH-3 (High findings route to Stage 27, Critical findings block). Confirm: Engagement lead (Dinesh Naik).
- A-26-06 [Assumption] Counting a surviving mutant as a test gap (not a product defect) is a fair reading of Stage 18 AT-09.

## Unknowns
- U-26-04 Whether the organisation would set a stricter kill-ratio target (none exists).

## Unresolved Issues
- None.

## Residual Risks
- RR-26-04 Thresholds are binary and agent-authored; no external review (single human).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
