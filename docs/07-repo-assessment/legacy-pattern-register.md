---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "legacy-pattern-register.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "scripts/*.py", "compose.yaml", "Dockerfile", "docs/07-repo-assessment/evidence/analysis/static_analysis.json", "docs/05-current-state/dependency-hotspots.md"]
supersedes: "none"
---
## Summary

Twenty-two legacy patterns (LP-01..LP-22). The repository is described by its own authors as an intentionally "old-fashioned" estate (`app/partner_feeds.py` docstring: "Intentionally retains procedural design and mutable shared records typical of older systems"; `app/historical_estate.py`: "Deliberately old-fashioned batch integration"). Patterns below are what a modernisation must recognise; whether each is a *defect to remove* or a *behaviour to preserve* is stated in the last column using the baseline principle (preserve until a decision says otherwise).

## Findings

| ID | Pattern | Where (evidence) | Why it is legacy / risk | Modernisation stance | Class | Confidence |
|---|---|---|---|---|---|---|
| LP-01 | **Shared database as integration bus** | `data/legacy.sqlite3` used by 7 processes (DM-10) | Tight coupling by schema, no contracts, lock contention | Preserve behaviour via characterisation; introduce interfaces in Stage 14 | [Verified Fact] | High |
| LP-02 | **Import-time global configuration** | `app/store.py` L4 `DB=Path(os.environ...)`; JSON configs loaded at import in server, partner_feeds, gateway_bridge, operational_report | Config cannot change after import; breaks test isolation (TQ-01) | Replace with injected settings | [Verified Fact] | High |
| LP-03 | **Hard-coded repo-relative file paths** | `Path(__file__).resolve().parents[1]/'data'` in 6 modules; cwd-relative paths in JS, Java docs | Unsafe to run anywhere but repo root; destructive writers | Parameterise paths | [Verified Fact] | High |
| LP-04 | **Procedural scripts with `if __name__=='__main__'` entry points, run manually; no scheduler** | all `app.*` CLIs; `run.sh` | Operator-dependent execution (RC-5) | Preserve run semantics; add orchestration later | [Verified Fact] | High |
| LP-05 | **Mutable in-place status flags on a staging table** | `partner_feeds.processing_status` overwritten by `reconcile` | Loss of history/evidence (RC-6) | Append-only/audit design (decision needed) | [Verified Fact] | High |
| LP-06 | **Business rules duplicated across languages** | Python `legacy_logic.py`, JS `legacy_policy.js`, `shift_reconciliation.py`, Java/SQL totals | Divergent decisions (RC-4, RC-8) | Single policy source after RC-3 | [Verified Fact] | High |
| LP-07 | **Business logic in the batch job / SQL join** | `shift_reconciliation.py` L9 (eligibility via LEFT JOIN); header comment "business logic remains embedded in this job" | Row multiplication; untestable | Extract rule, keep golden | [Verified Fact] | High |
| LP-08 | **String-built SQL with config-supplied identifiers** | 26 sites flagged (`static_analysis.json` `sql_string_building`): table/column names from constants, `integration/source-gateway.json`, or an allow-list (`server.py` L24, L37); **values are parameterised everywhere checked** | Injection-safe today only because identifiers are trusted; fragile | Keep allow-lists; use quoting helper | [Verified Fact] (sites) / [Inference] (safety) | Medium |
| LP-09 | **Semicolon-compressed, multi-statement one-liners; 1-space and 4-space indent mixed** | 20 files use `;`; 11 files use 1-space indent; max line 922 chars | Review and diff hostile | Automated formatter in a single mechanical commit, after characterisation | [Verified Fact] | High |
| LP-10 | **God handler** | `app/server.py do_GET` 50 lines CC 28; `source_gateway/server.py do_GET` CC 20 | Hard to test/extend | Router decomposition | [Verified Fact] | High |
| LP-11 | **Copy-paste duplication** | pagination clamp 3x in `app/server.py`; domain constant dicts per generator; README section repeated 3x | Divergent fixes | Extract helper | [Verified Fact] | High |
| LP-12 | **Silent error swallowing / count-and-continue** | Java `catch(NumberFormatException ignored)`; bridge `invalid+=1;continue`; `operational_report` `except Exception: inbox=0`; broad `except` at 4 sites (`operational_report`, `offline_inventory` x2, `smoke`) | Failures vanish; no audit | Emit rejects to quarantine (design decision) | [Verified Fact] | High |
| LP-13 | **File-drop batch integration (CSV/JSONL) with raw retention and digest idempotency** | `historical_estate.py` | Typical pre-API pattern; idempotent by whole-file hash only (one byte difference = new import) | Preserve semantics | [Verified Fact] | High |
| LP-14 | **Polling bridge with offset checkpoint** | `gateway_bridge.py` (`gateway_checkpoints`) | At-least-once; offset advanced after apply; no retry/backoff | Preserve; add retry policy by decision | [Verified Fact] | High |
| LP-15 | **Float money and positional parsing** | Java `double`, SQL `REAL` sums, `parts[4]` | Precision/column-order risk (latent on current data) | Decimal types; named columns | [Verified Fact] | High |
| LP-16 | **Default-allow fallbacks** | JS threshold 999,999; `priority()` unknown -> `queue`; gateway unknown failure mode -> 200 normal | Unsafe defaults in a GxP context | Fail-closed by decision (needs RC-3) | [Verified Fact] | High |
| LP-17 | **Synthetic data in the application tree and git-ignored data directory** | `data/` 1,512 files, 55 MB; `*.sqlite3` and `data/lake/` git-ignored | Baseline lives outside version control (backup only) | Keep backup/hash gate (OD-03/03a) | [Verified Fact] | High |
| LP-18 | **Environment switching via example env files, no loader** | `environments/*.env.example` | Profiles not wired | Config layer | [Verified Fact] | High |
| LP-19 | **Polyglot ad-hoc tooling without build files** | Java source-launch, Node script, SQL file executed by hand | No reproducible build | Decide whether to retain or port | [Verified Fact] | High |
| LP-20 | **Documentation as source of truth for rules** | `domain-assurance.md`, `contracts/decision-policies-archive.json` (roles, limits) not wired to code | Policy and code diverge | Policy-as-data | [Verified Fact] | High |
| LP-21 | **DDL on read paths / lazy schema creation** | `server.py` L26-27 (`init()` per partners request), `setup()` at start | Side effects on GET | Migration step | [Verified Fact] | High |
| LP-22 | **Static stand-ins for operational data** | `/api/incidents` literal; `GET /health` static | False assurance | Replace with real checks | [Verified Fact] | High |

## Evidence References

`evidence/analysis/static_analysis.json` (`findings.sql_string_building`, `broad_except`, `files.*`); code references as listed; `docs/05-current-state/dependency-hotspots.md` DH-01..DH-10.

## Assumptions

- A-07-13: "Legacy pattern" classification follows common modernisation practice; some patterns (LP-04, LP-13) are valid for a training estate and are flagged only because they constrain refactoring.

## Unknowns

- Whether any pattern is relied upon by an undocumented consumer (U-19).

## Unresolved Issues

- Stance column items marked "by decision" require RC-3/Stage 8 outcomes.

## Residual Risks

- R-07-10: Removing a "legacy" behaviour that is actually relied upon (e.g. fail-open thresholds, count-and-continue) without the golden baseline would change outputs silently.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial pattern register. |
