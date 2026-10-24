---
stage: "26 — TEVV + AI Red Teaming"
artifact: "edge-dataset-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/12-specs/acceptance-criteria.md (41 edge ACs)", "docs/12-specs/error-handling-spec.md EC-01..", "hub/web/app.py", "hub/security/settings.py", "hub/security/zone_h.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Edge cases are boundary values of declared limits. Each boundary below is read from code or spec; none is invented.**

## Summary
The edge set probes the declared limits of the hub: body size, page size, re-authentication window, lockout threshold, session timeouts, identifier syntax, empty and maximal collections. 41 edge ACs already have tests (Stage 15/16); the S26 suite adds boundary sweeps where an off-by-one would be a control bypass (re-auth window, body limit) and re-uses the others by reference.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### ED-1 Boundary table [Verified Fact: limit read from code/spec; "Probe" is the planned S26 case]
| ID | Limit | Source | Values probed | Expected | Test |
|---|---|---|---|---|---|
| ED-01 | Zone H re-authentication window `zone_h.reauth_window_seconds` | `hub/security/zone_h.py` (refuse when elapsed > window) | elapsed = window - 1 s, = window, = window + 1 s (test-only holder, sandbox) | accepted, accepted, refused `reauth_required` | S26-A03 |
| ED-02 | Request body limit 1 MiB | `hub/web/app.py BODY_LIMIT` | 1,048,576 bytes and 1,048,577 bytes (JSON padded) | processed (4xx validation allowed), then 413 E-REQ-TOO-LARGE; never 500 | S26-B05 |
| ED-03 | Page size clamp 100, cursor | `hub/web/api.py _int/_page` | `limit` = 0, 1, 100, 101, 500, -5, `abc`, `1e3`; `cursor` = -1, 10^9+1 | clamped to 1..100 or 400 E-REQ-INVALID; AC-REV-03 paging (500 -> 100) | existing AC-REV-03 stand-in + S26-D02 |
| ED-04 | Lockout threshold (5/15/15) | `hub/security/settings.py` | attempts 4, 5, 6 | locked at 5, generic error text, no user enumeration | existing TST-SEC-05 / S22 (re-run) |
| ED-05 | Session idle/absolute timeouts | `hub/security/settings.py` | idle - 1 s, idle + 1 s (FixedClock) | valid; expired | S26-A06 |
| ED-06 | Holder identity string | `zone_h.holders` match is exact string equality | `holder-1`, `Holder-1`, `holder-1 `, zero-width joiner suffix, Cyrillic o, `holder-10` | only the exact string passes | S26-A03 |
| ED-07 | Correlation id `^[A-Za-z0-9._:-]{8,64}$` | `hub/web/app.py _CID` | 7, 8, 64, 65 characters; hostile characters | echo valid, replace invalid | S26-B03 (extends S41) |
| ED-08 | Path segment `^[A-Za-z0-9._:@#=-]{1,200}$` | `hub/web/routes.py _SEG` | 0, 1, 200, 201 characters; encoded slash; NUL | match / no route (403 deny-by-default) | S26-B06 |
| ED-09 | JSON nesting depth | CPython `json` recursion limit | 64, 1,000, 20,000 | 400 E-REQ-INVALID or 413; never 500 or process crash | S26-B05 |
| ED-10 | String length | none declared (Unknown) | 1,000; 65,536; 1,048,577 characters in a free-text field | accepted or refused with a defined code; never 500 | S26-B05 |
| ED-11 | Empty collections | spec | no holders (shipped), no rule set active (shipped), empty queue | defined refusal / empty page, not an error | S26-A02, existing |
| ED-12 | Numeric edge values | `typed_values.numbers` in the corpus | `1e999`, `NaN`, `Infinity`, `-0`, 2^63, -(2^63)-1 as JSON numbers/strings in amount-like fields | validation 400/422 or quarantine, never 500, never silently stored as another value | S26-B05 |

### ED-2 Existing edge coverage re-run by reference [Verified Fact: AC list in docs/12-specs/acceptance-criteria.md]
41 edge ACs (Stage 12 count). Their tests run inside the full regression (RT-01); S26 does not re-implement them.

## Evidence References
`hub/web/app.py`, `hub/web/api.py`, `hub/web/routes.py`, `hub/security/settings.py`, `hub/security/zone_h.py`, `tests/hub/data_s26/adversarial_corpus_v1.json` (`typed_values`).

## Assumptions
- A-26-09 [Assumption] No documented maximum string length exists; ED-10 records observed behaviour as the baseline (Unknown limit, not a pass/fail of a declared number).

## Unknowns
- U-26-07 Intended maximum free-text length per field (no spec).

## Unresolved Issues
- None.

## Residual Risks
- RR-26-07 Boundary sweeps sample three or four points per limit.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
