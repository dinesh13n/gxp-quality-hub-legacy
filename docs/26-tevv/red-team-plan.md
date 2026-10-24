---
stage: "26 — TEVV + AI Red Teaming"
artifact: "red-team-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/24-security-privacy/threat-model.md T-01..T-26", "docs/24-security-privacy/attack-surface-map.md", "docs/24-security-privacy/prompt-injection-controls.md", "docs/12-specs/security-spec.md ABU-01..ABU-10", "hub/security/route_registry.json", "hub/web/ui_routes.json", ".fde/orchestrator-decisions.md OD-08, OD-17, OD-31, OD-32"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Rules of engagement: sandbox copies only, loopback only, synthetic users and a test-only holder list that exists nowhere in shipped config. This is adversarial testing of deterministic controls; there is no model to jailbreak (OD-08). Findings are recorded and routed; nothing is fixed during TEVV.**

## Summary
The stage prompt asks for red teaming of prompt injection, data leakage, control bypass, excessive agency and tool abuse. For a No-AI product each class is re-read as an attack on a deterministic control, executed as the S26 suite (about 25 test methods in four files plus one egress-guarded wrapper) against the in-process web app and the real loopback listener. 20 attack cases RT-A01..RT-A20 map to 11 of the Stage 24 threats.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RP-1 Class mapping for a No-AI product [Verified Fact: OD-08; Inference: mapping]
| Prompt class | Meaning here | Where tested |
|---|---|---|
| Prompt injection | instruction-like text in feed rows, notes, evidence, search terms and policy text must remain inert data; decisions depend only on rules and humans | S26-B02, B03, B04 (invariance) |
| Data leakage | credentials, tokens, C3 fields, paths, stack traces, SQL text must not appear in any response, header or audit detail | S26-B07 |
| Control bypass | skipping authentication, authorisation, CSRF, Zone H eligibility, re-authentication, loopback binding | S26-A01..A06 |
| Excessive agency | an automated or non-human principal (integration token, service identity, scheduler) performs a human-only action | S26-A02, A04 |
| Tool abuse | the hub's tools are its operator CLIs, tokens and HTTP operations; abuse = mass assignment, spoofed identity headers, method override, replayed re-auth tokens | S26-A03, A04, A06 |
| Model/network calls | none may occur | S26-D01 and E26 |

### RP-2 Attack cases [Verified Fact: declared; each is a pass/fail check with a threshold in release-thresholds.md]
| ID | Attack | Threat | Threshold | Test |
|---|---|---|---|---|
| RT-A01 | Call every registered operation as every role, no token, and a bogus token; compare with the registry | T-09, T-17 | RT-09 | S26-A01 |
| RT-A02 | Attempt ZH-01..ZH-10 as every actor kind with the shipped EMPTY holder list | T-03 | RT-10 | S26-A02 |
| RT-A03 | Look-alike holder identities, stale/foreign/replayed re-auth tokens, re-auth boundary | T-03, T-11 | RT-10 | S26-A03 |
| RT-A04 | Mass assignment keys (19) and spoofed identity/method headers (14) on every POST | T-09, T-17 | RT-09, RT-10 | S26-A04 |
| RT-A05 | Writes without CSRF proof, forged Origin/Referer, preflight | T-12 | RT-09 | S26-A05 |
| RT-A06 | Token after logout, cookie vs bearer mismatch, fixation, expiry boundary | T-11 | RT-09 | S26-A06 |
| RT-A07 | Hostile corpus on all write surfaces (data in, data out) | T-01, T-02, T-13 | RT-07 | S26-B02 |
| RT-A08 | Hostile corpus on all read surfaces and headers | T-02, T-13 | RT-07 | S26-B03 |
| RT-A09 | Injection invariance metamorphic pair | T-01, T-05 | RT-08 | S26-B04 |
| RT-A10 | Body size, nesting, duplicate keys, bad UTF-8, truncated JSON, wrong content type, numeric edge values | T-19 | RT-07 | S26-B05 |
| RT-A11 | Path/verb abuse: traversal, encodings, 200/201 segment, TRACE/PUT/DELETE/HEAD | T-09, T-13 | RT-07 | S26-B06 |
| RT-A12 | Leakage sweep of every GET route as every role plus error paths | T-07, T-20 | RT-11 | S26-B07 |
| RT-A13 | Unauthenticated request flood effect on the audit table (amplification) | T-19 | informational (Low if loopback) | S26-A07 |
| RT-A14 | Read-only / missing / empty store, fail-closed behaviour | T-16 | RT-12 | S26-C01 |
| RT-A15 | Corrupt/missing config, kill switch | T-23 | RT-12 | S26-C02 |
| RT-A16 | Audit tamper, delete, truncate, anchor edit | T-15 | RT-12 | S26-C03 |
| RT-A17 | Concurrent clients on the loopback listener | T-19 | RT-12 | S26-C04 |
| RT-A18 | Clock skew on sessions and re-auth | T-11 | RT-12 | S26-C05 |
| RT-A19 | No model/network call during the whole sweep; deny-list; dependency scan | T-04, T-06, T-21 | RT-05 | S26-D01, E26 |
| RT-A20 | Mutation of the controls themselves (DW-23) | all | RT-06 | `evidence/s26_mutation_gate.py` |

### RP-3 Rules of engagement [Verified Fact: declared]
1. Sandbox copies only (OD-03a); never the working tree or `data/`; backup checksum rc 0 before and after every run.
2. No network beyond loopback; the egress guard stays installed for E26; no real credentials exist or are used; all users and passwords are generated per test run.
3. Zone H holders: shipped config stays EMPTY. A test-only holder list (`holder-1`, `holder-2`) is configured only inside sandbox stores for S26-A03 and the rehearsal; it is labelled synthetic in the tests and is not a person or an approval.
4. No fix during TEVV. A defect becomes a finding in `red-team-findings.md` with severity per `release-thresholds.md` TH-1, then routed (Stage 27/30/Dinesh).
5. Destructive faults (chmod, edit, truncate) apply to private copies in the sandbox, deleted afterwards (own copies only).

### RP-4 Out of scope [Verified Fact]
External penetration test, TLS/proxy, browser-executed XSS (responses are inspected, not rendered), volumetric DoS, supply-chain of the Python runtime, social engineering, the legacy application's own defects (T-26; byte-identical), any AI-model attack (no model).

## Evidence References
`docs/24-security-privacy/threat-model.md`; `hub/security/route_registry.json`; `hub/web/ui_routes.json`; `tests/hub/test_tst_hub_stg24_injection.py`; `tests/hub/_inc08.py` (WStore); `tests/hub/_http8.py`.

## Assumptions
- A-26-12 [Assumption] The in-process `WebApp.handle` path is the same code the socket server calls (hub/web/app.py docstring); S26-C04 and parts of S26-A use the real listener to cover the transport layer.

## Unknowns
- U-26-10 Real browser behaviour of the UI pages (CSP, form handling) is not exercised.

## Unresolved Issues
- None.

## Residual Risks
- RR-26-10 Hand-written HTTP stack (RS-13) tested through a raw-socket client and in-process calls only.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
