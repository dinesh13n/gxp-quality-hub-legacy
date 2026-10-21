---
stage: "21 — Enterprise Integration"
artifact: "adapter-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/14-transformation/adapter-strategy.md (AD-01..AD-08)", "hub/adapters/legacy_sqlite.py, baseline_pins.json, intake_sources.py, gateway_client.py, legacy_captures.py", "hub/policy/asfound.py", "hub/search/corpus.py", "hub/intake/cli.py", "hub/runs/sources.py", "tests/hub/test_tst_co_04_readonly_adapters.py", "tests/hub/test_tst_co_05_legacy_paths_unchanged.py", "tests/hub/test_tst_hub_stg21_integration.py S02, S03, S06", "docs/21-integration/evidence/test-runs-laptop.json", "docs/21-integration/evidence/legacy-paths-and-checksums.txt"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Stage 21 implemented no new adapter and changed no adapter (DI-05 is evidence-only; no defect was found that would justify a code change).**

## Summary
All eight adapters of the Stage 14 strategy exist and are one-directional, legacy -> hub, read-only. **DW-12 is re-proven at the integration stage**: TST-CO-04 (6/6) and TST-CO-05 (3/3) green on the reference laptop; `git diff baseline-as-found` on every legacy path is empty; the backup checksum manifest is rc 0 before and after every run; STG21 S06 shows every file of the FX-BASE125 copy byte-identical after a full shadow intake of all four sources and a live pull from the stub; a static check shows the adapters open files only for reading and connect to SQLite in exactly one module.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AM-1 Adapter map
| AD | Integration (inventory) | Module | Reads | Read-only mechanism | Auth (see authentication-map) | Failure behaviour | Tests (Stage 21 run) | Tag |
|---|---|---|---|---|---|---|---|---|
| AD-01 | INT-01 | `hub/adapters/legacy_sqlite.py` | `legacy.sqlite3` | per-run snapshot copy, `mode=ro&immutable=1`, write-refusing authorizer, sha256 + schema pins | filesystem (host operator) | drift / hash mismatch -> fail closed (E-CO-LEGACY-SCHEMA-DRIFT / E-FX-HASH); working-tree source refused | TST-CO-04 a-f ok; S06 ok | [Verified Fact] |
| AD-02 | INT-02 | same | `enterprise_legacy.sqlite3` | same | same | same | TST-CO-04 ok | [Verified Fact] |
| AD-03 | INT-03/04/05 | `hub/adapters/intake_sources.py` (`partner_feed_deliveries`, `source_message_deliveries`, `gateway_inbox_deliveries`) over an AD-01 handle | `partner_feeds`, `source_messages`, `gateway_inbox` (identity / payload columns only; legacy status never read as truth) | AD-01 handle | as AD-01 | malformed items are classified, never raised | TST-INT-01..16 (09-16 re-run ok); S01, S06 | [Verified Fact] |
| AD-04 | INT-06 | `hub/adapters/gateway_client.py` | loopback `GET /api/events` | GET only, no body, no redirect, no proxy, 5 MiB cap; offsets in hub tables | none sent (stub has none) | bounded retry + back-off; then E-INT-SOURCE-UNREACHABLE -> RUN_FAILED, no item | S02 (live stub), S03, S04; TST-INT-25/26; INC06 S09 | [Verified Fact] |
| AD-05 | INT-07 | `hub/adapters/intake_sources.py` (`vendor_csv_deliveries`) | CSV by header names, `amount` as text | `open(path, "rb")`; `csv_path()` puts the legacy root through the sandbox guard | filesystem | blank / negative / unparsable values -> reason codes | TST-INT-27; S01, S06 | [Verified Fact] |
| AD-06 | INT-08 | `hub/policy/asfound.py`, `as_found_pins.json` | none at runtime (rule sets transcribed as data) | no import of legacy code (IF-1 rule 3) | n/a | n/a | TST-CO-03 (orchestrator regression) | [Verified Fact] |
| AD-07 | INT-09 | `hub/search/corpus.py` | `data/documents/`, archive documents | read files; content is data (untrusted) | filesystem | planted strings inert (PNFR-13) | TST-NFR G9 (orchestrator regression) | [Verified Fact] |
| AD-08 | INT-10 | `hub/adapters/legacy_captures.py` | INC-01 golden captures after MANIFEST check | read files | filesystem | missing / altered capture -> NOT-RUN, exit 6 | TST-CO-01/02 (orchestrator regression) | [Verified Fact] |

### AM-2 DW-12 acceptance
| Criterion (Stage 18) | Result | Evidence | Tag |
|---|---|---|---|
| TST-CO-04 green | 6 / 6 ok | `evidence/test-runs-laptop.json` | [Verified Fact] |
| TST-CO-05 green (incl. c: only allow-listed edits vs main) | 3 / 3 ok | same; `tests/hub/non_add_edits.json` (Stage 21) | [Verified Fact] |
| 0 legacy writes | FX-BASE125 copy byte-identical (S06); working-tree `data/` = backup (checksum rc 0) | S06; `evidence/legacy-paths-and-checksums.txt` | [Verified Fact] |
| `git diff baseline-as-found -- app legacy_* sql data` empty | empty (also `services integration contracts scripts ops`) | same | [Verified Fact] |
| checksum rc 0 | rc 0 before / after every run | runner output, same file | [Verified Fact] |

### AM-3 Static adapter properties (STG21 S06, S03)
- [Verified Fact] Every `open()` in `hub/adapters/*.py` has a read mode; `sqlite3.connect` appears only in `legacy_sqlite.py` (behind the RO URI and authorizer).
- [Verified Fact] `gateway_client.py` builds no `Request`, passes no `data=` / `method=`, calls no `urlopen` / `post` / `put`: the only operation is an idempotent GET, so retrying it cannot duplicate a side effect (stage guardrail "do not retry non-idempotent operations").

## Evidence References
- `evidence/test-runs-laptop.json`, `evidence/legacy-paths-and-checksums.txt`, `evidence/gateway-stub-conformance.json`.

## Assumptions
- A-21-AM-1 [Assumption] Running the unchanged legacy stub `services/source_gateway/server.py` from the sandbox code copy against a scratch DB copy is within the Stage 0B sandbox boundary (OD-03a: any execution in a full copy outside the working tree). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-AM-1 Adapters for real systems (MES / LIMS / QMS APIs, SFTP, message brokers) - not needed for R1 and no system exists; Engagement lead (Dinesh Naik).

## Unresolved Issues
- None for DW-12.

## Residual Risks
- RR-21-AM-1 AD-06..AD-08 were not re-run by the build agent (OD-23 test split); they run in the orchestrator's full regression before merge (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
