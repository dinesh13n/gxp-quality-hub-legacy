---
stage: "26 — TEVV + AI Red Teaming"
artifact: "adversarial-dataset-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["tests/hub/data_s26/adversarial_corpus_v1.json", "tests/hub/test_tst_hub_stg24_injection.py (S40 corpus of 17)", "docs/24-security-privacy/threat-model.md", "docs/12-specs/security-spec.md ABU-01..ABU-10"]
supersedes: "none"
---
**Label: synthetic, unvalidated. The corpus is strings and request shapes only. No string is a working exploit against an external system; every host name is an RFC 2606 example name (`x.example`, `evil.example`). It is test input for deterministic controls, not a model prompt set.**

## Summary
Adversarial corpus v1.0 (hash-pinned) has 114 hostile strings in 12 classes, 10 typed numeric values, 3 JSON nesting depths, 3 string lengths, 19 mass-assignment keys and 14 spoofed headers. It is a superset of the 17-string Stage 24 corpus (S40/S41). Version and hash are declared here BEFORE any result and a test (S26-B01) fails if the file changes.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AD-1 Version pin [Verified Fact]
File `tests/hub/data_s26/adversarial_corpus_v1.json`, schema `hub-s26-adversarial-corpus/v1`, version `1.0`, sha256 `1806bd77cb2c69619bd074515bf497049c1288dd0c957dac6a84d90b9a556f7b`. Any later change creates `adversarial_corpus_v2.json`; v1 is never edited (stage prompt: preserve dataset versions).

### AD-2 Classes [Verified Fact: counts from the file]
| Class | Strings | What it attacks | Threat (Stage 24) |
|---|---|---|---|
| MK markup | 12 | stored/reflected HTML in pages and JSON | T-02 insecure output handling |
| AT attribute breakers | 5 | quote/backtick escapes in attributes | T-02 |
| JU script URLs | 5 | `javascript:`/`data:` in link-like fields | T-02 |
| HD header/CRLF | 6 | response splitting via reason, correlation id, cookie, notes | T-02, ABU |
| SQ SQL | 12 | stacked queries, UNION to credential tables, ATTACH, PRAGMA | T-13 |
| FT FTS operators | 9 | NEAR/OR/NOT/column filters/wildcards in search | T-13 |
| PT path traversal | 12 | `..`, encoded, double-encoded, absolute, `file:`, `//host` | T-13, T-14 |
| UN Unicode | 15 | bidi override, NUL, BOM, zero-width, homoglyphs, fullwidth, combining, emoji, lone surrogate, C1/C0 controls | T-02, identity confusion |
| IN instruction-like (prompt-injection style) | 20 | text that tries to steer a decision, approve, release holds, define a clock, redefine policy, call a tool | T-01, T-03, T-05 |
| TP template/format | 9 | `{{ }}`, `${ }`, `%n`, Python format, JNDI | T-02, T-13 |
| CM shell | 6 | `$(id)`, backticks, pipes | T-13 |
| LG log forging | 3 | newline + fake JSON audit/log line | T-07, T-15 |
| **Total** | **114** | | |
Plus: `typed_values.numbers` (10), `json_nesting_depths` (64, 1,000, 20,000), `string_lengths` (1,000; 65,536; 1,048,577), `mass_assignment_keys` (19), `spoof_headers` (14).

### AD-3 Surfaces each class is sent to [Verified Fact: declared; S26-B02/B03/B05/B06]
Write surfaces: intake item notes/payload text (OP-INT-01 via the ingest service), evidence `source_ref` and `note` (OP-DEC-06), fact `basis` (OP-DEC-05), transition `basis` (OP-DEC-01), policy name/description (OP-POL-02), rule inputs (OP-POL-06), draft text (OP-REV-04), crosswalk link fields (OP-ID-02), login username (OP-SEC-01), conflict resolution note (OP-INT-03). Read surfaces: search `q` (OP-REV-03), queue filters (OP-REV-01), crosswalk lookup `id`, case id and event id path segments, `as_of`, `limit`, `cursor`, headers `X-Correlation-Id`, `X-Hub-Reason`, `Idempotency-Key`, `Cookie`, `Authorization`.

### AD-4 Expected outcome per class [Verified Fact: declared before results]
For every (string, surface) pair: no HTTP 500 (M-07); HTML pages carry no active tag from data and every non-HTML answer is JSON/plain text with `nosniff` (M-08); no response header contains an injected header name or value (M-02 rule in `evaluation-metrics.md`); the decision tables, case state and Zone H footprint do not change except by the intended write; refused or hostile requests add only audit rows and the audit chain verifies afterwards (M-09). Accepted storage of hostile text as DATA is allowed and expected (hostile text is evidence, not an error); the test checks it is returned escaped/JSON-encoded, never interpreted.

### AD-5 Metamorphic pair for injection invariance [Verified Fact: declared]
Two identical stores receive the same 12 partner-feed items; in store B the free-text fields (`notes`, evidence `note`, `basis`) carry IN-class strings, in store A neutral text of equal length. Decision-relevant outputs (decision events minus free text, case state, rule results for fixed inputs, flags, metric values, intake outcome codes) must be identical (RT-08).

### AD-6 Relationship to AI red teaming [Inference]
There is no model, so there is no jailbreak or tool-use surface. The IN class tests the only thing that remains meaningful: that instruction-like text is inert data for a deterministic system (PNFR-13). If AI is ever added (RQ-1..RQ-3, new Dinesh decision), this dataset must be extended with model-specific attacks before any AI work item starts (ER-1).

## Evidence References
`tests/hub/data_s26/adversarial_corpus_v1.json`; Stage 24 `test_tst_hub_stg24_injection.py` (17-string corpus); `docs/24-security-privacy/prompt-injection-controls.md`.

## Assumptions
- A-26-10 [Assumption] A string corpus covers the classes the threat model names; it is not a fuzzing campaign (RS-14 stays open).

## Unknowns
- U-26-08 Attack classes not in the corpus (for example HTTP request smuggling, slow-loris, TLS) are untested and unknown.

## Unresolved Issues
- None.

## Residual Risks
- RR-26-08 Corpus is finite and hand-written; coverage of unknown classes is not shown.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
