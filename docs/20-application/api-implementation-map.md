---
stage: "20 — Application & Services Engineering"
artifact: "api-implementation-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/cli.py", "hub/web/cli.py", "hub/gate/actions.py", "hub/policy/service.py", "hub/review/producer.py", "hub/golden/run.py", "hub/golden/observe.py", "hub/security/route_registry.json (unchanged)", "docs/12-specs (OpenAPI x-roles, F02/F03/F08/F10)", "tests/hub/test_tst_hub_stg20_*.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Contracts are the Stage 12 specs as finalised by Stage 17 (OD-22/OD-25); new surfaces below are proposed for the Stage 12 v0.2 package (DW-13, Stage 23) where the spec has no entry.**

## Summary
Stage 20 added no HTTP route and did not change the route registry. It added two CLI commands (`python -m hub golden-observe`, `python -m hub.web produce-traces`), two CLI options (`golden-compare --observe / --observed`), one Zone H payload operation (ZH-10 `withdraw_policy`, reachable through the existing choke point `POST /api/v2/zone-h/actions`), and service methods (`PolicyService.withdraw`, `producer.produce`, `producer.flag_trail`, `zone_h.refusal`). Each is listed against its contract and test.

## Findings
| Surface | Kind | Contract | Implemented in | Test | Spec status | Tag |
|---|---|---|---|---|---|---|
| `python -m hub golden-observe --data-dir D --legacy-root L [--out F]` | CLI (host operator) | FAC-05, BEH-CO-01, AC-CO-01 (observed new side) | `hub/cli.py`, `hub/golden/observe.py` | STG20 S04, S05; TST-CO-01 | addendum needed (new command) | [Verified Fact] |
| `golden-compare --observe` / `--observed F` | CLI option | FAC-05; record accepted only if code digest + baseline sha match | `hub/golden/run.py` | TST-CO-01 a-f, STG20 S05, S06 | addendum needed | [Verified Fact] |
| `golden-compare` default (no option) | behaviour change | module probes NOT-RUN (exit 6) instead of declared values | `hub/golden/run.py` | TST-CO-01 f, TST-CO-02 e | addendum needed (S20-DEV-01) | [Verified Fact] |
| `python -m hub deviations` | CLI (unchanged) | FR-CO-01, FAC-06 | register seed v2 | STG20 S07, S08 | — | [Verified Fact] |
| ZH-10 payload `{"op": "withdraw_policy", "policy_id", "version", "withdrawn_from", "reason"}` via `POST /api/v2/zone-h/actions` | HTTP (existing OP-GATE-02) | FR-POL-01, BEH-POL-05, FAC-13 (proposed), AC-GATE-02/21 | `hub/gate/actions.py` -> `PolicyService.withdraw` | STG20 S11, S12 | FAC-13 proposed (DB-3); op name addendum needed | [Verified Fact] |
| `PolicyService.withdraw(sess, policy_id, version, withdrawn_from, reason, authority_ref)` | service | as above; ZH-10 eligibility via `_zone_h` hook | `hub/policy/service.py` | STG20 S12, S13 | — | [Verified Fact] |
| `PolicyService.status_report()` gains key `withdrawn` | read model | AC-POL-05 unchanged | `hub/policy/service.py` | TST-POL-05, STG20 S11 | additive | [Verified Fact] |
| `python -m hub.web produce-traces --data-dir D --legacy-root L --function F [--ruleset-ref R]` | CLI (host operator) | FR-REV-01, BEH-REV-02, PNFR-15, RTD-69 | `hub/web/cli.py`, `hub/review/producer.py` | STG20 S14 | addendum needed (new command) | [Verified Fact] |
| `producer.flag_trail(con, flag_id)` | service read | FR-GATE-06 / BEH-GATE-08 trail for intake flags without a case | `hub/review/producer.py` | STG20 S15 | no HTTP route (not specified) | [Verified Fact] |
| CLI error output (all runners) | contract record | FAC-10 (addendum option, DQ-05) | unchanged | STG20 S10 | `spec-addendum-cli-error-shape.md` | [Verified Fact] |
| `tests/hub/run_hub_groups.py` | test tooling | DW-02/03 | tests only | STG20 S01 | n/a | [Verified Fact] |

- [Verified Fact] Route registry (`hub/security/route_registry.json`) and OpenAPI-derived permission matrix unchanged (no new route); TST-SEC-01 green in the targeted run.
- [Inference] Because withdrawal enters through the existing Zone H choke point, its HTTP authorisation, CSRF, re-auth token and audit behaviour are inherited unchanged (verified for refusals in S12, acceptance in S11).

## Evidence References
Targeted sandbox runs listed in `application-test-summary.md`; `docs/20-application/evidence/golden-compare-observed.json`.

## Assumptions
- A-20-API-1 [Assumption] Withdrawal is classified ZH-10 ("policy change", BEH-POL-05: "Edits are Zone H (ZH-10)"), not ZH-05; confirm with DW-13 (Stage 23): Engagement lead (Dinesh Naik).

## Unknowns
- U-20-API-1 Whether a dedicated HTTP read route for flag trails / withdrawal state is wanted (none specified) - Stage 23 / Stage 26 walkthroughs.

## Unresolved Issues
- New commands / option / payload op need Stage 12 v0.2 addendum entries (DW-13).

## Residual Risks
- RR-API-1 Operators who scripted `golden-compare` without options now get NOT-RUN rows instead of declared values (exit code unchanged: 6) (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
