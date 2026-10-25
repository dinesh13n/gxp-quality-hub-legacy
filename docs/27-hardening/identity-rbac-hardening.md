---
stage: "27 — Production Hardening"
artifact: "identity-rbac-hardening.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/auth.py", "hub/security/authz.py", "hub/web/authz.py", "hub/gate/service.py", "hub/decision/service.py", "hub/decision/access.py", "hub/web/ratelimit.py", "docs/26-tevv/evidence/s26-tests/authz-matrix.json", "tests/hub/test_tst_hub_stg27_findings.py", "tests/hub/test_tst_hub_stg27_limiter.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
Identity and RBAC were already the most tested part of the hub (Stage 26: 0 wrongly allowed cells in 138 allowed and 222 refused route-by-role cells, 80 of 80 Zone H attempts refused). Stage 27 closed the three defects that attack found: the order of checks on OP-GATE-02 (F-01), the restricted-evidence note visible to a reviewer (F-02, High) and the unbounded audit growth from unauthenticated traffic (RS-04). It also pinned the two layers of deny-by-default separately (M5) and the service-actor tripwire (M9) and the authority_ref check (M10), which a mutation run had shown to be unprotected. Single-factor passwords (RS-02), optional service-token expiry (RS-08) and the single approver (RS-16) are unchanged and remain with Dinesh.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IR-1 Privilege levels [Verified Fact]
| Level | Who | What it can reach | Control |
|---|---|---|---|
| anonymous | no token | `/healthz` and login only; every other registered route 401; unregistered route 403 | `hub/web/authz.py`, S26 A01 matrix |
| reviewer | human, role `reviewer` | read cases / events / queues, attach evidence at quality level; NOT restricted evidence or its note (F-02) | `hub/decision/access.py`, F02 |
| quality_lead, compliance | human | restricted evidence and its note, decisions within their routes | role matrix `hub/security/route_registry.json` |
| dispositioner | human | reaches the gate routes but is not a Zone H holder unless listed in `zone_h.holders` (EMPTY in the shipped config) | `hub/security/zone_h.py`, A02 |
| finance_read | human | no HTTP read surface built yet (RS-05) | route registry |
| integration | service principal | intake route only; refused by every Zone H action (M9 tripwire counts a success as a defect) | `hub/gate/service.py` |
| host operator | OS user running the CLI | `python -m hub.admin` etc.; owns the store file (0600 since S27-DEV-14) | OS permissions |

### IR-2 What Stage 27 changed [Verified Fact]
- **F-01 (S27-DEV-05).** `GateService.require_holder` now checks the session first. An anonymous call writes one `ZONE_H_ATTEMPT` / `denied` / `unauthenticated` audit row whose details hold only `unrecognised` or a valid action code (never attacker text) and raises 401. An authenticated caller with an unknown action still gets 422 E-GATE-UNKNOWN-ACTION. Test `STG27_F01`; mutant X1 (check removed) killed.
- **F-02 (S27-DEV-04, A-27-02).** `DecisionService._withhold_note` is applied in `events()` and `event_with_evidence()`. For EVIDENCE_ATTACHED, a reader whose roles can not read the evidence record's level gets `basis = WITHHELD_BASIS` and `basis_withheld = true`. The stored basis, the event hash and the chain are untouched (a decision hash covers the basis, so the redaction is deliberately view-layer only). A record that can not be resolved is withheld as well. Test `STG27_F02` (reviewer, finance, integration; quality_lead and compliance still read the note; a quality-level note is unchanged for all); mutant X2 killed.
- **RS-04 (S27-DEV-07, A-27-04).** `hub/web/ratelimit.py`: requests refused before an identity exists (401, bad credentials, 403 on an unregistered route) are counted per peer. After `max_rejected` inside `window_seconds` the peer gets 429 before the store is opened: no audit row, no session row. Authenticated traffic, validation errors and role refusals are never counted. 5 tests in `STG27_L01..L04` (L03b included); mutant X7 (never blocks) killed.
- **M5 / M9 / M10.** `STG27_M5` calls `WebAuthorizer.authorize` directly for unregistered routes (the app-level dispatch refused first, so removing the authorizer branch changed nothing); `STG27_M9` plants audit rows to prove the tripwire counts non-human successes only; `STG27_M10` proves blank / non-string `authority_ref` is refused before any holder check or write. All three mutants are now killed.

### IR-3 Unchanged controls re-verified in this stage [Verified Fact]
Groups I8a (35) and I8b (43), S23 (26), S24 (21) and S26 (23) pass after the changes: password hashing (PBKDF2-HMAC-SHA256, 600,000 iterations, minimum length 12), lockout 5 / 15 / 15 minutes, session idle 30 min / absolute 8 h, re-authentication window 300 s, CSRF header on writes, cookie flags, Zone H holder rule in one place.

### IR-4 Gaps [Inference unless marked]
- RS-02 single-factor local passwords. Impact: credential theft is enough. Confidence: high. Route: Dinesh (DQ-S24-01).
- RS-08 service-token expiry optional (DQ-S24-05, recommended 90 days). Not built.
- RS-16 single approver: audit and hash chain are the compensating controls; accepted by Dinesh only as a general risk in OD-30.
- The limiter keys on the socket peer. Behind a proxy that peer is the proxy; no `X-Forwarded-For` is trusted (a spoofable header would defeat the limiter). [Verified Fact: the code reads `req.peer` only.]

## Evidence References
- `hub/gate/service.py`, `hub/decision/service.py`, `hub/web/ratelimit.py`, `hub/web/app.py`
- `tests/hub/test_tst_hub_stg27_findings.py` (F01, F02, M5, M9, M10), `test_tst_hub_stg27_limiter.py`
- `docs/27-hardening/evidence/mutation-s27.json` (M5, M9, M10, X1, X2, X7 KILLED)
- Stage 26 matrix: `docs/26-tevv/tevv-results.md`

## Assumptions
- A-27-02 as in `hardening-plan.md`.
- A-27-04 as in `hardening-plan.md`.
- The role names in IR-1 are the ones in the shipped route registry; no real person holds any role.

## Unknowns
- U-27-05 Who the real holders are: unknown by design; `zone_h.holders` stays EMPTY and naming holders is Dinesh's act (OD-31).
- U-27-06 Whether a second factor is wanted before exposure.

## Unresolved Issues
- D-27-01 (F-02 rule) and D-27-04 (limiter defaults) are open.
- DQ-S24-01, -05 and -08 (control values, token expiry, field classes) are open from Stage 24.

## Residual Risks
- A withheld note hides the text from a reviewer who may legitimately need it; the rule is an assumption until D-27-01.
- A shared peer address makes the limiter a coarse tool (fail closed for all local clients during a block).
- Single-factor passwords remain a Medium residual risk (RS-02).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
