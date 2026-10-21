---
stage: "20 — Application & Services Engineering"
artifact: "application-component-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/ (branch stage-20-application)", "docs/10-architecture component model C1..C11", "docs/16-repo-validation/evidence/package-graph.txt", "docs/20-application/evidence/static-checks-main-41098c0.json", "docs/20-application/evidence/static-checks-stage20.json", "docs/18-delivery/delivery-backlog.md DW-02..DW-09", "tests/hub/non_add_edits.json"]
supersedes: "none"
---
**Label: synthetic repository (GxP Quality (FDE Capstone)), unvalidated. Stage 20 runs in BUILD - SCOPED WRITE mode on branch `stage-20-application` (OD-26). Nothing here is cut over, approved or in production.**

## Summary
The application is the stdlib-only Python modular monolith `hub/` beside the unchanged legacy estate (ADR-001/003). Stage 20 delivered the Stage 18 increments DI-02 (change safety: DW-02..DW-05), DI-03 (structure: DW-06) and DI-04 (R1 gaps: DW-07..DW-09) on one branch (OD-26 named one branch instead of the three the plan sketched). It added 7 hub modules, 2 data files, 9 test / test-infrastructure files and modified 23 existing hub files and 7 existing test files - every modification listed with its work item in `tests/hub/non_add_edits.json` (deviations S20-DEV-01..08, `application-readiness.md`). No legacy file, `data/`, `pyproject.toml` or CI workflow changed.

## Findings
### CM-1 Components touched in Stage 20 (component ids from docs/10-architecture)
| Component | Package / module | Stage 20 change | Work item | Tag |
|---|---|---|---|---|
| C11 coexistence / change safety | `hub/golden/observe.py` (new), `hub/golden/run.py`, `hub/golden/probes_s20.json` (new), `hub/cli.py` | golden-compare observes the BUILT modules (`golden-observe`, `--observe`, `--observed`); no declared values | DW-04 | [Verified Fact] |
| C11 deviation register | `hub/coexistence/seed_s20.json` (new), `hub/coexistence/register.py` | DV-01..DV-11 proposed; DV-07a text; DV-09 label; safe refresh of INC-02 rows | DW-05 | [Verified Fact] |
| C3 policy / rules | `hub/policy/withdrawal.py` (new), `hub/policy/service.py`, `hub/policy/clocks.py` | POLICY_WITHDRAWN (ZH-10), effective-status overlay, overlap window | DW-07 | [Verified Fact] |
| C5 Zone H gate | `hub/security/zone_h.py` (new), `hub/gate/service.py`, `hub/policy/gate.py`, `hub/security/authz.py`, `hub/gate/actions.py` | one holder rule; ZH-10 op `withdraw_policy` | DW-06, DW-07 | [Verified Fact] |
| C2 decision record | `hub/decision/service.py` | closing_set skips a withdrawn CLOSURE version | DW-07 | [Verified Fact] |
| C9 metrics | `hub/metrics/service.py` | `detail.policy_withdrawal` on values computed after a withdrawal | DW-07 | [Verified Fact] |
| C10 reviewer support | `hub/review/producer.py` (new), `hub/web/cli.py` (`produce-traces`) | automatic rule-trace producer; flag trail | DW-08 | [Verified Fact] |
| R2 consistency | `hub/r2/consistency.py` | withdrawn CONSISTENCY version skipped in a run | DW-07 | [Verified Fact] |
| persistence (M006 check) | `hub/store/m006.py` (new), `hub/web/schema.py`; users `hub/gate/dispositions.py`, `hub/review/service.py`, `hub/search/schema.py` | M006 presence/drift check outside the HTTP layer | DW-06 | [Verified Fact] |
| core errors | `hub/core/req_errors.py` (new), `hub/web/errors.py` (re-export) | E-REQ-INVALID defined in core | DW-06 | [Verified Fact] |
| hygiene | `hub/metrics/cli.py`, `hub/policy/cli.py`, `hub/security/auth.py`, `hub/web/server.py`, `hub/web/ui.py` | 12 pyflakes findings removed | DW-06 | [Verified Fact] |
| test infrastructure | `tests/hub/regression_groups.json`, `_groups.py`, `run_hub_groups.py` (new); `_driver.py --shard` | regression as data; TST-CO-03 selected; group C split | DW-02, DW-03 | [Verified Fact] |

### CM-2 Structure before / after (same AST method as Stage 16; validated: reproduces Stage 16's 6 / 10 cycles and ruff's 11 C901 and 12 pyflakes findings on main 41098c0)
| Measure | main 41098c0 | stage-20 | Tag |
|---|---|---|---|
| module-level 2-package cycles | 6 | 4 (gate<->web, review<->web removed) | [Verified Fact] |
| module-level 3-package cycles | 10 | 6 | [Verified Fact] |
| domain modules importing hub.web | 4 files | 0 | [Verified Fact] |
| copies of the Zone H holder rule | 3 | 1 (`hub/security/zone_h.py`) | [Verified Fact] |
| pyflakes F401/F841 findings | 12 | 0 (10 checker false positives in a nested class body remain, documented) | [Verified Fact] |
| functions with McCabe > 15 | 11 | 10 (`golden/run.run` 16 -> below 15) | [Verified Fact] |
Remaining cycles (`decision<->gate`, `gate<->runs`, `ops<->store`, `r2<->search` and six 3-cycles) are rooted in `decision.service -> gate.service` and the R2/search pairing; target 0 was an Assumption (A-18-DB-4) and is not met (see Unresolved Issues).

## Evidence References
`docs/20-application/evidence/static-checks-main-41098c0.json`, `static-checks-stage20.json` (reproduce: `python3 -B docs/20-application/evidence/s20_static_checks.py <root>`); `git diff --name-status main` on the branch; `tests/hub/non_add_edits.json`.

## Assumptions
- A-20-CM-1 [Assumption] The R2 HTTP surface (`hub/r2/api.py`, `web.py`, `cli serve`) is an HTTP layer, so its `hub.web` imports are not a domain leak; the server entry decision is DQ-08 / DW-30. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-20-CM-1 Whether a cycle count of 0 is required (A-18-DB-4); owner Engagement lead (Dinesh Naik), Stage 27.

## Unresolved Issues
- UI-CM-1 Package cycles 4 + 6 remain (S16-D06 partially closed); breaking `decision -> gate` needs moving the transition-time holder check, a larger refactor deferred to Stage 27 (DW-29 neighbourhood).
- UI-CM-2 Ten functions remain above McCabe 15 (S16-D08 partially closed); refactoring frozen core logic without a test-backed need was judged riskier than the debt.

## Residual Risks
- RR-CM-1 23 frozen hub files were edited (listed, test-gated); review burden at PR time (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
