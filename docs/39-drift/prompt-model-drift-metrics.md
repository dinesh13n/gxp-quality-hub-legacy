---
stage: "39 — Drift + Continuous Improvement"
artifact: "prompt-model-drift-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["hub/cli.py (no-ai-check, selfcheck)", "hub/guards/", "hub/obs/alerts.py ALT-01 ALT-02", "hub/obs/slo.py INV-01 INV-02", "hub/policy/as_found_pins.json", "hub/policy/rulesets.py", "hub/runtime.py", "Dockerfile", "pyproject.toml", "tests/characterization/ (CT-13)", "docs/08-ai-qualification/qualification-decision.md", "docs/19-intelligence/", "docs/26-tevv/release-thresholds.md RT-05, RT-14", "docs/24-security-privacy/security-test-results.md", ".fde/orchestrator-decisions.md (OD-08, OD-14, OD-16, OD-24, OD-25, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
There is no prompt and no model in the product (OD-08; Stage 19 and 22 not applicable). Applied to this layer, drift means three things: (1) **introduction drift**: any model call, egress, AI dependency or prompt-like artefact appearing at all is drift, tracked by the Stage 26/31 tripwires; (2) **decision-logic drift**: the rule sets and decision policies are the product's "model", and they drift when their sources or activation state change; (3) **runtime/dependency drift**: interpreter, SQLite, Node and container-image versions, including two concrete cases already present (the CT-13 Node patch drift and the Python 3.10 end of life). Coding assistants used to build the system are development tooling, not product AI (OD-08); their changes are covered by `agent-drift-metrics.md`.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PM-1 Introduction drift (tripwires, zero tolerance)
| ID | Metric | Source | Threshold | Tier | State |
|---|---|---|---|---|---|
| PM-01 | `model_calls_total` | Stage 31 metric; ALT-01; INV-01; Stage 26 RT-05 | > 0 (and absent metric also fires) | incident (SEV-B), not a drift event; stop the release | [Verified Fact] alert and invariant exist |
| PM-02 | `egress_attempts_total` | ALT-02; INV-02; hub egress guard installed on every `python -m hub` invocation | > 0 | incident (SEV-B) | [Verified Fact] |
| PM-03 | `python -m hub no-ai-check` | dependency/import deny-list scan; exit 9 on findings | rc != 0 | CHANGE blocked until explained; any hit is C7 (AI introduction needs a new Dinesh decision plus re-qualification RQ-1..RQ-3) | [Verified Fact] command exists |
| PM-04 | Non-stdlib imports under `hub/` | scan (Stage 26 RT-05 requires 0); `pyproject.toml` dependency list | any new third-party import or dependency | CHANGE (C6 toolchain) with ADR | [Verified Fact] RT-05 declared; [Inference] same scan reusable |
| PM-05 | AI re-qualification triggers | RQ-1..RQ-3 in `docs/08-ai-qualification/qualification-decision.md` | any trigger observed (e.g. a request for AI-assisted document Q&A, T3) | CHANGE (C7) | [Verified Fact] triggers exist; [Unknown] none has fired |

### PM-2 Decision-logic drift (the product's "model")
| ID | Metric | Source | Threshold | Tier | State |
|---|---|---|---|---|---|
| PM-06 | As-found source pins | sha256 of `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json` versus `hub/policy/as_found_pins.json` | any difference | INVESTIGATE; the file says "Changing a pin = reviewed PR" | [Verified Fact] |
| PM-07 | Active rule sets | count of rule sets with active = true (policy store; shipped value 0, OD-16) and `zone_h.holders` list (shipped EMPTY, OD-17/OD-31) | active count > 0 or holders non-empty without a recorded decision and `approval_ref` | CHANGE class C4 (RL-03 proposes, RL-04 activates, both VACANT; refused today) | [Verified Fact] shipped values; ALT-03 covers non-human Zone H acceptance |
| PM-08 | Decision defaults | `defaulted_outputs_total` (FR-POL-06) by function | candidate: any increase vs previous evaluation window once traffic exists | WATCH then INVESTIGATE | [Verified Fact] metric implemented; [Unknown] baseline (no traffic) |
| PM-09 | Characterization drift | `tests/characterization/run_characterization.py` and `python -m hub golden-compare` | any new failing CT beyond CT-13; golden-compare exit 6 is the DESIGNED state while DV-01..09 preserve-or-fix is open (OD-15) | INVESTIGATE; do not edit goldens (TST-CO-05 c rejects harness edits) | [Verified Fact] 133/134, CT-13 only |
| PM-10 | Decision-flag state | `capability_authority`, `disposition.mode`, `schedule.enabled`, `network.exposure_approved` and the other closed-schema keys of `hub/config.py` versus the recorded decided values | a safe value changed without `approval_ref` | CHANGE (C3/C5) | [Verified Fact] schema is closed; DW-17 audits CONFIG_CHANGED once live (verified live is [Unknown]) |

### PM-3 Runtime and dependency drift (two live cases)
| ID | Case | Verified Fact | Inference / Unknown | Proposed treatment |
|---|---|---|---|---|
| PM-11 | **CT-13 Node patch drift** (`batch:node_cwd_other`) | golden captured with Node v22.23.2; laptop has v22.23.4; the stderr tail differs; 133/134 pass; cause "environment, not product regression" (S24-DEV-04, `docs/24-security-privacy/security-test-results.md`; confirmed at Stage 26 and 31 evidence) | Inference: harness compares a version-bearing stderr tail byte for byte, so every Node patch release re-opens it. Unknown: whether Java has a comparable sensitivity (not observed). | Do not edit the harness (rejected by TST-CO-05 c). Either pin Node 22.23.2 for the reference environment or re-record the golden under a change record (class C2/C6, Dinesh decides, DQ CT-13 "golden or Node pin" is open). Until decided: register as KNOWN-DRIFT with the exact signature, so any OTHER stderr difference remains visible. |
| PM-12 | **Python 3.10 end of life** | runtime floor is 3.10 (`pyproject.toml` requires-python >=3.10; `hub/runtime.py` DEFAULT_FLOOR "3.10"); the reference laptop runs 3.10.12; `Dockerfile` uses `python:3.12-slim`; Dinesh decided production targets 3.12+ with the 3.10 floor kept (OD-24); Stage 26 RT-14 and the C6 class require green on both; no 3.12+ regression evidence exists (OD-33); goldens are environment-specific (10/16 CT checks differ on 3.13 by environment only, OD-23) | Inference (public release schedule, PEP 619, not verified in this session): Python 3.10 reaches end of life at the end of October 2026, i.e. about a week after this run date; after that date the floor interpreter receives no security fixes. Unknown: exact date to be confirmed by Dinesh from python.org; whether any host will run 3.10 after that date (none is in production). | Treat as a dated trigger, not a metric (see `change-trigger-thresholds.md` TRG-04): obtain 3.12+ regression and characterization evidence, decide whether the floor moves, and re-baseline goldens under a change record. Stage 27 D-27-02 (Python 3.12 floor) is the open decision. No code change is made here. |
| PM-13 | SQLite / FTS5 version | floor SQLite 3.37 (OD-14); `selfcheck` prints versions | Unknown: version on any future host | `python -m hub selfcheck` result recorded with each evaluation |
| PM-14 | Container base image | `Dockerfile` `FROM python:3.12-slim` (legacy Dockerfile/compose hardening is a Stage 30 item, D-27-06) | Inference: an unpinned minor tag drifts with every rebuild; digest pinning is a hardening choice | candidate: record the image digest at any build; change via C6 |
| PM-15 | Toolchain inventory | `selfcheck` plus `node --version`, `java -version` captured by the harness (`run_characterization.py` records python/sqlite/java/node) | record only | WATCH; INVESTIGATE when a recorded version differs from the previous evaluation |

## Evidence References
See header. Result data: `docs/26-tevv/evidence/characterization-final-output.txt` (CT-13 only failure), `docs/31-observability/evidence/results.json` ("133/134 CT checks passed").

## Assumptions
- A-39-09 End of life of Python 3.10 is end of October 2026 (public schedule, not verified here). Confirm: Dinesh (python.org release schedule).
- A-39-10 Reading rule sets and decision flags as the product's "model" is a framing choice for governance, not a claim that they are learned.

## Unknowns
- U-39-07 Which interpreter any future host will run; whether the 3.12 move happens before or after 3.10 EOL (D-27-02 open).
- U-39-08 Whether Node/Java are needed at all after cutover (legacy JS/Java run only for characterization; HAR-05).

## Unresolved Issues
- CT-13 decision (golden or Node pin); Python 3.12+ evidence (RT-14); D-27-02. All route to Dinesh; none decided here.

## Residual Risks
- RR-39-07 After the 3.10 end-of-life date the floor stays supported by the code but not by the interpreter vendor. Medium (no production host exists; High if one is created before the decision).
- RR-39-08 A permanently red CT-13 normalises red; a second real drift could hide behind it. Medium. Mitigation: signature-specific known-drift entry (PM-11).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
