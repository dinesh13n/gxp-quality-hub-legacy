---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "inc04-design-notes.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-04 policy & rule service (C4, ADR-007, F03, AD-06, M002)"
evidence_sources: ["docs/12-specs/features/f03-policy-definitions-rule-service.md", "docs/10-architecture/adrs/ADR-007-policy-and-rule-service.md", "docs/14-transformation/transformation-backlog.md TB-12", "docs/14-transformation/adapter-strategy.md AD-06", "docs/14-transformation/schema-migration-plan.md M002", ".fde/orchestrator-decisions.md OD-03a, OD-08, OD-12, OD-14, OD-15, OD-16", "docs/14-transformation/evidence/increment-test-map.csv"]
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved.**

## Summary
Design decisions for INC-04, written before the code so a dead session leaves the reasoning on the branch.
The rule service ships **no active rule set** (OD-16 / OD-S12-04). The three as-found rule sets are loaded as
named, versioned, read-only, **inactive** candidates. Activation is refused without a recorded human decision in
the INC-03 audit chain. No model call, no new dependency (ADR-002, OD-08).

## Findings
| # | Decision | Reason | Tag |
|---|---|---|---|
| D-01 | New package `hub/policy/` (add-only; `hub/core/errors.py`, `hub/store/*.py`, `hub/security/*.py`, `hub/cli.py` are frozen by TST-CO-05 c). Own CLI `python -m hub.policy`. | Add-only rule; same pattern as INC-03 (`hub.admin`). | [Verified Fact] rule; [Inference] pattern |
| D-02 | **M002 is applied by `hub.policy.schema`, not by `hub.store.migrate`.** The file lives in `hub/policy/migrations/` and is recorded in its own table `policy_schema_migrations` (sha256, insert-only), after a backup-before-migrate. | A file in `hub/store/forward/` becomes part of `migrate.known_versions()` and makes the INC-03 test S01 (`applied == ["M001"]`) fail; that test and `migrate.py` cannot be edited (TST-CO-05 c). Recorded as DEV-28 / RTD-37: fold M002 into the main runner at Stage 16/17 with a one-line test update. | [Verified Fact] constraint; [Inference] solution |
| D-03 | Tables = DDL v0.1 verbatim (`policy_object`, `policy_events`, `rule_set`, `rule_row`, `active_ruleset`) plus immutability triggers on `rule_set`/`rule_row` (edit = new version) and a hold-all delete guard. | AC-POL-25, OD-S12-09 / OD-15. | [Inference] |
| D-04 | Rule set content is **data**: `rule_row.outcome` is a JSON object `{function, kind, ...}` with kind `rule` / `domain` / `param` / `register`; `conditions` use the schema ops (`eq,in,gt,gte,lt,lte,starts_with,is_null,not_null`); a value may be `{"$input": name}` (schema allows any value). | DDL has no domain/param columns; avoids a DDL change. | [Inference] |
| D-05 | `hub/policy/engine.py` is a pure function module (imports only `decimal`, `re`): no clock, I/O, randomness, DB. | AC-POL-22, BEH-POL-06. | [Inference] |
| D-06 | Numbers: `Decimal` parsed from int / float (via `repr`) / strict numeric string; bool, NaN, infinity, None, other strings -> `E-POL-INPUT-INVALID` (BEH-POL-11). | AC-POL-23; changes as-found JS behaviour for 'abc'/null (golden `js_policy_table.allows`), recorded as DEV-30 (OD-S12-13, mode B). | [Verified Fact] golden; [Inference] |
| D-07 | `defaulted` marker: row flagged `is_default` (JS 999999 row) -> `NO_MATCH_REGION_YEAR`; input outside a declared domain -> `UNKNOWN_INPUT_VALUE`; null domain input -> `NULL_INPUT`. The PRIORITY catch-all `queue` row is an ordinary row (AC-POL-21: known LOW/OPEN -> `defaulted=false`). | AC-POL-19/20/21. | [Verified Fact] spec |
| D-08 | `as-found-batch` takes the row-level predicate only (status in {HOLD,REVIEW} or value > threshold); threshold is an input, or looked up by (region, policy_code) in the 40 loaded `policy_register` rows with `active = 1`. One result per input: the legacy row-multiplying JOIN (BB-07) is not reproduced. Legacy ignores `valid_from`/`valid_to`; so does the set. | AC-POL-15, OD-S12-13. | [Verified Fact] |
| D-09 | Loader (AD-06): reads `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json` as **text/data** (sha256-pinned in `hub/policy/as_found_pins.json`; constants cross-checked by AST/regex; never imported/executed) and `enterprise_legacy.sqlite3` through the INC-02 read-only snapshot adapter. Idempotent: same content hash -> no-op; different -> `E-POL-ASFOUND-DRIFT`. | A-14-07, adapter-strategy AS-2. | [Inference] |
| D-10 | **Recorded human decision** = audit record `POLICY_DECISION_RECORDED` (actor human, Zone H holder, `details = {decision: "activate", function, ruleset_ref, authority_ref, reason}`) written by `record_activation_decision`. `activate` takes its `audit_seq`, re-reads the row, requires: action/outcome/actor_kind/object_ref match, actor still a configured holder, decision not already consumed, and `audit.verify` of the chain `ok`; else `E-POL-DECISION-REQUIRED`. The activating session must itself pass the Zone H check. `RULESET_ACTIVATED` / `RULESET_DEACTIVATED` go to `policy_events` and, in the same transaction, the hash-chained audit log. Deactivation needs a holder + `authority_ref` (risk-reducing) but no prior decision. | OD-16: "activation requires a recorded human decision". | [Inference] |
| D-11 | Zone H eligibility (no gate service until INC-05): human + role `dispositioner` + in `zone_h.holders` + re-auth within window; empty holder list -> `E-GATE-NO-HOLDERS`; otherwise `E-GATE-NOT-AUTHORISED`; every attempt audited `ZONE_H_ATTEMPT`. | F02 / AC-GATE-02, AC-GATE-09. | [Inference] |
| D-12 | Out of the 25 tests, not built: divergence report (BEH-POL-10, AC-POL-24 is R2 and not in the INC-04 test map), policy withdrawal (BEH-POL-05 mentions it; `status` enum has no withdrawn value), HTTP routes (no server yet). | Scope = test map. | [Verified Fact] |

## Evidence References
See header. Test map: `docs/14-transformation/evidence/increment-test-map.csv` (25 INC-04 rows: TST-CO-03, TST-POL-01..23, TST-POL-25).

## Assumptions
- A-15-04-1 [Assumption] Recording a decision as an audit-chain record satisfies "recorded human decision" (OD-16). Confirm: Engagement lead (Dinesh Naik).
- A-15-04-2 [Assumption] Holders are the humans listed in `zone_h.holders` (empty by default, OD-S12-06 open); tests use explicit synthetic holders.

## Unknowns
- U-15-04-1 Which of the three rules is correct (OPD-04 / RC-4); the service does not say.

## Unresolved Issues
- OD-S12-04 authority for activation; OD-S12-13 preserve vs fix for input validation.

## Residual Risks
- A reader could take a loaded as-found set as "the" rule. Every result carries `authoritative` and every set is inactive.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-04 design notes. |
