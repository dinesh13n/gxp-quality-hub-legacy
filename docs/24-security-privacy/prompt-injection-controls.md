---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "prompt-injection-controls.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "hub/web/*.py", "hub/gate/", "hub/r2/protection.py", "hub/core/untrusted.py", "hub/guards/", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", "docs/12-specs/security-spec.md", "docs/16-repo-validation/security-scan-summary.md", ".fde/orchestrator-decisions.md", "docs/08-ai-qualification/", "docs/00-preflight/operating-contract/data-use-constraints.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Controls against prompt and indirect injection. The product has NO model (OD-08): nothing reads text as instructions, so the controls are structural: keep hostile text as data, never let it reach a decision parameter, a query, a header or active markup, and keep the door shut for a future model. The estate really contains such text (86 feed rows, 22 of 1,200 documents, 9 evidence events, 15 tiny + 150 bundled lake events). A new 17-string hostile corpus (markup, attribute breakers, script URL, CRLF, SQL, FTS operators, path traversal, bidi, NUL, instruction text, template and format strings) was sent through intake notes, search, lookup, source filters, unknown routes, UI paths and headers: no 500, no active tag in any HTML page, no injected header, no decision event or Zone H action, 0 gate audit records.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PIC-1 Controls [Verified Fact]
| ID | Control | Mechanism | Test |
|---|---|---|---|
| PIC-01 | Inbound text is typed `Untrusted`; the type refuses use as a decision parameter and a static lint (rules U1, U2) checks the code | `hub/core/untrusted.py`, `hub/intake/untrusted_lint.py` | TST-INT-17..29, INC08-S09 |
| PIC-02 | No model call exists; deny-list on imports; egress tripwire; `model_calls_total = 0` | `hub/guards/no_ai.py`, `hub/guards/egress.py` | TST-CO-11, TST-CO-12, E24 |
| PIC-03 | Instruction-like text has no effect on a decision field: the 86 feed rows and 10 variants are ingested over HTTP, the 22 documents searched; decision tables byte-identical | TST-NFR-13 (existing) + S40 (new corpus) |
| PIC-04 | Escape on output; CSP `default-src 'self'`; `nosniff`; JSON served as `application/json` | `hub/web/ui.py`, `hub/web/app.py` | INC08-S10, S40 |
| PIC-05 | `state: DISPOSITIONED`, `qa_disposition` and similar attributes in inbound data are stored as source attributes and cannot create a Zone H event | `hub/gate/`, trigger `decision_events_zone_h` | AC-INT-24, ABU-02 |
| PIC-06 | SQL: bound parameters; FTS terms quoted; identifier allow-lists; a baseline of every formatted / indirect `execute` | S32 baseline, ABU-06 | S32, S40 |
| PIC-07 | Header values (correlation id, reason) are validated or stored as data and never echoed into a response header | `hub/web/app.py` `_CID`, `transport.py` | S41 |
| PIC-08 | Search shows hits for injection strings (they are data) with the untrusted marker; restricted hits need a role and a reason | R2 | I9, INC09 |
### PIC-2 If an AI component is ever added (not in scope) [Inference]
Re-qualification triggers RQ-1..RQ-3 (OD-08) and a new Dinesh decision come first. Then, at minimum: a separate trust label for model-bound context, no tool that writes, a human at Zone H (already enforced), logging of prompts without secrets, and red-team cases built from the existing fixtures (SD-3, Stage 26). None of this is built because there is nothing to attach it to.

## Evidence References
`tests/hub/test_tst_hub_stg24_injection.py` (S40, S41), `evidence/hostile-corpus.json`, `docs/12-specs/security-spec.md` ABU-01..10, `docs/00-preflight/operating-contract/data-use-constraints.md` DU-03.

## Assumptions
- A-S24-PIC-1 The 17 strings are a sample; passing them does not prove absence of every encoding bug (Inference).

## Unknowns
- U-S24-PIC-1 Behaviour of any future model against these fixtures (nothing to test).

## Unresolved Issues
- Output encoding is checked on 5 HTML / JSON surfaces and 85 probe requests; a complete crawl of every UI field is not claimed.

## Residual Risks
RS-15 (if AI is added), RS-13.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
