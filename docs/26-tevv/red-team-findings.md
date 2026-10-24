---
stage: "26 — TEVV + AI Red Teaming"
artifact: "red-team-findings.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/evidence/s26-tests/*.json", "docs/26-tevv/evidence/hub-mutation-s26.json", "docs/26-tevv/evidence/regression/*.json", "tests/hub/test_tst_hub_stg26_*.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW. Nothing here accepts a risk, approves a fix or signs for anyone. Severities are the agent's own reading of the scale declared in `release-thresholds.md` TH-1 and are labelled [Inference]; Dinesh Naik (Engagement lead) may re-rate any of them.**

## Summary
The red team attacked the deterministic controls only (the product has no model; "prompt injection" here means hostile text in every input field). It sent 114 corpus strings plus typed values, structure abuse, URL/verb abuse, spoofed headers, session abuse, transport anomalies and fault injections at the real code paths in sandbox copies. **No Critical finding.** Eleven findings are registered: 1 High, 6 Medium, 4 Low (S26-F-01..S26-F-11). The strongest negative results: 0 Zone H bypasses in 80 shipped-config attempts plus the look-alike, stale-proof and boundary probes with a test-only holder list; 0 differing decision outputs between instruction-like text and neutral text (12 cases, 20 strings, 350 rows compared); 0 wrongly allowed cells in 138 allowed and 222 refused route-role cells (plus 32 UI cells); 0 secret or path or traceback leaks in 469 responses; 0 model calls, 0 connection attempts. Nothing was fixed in this stage (VALIDATE); every finding is pinned in a test that fails on any OTHER occurrence, so a later fix shows up as a deliberate test change.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Register [Verified Fact: observed in sandbox runs; severities are Inference]
| ID | Severity [Inference] | Title | Route (proposal, nothing accepted) |
|---|---|---|---|
| S26-F-01 | Medium | OP-GATE-02 validates the action name before authentication: unauthenticated request returns 422 `E-GATE-UNKNOWN-ACTION` instead of 401 | Stage 27 |
| S26-F-02 | High | Restricted evidence `note` is readable by a reviewer through the event list (`basis` of EVIDENCE_ATTACHED) | Stage 27; Dinesh decides the access rule (A-15-05-1) |
| S26-F-03 | Medium | A lone UTF-16 surrogate in any JSON string stored by the hub gives HTTP 500 `E-HUB-INTERNAL` (5 write surfaces in the sweep, 6 field variants in B08) | Stage 27 |
| S26-F-04 | Low | Operator CLI: unreadable / non-JSON / non-object config file ends in a Python traceback, exit 1, no `E-CFG-*` code | Stage 27 |
| S26-F-05 | Medium | Unknown configuration keys are accepted silently (a mistyped safety key such as `hub.kil` is inert) | Stage 27 |
| S26-F-06 | Low | The loopback listener sets no per-connection read timeout (a short body holds a handler thread) | Stage 27 / Stage 29 |
| S26-F-07 | Low | Any store fault (read-only file, corrupt header) answers every request, also `/healthz`, with the same generic 500 | Stage 27 (observability), by design fail-closed |
| S26-F-08 | Medium | Mutant M9 survived: the Zone H service-actor tripwire counts the wrong actor kind and no test notices (S26 and `TST_OBS`) | Stage 27 test gap |
| S26-F-09 | Medium | Mutant M10 survived: schedule enable without `authority_ref` accepted and no test notices (S26 and `TST_RUN`) | Stage 27 test gap |
| S26-F-10 | Low | Mutant M5 survived: removing the deny-by-default branch in `WebAuthorizer` changes nothing because `WebApp._dispatch` refuses first (equivalent at system level) | Stage 27: test each layer or remove the duplicate |
| S26-F-11 | Low | Group wall times: S26 145 s and E26 174 s on the reference laptop against the 120 s headroom target and the 180 s per-call cap | Stage 27 / orchestrator (cloud run has no cap) |

### S26-F-01 [Verified Fact]
- Attack: AT-A01 route x principal matrix, principals `none` and `bogus` on every one of the 48 API operations.
- Observed: `POST` on OP-GATE-02 with no / unknown action returns 422 `E-GATE-UNKNOWN-ACTION` before the session is looked at. All other cells equal the registry.
- Impact: none on state (one audit row, nothing else changes). Inconsistent with ER-1 (authenticate before validate); reveals to an anonymous caller that the route exists and what action names are valid (the route is registered, so low).
- Risk (Inference): Medium by the scale (wrong refusal, safe in effect). Confidence: high (reproduced in `authz-matrix.json`).
- Unresolved: is the 422 intended for pack-gate routes (a design choice)? Owner: Stage 27.

### S26-F-02 [Verified Fact]
- Attack: leakage sweep B07 over 469 responses with a restricted evidence record whose note holds a marker.
- Observed: the evidence record itself is redacted for non-readers (AC-DEC-13 holds on OP-DEC-04), but the same note is copied into the `basis` of the EVIDENCE_ATTACHED event, and `GET /api/v2/cases/{id}/events` and `/api/v2/events/{id}` return it to `reviewer`. The marker was not seen for the finance and service roles. Zero other leak locations.
- Impact: a reviewer can read text that the access rule says is for quality_lead, compliance and dispositioner. Not a credential. Data in the sandbox is synthetic.
- Risk (Inference): High, conservative reading: an access-control rule can be bypassed by an ordinary authorised role without host access. The scale text for High names host access or leaving loopback, so Medium is arguable; the agent chose the higher rating. Confidence: high.
- Unresolved: which routes should show `basis` for restricted evidence (the matrix is itself an Assumption A-15-05-1)? Owner: Dinesh to decide the rule, Stage 27 to implement.
- Mutation cross-check: mutant M6 (reviewer added to restricted readers) was killed by `TST_DEC_13` but not by S26, so S26 B07 would not catch a wider regression of this rule alone.

### S26-F-03 [Verified Fact]
- Attack: corpus string UN #10 (JSON `"\ud800"`, a lone surrogate) on every write surface.
- Observed: 500 `E-HUB-INTERNAL` on intake, evidence note and source_ref, policy name, login username and password, flag override. The generic envelope leaks nothing (checked), nothing is written (B08: 0 changed tables), the next valid request succeeds, integrity ok, chain ok.
- Impact: denial of one request, no state change. RT-07 requires 0 HTTP 500, so RT-07 is NOT MET.
- Risk (Inference): Medium (unhandled exception 500 without state change). Confidence: high.
- Unresolved: reject at the wire (400) or encode with `surrogatepass`? Owner: Stage 27.

### S26-F-04, S26-F-05 [Verified Fact]
- `config-faults.json`: 11 faulty configurations are refused as designed (exit 2 `E-CFG-INVALID`; `hub.kill: true` exit 3 `E-HUB-KILLED`). File missing, truncated JSON, not JSON and JSON array all stop the CLI (non-zero) but with a traceback and no hub code (F-04). Unknown top-level key, unknown `zone_h` key and `hub.kil` are accepted with exit 0 (F-05).
- Impact: F-04 is an operator-only surface. F-05: an operator who mistypes `hub.kill` believes the kill switch is set while it is not; a mistyped `zone_h` key leaves holders EMPTY (fail-safe direction). Risk (Inference): F-04 Low, F-05 Medium. Confidence: high.

### S26-F-06, S26-F-07 [Verified Fact]
- `transport-anomalies.json`: chunked 400, negative / non-numeric Content-Length 400, duplicate or huge Content-Length and garbage start line closed, 70 kB header line and 200 headers and long URI no 5xx, absolute-URI and bare-LF answered 200; 40 idle connections did not starve the server. A client that declares 1000 bytes and sends 2 was still waiting after 1.5 s; `Handler.timeout` is None. 8 x 8 concurrent requests: 0 unexpected answers, chain ok, integrity ok.
- `store-faults.json`: read-only DB (skipped when run as root) and corrupt header: every request including `/healthz` answers the generic 500 with no path or SQL text; after the fault is removed the next write succeeds and the chain verifies. A missing store is refused at start with `E-STORE-NOT-MIGRATED`.
- Risk (Inference): both Low on loopback (RS-04 family). Confidence: high for F-06, medium for F-07 (whether `/healthz` should distinguish a store fault is a design question).

### S26-F-08, S26-F-09, S26-F-10 [Verified Fact]
- Source: `hub-mutation-s26.json`. M9 (`zone_h_service_actor_accepted` uses `actor_kind = 'human'`) and M10 (`set_enabled` skips the authority_ref check) survive S26 and the earlier `TST_OBS` / `TST_RUN` groups. M5 survives S26 and `TST_SEC`; reading the code, `WebApp._dispatch` raises the same refusal first, so this is an equivalent mutant at system level [Inference].
- RT-06 rule: a survivor in a Zone H, authentication, authorisation, CSRF or loopback mutant is at least Medium: F-08 and F-09 Medium; F-10 Low because the behaviour is protected by a second layer [Inference].

### Negative results (attacks that failed) [Verified Fact]
| Attack | Result | Evidence |
|---|---|---|
| Zone H by every actor kind, shipped empty holders (80 attempts) | 0 accepted; footprint unchanged | `zone-h-bypass-shipped.json` |
| Look-alike ids (case, trailing dot, space, NUL, zero-width), stale proof, window boundary | all refused; window-1 s / -1 ms accepted, +1 ms / +1 s / +1 us refused, exact accepted on the pure rule | `zone-h-identity-boundary.json` |
| Mass-assignment keys (19), spoofed identity headers (14) | 0 effect; actor is server derived | `mass-assignment-spoofing.json` |
| CSRF / CORS: 16 POST ops, 6 UI forms, 96 refused requests | 0 accepted, 0 CORS header | `csrf-cors.json` |
| Hostile text on 10 write surfaces (1,135 requests) and all read surfaces (1,894 requests) | 0 active markup, 0 header injection; 5 HTTP 500 all S26-F-03 | `hostile-*.json` |
| Instruction-like text vs neutral text | 0 differing sections of 13 | `injection-invariance.json` |
| Body structure abuse (nesting, duplicate keys, bad UTF-8, NaN, huge int) | 0 HTTP 500; limit exact is 422, +1 byte is 413 | `body-structure-abuse.json` |
| URL / verb abuse (515 requests) | 0 HTTP 500; all traversal tricks 403 | `url-verb-abuse.json` |
| Session abuse (idle 1,800 s, absolute 28,800 s, rollback of the clock) | boundaries hold; an expired session stays dead | `session-abuse.json`, `clock-rollback.json` |
| Audit tamper (alter, delete, truncate after anchor, edit anchor) | each detected by verify (and by `OP-SEC-04` for the altered row); triggers refuse SQL edits | `audit-tamper.json` |
| Unauthenticated flood (201 requests) | 201 audit rows of 81 bytes, no raw path stored; growth is the known RS-04 | `audit-amplification.json` |
| Model / network | 0 connects, 0 DNS lookups, 0 model calls; 13 hostile gateway URLs refused | `no-ai-proof.json` |

### Known limitation demonstrated, not a new finding [Verified Fact]
- A host-level actor who recomputes the whole hash chain AND rewrites the anchor file produces a chain that verifies ok (RS-03 / R-SEC-1). The opt-in anchor seal (Stage 24) is the documented mitigation and is not enabled in the sandbox. Risk stays OPEN; this stage accepts nothing.

## Evidence References
`docs/26-tevv/evidence/s26-tests/*.json` (22 files), `docs/26-tevv/evidence/hub-mutation-s26.json`, `docs/26-tevv/evidence/regression/report-S26.json`, `tests/hub/test_tst_hub_stg26_{control,input,wire,resilience,noai_walkthrough}.py`, corpus `tests/hub/data_s26/adversarial_corpus_v1.json` (sha256 1806bd77...f7b).

## Assumptions
- A-26-13 [Assumption] Severity ratings follow TH-1 as written; where the scale is ambiguous (S26-F-02) the higher rating was chosen. Confirm: Engagement lead.
- A-26-14 [Assumption] A surviving mutant is a test gap, not a product defect (A-26-06), unless the mutant is equivalent (F-10).

## Unknowns
- U-26-05 Whether the 3.12+ runtime changes any finding (surrogate handling, `http.server` behaviour): not run (RT-14).
- U-26-06 Behaviour under a real browser (walkthroughs unsigned).

## Unresolved Issues
- All eleven findings are OPEN. None is remediated or accepted in this stage.

## Residual Risks
- See `residual-tevv-risks.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
