---
stage: "26 — TEVV + AI Red Teaming"
artifact: "failure-dataset-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/12-specs/error-handling-spec.md", "hub/core/errors.py", "hub/store/db.py", "hub/security/audit.py", "hub/config.py", "docs/18-delivery/acceptance-test-plan.md AT-12"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Failure cases are injected faults in throwaway sandbox stores. They are NOT disaster-recovery or availability tests (Stages 28/29, class C) and give no recovery-time or recovery-point figure.**

## Summary
Eight fault classes (FD-01..FD-08) with the injection method, the expected safe outcome and the metric. Faults are injected only in private store copies under the sandbox root; the working tree and `data/` are never touched.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FD-1 Fault catalogue [Verified Fact: declared; S26-C01..C06]
| ID | Fault | Injection | Expected safe outcome | Test |
|---|---|---|---|---|
| FD-01 | Store file not writable (read-only) | `chmod` the hub SQLite file read-only in a copy, send a write request | request fails closed with a defined hub error or 500 WITHOUT any partial state; integrity_check ok; no stack trace on the wire | S26-C01 |
| FD-02 | Store missing / empty file | point `data_dir` at an empty directory | startup/self-check refuses with a defined code (not a traceback); no file created outside the sandbox | S26-C01 |
| FD-03 | Config corrupt / missing / unknown key | write truncated JSON, `[]`, wrong types, unknown top-level key | `ConfigInvalid` exit code; refuses to serve; no default silently applied for a safety key | S26-C02 |
| FD-04 | Kill switch | set config `hub.kill: true` (`hub/config.py`) | every hub CLI command except `selfcheck` refuses with `E-HUB-KILLED` (exit 3) and changes nothing | S26-C02 |
| FD-05 | Audit chain tamper | alter one record, delete one record, truncate the tail, edit the anchor file | `verify-audit` / OP-SEC-04 reports not ok with the right `failure_kind`; insert-only triggers refuse the edit through SQL | S26-C03 |
| FD-06 | Concurrent clients | 8 threads x 6 requests (reads, refused writes, valid idempotent writes) against the real loopback listener | no 5xx; no lost audit row; chain verifies; `integrity_check` ok; idempotent writes applied once | S26-C04 |
| FD-07 | Clock skew | FixedClock set backwards/forwards across a session and a re-auth | expired session refused; a re-auth timestamp in the future does not extend the window; no exception | S26-A06, S26-C05 |
| FD-08 | Hostile partner feed shapes | unparsable JSON, unsupported schema revision, negative quantity, unmatched key (existing shipped variants plus the typed values) | defined intake outcome code (quarantine/refuse), raw item kept, replay changes 0 | existing TST-INT + S26-B02 |

### FD-2 What a pass means [Verified Fact: declared]
A pass is a SAFE failure: defined error, no partial write, no secret in the message, audit trail intact. A fault that the system survives by silently doing something else (for example falling back to a default for a safety key) is a finding.

### FD-3 Out of scope [Verified Fact]
Disk full, power loss mid-write, process kill during migration, backup/restore timing (Stage 28/29; backup/restore mechanics are covered by TST-CO-07/09 and the rollback rehearsals), network partition (no network by design).

## Evidence References
`hub/core/errors.py` (error registry), `hub/store/db.py`, `hub/security/audit.py`, `hub/security/exposure.py`, `docs/12-specs/error-handling-spec.md`.

## Assumptions
- A-26-11 [Assumption] SQLite file permission faults are a fair stand-in for storage faults on the laptop; they do not model a failing disk.

## Unknowns
- U-26-09 Behaviour on a real shared filesystem (the production target is undecided).

## Unresolved Issues
- None.

## Residual Risks
- RR-26-09 No crash-consistency test (kill -9 mid-transaction): SQLite journaling is relied on, not proven here.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
