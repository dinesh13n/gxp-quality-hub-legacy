---
stage: "20 — Application & Services Engineering"
artifact: "error-handling-implementation.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/core/errors.py", "hub/core/req_errors.py", "hub/policy/errors.py", "hub/golden/run.py", "hub/golden/observe.py", "hub/policy/service.py withdraw()", "hub/review/producer.py", "docs/20-application/spec-addendum-cli-error-shape.md", "tests/hub/test_tst_hub_stg20_*.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. No new error code was introduced in Stage 20; all refusals reuse catalogued codes.**

## Summary
Stage 20 error handling: fail closed, reuse existing codes, never fabricate a value. Golden-compare turns an unusable observation into NOT-RUN rows (exit 6) with a reason; withdrawal and the producer refuse before writing; the CLI error shape is recorded as an addendum (DW-09, DQ-05).

## Findings
| Situation | Behaviour | Code / exit | Writes on refusal | Test | Tag |
|---|---|---|---|---|---|
| golden-compare without an observation | 9 module probes NOT-RUN, reason "module observation not supplied ..." | exit 6 (E-CO-UNAPPROVED-DEVIATION) | none | TST-CO-01 f | [Verified Fact] |
| observation record stale (code digest) / other baseline / unknown schema | NOT-RUN, reason names the mismatch; `observation.status = refused` | exit 6 | none | STG20 S05 | [Verified Fact] |
| `--observe` without `--legacy-root` | refused, NOT-RUN | exit 6 | none | STG20 S06 | [Verified Fact] |
| golden-observe on a non-sandbox path | E-CO-NOT-SANDBOX (sandbox guard) | 7 | none | guard reused (TST-CO-06 family) | [Inference] same guard as golden-compare |
| withdrawal: no holders / non-holder | E-GATE-NO-HOLDERS (423) / E-GATE-NOT-AUTHORISED (403), audited ZONE_H_ATTEMPT denied | 19 | no policy event | STG20 S12 | [Verified Fact] |
| withdrawal: empty authority_ref | E-POL-AUTHORITY-REQUIRED | 23 | none | STG20 S12 | [Verified Fact] |
| withdrawal: candidate / already withdrawn / date before effective_from / bad date / empty reason | E-POL-INVALID | 23 | none | STG20 S12 | [Verified Fact] |
| producer without active set and without --ruleset-ref | E-POL-NO-ACTIVE-RULESET | 23 | none | STG20 S14 | [Verified Fact] |
| producer: input refused by rule service | counted `input_invalid`, no trace | — | none for that case | design (S14 counts 0 on FX) | [Verified Fact] |
| flag action with empty reason | E-GATE-REASON-REQUIRED | — | none | STG20 S15 | [Verified Fact] |
| CLI error output | one JSON object on stderr, documented shape | per class | — | STG20 S10 | [Verified Fact] |
- [Verified Fact] E-REQ-INVALID moved to `hub/core/req_errors.py` and is re-exported by `hub/web/errors.py`; it is the same class object (STG20 S22), so the HTTP status mapping (400) is unchanged.
- [Verified Fact] Every withdrawal write is one `audit.change` transaction: the policy event and the audit record commit together or not at all (existing mechanism).

## Evidence References
Tests listed; `spec-addendum-cli-error-shape.md`.

## Assumptions
- A-20-EH-1 [Assumption] Reusing E-POL-INVALID for withdrawal validation (rather than a new code) is acceptable for Stage 12 v0.2; confirm: Engagement lead (Dinesh Naik), DW-13.

## Unknowns
- None.

## Unresolved Issues
- Exit-code collisions 2 / 9 (DQ-04) untouched - Stage 23.

## Residual Risks
- RR-EH-1 `golden-observe` raises a Python ValueError (traceback, exit 1) only if its scratch-path guard detects a path outside the observe directory - an internal invariant, not reachable with guarded inputs (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
